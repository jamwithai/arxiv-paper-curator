from typing import Optional

from src.services.agents.context import LLMClient
from src.services.embeddings.jina_client import JinaEmbeddingsClient
from src.services.langfuse.client import LangfuseTracer
from src.services.opensearch.client import OpenSearchClient

from .agentic_rag import AgenticRAGService
from .config import GraphConfig


def make_agentic_rag_service(
    opensearch_client: OpenSearchClient,
    llm_client: LLMClient,
    embeddings_client: JinaEmbeddingsClient,
    langfuse_tracer: Optional[LangfuseTracer] = None,
    top_k: int = 3,
    use_hybrid: bool = True,
    model: Optional[str] = None,
) -> AgenticRAGService:
    """
    Create AgenticRAGService with dependency injection.

    Args:
        opensearch_client: Client for document search
        llm_client: Client for LLM generation (OllamaClient or MiniMaxClient)
        embeddings_client: Client for embeddings
        langfuse_tracer: Optional Langfuse tracer for observability
        top_k: Number of documents to retrieve (default: 3)
        use_hybrid: Use hybrid search (default: True)
        model: Optional model name override

    Returns:
        Configured AgenticRAGService instance
    """
    # Create graph configuration with the provided parameters
    config_kwargs = {"top_k": top_k, "use_hybrid": use_hybrid}
    if model:
        config_kwargs["model"] = model
    graph_config = GraphConfig(**config_kwargs)

    return AgenticRAGService(
        opensearch_client=opensearch_client,
        llm_client=llm_client,
        embeddings_client=embeddings_client,
        langfuse_tracer=langfuse_tracer,
        graph_config=graph_config,
    )
