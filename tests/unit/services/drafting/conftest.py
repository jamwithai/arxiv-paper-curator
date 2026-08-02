from unittest.mock import AsyncMock, Mock

import pytest

from src.services.drafting.models import Claim, DraftOutline, OutlineSection, SectionDraft
from src.services.drafting.service import DraftingService


@pytest.fixture
def mock_opensearch_client():
    """Mock OpenSearch client returning two sample chunks by default."""
    client = Mock()
    client.search_unified = Mock(
        return_value={
            "hits": [
                {"chunk_id": "c1", "chunk_text": "Transformers use self-attention.", "arxiv_id": "1706.03762"},
                {"chunk_id": "c2", "chunk_text": "BERT is bidirectional.", "arxiv_id": "1810.04805"},
            ]
        }
    )
    return client


@pytest.fixture
def mock_jina_embeddings_client():
    client = Mock()
    client.embed_query = AsyncMock(return_value=[0.1] * 1024)
    return client


@pytest.fixture
def mock_llm_client():
    """Mock LLM client whose with_structured_output() dispatches by schema class.

    DraftingService calls with_structured_output twice per draft() run - once for
    DraftOutline (outline generation), once per section for SectionDraft - so a
    single fixed return_value (as in the agents conftest) isn't enough here.
    """
    client = Mock()
    langchain_model = Mock()

    outline_structured = Mock()
    outline_structured.ainvoke = AsyncMock(
        return_value=DraftOutline(
            topic="test topic",
            sections=[OutlineSection(title="Section A", description="Covers A")],
        )
    )

    section_structured = Mock()
    section_structured.ainvoke = AsyncMock(
        return_value=SectionDraft(
            claims=[
                Claim(text="Claim backed by c1", chunk_id="c1"),
                Claim(text="Unsupported claim", chunk_id=None),
            ]
        )
    )

    def _with_structured_output(schema, method=None):
        if schema is DraftOutline:
            return outline_structured
        if schema is SectionDraft:
            return section_structured
        raise AssertionError(f"Unexpected schema passed to with_structured_output: {schema}")

    langchain_model.with_structured_output = Mock(side_effect=_with_structured_output)
    client.get_langchain_model = Mock(return_value=langchain_model)

    # Exposed so individual tests can override behavior/assert calls.
    client.outline_structured = outline_structured
    client.section_structured = section_structured
    return client


@pytest.fixture
def drafting_service(mock_opensearch_client, mock_llm_client, mock_jina_embeddings_client):
    return DraftingService(
        opensearch_client=mock_opensearch_client,
        llm_client=mock_llm_client,
        embeddings_client=mock_jina_embeddings_client,
        model="deepseek-v4-pro",
        top_k_per_section=2,
    )
