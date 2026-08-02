from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional

from langchain_core.language_models.chat_models import BaseChatModel


class LLMClient(ABC):
    """Common interface for LLM providers (Ollama, DeepSeek, ...).

    Implementations back both the direct-generation path used by
    ``routers/ask.py`` and the LangChain path used by the LangGraph
    agent nodes (``get_langchain_model``).
    """

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check whether the underlying LLM service is reachable."""

    @abstractmethod
    async def generate(self, model: str, prompt: str, stream: bool = False, **kwargs: Any) -> Optional[Dict[str, Any]]:
        """Generate text for a raw prompt, returning a dict with a ``usage_metadata`` field."""

    @abstractmethod
    def generate_stream(self, model: str, prompt: str, **kwargs: Any) -> AsyncIterator[Dict[str, Any]]:
        """Generate text for a raw prompt, streaming response chunks."""

    @abstractmethod
    async def generate_rag_answer(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        model: str,
        use_structured_output: bool = False,
        domain: str = "ai",
    ) -> Dict[str, Any]:
        """Generate a RAG answer (with sources/citations) from retrieved chunks.

        :param domain: Corpus domain ("ai", "education", "accounting") - controls
            how the system prompt and citations are framed (see Stage 2 plan).
        """

    @abstractmethod
    def generate_rag_answer_stream(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        model: str,
        domain: str = "ai",
    ) -> AsyncIterator[Dict[str, Any]]:
        """Generate a streaming RAG answer from retrieved chunks."""

    @abstractmethod
    def get_langchain_model(self, model: str, temperature: float = 0.0) -> BaseChatModel:
        """Return a LangChain chat model bound to this provider, for use in LangGraph nodes."""
