"""Unified OpenSearch client supporting both simple BM25 and hybrid search."""

import logging
from typing import Any, Dict, List, Optional

from opensearchpy import OpenSearch
from src.config import Settings

from .index_config_hybrid import (
    ARXIV_PAPERS_CHUNKS_MAPPING,
    HYBRID_RRF_PIPELINE,
    LEGAL_DOCS_CHUNKS_MAPPING,
    LEGAL_DOCS_SEARCH_FIELDS,
)
from .query_builder import QueryBuilder

logger = logging.getLogger(__name__)

# Domains whose index uses the bilingual legal-docs mapping instead of the
# arXiv chunk mapping. See Stage 2 plan (2a/2b).
BILINGUAL_DOMAINS = {"education", "accounting"}


class OpenSearchClient:
    """OpenSearch client supporting BM25 and hybrid search with native RRF.

    Multi-domain: each domain (ai / education / accounting) is a separate
    index (see `OpenSearchSettings.domain_indices`). Methods default to the
    `ai` domain's index for backward compatibility; pass `domain=` to target
    a different corpus.
    """

    def __init__(self, host: str, settings: Settings):
        self.host = host
        self.settings = settings
        self.domain_indices = settings.opensearch.domain_indices
        self.default_domain = settings.opensearch.default_domain
        # Kept for backward compatibility with callers that don't pass `domain=`.
        self.index_name = self.domain_indices.get(
            self.default_domain, f"{settings.opensearch.index_name}-{settings.opensearch.chunk_index_suffix}"
        )

        self.client = OpenSearch(
            hosts=[host],
            use_ssl=False,
            verify_certs=False,
            ssl_show_warn=False,
        )

        logger.info(f"OpenSearch client initialized with host: {host}")

    def resolve_index(self, domain: Optional[str] = None) -> str:
        """Resolve a domain name to its index name.

        :param domain: Domain key (e.g. "ai", "education", "accounting"), or
            None to use the default domain
        :returns: Index name for that domain
        :raises ValueError: If domain is not configured in `domain_indices`
        """
        domain = domain or self.default_domain
        if domain not in self.domain_indices:
            raise ValueError(f"Unknown domain: {domain!r}. Configured domains: {list(self.domain_indices)}")
        return self.domain_indices[domain]

    def health_check(self) -> bool:
        """Check if OpenSearch cluster is healthy."""
        try:
            health = self.client.cluster.health()
            return health["status"] in ["green", "yellow"]
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    def get_index_stats(self, domain: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics for a domain's index."""
        index_name = self.resolve_index(domain)
        try:
            if not self.client.indices.exists(index=index_name):
                return {"index_name": index_name, "exists": False, "document_count": 0}

            stats_response = self.client.indices.stats(index=index_name)
            index_stats = stats_response["indices"][index_name]["total"]

            return {
                "index_name": index_name,
                "exists": True,
                "document_count": index_stats["docs"]["count"],
                "deleted_count": index_stats["docs"]["deleted"],
                "size_in_bytes": index_stats["store"]["size_in_bytes"],
            }

        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {"index_name": index_name, "exists": False, "document_count": 0, "error": str(e)}

    def setup_indices(self, force: bool = False, domain: Optional[str] = None) -> Dict[str, bool]:
        """Setup the hybrid search index and RRF pipeline for one domain."""
        results = {}
        results["hybrid_index"] = self._create_hybrid_index(force, domain)
        results["rrf_pipeline"] = self._create_rrf_pipeline(force)
        return results

    def setup_all_domain_indices(self, force: bool = False) -> Dict[str, Dict[str, bool]]:
        """Setup indices for every configured domain (ai, education, accounting)."""
        results = {domain: self.setup_indices(force, domain) for domain in self.domain_indices}
        return results

    def _create_hybrid_index(self, force: bool = False, domain: Optional[str] = None) -> bool:
        """Create hybrid index for all search types (BM25, vector, hybrid).

        :param force: If True, recreate index even if it exists
        :param domain: Domain to create the index for (determines the mapping used)
        :returns: True if created, False if already exists
        """
        index_name = self.resolve_index(domain)
        mapping = LEGAL_DOCS_CHUNKS_MAPPING if (domain or self.default_domain) in BILINGUAL_DOMAINS else ARXIV_PAPERS_CHUNKS_MAPPING
        try:
            if force and self.client.indices.exists(index=index_name):
                self.client.indices.delete(index=index_name)
                logger.info(f"Deleted existing hybrid index: {index_name}")

            if not self.client.indices.exists(index=index_name):
                self.client.indices.create(index=index_name, body=mapping)
                logger.info(f"Created hybrid index: {index_name}")
                return True

            logger.info(f"Hybrid index already exists: {index_name}")
            return False

        except Exception as e:
            # Handle race condition when multiple workers start simultaneously:
            # all check exists() -> False, all try to create, only one succeeds.
            if "resource_already_exists_exception" in str(e):
                logger.info(f"Hybrid index already exists (created by another worker): {index_name}")
                return False
            logger.error(f"Error creating hybrid index: {e}")
            raise

    def _create_rrf_pipeline(self, force: bool = False) -> bool:
        """Create RRF search pipeline for native hybrid search.

        :param force: If True, recreate pipeline even if it exists
        :returns: True if created, False if already exists
        """
        try:
            pipeline_id = HYBRID_RRF_PIPELINE["id"]

            if force:
                try:
                    self.client.ingest.get_pipeline(id=pipeline_id)
                    self.client.ingest.delete_pipeline(id=pipeline_id)
                    logger.info(f"Deleted existing RRF pipeline: {pipeline_id}")
                except Exception:
                    pass

            try:
                self.client.ingest.get_pipeline(id=pipeline_id)
                logger.info(f"RRF pipeline already exists: {pipeline_id}")
                return False
            except Exception:
                pass
            pipeline_body = {
                "description": HYBRID_RRF_PIPELINE["description"],
                "phase_results_processors": HYBRID_RRF_PIPELINE["phase_results_processors"],
            }

            self.client.transport.perform_request("PUT", f"/_search/pipeline/{pipeline_id}", body=pipeline_body)

            logger.info(f"Created RRF search pipeline: {pipeline_id}")
            return True

        except Exception as e:
            logger.error(f"Error creating RRF pipeline: {e}")
            raise

    def search_papers(
        self, query: str, size: int = 10, from_: int = 0, categories: Optional[List[str]] = None, latest: bool = True
    ) -> Dict[str, Any]:
        """BM25 search for papers."""
        return self._search_bm25_only(query=query, size=size, from_=from_, categories=categories, latest=latest)

    def search_chunks_vector(
        self, query_embedding: List[float], size: int = 10, categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Pure vector search on chunks.

        :param query_embedding: Query embedding vector
        :param size: Number of results
        :param categories: Optional category filter
        :returns: Search results
        """
        try:
            # Build filter
            filter_clause = []
            if categories:
                filter_clause.append({"terms": {"categories": categories}})

            search_body = {
                "size": size,
                "query": {"knn": {"embedding": {"vector": query_embedding, "k": size}}},
                "_source": {"excludes": ["embedding"]},
            }

            if filter_clause:
                search_body["query"] = {"bool": {"must": [search_body["query"]], "filter": filter_clause}}

            response = self.client.search(index=self.index_name, body=search_body)

            results = {"total": response["hits"]["total"]["value"], "hits": []}

            for hit in response["hits"]["hits"]:
                chunk = hit["_source"]
                chunk["score"] = hit["_score"]
                chunk["chunk_id"] = hit["_id"]
                results["hits"].append(chunk)

            return results

        except Exception as e:
            logger.error(f"Vector search error: {e}")
            return {"total": 0, "hits": []}

    def _search_fields_for(self, domain: Optional[str]) -> Optional[List[str]]:
        """Resolve the BM25 multi-match fields for a domain, or None for the QueryBuilder default."""
        return LEGAL_DOCS_SEARCH_FIELDS if (domain or self.default_domain) in BILINGUAL_DOMAINS else None

    def search_unified(
        self,
        query: str,
        query_embedding: Optional[List[float]] = None,
        size: int = 10,
        from_: int = 0,
        categories: Optional[List[str]] = None,
        latest: bool = False,
        use_hybrid: bool = True,
        min_score: float = 0.0,
        domain: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Unified search method supporting BM25, vector, and hybrid modes.

        :param query: Text query for search
        :param query_embedding: Optional embedding for vector/hybrid search
        :param size: Number of results to return
        :param from_: Offset for pagination
        :param categories: Optional category filter
        :param latest: Sort by date instead of relevance
        :param use_hybrid: If True and embedding provided, use hybrid search
        :param min_score: Minimum score threshold
        :param domain: Domain to search (e.g. "ai", "education", "accounting"); defaults to the configured default domain
        :returns: Search results
        """
        try:
            # If no embedding provided or hybrid disabled, use BM25 only
            if not query_embedding or not use_hybrid:
                return self._search_bm25_only(
                    query=query, size=size, from_=from_, categories=categories, latest=latest, domain=domain
                )

            # Use native OpenSearch hybrid search with RRF pipeline
            return self._search_hybrid_native(
                query=query, query_embedding=query_embedding, size=size, categories=categories, min_score=min_score, domain=domain
            )

        except Exception as e:
            logger.error(f"Unified search error: {e}")
            return {"total": 0, "hits": []}

    def _search_bm25_only(
        self,
        query: str,
        size: int,
        from_: int,
        categories: Optional[List[str]],
        latest: bool,
        domain: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Pure BM25 search implementation."""
        index_name = self.resolve_index(domain)
        builder = QueryBuilder(
            query=query,
            size=size,
            from_=from_,
            fields=self._search_fields_for(domain),
            categories=categories,
            latest_papers=latest,
            search_chunks=True,  # Enable chunk search mode
        )
        search_body = builder.build()

        response = self.client.search(index=index_name, body=search_body)

        results = {"total": response["hits"]["total"]["value"], "hits": []}

        for hit in response["hits"]["hits"]:
            chunk = hit["_source"]
            chunk["score"] = hit["_score"]
            chunk["chunk_id"] = hit["_id"]

            if "highlight" in hit:
                chunk["highlights"] = hit["highlight"]

            results["hits"].append(chunk)

        logger.info(f"BM25 search for '{query[:50]}...' returned {results['total']} results (index: {index_name})")
        return results

    def _search_hybrid_native(
        self,
        query: str,
        query_embedding: List[float],
        size: int,
        categories: Optional[List[str]],
        min_score: float,
        domain: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Native OpenSearch hybrid search with RRF pipeline."""
        index_name = self.resolve_index(domain)
        builder = QueryBuilder(
            query=query,
            size=size * 2,
            from_=0,
            fields=self._search_fields_for(domain),
            categories=categories,
            latest_papers=False,
            search_chunks=True,
        )
        bm25_search_body = builder.build()

        bm25_query = bm25_search_body["query"]

        hybrid_query = {"hybrid": {"queries": [bm25_query, {"knn": {"embedding": {"vector": query_embedding, "k": size * 2}}}]}}

        search_body = {
            "size": size,
            "query": hybrid_query,
            "_source": bm25_search_body["_source"],
            "highlight": bm25_search_body["highlight"],
        }

        # Execute search with RRF pipeline
        response = self.client.search(
            index=index_name, body=search_body, params={"search_pipeline": HYBRID_RRF_PIPELINE["id"]}
        )

        results = {"total": response["hits"]["total"]["value"], "hits": []}

        for hit in response["hits"]["hits"]:
            if hit["_score"] < min_score:
                continue

            chunk = hit["_source"]
            chunk["score"] = hit["_score"]
            chunk["chunk_id"] = hit["_id"]

            if "highlight" in hit:
                chunk["highlights"] = hit["highlight"]

            results["hits"].append(chunk)

        results["total"] = len(results["hits"])
        logger.info(f"Native hybrid search for '{query[:50]}...' returned {results['total']} results (index: {index_name})")
        return results

    def search_chunks_hybrid(
        self,
        query: str,
        query_embedding: List[float],
        size: int = 10,
        categories: Optional[List[str]] = None,
        min_score: float = 0.0,
        domain: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Hybrid search combining BM25 and vector similarity using native RRF."""
        return self._search_hybrid_native(
            query=query, query_embedding=query_embedding, size=size, categories=categories, min_score=min_score, domain=domain
        )

    def index_chunk(self, chunk_data: Dict[str, Any], embedding: List[float], domain: Optional[str] = None) -> bool:
        """Index a single chunk with its embedding.

        :param chunk_data: Chunk data dictionary
        :param embedding: Embedding vector
        :param domain: Domain to index into; defaults to the configured default domain
        :returns: True if successful
        """
        index_name = self.resolve_index(domain)
        try:
            chunk_data["embedding"] = embedding

            response = self.client.index(index=index_name, body=chunk_data, refresh=True)

            return response["result"] in ["created", "updated"]

        except Exception as e:
            logger.error(f"Error indexing chunk: {e}")
            return False

    def bulk_index_chunks(self, chunks: List[Dict[str, Any]], domain: Optional[str] = None) -> Dict[str, int]:
        """Bulk index multiple chunks with embeddings.

        :param chunks: List of dicts with 'chunk_data' and 'embedding'
        :param domain: Domain to index into; defaults to the configured default domain
        :returns: Statistics
        """
        from opensearchpy import helpers

        index_name = self.resolve_index(domain)
        try:
            actions = []
            for chunk in chunks:
                chunk_data = chunk["chunk_data"].copy()
                chunk_data["embedding"] = chunk["embedding"]

                action = {"_index": index_name, "_source": chunk_data}
                actions.append(action)

            success, failed = helpers.bulk(self.client, actions, refresh=True)

            logger.info(f"Bulk indexed {success} chunks, {len(failed)} failed (index: {index_name})")
            return {"success": success, "failed": len(failed)}

        except Exception as e:
            logger.error(f"Bulk chunk indexing error: {e}")
            raise

    def delete_paper_chunks(self, arxiv_id: str) -> bool:
        """Delete all chunks for a specific paper.

        :param arxiv_id: ArXiv ID of the paper
        :returns: True if deletion was successful
        """
        try:
            response = self.client.delete_by_query(
                index=self.index_name, body={"query": {"term": {"arxiv_id": arxiv_id}}}, refresh=True
            )

            deleted = response.get("deleted", 0)
            logger.info(f"Deleted {deleted} chunks for paper {arxiv_id}")
            return deleted > 0

        except Exception as e:
            logger.error(f"Error deleting chunks: {e}")
            return False

    def get_chunks_by_paper(self, arxiv_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a specific paper.

        :param arxiv_id: ArXiv ID of the paper
        :returns: List of chunks sorted by chunk_index
        """
        try:
            search_body = {
                "query": {"term": {"arxiv_id": arxiv_id}},
                "size": 1000,
                "sort": [{"chunk_index": "asc"}],
                "_source": {"excludes": ["embedding"]},
            }

            response = self.client.search(index=self.index_name, body=search_body)

            chunks = []
            for hit in response["hits"]["hits"]:
                chunk = hit["_source"]
                chunk["chunk_id"] = hit["_id"]
                chunks.append(chunk)

            return chunks

        except Exception as e:
            logger.error(f"Error getting chunks: {e}")
            return []
