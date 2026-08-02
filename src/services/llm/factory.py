from functools import lru_cache

from src.config import get_settings
from src.exceptions import ConfigurationError
from src.services.llm.base import LLMClient
from src.services.llm.deepseek import DeepSeekClient
from src.services.llm.ollama import OllamaClient


@lru_cache(maxsize=1)
def get_llm_client() -> LLMClient:
    """
    Create and return a singleton LLM client instance for the configured provider.

    The provider is selected via ``LLM_PROVIDER`` in settings (``deepseek`` or ``ollama``).

    Returns:
        LLMClient: Configured client for the active provider.

    Raises:
        ConfigurationError: If ``llm_provider`` is not a supported value.
    """
    settings = get_settings()

    if settings.llm_provider == "deepseek":
        return DeepSeekClient(settings)
    elif settings.llm_provider == "ollama":
        return OllamaClient(settings)
    else:
        raise ConfigurationError(f"Unsupported LLM_PROVIDER: {settings.llm_provider!r}. Expected 'deepseek' or 'ollama'.")
