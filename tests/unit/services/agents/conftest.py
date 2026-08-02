from unittest.mock import AsyncMock, Mock

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from src.services.agents.context import Context


@pytest.fixture
def mock_opensearch_client():
    """Mock OpenSearch client returning two sample hits by default."""
    client = Mock()
    client.search_unified = Mock(
        return_value={
            "hits": [
                {
                    "chunk_text": "Transformers are neural network architectures based on self-attention mechanisms.",
                    "arxiv_id": "1706.03762",
                    "title": "Attention Is All You Need",
                    "authors": "Vaswani et al.",
                    "score": 0.95,
                    "section_name": "Abstract",
                },
                {
                    "chunk_text": "BERT is a bidirectional transformer pretrained on masked language modeling.",
                    "arxiv_id": "1810.04805",
                    "title": "BERT: Pre-training of Deep Bidirectional Transformers",
                    "authors": "Devlin et al.",
                    "score": 0.90,
                    "section_name": "Abstract",
                },
            ]
        }
    )
    return client


@pytest.fixture
def mock_jina_embeddings_client():
    """Mock Jina embeddings client."""
    client = Mock()
    client.embed_query = AsyncMock(return_value=[0.1] * 1024)
    return client


@pytest.fixture
def mock_llm_client():
    """Mock LLM client whose get_langchain_model() returns a mock LangChain model.

    Individual tests override `.get_langchain_model.return_value` (or the
    `.ainvoke` / `.with_structured_output` behavior of that return value) to
    control what the "LLM" produces for a given node under test.
    """
    client = Mock()
    langchain_model = Mock()
    langchain_model.ainvoke = AsyncMock(return_value=AIMessage(content="Mock LLM response"))
    structured_model = Mock()
    structured_model.ainvoke = AsyncMock()
    langchain_model.with_structured_output = Mock(return_value=structured_model)
    client.get_langchain_model = Mock(return_value=langchain_model)
    return client


@pytest.fixture
def test_context(mock_llm_client, mock_opensearch_client, mock_jina_embeddings_client):
    """Runtime Context populated with mocked dependencies."""
    return Context(
        llm_client=mock_llm_client,
        opensearch_client=mock_opensearch_client,
        embeddings_client=mock_jina_embeddings_client,
        langfuse_tracer=None,
        langfuse_enabled=False,
    )


@pytest.fixture
def sample_human_message():
    return HumanMessage(content="What is machine learning?")


@pytest.fixture
def sample_ai_message():
    return AIMessage(content="Machine learning is a subset of AI.")


@pytest.fixture
def sample_tool_message():
    return ToolMessage(
        content="Transformers are neural network architectures based on self-attention mechanisms.",
        tool_call_id="retrieve_1",
    )
