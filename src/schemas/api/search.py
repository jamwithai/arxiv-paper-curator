from typing import List, Optional

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Search request model."""

    query: str = Field(..., min_length=1, max_length=500, description="Search query across title, abstract, and authors")
    size: int = Field(default=10, ge=1, le=50, description="Number of results to return")
    from_: int = Field(default=0, ge=0, alias="from", description="Offset for pagination")
    categories: Optional[List[str]] = Field(default=None, description="Filter by categories")
    latest_papers: bool = Field(default=False, description="Sort by publication date (newest first) instead of relevance")


class SearchHit(BaseModel):
    """Individual search result."""

    arxiv_id: str
    title: str
    authors: Optional[str]
    abstract: Optional[str]
    published_date: Optional[str]
    pdf_url: Optional[str]
    score: float
    highlights: Optional[dict] = None


class SearchResponse(BaseModel):
    """Search response model."""

    query: str
    total: int
    hits: List[SearchHit]
    error: Optional[str] = None
