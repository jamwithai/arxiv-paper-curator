from typing import List, Optional

from pydantic import BaseModel, Field


class DraftRequest(BaseModel):
    """Request to draft a citation-grounded outline for thesis Chapter 1-2."""

    topic: str = Field(
        ..., description="Thesis topic/research question to draft an outline for", min_length=1, max_length=500
    )
    domain: str = Field("ai", description="Corpus domain to ground the draft in: 'ai', 'education', or 'accounting'")
    model: Optional[str] = Field(
        None, description="Optional LLM model override; defaults to the configured 'strong' tier"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Ứng dụng mô hình RAG trong tra cứu văn bản quy phạm pháp luật giáo dục",
                "domain": "education",
            }
        }


class ClaimResponse(BaseModel):
    """A single grounded (or flagged) statement within a drafted section."""

    text: str = Field(..., description="Claim text")
    chunk_id: Optional[str] = Field(None, description="Source chunk_id backing this claim, if any")
    verified: bool = Field(..., description="Whether chunk_id was confirmed against the actually retrieved sources")
    source_excerpt: Optional[str] = Field(None, description="Excerpt of the source chunk, for manual verification")


class SectionResponse(BaseModel):
    """One drafted outline section, with all claims fact-checked."""

    title: str
    description: str
    claims: List[ClaimResponse]
    verified_ratio: float = Field(..., description="Fraction of claims in this section traceable to a real source")


class SourceResponse(BaseModel):
    """One row of the sources table: a retrieved chunk cited by at least one claim."""

    chunk_id: str
    citation_id: str = Field(..., description="Human-facing citation (arXiv id, or document number for VN domains)")
    excerpt: str


class DraftResponse(BaseModel):
    """Citation-grounded outline draft for thesis Chapter 1-2.

    This is a verified outline + sources, not finished prose meant to be copied
    as-is - see the Stage 3 plan's design rationale (AI-detection risk, risk of
    misciting regulatory documents, and the requirement that the thesis author
    can defend every claim before a committee).
    """

    topic: str
    domain: str
    sections: List[SectionResponse]
    sources: List[SourceResponse]
    markdown: str = Field(..., description="Rendered Markdown draft with inline citations and a sources table")
    overall_verified_ratio: float = Field(..., description="Fraction of all claims across all sections that are traceable")

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Ứng dụng mô hình RAG trong tra cứu văn bản quy phạm pháp luật giáo dục",
                "domain": "education",
                "sections": [],
                "sources": [],
                "markdown": "# Ứng dụng mô hình RAG...\n\n## 1. Lý do chọn đề tài\n...",
                "overall_verified_ratio": 0.83,
            }
        }
