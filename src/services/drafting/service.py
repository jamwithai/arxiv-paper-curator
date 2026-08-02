import logging
from typing import Any, Dict, List, Optional

from src.domain_profiles import DomainProfile, get_domain_profile
from src.services.embeddings.jina_client import JinaEmbeddingsClient
from src.services.llm.base import LLMClient
from src.services.opensearch.client import OpenSearchClient

from .models import (
    Claim,
    DraftingResult,
    DraftOutline,
    OutlineSection,
    SectionDraft,
    SourceEntry,
    VerifiedClaim,
    VerifiedSection,
)
from .prompts import OUTLINE_PROMPT, SECTION_DRAFT_PROMPT

logger = logging.getLogger(__name__)


def _chunk_text(chunk: Optional[Dict[str, Any]]) -> str:
    """Resolve chunk body text across arXiv (chunk_text) and bilingual (chunk_text_vi/en) mappings."""
    if not chunk:
        return ""
    return chunk.get("chunk_text") or chunk.get("chunk_text_vi") or chunk.get("chunk_text_en") or ""


def _citation_id(chunk: Dict[str, Any]) -> str:
    """Resolve the human-facing citation id (arxiv_id, or doc_number/doc_id for bilingual domains)."""
    return chunk.get("arxiv_id") or chunk.get("doc_number") or chunk.get("doc_id") or chunk.get("chunk_id", "")


class DraftingService:
    """Citation-grounded drafting for thesis Chapter 1-2 sections (Stage 3).

    Pipeline: outline -> per-section retrieval -> grounded generation -> verification.
    Verification never trusts the LLM's cited chunk_id at face value - it checks the
    id against the chunks actually retrieved for that section (`_verify_section`).
    That membership check is what makes "% claims traceable to a source" a real
    metric rather than a self-report, and it never requires re-calling the LLM.

    This is a standalone pipeline, not a LangGraph graph: the control flow is a
    fixed sequence (outline -> per-section retrieve/draft/verify), so a graph
    would add indirection without buying anything the agentic RAG flow needs
    (retry loops, conditional routing).
    """

    def __init__(
        self,
        opensearch_client: OpenSearchClient,
        llm_client: LLMClient,
        embeddings_client: JinaEmbeddingsClient,
        model: str,
        top_k_per_section: int = 5,
        temperature: float = 0.2,
    ):
        self.opensearch = opensearch_client
        self.llm = llm_client
        self.embeddings = embeddings_client
        self.model = model
        self.top_k_per_section = top_k_per_section
        self.temperature = temperature

    async def draft(self, topic: str, domain: str = "ai", model: Optional[str] = None) -> DraftingResult:
        """Run the full outline -> retrieve -> draft -> verify pipeline for one topic.

        :param topic: Thesis topic / research question to draft an outline for
        :param domain: Corpus domain to ground the draft in ("ai", "education", "accounting")
        :param model: Optional LLM model override; defaults to the service's configured model
        :raises ValueError: If topic is empty or the LLM returns an empty outline
        """
        if not topic or not topic.strip():
            raise ValueError("Topic cannot be empty")

        model_to_use = model or self.model
        domain_profile = get_domain_profile(domain)

        outline = await self._generate_outline(topic, domain_profile, model_to_use)

        verified_sections: List[VerifiedSection] = []
        source_map: Dict[str, SourceEntry] = {}

        for section in outline.sections:
            chunks = await self._retrieve_for_section(topic, section, domain)
            section_draft = await self._draft_section(section, chunks, domain_profile, model_to_use)
            verified_sections.append(self._verify_section(section, section_draft, chunks))

            for chunk in chunks:
                chunk_id = chunk.get("chunk_id")
                if chunk_id and chunk_id not in source_map:
                    source_map[chunk_id] = SourceEntry(
                        chunk_id=chunk_id,
                        citation_id=_citation_id(chunk),
                        excerpt=_chunk_text(chunk)[:300],
                    )

        sources = list(source_map.values())
        markdown = self._render_markdown(topic, domain_profile.label, verified_sections, sources)

        return DraftingResult(
            topic=topic,
            domain=domain,
            sections=verified_sections,
            sources=sources,
            markdown=markdown,
        )

    async def _generate_outline(self, topic: str, domain_profile: DomainProfile, model: str) -> DraftOutline:
        prompt = OUTLINE_PROMPT.format(domain_label=domain_profile.label, topic=topic)
        structured_llm = self.llm.get_langchain_model(
            model=model, temperature=self.temperature
        ).with_structured_output(DraftOutline, method="json_mode")

        outline = await structured_llm.ainvoke(prompt)
        if not outline.sections:
            raise ValueError("LLM returned an outline with no sections")
        return outline

    async def _retrieve_for_section(self, topic: str, section: OutlineSection, domain: str) -> List[Dict[str, Any]]:
        query = f"{topic} - {section.title}: {section.description}"

        embedding = None
        try:
            embedding = await self.embeddings.embed_query(query)
        except Exception as e:
            logger.warning(f"Embedding failed for section '{section.title}', falling back to BM25: {e}")

        results = self.opensearch.search_unified(
            query=query,
            query_embedding=embedding,
            size=self.top_k_per_section,
            use_hybrid=embedding is not None,
            domain=domain,
        )
        return results.get("hits", [])

    async def _draft_section(
        self,
        section: OutlineSection,
        chunks: List[Dict[str, Any]],
        domain_profile: DomainProfile,
        model: str,
    ) -> SectionDraft:
        if not chunks:
            # No sources retrieved: the section must be flagged, never fabricated.
            return SectionDraft(claims=[Claim(text=f"{section.title}: cần bổ sung tài liệu.", chunk_id=None)])

        context = "\n\n".join(f"[chunk_id: {c.get('chunk_id')}]\n{_chunk_text(c)}" for c in chunks)

        prompt = SECTION_DRAFT_PROMPT.format(
            section_title=section.title,
            section_description=section.description,
            domain_label=domain_profile.label,
            citation_style=domain_profile.citation_style,
            context=context,
        )
        structured_llm = self.llm.get_langchain_model(
            model=model, temperature=self.temperature
        ).with_structured_output(SectionDraft, method="json_mode")

        return await structured_llm.ainvoke(prompt)

    def _verify_section(
        self, section: OutlineSection, draft: SectionDraft, chunks: List[Dict[str, Any]]
    ) -> VerifiedSection:
        chunk_map = {c.get("chunk_id"): c for c in chunks if c.get("chunk_id")}

        verified_claims = []
        for claim in draft.claims:
            source_chunk = chunk_map.get(claim.chunk_id) if claim.chunk_id else None
            verified_claims.append(
                VerifiedClaim(
                    text=claim.text,
                    chunk_id=claim.chunk_id,
                    verified=source_chunk is not None,
                    source_excerpt=_chunk_text(source_chunk)[:300] if source_chunk else None,
                )
            )

        return VerifiedSection(title=section.title, description=section.description, claims=verified_claims)

    def _render_markdown(
        self,
        topic: str,
        domain_label: str,
        sections: List[VerifiedSection],
        sources: List[SourceEntry],
    ) -> str:
        lines = [f"# {topic}", "", f"_Corpus: {domain_label}_", ""]

        for i, section in enumerate(sections, 1):
            lines.append(f"## {i}. {section.title}")
            lines.append("")
            for claim in section.claims:
                marker = f"[{claim.chunk_id}]" if claim.verified else "**[cần bổ sung tài liệu]**"
                lines.append(f"- {claim.text} {marker}")
            lines.append("")
            lines.append(f"_Traceable claims: {section.verified_ratio:.0%}_")
            lines.append("")

        lines.append("## Sources")
        lines.append("")
        lines.append("| chunk_id | citation | excerpt |")
        lines.append("|---|---|---|")
        for source in sources:
            excerpt = source.excerpt.replace("\n", " ").replace("|", "\\|")
            lines.append(f"| {source.chunk_id} | {source.citation_id} | {excerpt} |")

        return "\n".join(lines)
