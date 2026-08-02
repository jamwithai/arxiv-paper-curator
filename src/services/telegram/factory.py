import logging
from typing import Optional

from src.config import get_settings
from src.services.telegram.bot import TelegramBot

logger = logging.getLogger(__name__)


def make_telegram_service(
    opensearch_client,
    embeddings_client,
    llm_client,
    cache_client=None,
    langfuse_tracer=None,
) -> Optional[TelegramBot]:
    """
    Create Telegram bot if enabled.

    Args:
        opensearch_client: OpenSearch client
        embeddings_client: Embeddings service client
        llm_client: LLM client for generation
        cache_client: Optional cache client
        langfuse_tracer: Optional Langfuse tracer (not used)

    Returns:
        TelegramBot instance or None if disabled
    """
    settings = get_settings()

    if not settings.telegram.enabled:
        logger.info("Telegram bot is disabled")
        return None

    if not settings.telegram.bot_token:
        logger.warning("Telegram bot token not configured")
        return None

    bot = TelegramBot(
        bot_token=settings.telegram.bot_token,
        opensearch_client=opensearch_client,
        embeddings_client=embeddings_client,
        llm_client=llm_client,
        cache_client=cache_client,
    )

    logger.info("Telegram bot created successfully")
    return bot
