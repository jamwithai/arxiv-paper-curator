from typing import Any, Dict

from pydantic import BaseModel, Field

from src.config import Settings, default_llm_model, get_settings


def _default_model() -> str:
    """Default LLM model, based on the active LLM_PROVIDER."""
    return default_llm_model(get_settings())


class GraphConfig(BaseModel):
    """Configuration for the entire graph execution.

    This is the configuration used by AgenticRAGService for controlling
    graph behavior, retrieval settings, and execution parameters.

    :param max_retrieval_attempts: Maximum number of retrieval attempts before fallback
    :param guardrail_threshold: Threshold score for guardrail validation (0-100)
    :param model: Default model to use for LLM calls, based on LLM_PROVIDER
    :param temperature: Temperature for LLM generation (0.0 = deterministic)
    :param top_k: Number of documents to retrieve from search
    :param use_hybrid: Whether to use hybrid search (BM25 + vector)
    :param enable_tracing: Whether to enable Langfuse tracing
    :param metadata: Additional runtime metadata for tracking and analytics
    :param settings: Application settings instance for environment and service config
    """

    max_retrieval_attempts: int = 2
    guardrail_threshold: int = 60
    model: str = Field(default_factory=_default_model)
    temperature: float = 0.0
    top_k: int = 3
    use_hybrid: bool = True
    enable_tracing: bool = True
    metadata: Dict[str, Any] = {}
    settings: Settings = Field(default_factory=get_settings)
