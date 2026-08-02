from unittest.mock import Mock

import pytest

from src.services.drafting.models import SectionDraft


@pytest.mark.asyncio
async def test_draft_raises_for_empty_topic(drafting_service):
    with pytest.raises(ValueError, match="Topic cannot be empty"):
        await drafting_service.draft(topic="   ")


@pytest.mark.asyncio
async def test_draft_verifies_claims_against_retrieved_chunks(drafting_service, mock_opensearch_client):
    """Claims citing a chunk_id that was actually retrieved must be verified=True;
    claims with no chunk_id must be flagged, never silently trusted."""
    result = await drafting_service.draft(topic="RAG for legal documents", domain="education")

    assert result.topic == "RAG for legal documents"
    assert result.domain == "education"
    assert len(result.sections) == 1

    section = result.sections[0]
    assert section.title == "Section A"
    assert len(section.claims) == 2

    verified_claim = next(c for c in section.claims if c.chunk_id == "c1")
    assert verified_claim.verified is True
    assert verified_claim.source_excerpt == "Transformers use self-attention."

    unsupported_claim = next(c for c in section.claims if c.chunk_id is None)
    assert unsupported_claim.verified is False
    assert unsupported_claim.source_excerpt is None

    assert section.verified_ratio == 0.5
    assert result.overall_verified_ratio == 0.5

    mock_opensearch_client.search_unified.assert_called_once()
    assert mock_opensearch_client.search_unified.call_args.kwargs["domain"] == "education"


@pytest.mark.asyncio
async def test_draft_rejects_chunk_id_not_actually_retrieved(drafting_service, mock_llm_client):
    """A claim citing a chunk_id the retriever never returned (hallucinated citation)
    must be marked unverified, even though the LLM supplied a non-null chunk_id."""
    mock_llm_client.section_structured.ainvoke.return_value = SectionDraft(
        claims=[{"text": "Fabricated citation", "chunk_id": "does-not-exist"}]
    )

    result = await drafting_service.draft(topic="test topic")

    claim = result.sections[0].claims[0]
    assert claim.chunk_id == "does-not-exist"
    assert claim.verified is False
    assert result.overall_verified_ratio == 0.0


@pytest.mark.asyncio
async def test_draft_flags_section_with_no_retrieved_chunks(drafting_service, mock_opensearch_client, mock_llm_client):
    """When retrieval returns nothing, the section must be flagged 'cần bổ sung tài
    liệu' rather than asking the LLM to draft from no sources."""
    mock_opensearch_client.search_unified = Mock(return_value={"hits": []})

    result = await drafting_service.draft(topic="test topic")

    section = result.sections[0]
    assert len(section.claims) == 1
    assert section.claims[0].chunk_id is None
    assert section.claims[0].verified is False
    assert "cần bổ sung tài liệu" in section.claims[0].text
    mock_llm_client.section_structured.ainvoke.assert_not_called()


@pytest.mark.asyncio
async def test_draft_falls_back_to_bm25_when_embeddings_fail(drafting_service, mock_jina_embeddings_client, mock_opensearch_client):
    mock_jina_embeddings_client.embed_query.side_effect = Exception("embeddings service down")

    await drafting_service.draft(topic="test topic")

    call_kwargs = mock_opensearch_client.search_unified.call_args.kwargs
    assert call_kwargs["query_embedding"] is None
    assert call_kwargs["use_hybrid"] is False


@pytest.mark.asyncio
async def test_draft_collects_sources_from_all_retrieved_chunks(drafting_service):
    """The sources table should include every retrieved chunk (so the author can
    see what was available), not just the ones a claim happened to cite."""
    result = await drafting_service.draft(topic="test topic")

    chunk_ids = {s.chunk_id for s in result.sources}
    assert chunk_ids == {"c1", "c2"}
    c1_source = next(s for s in result.sources if s.chunk_id == "c1")
    assert c1_source.citation_id == "1706.03762"


@pytest.mark.asyncio
async def test_draft_markdown_includes_flagged_claims_and_sources_table(drafting_service):
    result = await drafting_service.draft(topic="test topic")

    assert "# test topic" in result.markdown
    assert "cần bổ sung tài liệu" in result.markdown
    assert "[c1]" in result.markdown
    assert "## Sources" in result.markdown
    assert "1706.03762" in result.markdown


@pytest.mark.asyncio
async def test_draft_raises_for_empty_outline(drafting_service, mock_llm_client):
    from src.services.drafting.models import DraftOutline

    mock_llm_client.outline_structured.ainvoke.return_value = DraftOutline(topic="empty", sections=[])

    with pytest.raises(ValueError, match="no sections"):
        await drafting_service.draft(topic="test topic")
