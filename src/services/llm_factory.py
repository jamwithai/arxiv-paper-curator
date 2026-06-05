"""LLM client factory for selecting between Ollama and MiniMax providers."""

import logging
from functools import lru_cache
from typing import Union

from src.config import get_settings
from src.services.minimax.client import MiniMaxClient
from src.services.ollama.client import OllamaClient

logger = logging.getLogger(__name__)

LLMClient = Union[OllamaClient, MiniMaxClient]


@lru_cache(maxsize=1)
def make_llm_client() -> LLMClient:
    """Create the appropriate LLM client based on LLM_PROVIDER setting.

    Supports:
        - "ollama": Local Ollama LLM service (default)
        - "minimax": MiniMax cloud LLM via OpenAI-compatible API

    Returns:
        Configured LLM client instance
    """
    settings = get_settings()
    provider = settings.llm_provider.lower()

    if provider == "minimax":
        if not settings.minimax_api_key:
            raise ValueError(
                "MINIMAX_API_KEY is required when LLM_PROVIDER=minimax. "
                "Set it in your .env file."
            )
        logger.info(f"Using MiniMax LLM provider (model: {settings.minimax_model})")
        return MiniMaxClient(settings)
    else:
        logger.info(f"Using Ollama LLM provider (model: {settings.ollama_model})")
        return OllamaClient(settings)
