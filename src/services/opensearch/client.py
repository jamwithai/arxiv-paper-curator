import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from opensearchpy import OpenSearch
from opensearchpy.exceptions import NotFoundError, RequestError
from src.config import Settings, get_settings

from .index_config import ARXIV_PAPERS_INDEX, ARXIV_PAPERS_MAPPING
from .query_builder import PaperQueryBuilder

logger = logging.getLogger(__name__)


class OpenSearchClient:
    """
    Client for OpenSearch operations including index management and search.

    This client provides methods for creating indices, indexing papers,
    searching with BM25 scoring, and managing OpenSearch cluster operations.
    """

    def __init__(self, host: str = "http://localhost:9200", settings: Optional[Settings] = None):
        """Initialize OpenSearch client.

        :param host: OpenSearch cluster endpoint URL
        :param settings: Application settings instance (uses default if None)
        :type host: str
        :type settings: Optional[Settings]
        """
        self.host = host
        self.settings = settings or get_settings()
        self.index_name = self.settings.opensearch.index_name
        self.client = OpenSearch(
            hosts=[host],
            http_compress=True,
            use_ssl=False,
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
        )
        # Use configured index name, fall back to constant if not set
        self.index_name = self.settings.opensearch.index_name or ARXIV_PAPERS_INDEX
        logger.info(f"OpenSearch client initialized with host: {host}")

    def create_index(self, force: bool = False) -> bool:
        """Create the arxiv-papers index with proper mappings.

        :param force: If True, delete existing index before creating
        :type force: bool
        :returns: True if index was created, False if it already exists
        :rtype: bool
        """
        try:
            # Check if index exists
            if self.client.indices.exists(index=self.index_name):
                if force:
                    logger.info(f"Deleting existing index: {self.index_name}")
                    self.client.indices.delete(index=self.index_name)
                else:
                    logger.info(f"Index {self.index_name} already exists")
                    return False

            # Create index with mappings
            response = self.client.indices.create(index=self.index_name, body=ARXIV_PAPERS_MAPPING)

            if response.get("acknowledged"):
                logger.info(f"Successfully created index: {self.index_name}")
                return True
            else:
                logger.error(f"Failed to create index: {response}")
                return False

        except RequestError as e:
            logger.error(f"Error creating index: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error creating index: {e}")
            return False

    def index_paper(self, paper_data: Dict[str, Any]) -> bool:
        """Index a single paper document.

        :param paper_data: Paper data to index
        :type paper_data: Dict[str, Any]
        :returns: True if successful, False otherwise
        :rtype: bool
        """
        try:
            # Ensure required fields
            if "arxiv_id" not in paper_data:
                logger.error("Missing arxiv_id in paper data")
                return False

            # Add timestamps if not present
            if "created_at" not in paper_data:
                paper_data["created_at"] = datetime.now(timezone.utc).isoformat()
            if "updated_at" not in paper_data:
                paper_data["updated_at"] = datetime.now(timezone.utc).isoformat()

            # Convert authors list to string if needed
            if isinstance(paper_data.get("authors"), list):
                paper_data["authors"] = ", ".join(paper_data["authors"])

            # Index the document
            response = self.client.index(
                index=self.index_name,
                id=paper_data["arxiv_id"],
                body=paper_data,
                refresh=True,  # Make it immediately searchable
            )

            if response.get("result") in ["created", "updated"]:
                logger.debug(f"Indexed paper: {paper_data['arxiv_id']}")
                return True
            else:
                logger.error(f"Failed to index paper: {response}")
                return False

        except Exception as e:
            logger.error(f"Error indexing paper {paper_data.get('arxiv_id', 'unknown')}: {e}")
            return False

    def bulk_index_papers(self, papers: List[Dict[str, Any]]) -> Dict[str, int]:
        """Bulk index multiple papers.

        :param papers: List of paper data to index
        :type papers: List[Dict[str, Any]]
        :returns: Dictionary with counts of successful and failed indexing
        :rtype: Dict[str, int]
        """
        results = {"success": 0, "failed": 0}

        for paper in papers:
            if self.index_paper(paper):
                results["success"] += 1
            else:
                results["failed"] += 1

        logger.info(f"Bulk indexing complete: {results['success']} successful, {results['failed']} failed")
        return results

    def search_papers(
        self,
        query: str,
        size: int = 10,
        from_: int = 0,
        fields: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        track_total_hits: bool = True,
        latest_papers: bool = False,
    ) -> Dict[str, Any]:
        """Search papers using BM25 scoring with query builder.

        :param query: Search query text
        :param size: Number of results to return
        :param from_: Offset for pagination
        :param fields: List of fields to search in (default: title, abstract, authors)
        :param categories: Filter by categories
        :param track_total_hits: Whether to track total hits accurately
        :param latest_papers: Sort by publication date instead of relevance
        :type query: str
        :type size: int
        :type from_: int
        :type fields: Optional[List[str]]
        :type categories: Optional[List[str]]
        :type track_total_hits: bool
        :type latest_papers: bool
        :returns: Search results with hits and metadata
        :rtype: Dict[str, Any]
        """
        try:
            # Build query using query builder
            query_builder = PaperQueryBuilder(
                query=query,
                size=size,
                from_=from_,
                fields=fields,
                categories=categories,
                track_total_hits=track_total_hits,
                latest_papers=latest_papers,
            )

            search_body = query_builder.build()

            # Execute search
            response = self.client.search(index=self.index_name, body=search_body)

            # Format results
            results = {"total": response["hits"]["total"]["value"], "hits": []}

            for hit in response["hits"]["hits"]:
                paper = hit["_source"]
                paper["score"] = hit["_score"]
                if "highlight" in hit:
                    paper["highlights"] = hit["highlight"]
                results["hits"].append(paper)

            logger.info(f"Search for '{query}' returned {results['total']} results")
            return results

        except NotFoundError:
            logger.error(f"Index {self.index_name} not found")
            return {"total": 0, "hits": [], "error": "Index not found"}
        except Exception as e:
            logger.error(f"Search error: {e}")
            return {"total": 0, "hits": [], "error": str(e)}

    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the index.

        :returns: Dictionary with index statistics
        :rtype: Dict[str, Any]
        """
        try:
            stats = self.client.indices.stats(index=self.index_name)
            count = self.client.count(index=self.index_name)

            return {
                "index_name": self.index_name,
                "document_count": count["count"],
                "size_in_bytes": stats["indices"][self.index_name]["total"]["store"]["size_in_bytes"],
                "health": self.client.cluster.health(index=self.index_name)["status"],
            }
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {"error": str(e)}

    def health_check(self) -> bool:
        """Check if OpenSearch is healthy and accessible.

        :returns: True if healthy, False otherwise
        :rtype: bool
        """
        try:
            health = self.client.cluster.health()
            return health["status"] in ["green", "yellow"]
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    def get_cluster_info(self) -> Optional[Dict[str, Any]]:
        """Get OpenSearch cluster information.

        :returns: Dictionary with cluster info or None if error
        :rtype: Optional[Dict[str, Any]]
        """
        try:
            info = self.client.info()
            return info
        except Exception as e:
            logger.error(f"Error getting cluster info: {e}")
            return None

    def get_cluster_health(self) -> Optional[Dict[str, Any]]:
        """Get detailed cluster health information.

        :returns: Dictionary with cluster health details or None if error
        :rtype: Optional[Dict[str, Any]]
        """
        try:
            health = self.client.cluster.health()
            return health
        except Exception as e:
            logger.error(f"Error getting cluster health: {e}")
            return None

    def get_index_mapping(self) -> Optional[Dict[str, Any]]:
        """Get index mapping (alias for get_mappings for compatibility).

        :returns: Dictionary with index mapping or None if error
        :rtype: Optional[Dict[str, Any]]
        """
        try:
            mappings = self.client.indices.get_mapping(index=self.index_name)
            # Extract just the properties from the nested structure
            if mappings and self.index_name in mappings:
                return mappings[self.index_name].get("mappings", {})
            return {}
        except Exception as e:
            logger.error(f"Error getting index mapping: {e}")
            return None

    def get_index_settings(self) -> Optional[Dict[str, Any]]:
        """Get index settings (alias for get_settings for compatibility).

        :returns: Dictionary with index settings or None if error
        :rtype: Optional[Dict[str, Any]]
        """
        try:
            settings = self.client.indices.get_settings(index=self.index_name)
            # Extract just the settings for this index
            if settings and self.index_name in settings:
                return settings[self.index_name].get("settings", {})
            return {}
        except Exception as e:
            logger.error(f"Error getting index settings: {e}")
            return None
