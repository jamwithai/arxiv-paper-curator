from functools import lru_cache

from src.config import get_settings
from src.services.minimax.client import MiniMaxClient


@lru_cache(maxsize=1)
def make_minimax_client() -> MiniMaxClient:
    """Create and return a singleton MiniMax client instance.

    Returns:
        MiniMaxClient: Configured MiniMax client
    """
    settings = get_settings()
    return MiniMaxClient(settings)
