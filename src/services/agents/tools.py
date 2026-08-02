import logging

from langchain_core.documents import Document
from langchain_core.tools import tool
from langgraph.runtime import get_runtime

from src.services.embeddings.jina_client import JinaEmbeddingsClient
from src.services.opensearch.client import OpenSearchClient

from .context import Context

logger = logging.getLogger(__name__)


def create_retriever_tool(
    opensearch_client: OpenSearchClient,
    embeddings_client: JinaEmbeddingsClient,
    top_k: int = 3,
    use_hybrid: bool = True,
):
    """Create a retriever tool that wraps OpenSearch service.

    :param opensearch_client: Existing OpenSearch service
    :param embeddings_client: Existing Jina embeddings service
    :param top_k: Number of chunks to retrieve
    :param use_hybrid: Use hybrid search (BM25 + vector)
    :returns: LangChain tool for retrieving papers
    """

    @tool(response_format="content_and_artifact")
    async def retrieve_papers(query: str) -> tuple[str, list[Document]]:
        """Search and return relevant arXiv research papers.

        Use this tool when the user asks about:
        - Machine learning concepts or techniques
        - Deep learning architectures
        - Natural language processing
        - Computer vision methods
        - AI research topics
        - Specific algorithms or models

        :param query: The search query describing what papers to find
        :returns: (formatted context for the LLM, retrieved Documents as the tool
            artifact - the artifact carries structured metadata so downstream
            nodes can build source citations without parsing the LLM-facing text)
        """
        # Resolve domain from the active graph run (per-request), falling back to
        # the default domain if invoked outside a graph run (e.g. direct tests).
        domain = None
        try:
            domain = get_runtime(Context).context.domain
        except Exception:
            domain = None

        logger.info(f"Retrieving papers for query: {query[:100]}... (domain: {domain or 'default'})")
        logger.debug(f"Search mode: {'hybrid' if use_hybrid else 'bm25'}, top_k: {top_k}")

        # Generate query embedding
        logger.debug("Generating query embedding")
        query_embedding = await embeddings_client.embed_query(query)
        logger.debug(f"Generated embedding with {len(query_embedding)} dimensions")

        # Search using OpenSearch
        logger.debug("Searching OpenSearch")
        search_results = opensearch_client.search_unified(
            query=query,
            query_embedding=query_embedding,
            size=top_k,
            use_hybrid=use_hybrid,
            domain=domain,
        )

        # Convert SearchHit to LangChain Document
        documents = []
        hits = search_results.get("hits", [])
        logger.info(f"Found {len(hits)} documents from OpenSearch")

        for hit in hits:
            # arXiv chunks use "chunk_text"/"arxiv_id"; bilingual domain chunks
            # (education/accounting) use "chunk_text_vi"/"chunk_text_en"/"doc_id"
            # instead (see LEGAL_DOCS_CHUNKS_MAPPING). Resolve whichever is present.
            chunk_text = hit.get("chunk_text") or hit.get("chunk_text_vi") or hit.get("chunk_text_en") or ""
            doc_id = hit.get("arxiv_id") or hit.get("doc_id", "")
            source = (
                f"https://arxiv.org/pdf/{doc_id}.pdf"
                if hit.get("arxiv_id")
                else f"doc:{doc_id}" if doc_id else ""
            )

            doc = Document(
                page_content=chunk_text,
                metadata={
                    "arxiv_id": doc_id,
                    "title": hit.get("title", ""),
                    "authors": hit.get("authors", ""),
                    "score": hit.get("score", 0.0),
                    "source": source,
                    "section": hit.get("section_name", ""),
                    "search_mode": "hybrid" if use_hybrid else "bm25",
                    "top_k": top_k,
                },
            )
            documents.append(doc)

        logger.debug(f"Converted {len(documents)} hits to LangChain Documents")
        logger.info(f"✓ Retrieved {len(documents)} papers successfully")

        content = "\n\n".join(
            f"[{i}. {doc.metadata.get('arxiv_id') or doc.metadata.get('source', '')}]\n{doc.page_content}"
            for i, doc in enumerate(documents, 1)
        )
        return content, documents

    return retrieve_papers
