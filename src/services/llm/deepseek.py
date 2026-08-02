import json
import logging
import time
from typing import Any, AsyncIterator, Dict, List, Optional

import httpx
from langchain_deepseek import ChatDeepSeek

from src.config import Settings
from src.exceptions import DeepSeekConnectionError, DeepSeekException, DeepSeekTimeoutError
from src.services.llm.base import LLMClient
from src.services.llm.prompts import RAGPromptBuilder

logger = logging.getLogger(__name__)


class DeepSeekClient(LLMClient):
    """Client for interacting with the DeepSeek API (OpenAI-compatible chat completions)."""

    def __init__(self, settings: Settings):
        self.base_url = settings.deepseek_base_url.rstrip("/")
        self.api_key = settings.deepseek_api_key
        self.timeout = httpx.Timeout(float(settings.deepseek_timeout))

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def health_check(self) -> Dict[str, Any]:
        """Check if the DeepSeek API is reachable and the API key is valid."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/models", headers=self._headers())

                if response.status_code == 200:
                    return {"status": "healthy", "message": "DeepSeek API is reachable"}
                elif response.status_code == 401:
                    raise DeepSeekException("DeepSeek API key is invalid")
                else:
                    raise DeepSeekException(f"DeepSeek returned status {response.status_code}")

        except httpx.ConnectError as e:
            raise DeepSeekConnectionError(f"Cannot connect to DeepSeek API: {e}")
        except httpx.TimeoutException as e:
            raise DeepSeekTimeoutError(f"DeepSeek API timeout: {e}")
        except DeepSeekException:
            raise
        except Exception as e:
            raise DeepSeekException(f"DeepSeek health check failed: {str(e)}")

    async def generate(self, model: str, prompt: str, stream: bool = False, **kwargs: Any) -> Optional[Dict[str, Any]]:
        """Generate text using the DeepSeek chat completions endpoint.

        Returns a dict shaped like the Ollama client's response (with a top-level
        ``response`` field and a ``usage_metadata`` dict), so downstream callers
        (RAGPromptBuilder-based flows, routers) don't need to branch on provider.
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                data = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": stream,
                    **{k: v for k, v in kwargs.items() if k not in ("format",)},
                }

                logger.info(f"Sending request to DeepSeek: model={model}, stream={stream}")
                start_time = time.time()
                response = await client.post(f"{self.base_url}/chat/completions", json=data, headers=self._headers())
                latency_ms = round((time.time() - start_time) * 1000, 2)

                if response.status_code != 200:
                    raise DeepSeekException(f"Generation failed: {response.status_code} {response.text}")

                result = response.json()
                choice = result["choices"][0]
                answer_text = choice["message"]["content"]
                usage = result.get("usage", {})

                usage_metadata = {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                    "latency_ms": latency_ms,
                }

                return {"response": answer_text, "usage_metadata": usage_metadata}

        except httpx.ConnectError as e:
            raise DeepSeekConnectionError(f"Cannot connect to DeepSeek API: {e}")
        except httpx.TimeoutException as e:
            raise DeepSeekTimeoutError(f"DeepSeek API timeout: {e}")
        except DeepSeekException:
            raise
        except Exception as e:
            raise DeepSeekException(f"Error generating with DeepSeek: {e}")

    async def generate_stream(self, model: str, prompt: str, **kwargs: Any) -> AsyncIterator[Dict[str, Any]]:
        """Generate text with a streaming response (Server-Sent Events)."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                data = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": True,
                    **{k: v for k, v in kwargs.items() if k not in ("format",)},
                }

                logger.info(f"Starting streaming generation: model={model}")

                async with client.stream(
                    "POST", f"{self.base_url}/chat/completions", json=data, headers=self._headers()
                ) as response:
                    if response.status_code != 200:
                        raise DeepSeekException(f"Streaming generation failed: {response.status_code}")

                    async for line in response.aiter_lines():
                        line = line.strip()
                        if not line or not line.startswith("data:"):
                            continue
                        payload = line[len("data:"):].strip()
                        if payload == "[DONE]":
                            yield {"response": "", "done": True}
                            break
                        try:
                            chunk = json.loads(payload)
                            delta = chunk["choices"][0].get("delta", {})
                            text = delta.get("content", "")
                            yield {"response": text, "done": False}
                        except (json.JSONDecodeError, KeyError, IndexError):
                            logger.warning(f"Failed to parse streaming chunk: {payload}")
                            continue

        except httpx.ConnectError as e:
            raise DeepSeekConnectionError(f"Cannot connect to DeepSeek API: {e}")
        except httpx.TimeoutException as e:
            raise DeepSeekTimeoutError(f"DeepSeek API timeout: {e}")
        except DeepSeekException:
            raise
        except Exception as e:
            raise DeepSeekException(f"Error in streaming generation: {e}")

    async def generate_rag_answer(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        model: str,
        use_structured_output: bool = False,
        domain: str = "ai",
    ) -> Dict[str, Any]:
        """Generate a RAG answer using retrieved chunks.

        ``use_structured_output`` is accepted for interface parity with the
        Ollama client, but DeepSeek's chat completions endpoint does not
        support Ollama-style ``format`` JSON schemas, so this always uses
        the plain-text prompt path.
        """
        try:
            prompt = RAGPromptBuilder(domain).create_rag_prompt(query, chunks)
            response = await self.generate(model=model, prompt=prompt, temperature=0.7, top_p=0.9)

            if not response or "response" not in response:
                raise DeepSeekException("No response generated from DeepSeek")

            answer_text = response["response"]

            # arXiv chunks are cited by PDF URL; bilingual domain chunks (education/
            # accounting) don't have a PDF URL, so cite by document number/id instead.
            sources = []
            seen = set()
            for chunk in chunks:
                arxiv_id = chunk.get("arxiv_id")
                if arxiv_id:
                    arxiv_id_clean = arxiv_id.split("v")[0] if "v" in arxiv_id else arxiv_id
                    source = f"https://arxiv.org/pdf/{arxiv_id_clean}.pdf"
                else:
                    doc_ref = chunk.get("doc_number") or chunk.get("doc_id")
                    source = f"doc:{doc_ref}" if doc_ref else None
                if source and source not in seen:
                    sources.append(source)
                    seen.add(source)

            citation_ids = [chunk.get("arxiv_id") or chunk.get("doc_number") or chunk.get("doc_id") for chunk in chunks]
            citations = list({c for c in citation_ids if c})

            return {
                "answer": answer_text,
                "sources": sources,
                "confidence": "medium",
                "citations": citations[:5],
            }

        except Exception as e:
            logger.error(f"Error generating RAG answer: {e}")
            raise DeepSeekException(f"Failed to generate RAG answer: {e}")

    async def generate_rag_answer_stream(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        model: str,
        domain: str = "ai",
    ) -> AsyncIterator[Dict[str, Any]]:
        """Generate a streaming RAG answer using retrieved chunks."""
        try:
            prompt = RAGPromptBuilder(domain).create_rag_prompt(query, chunks)
            async for chunk in self.generate_stream(model=model, prompt=prompt, temperature=0.7, top_p=0.9):
                yield chunk
        except Exception as e:
            logger.error(f"Error generating streaming RAG answer: {e}")
            raise DeepSeekException(f"Failed to generate streaming RAG answer: {e}")

    def get_langchain_model(self, model: str, temperature: float = 0.0) -> ChatDeepSeek:
        """Return a LangChain-compatible DeepSeek chat model for use in LangGraph nodes."""
        return ChatDeepSeek(
            model=model,
            temperature=temperature,
            api_key=self.api_key,
            api_base=self.base_url,
            timeout=self.timeout.read,
        )
