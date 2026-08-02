from typing import List, Optional

from pydantic import BaseModel, Field


class OutlineSection(BaseModel):
    """One section of a drafted outline."""

    title: str = Field(..., description="Section heading, e.g. 'Ly do chon de tai'")
    description: str = Field(..., description="What this section should cover, 1-2 sentences")


class DraftOutline(BaseModel):
    """LLM-generated outline for Chapter 1-2 of a thesis, scoped to one domain."""

    topic: str
    sections: List[OutlineSection]


class Claim(BaseModel):
    """A single grounded statement within a section draft.

    `chunk_id` must reference one of the chunks retrieved for this section, or be
    null if no retrieved chunk supports the claim. The verification pass checks
    this membership against the actual retrieval results - it never trusts the
    LLM's citation at face value (see DraftingService._verify_section).
    """

    text: str
    chunk_id: Optional[str] = Field(
        None, description="chunk_id of the retrieved source backing this claim, or null if unsupported"
    )


class SectionDraft(BaseModel):
    """LLM output for one outline section: a list of claims, each optionally cited."""

    claims: List[Claim]


class VerifiedClaim(BaseModel):
    """A claim after checking its `chunk_id` against the chunks retrieved for the section."""

    text: str
    chunk_id: Optional[str]
    verified: bool
    source_excerpt: Optional[str] = None


class VerifiedSection(BaseModel):
    """One outline section with all claims fact-checked against their sources."""

    title: str
    description: str
    claims: List[VerifiedClaim]

    @property
    def verified_ratio(self) -> float:
        if not self.claims:
            return 0.0
        return sum(1 for c in self.claims if c.verified) / len(self.claims)


class SourceEntry(BaseModel):
    """One row of the sources table appended to the drafting output."""

    chunk_id: str
    citation_id: str
    excerpt: str


class DraftingResult(BaseModel):
    """Full output of the citation-grounded drafting pipeline."""

    topic: str
    domain: str
    sections: List[VerifiedSection]
    sources: List[SourceEntry]
    markdown: str

    @property
    def overall_verified_ratio(self) -> float:
        all_claims = [c for section in self.sections for c in section.claims]
        if not all_claims:
            return 0.0
        return sum(1 for c in all_claims if c.verified) / len(all_claims)
