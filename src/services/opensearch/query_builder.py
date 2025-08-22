import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PaperQueryBuilder:
    """
    Query builder for arXiv papers search following reference patterns.

    Builds complex OpenSearch queries with proper scoring, filtering, and highlighting.
    """

    def __init__(
        self,
        query: str,
        size: int = 10,
        from_: int = 0,
        fields: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        track_total_hits: bool = True,
        latest_papers: bool = False,
    ):
        """Initialize query builder.

        :param query: Search query text
        :param size: Number of results to return
        :param from_: Offset for pagination
        :param fields: Fields to search in
        :param categories: Filter by categories
        :param track_total_hits: Whether to track total hits accurately
        :param latest_papers: Sort by publication date instead of relevance
        """
        self.query = query
        self.size = size
        self.from_ = from_
        # Multi-field search with boosting: title (highest), abstract (medium), authors (lower)
        self.fields = fields or ["title^3", "abstract^2", "authors^1"]
        self.categories = categories
        self.track_total_hits = track_total_hits
        self.latest_papers = latest_papers

    def build(self) -> Dict[str, Any]:
        """Build the complete OpenSearch query.

        :returns: Complete query dictionary ready for OpenSearch
        """
        query_body = {
            "query": self._build_query(),
            "size": self.size,
            "from": self.from_,
            "track_total_hits": self.track_total_hits,
            "_source": self._build_source_fields(),
            "highlight": self._build_highlight(),
        }

        # Add sorting if needed
        sort = self._build_sort()
        if sort:
            query_body["sort"] = sort

        return query_body

    def _build_query(self) -> Dict[str, Any]:
        """Build the main query with filters.

        :returns: Query dictionary with bool structure
        """
        # Build must clauses
        must_clauses = []

        # Main text search
        if self.query.strip():
            must_clauses.append(self._build_text_query())

        # Build filter clauses
        filter_clauses = self._build_filters()

        # Construct bool query
        bool_query = {}

        if must_clauses:
            bool_query["must"] = must_clauses
        else:
            # If no text query, match all documents
            bool_query["must"] = [{"match_all": {}}]

        if filter_clauses:
            bool_query["filter"] = filter_clauses

        return {"bool": bool_query}

    def _build_text_query(self) -> Dict[str, Any]:
        """Build the main text search query.

        :returns: Multi-match query for text search
        """
        return {
            "multi_match": {
                "query": self.query,
                "fields": self.fields,
                "type": "best_fields",
                "operator": "or",
                "fuzziness": "AUTO",
                "prefix_length": 2,
            }
        }

    def _build_filters(self) -> List[Dict[str, Any]]:
        """Build filter clauses for the query.

        :returns: List of filter clauses
        """
        filters = []

        # Category filter
        if self.categories:
            filters.append({"terms": {"categories": self.categories}})

        return filters

    def _build_source_fields(self) -> List[str]:
        """Define which fields to return in results.

        :returns: List of field names to include in response
        """
        return ["arxiv_id", "title", "authors", "abstract", "categories", "published_date", "pdf_url"]

    def _build_highlight(self) -> Dict[str, Any]:
        """Build highlighting configuration.

        :returns: Highlight configuration dictionary
        """
        return {
            "fields": {
                "title": {
                    "fragment_size": 0,  # Return entire field
                    "number_of_fragments": 0,
                },
                "abstract": {"fragment_size": 150, "number_of_fragments": 3, "pre_tags": ["<mark>"], "post_tags": ["</mark>"]},
                "authors": {
                    "fragment_size": 0,  # Return entire field
                    "number_of_fragments": 0,
                    "pre_tags": ["<mark>"],
                    "post_tags": ["</mark>"],
                },
            },
            "require_field_match": False,
        }

    def _build_sort(self) -> Optional[List[Dict[str, Any]]]:
        """Build sorting configuration.

        :returns: Sort configuration or None for relevance scoring
        """
        # If latest_papers is requested, always sort by publication date
        if self.latest_papers:
            return [{"published_date": {"order": "desc"}}, "_score"]

        # For text queries, use relevance scoring (no explicit sort)
        if self.query.strip():
            return None

        # For empty queries, sort by publication date (newest first)
        return [{"published_date": {"order": "desc"}}, "_score"]


def build_search_query(
    query: str,
    size: int = 10,
    from_: int = 0,
    categories: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Helper function to build a search query with optional filters.

    :param query: Search query text
    :param size: Number of results
    :param from_: Offset for pagination
    :param categories: Optional filter by categories
    :returns: Search query dictionary
    """
    builder = PaperQueryBuilder(query=query, size=size, from_=from_, categories=categories)
    return builder.build()
