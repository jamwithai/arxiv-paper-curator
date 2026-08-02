from typing import Optional

from src.config import Settings, default_llm_model, get_settings
from src.services.embeddings.jina_client import JinaEmbeddingsClient
from src.services.llm.base import LLMClient
from src.services.opensearch.client import OpenSearchClient

from .service import DraftingService


def make_drafting_service(
    opensearch_client: OpenSearchClient,
    llm_client: LLMClient,
    embeddings_client: JinaEmbeddingsClient,
    settings: Optional[Settings] = None,
    top_k_per_section: int = 5,
) -> DraftingService:
    """Create a DraftingService.

    Defaults to the "strong" LLM tier (see Stage 1 plan: `strong` is routed to
    `generate_answer_node` and all of Stage 3, since drafting quality matters
    more than latency here).
    """
    settings = settings or get_settings()
    return DraftingService(
        opensearch_client=opensearch_client,
        llm_client=llm_client,
        embeddings_client=embeddings_client,
        model=default_llm_model(settings),
        top_k_per_section=top_k_per_section,
    )
