import json
import logging
import re
from typing import Any, Dict, List, Optional

import httpx
from langchain_openai import ChatOpenAI
from src.config import Settings
from src.exceptions import MiniMaxConnectionError, MiniMaxException, MiniMaxTimeoutError
from src.services.ollama.prompts import RAGPromptBuilder, ResponseParser

logger = logging.getLogger(__name__)

# MiniMax models available via OpenAI-compatible API
MINIMAX_MODELS = ["MiniMax-M3", "MiniMax-M2.7", "MiniMax-M2.7-highspeed"]


def _clamp_temperature(temperature: float) -> float:
    """Clamp temperature to MiniMax's accepted range (0.01, 1.0].

    MiniMax API requires temperature > 0 and <= 1.0.
    Values of 0 are clamped to 0.01 for near-deterministic behavior.

    Args:
        temperature: Requested temperature value

    Returns:
        Clamped temperature value
    """
    if temperature <= 0:
        return 0.01
    return min(temperature, 1.0)


def _strip_think_tags(text: str) -> str:
    """Strip <think>...</think> tags from MiniMax responses.

    MiniMax models may include thinking tags in structured output responses.

    Args:
        text: Raw response text

    Returns:
        Text with think tags removed
    """
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


class MiniMaxClient:
    """Client for interacting with MiniMax LLM via OpenAI-compatible API.

    MiniMax provides an OpenAI-compatible API at https://api.minimax.io/v1.
    This client wraps it for use as a drop-in alternative to OllamaClient.

    API Reference: https://platform.minimax.io/docs/api-reference/text-openai-api
    """

    def __init__(self, settings: Settings):
        """Initialize MiniMax client with settings.

        Args:
            settings: Application settings containing MiniMax configuration
        """
        self.base_url = settings.minimax_base_url
        self.api_key = settings.minimax_api_key
        self.default_model = settings.minimax_model
        self.timeout = httpx.Timeout(float(settings.minimax_timeout))
        self.prompt_builder = RAGPromptBuilder()
        self.response_parser = ResponseParser()

    def get_langchain_model(
        self,
        model: Optional[str] = None,
        temperature: float = 1.0,
        **kwargs,
    ) -> ChatOpenAI:
        """Return a LangChain ChatOpenAI model pointing to MiniMax API.

        This is the primary interface used by agent nodes for LLM calls.

        Args:
            model: Model name (defaults to configured model)
            temperature: Generation temperature (clamped to MiniMax range)
            **kwargs: Additional model parameters

        Returns:
            ChatOpenAI instance configured for MiniMax
        """
        return ChatOpenAI(
            model=model or self.default_model,
            api_key=self.api_key,
            base_url=self.base_url,
            temperature=_clamp_temperature(temperature),
            **kwargs,
        )

    async def health_check(self) -> Dict[str, Any]:
        """Check if MiniMax API is reachable via a lightweight chat completions call.

        Returns:
            Dictionary with health status information
        """
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
                # Use a minimal chat completion request to verify connectivity
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.default_model,
                        "messages": [{"role": "user", "content": "hi"}],
                        "max_tokens": 1,
                    },
                )

                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "message": "MiniMax API is reachable",
                        "provider": "minimax",
                    }
                else:
                    raise MiniMaxException(f"MiniMax returned status {response.status_code}")

        except httpx.ConnectError as e:
            raise MiniMaxConnectionError(f"Cannot connect to MiniMax API: {e}")
        except httpx.TimeoutException as e:
            raise MiniMaxTimeoutError(f"MiniMax API timeout: {e}")
        except MiniMaxException:
            raise
        except Exception as e:
            raise MiniMaxException(f"MiniMax health check failed: {str(e)}")

    async def list_models(self) -> List[Dict[str, Any]]:
        """Get list of available MiniMax models.

        Returns:
            List of model information dictionaries
        """
        return [{"id": m, "provider": "minimax"} for m in MINIMAX_MODELS]

    async def generate(
        self,
        model: str,
        prompt: str,
        stream: bool = False,
        **kwargs,
    ) -> Optional[Dict[str, Any]]:
        """Generate text using MiniMax OpenAI-compatible chat API.

        Args:
            model: Model name to use
            prompt: Input prompt for generation
            stream: Whether to stream response (ignored, use generate_stream)
            **kwargs: Additional generation parameters (temperature, top_p, etc.)

        Returns:
            Response dictionary with generated text and usage metadata
        """
        temperature = _clamp_temperature(kwargs.pop("temperature", 1.0))
        # MiniMax does not support response_format; remove if present
        kwargs.pop("format", None)
        kwargs.pop("response_format", None)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "model": model or self.default_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "stream": False,
                }
                # Pass through supported params
                if "top_p" in kwargs:
                    payload["top_p"] = kwargs["top_p"]

                logger.info(f"Sending request to MiniMax: model={payload['model']}")
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )

                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    content = _strip_think_tags(content)
                    usage = data.get("usage", {})

                    return {
                        "response": content,
                        "usage_metadata": {
                            "prompt_tokens": usage.get("prompt_tokens", 0),
                            "completion_tokens": usage.get("completion_tokens", 0),
                            "total_tokens": usage.get("total_tokens", 0),
                        },
                    }
                else:
                    raise MiniMaxException(f"Generation failed: {response.status_code} - {response.text}")

        except httpx.ConnectError as e:
            raise MiniMaxConnectionError(f"Cannot connect to MiniMax API: {e}")
        except httpx.TimeoutException as e:
            raise MiniMaxTimeoutError(f"MiniMax API timeout: {e}")
        except MiniMaxException:
            raise
        except Exception as e:
            raise MiniMaxException(f"Error generating with MiniMax: {e}")

    async def generate_stream(self, model: str, prompt: str, **kwargs):
        """Generate text with streaming response via MiniMax API.

        Args:
            model: Model name to use
            prompt: Input prompt for generation
            **kwargs: Additional generation parameters

        Yields:
            JSON chunks from streaming response
        """
        temperature = _clamp_temperature(kwargs.pop("temperature", 1.0))
        kwargs.pop("format", None)
        kwargs.pop("response_format", None)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "model": model or self.default_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "stream": True,
                }
                if "top_p" in kwargs:
                    payload["top_p"] = kwargs["top_p"]

                logger.info(f"Starting streaming generation: model={payload['model']}")

                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                ) as response:
                    if response.status_code != 200:
                        raise MiniMaxException(f"Streaming generation failed: {response.status_code}")

                    async for line in response.aiter_lines():
                        line = line.strip()
                        if not line or not line.startswith("data: "):
                            continue
                        data_str = line[len("data: "):]
                        if data_str == "[DONE]":
                            yield {"done": True}
                            break
                        try:
                            chunk = json.loads(data_str)
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                content = _strip_think_tags(content)
                            yield {"response": content, "done": False}
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse streaming chunk: {line}")
                            continue

        except httpx.ConnectError as e:
            raise MiniMaxConnectionError(f"Cannot connect to MiniMax API: {e}")
        except httpx.TimeoutException as e:
            raise MiniMaxTimeoutError(f"MiniMax API timeout: {e}")
        except MiniMaxException:
            raise
        except Exception as e:
            raise MiniMaxException(f"Error in streaming generation: {e}")

    async def generate_rag_answer(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        model: str = "MiniMax-M3",
        use_structured_output: bool = False,
    ) -> Dict[str, Any]:
        """Generate a RAG answer using retrieved chunks.

        Args:
            query: User's question
            chunks: Retrieved document chunks with metadata
            model: Model to use for generation
            use_structured_output: Whether to use structured output

        Returns:
            Dictionary with answer, sources, confidence, and citations
        """
        try:
            prompt = self.prompt_builder.create_rag_prompt(query, chunks)

            response = await self.generate(
                model=model,
                prompt=prompt,
                temperature=0.7,
                top_p=0.9,
            )

            if response and "response" in response:
                answer_text = response["response"]
                logger.debug(f"Raw LLM response: {answer_text[:500]}")

                if use_structured_output:
                    parsed_response = self.response_parser.parse_structured_response(answer_text)
                    return parsed_response

                # Build simple response structure
                sources = []
                seen_urls = set()
                for chunk in chunks:
                    arxiv_id = chunk.get("arxiv_id")
                    if arxiv_id:
                        arxiv_id_clean = arxiv_id.split("v")[0] if "v" in arxiv_id else arxiv_id
                        pdf_url = f"https://arxiv.org/pdf/{arxiv_id_clean}.pdf"
                        if pdf_url not in seen_urls:
                            sources.append(pdf_url)
                            seen_urls.add(pdf_url)

                citations = list(set(chunk.get("arxiv_id") for chunk in chunks if chunk.get("arxiv_id")))

                return {
                    "answer": answer_text,
                    "sources": sources,
                    "confidence": "medium",
                    "citations": citations[:5],
                }
            else:
                raise MiniMaxException("No response generated from MiniMax")

        except Exception as e:
            logger.error(f"Error generating RAG answer: {e}")
            raise MiniMaxException(f"Failed to generate RAG answer: {e}")

    async def generate_rag_answer_stream(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        model: str = "MiniMax-M3",
    ):
        """Generate a streaming RAG answer using retrieved chunks.

        Args:
            query: User's question
            chunks: Retrieved document chunks with metadata
            model: Model to use for generation

        Yields:
            Streaming response chunks with partial answers
        """
        try:
            prompt = self.prompt_builder.create_rag_prompt(query, chunks)

            async for chunk in self.generate_stream(
                model=model,
                prompt=prompt,
                temperature=0.7,
                top_p=0.9,
            ):
                yield chunk

        except Exception as e:
            logger.error(f"Error generating streaming RAG answer: {e}")
            raise MiniMaxException(f"Failed to generate streaming RAG answer: {e}")
