import pytest
from unittest.mock import AsyncMock, Mock, patch
from langchain_core.documents import Document
from langchain_core.messages import ToolMessage

from src.services.agents.tools import create_retriever_tool


def _tool_call(query: str, call_id: str = "call_1") -> dict:
    """Build a ToolCall dict, the invocation shape ToolNode actually uses.

    `retrieve_papers` is a response_format="content_and_artifact" tool: invoking
    it with a plain {"query": ...} dict only returns the content string.
    Invoking with a ToolCall dict returns the full ToolMessage, including
    `.artifact` - which is what these tests need to verify.
    """
    return {"name": "retrieve_papers", "args": {"query": query}, "id": call_id, "type": "tool_call"}


@pytest.mark.asyncio
async def test_create_retriever_tool_basic(mock_opensearch_client, mock_jina_embeddings_client):
    """Test basic retriever tool creation and invocation."""
    tool = create_retriever_tool(
        opensearch_client=mock_opensearch_client,
        embeddings_client=mock_jina_embeddings_client,
        top_k=2,
        use_hybrid=True,
    )

    # Verify tool properties
    assert tool.name == "retrieve_papers"
    assert "Search and return relevant arXiv research papers" in tool.description

    # Invoke tool via ToolCall (the shape ToolNode uses) to get the full ToolMessage
    message = await tool.ainvoke(_tool_call("machine learning"))

    assert isinstance(message, ToolMessage)
    assert isinstance(message.content, str)
    assert isinstance(message.artifact, list)
    assert len(message.artifact) == 2
    assert all(isinstance(doc, Document) for doc in message.artifact)

    # Verify first document (the artifact, not the LLM-facing content string)
    first_doc = message.artifact[0]
    assert first_doc.page_content == "Transformers are neural network architectures based on self-attention mechanisms."
    assert first_doc.metadata["arxiv_id"] == "1706.03762"
    assert first_doc.metadata["title"] == "Attention Is All You Need"
    assert first_doc.metadata["score"] == 0.95

    # Content string is what the LLM sees; must carry the same source text
    assert "Transformers are neural network architectures" in message.content
    assert "1706.03762" in message.content

    # Verify embeddings were generated
    mock_jina_embeddings_client.embed_query.assert_called_once_with("machine learning")

    # Verify search was called correctly
    mock_opensearch_client.search_unified.assert_called_once()
    call_args = mock_opensearch_client.search_unified.call_args
    assert call_args.kwargs["query"] == "machine learning"
    assert call_args.kwargs["size"] == 2  # search_unified uses 'size', not 'top_k'
    assert call_args.kwargs["use_hybrid"] is True


@pytest.mark.asyncio
async def test_retriever_tool_empty_results(mock_opensearch_client, mock_jina_embeddings_client):
    """Test retriever tool with no results."""
    mock_opensearch_client.search_unified = Mock(return_value={"hits": []})

    tool = create_retriever_tool(
        opensearch_client=mock_opensearch_client,
        embeddings_client=mock_jina_embeddings_client,
    )

    message = await tool.ainvoke(_tool_call("nonexistent topic"))

    assert message.artifact == []
    assert message.content == ""


@pytest.mark.asyncio
async def test_retriever_tool_custom_top_k(mock_opensearch_client, mock_jina_embeddings_client):
    """Test retriever tool with custom top_k parameter."""
    tool = create_retriever_tool(
        opensearch_client=mock_opensearch_client,
        embeddings_client=mock_jina_embeddings_client,
        top_k=5,
        use_hybrid=False,
    )

    await tool.ainvoke(_tool_call("test query"))

    call_args = mock_opensearch_client.search_unified.call_args
    # search_unified uses 'size' parameter, not 'top_k'
    assert call_args.kwargs["size"] == 5
    assert call_args.kwargs["use_hybrid"] is False


@pytest.mark.asyncio
async def test_retriever_tool_metadata_fields(mock_opensearch_client, mock_jina_embeddings_client):
    """Test that all expected metadata fields are present."""
    mock_opensearch_client.search_unified = Mock(
        return_value={
            "hits": [
                {
                    "chunk_text": "Test content",
                    "arxiv_id": "2301.00001",
                    "title": "Test Paper",
                    "authors": "Author One, Author Two",
                    "score": 0.95,
                    "section_name": "Introduction",
                }
            ]
        }
    )

    tool = create_retriever_tool(
        opensearch_client=mock_opensearch_client,
        embeddings_client=mock_jina_embeddings_client,
    )

    message = await tool.ainvoke(_tool_call("test"))

    doc = message.artifact[0]
    assert "arxiv_id" in doc.metadata
    assert "title" in doc.metadata
    assert "authors" in doc.metadata
    assert "score" in doc.metadata
    assert "source" in doc.metadata
    assert "section" in doc.metadata


@pytest.mark.asyncio
async def test_retriever_tool_passes_active_domain_to_search(mock_opensearch_client, mock_jina_embeddings_client):
    """The retriever tool must read `domain` from the active graph run (Stage 2),
    not just search whichever index the client defaults to."""
    fake_runtime = Mock()
    fake_runtime.context.domain = "education"

    tool = create_retriever_tool(
        opensearch_client=mock_opensearch_client,
        embeddings_client=mock_jina_embeddings_client,
    )

    with patch("src.services.agents.tools.get_runtime", return_value=fake_runtime):
        await tool.ainvoke(_tool_call("test query"))

    call_args = mock_opensearch_client.search_unified.call_args
    assert call_args.kwargs["domain"] == "education"


@pytest.mark.asyncio
async def test_retriever_tool_domain_defaults_to_none_outside_a_graph_run(
    mock_opensearch_client, mock_jina_embeddings_client
):
    """Without an active LangGraph run (e.g. direct unit invocation), get_runtime()
    raises - the tool must fall back gracefully instead of crashing."""
    tool = create_retriever_tool(
        opensearch_client=mock_opensearch_client,
        embeddings_client=mock_jina_embeddings_client,
    )

    await tool.ainvoke(_tool_call("test query"))

    call_args = mock_opensearch_client.search_unified.call_args
    assert call_args.kwargs["domain"] is None


@pytest.mark.asyncio
async def test_retriever_tool_resolves_bilingual_chunk_fields(mock_opensearch_client, mock_jina_embeddings_client):
    """Bilingual domain hits use chunk_text_vi/chunk_text_en/doc_id instead of
    chunk_text/arxiv_id (see LEGAL_DOCS_CHUNKS_MAPPING) - the tool must not KeyError."""
    mock_opensearch_client.search_unified = Mock(
        return_value={
            "hits": [
                {
                    "doc_id": "tt01",
                    "chunk_text_vi": "Quy định về đánh giá học sinh.",
                    "chunk_text_en": "",
                    "title": "Thông tư 22/2021/TT-BGDDT",
                    "score": 0.9,
                }
            ]
        }
    )

    tool = create_retriever_tool(
        opensearch_client=mock_opensearch_client,
        embeddings_client=mock_jina_embeddings_client,
    )

    message = await tool.ainvoke(_tool_call("đánh giá học sinh"))

    doc = message.artifact[0]
    assert doc.page_content == "Quy định về đánh giá học sinh."
    assert doc.metadata["arxiv_id"] == "tt01"
    assert doc.metadata["source"] == "doc:tt01"
