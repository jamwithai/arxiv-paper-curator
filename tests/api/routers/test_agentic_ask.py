from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient
from src import dependencies
from src.main import app
from src.services.agents.agentic_rag import AgenticRAGService


@pytest.fixture
def mock_agentic_rag_service():
    """Mock AgenticRAGService for API testing."""
    service = Mock(spec=AgenticRAGService)
    service.ask = AsyncMock(
        return_value={
            "query": "What is machine learning?",
            "answer": "Machine learning is a subset of AI that enables systems to learn from data.",
            "sources": ["https://arxiv.org/pdf/2301.00001.pdf"],
            "reasoning_steps": [
                "Validated query is about AI research",
                "Retrieved 3 relevant papers",
                "Generated answer from sources",
            ],
            "retrieval_attempts": 1,
            "rewritten_query": None,
        }
    )
    return service


@pytest.fixture
def client(mock_agentic_rag_service):
    """FastAPI test client with mocked dependencies."""

    # Override the dependency to return our mock service
    def override_get_agentic_rag_service():
        return mock_agentic_rag_service

    app.dependency_overrides[dependencies.get_agentic_rag_service] = override_get_agentic_rag_service

    yield TestClient(app)

    # Clean up after test
    app.dependency_overrides.clear()


class TestAgenticAskEndpoint:
    """Tests for POST /api/v1/ask-agentic endpoint."""

    def test_ask_agentic_success(self, client, mock_agentic_rag_service):
        """Test successful agentic RAG request."""
        response = client.post(
            "/api/v1/ask-agentic",
            json={"query": "What is machine learning?", "model": "llama3.2:1b", "top_k": 3, "use_hybrid": True},
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "query" in data
        assert "answer" in data
        assert "sources" in data
        assert "reasoning_steps" in data
        assert "retrieval_attempts" in data
        assert "chunks_used" in data
        assert "search_mode" in data

        # Verify content
        assert data["query"] == "What is machine learning?"
        assert "machine learning" in data["answer"].lower()
        assert len(data["sources"]) > 0
        assert len(data["reasoning_steps"]) > 0
        assert data["retrieval_attempts"] == 1

    def test_ask_agentic_minimal_request(self, client, mock_agentic_rag_service):
        """Test agentic RAG with minimal required fields."""
        response = client.post("/api/v1/ask-agentic", json={"query": "What is neural network?"})

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data

    def test_ask_agentic_empty_query(self, client, mock_agentic_rag_service):
        """Test agentic RAG with empty query returns 422."""
        mock_agentic_rag_service.ask = AsyncMock(side_effect=ValueError("Query cannot be empty"))

        response = client.post("/api/v1/ask-agentic", json={"query": ""})

        assert response.status_code == 422

    def test_ask_agentic_missing_query(self, client):
        """Test agentic RAG without query field returns 422."""
        response = client.post("/api/v1/ask-agentic", json={"model": "llama3.2:1b"})

        assert response.status_code == 422

    def test_ask_agentic_service_error(self, client, mock_agentic_rag_service):
        """Test agentic RAG when service raises exception."""
        mock_agentic_rag_service.ask = AsyncMock(side_effect=Exception("Service error"))

        response = client.post("/api/v1/ask-agentic", json={"query": "Test query"})

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data

    def test_ask_agentic_with_sources(self, client, mock_agentic_rag_service):
        """Test that sources are properly returned in response."""
        mock_agentic_rag_service.ask = AsyncMock(
            return_value={
                "query": "What is transformer architecture?",
                "answer": "Transformers use self-attention mechanisms.",
                "sources": ["https://arxiv.org/pdf/1706.03762.pdf"],
                "reasoning_steps": ["Retrieved papers", "Generated answer"],
                "retrieval_attempts": 1,
                "rewritten_query": None,
            }
        )

        response = client.post("/api/v1/ask-agentic", json={"query": "What is transformer architecture?"})

        assert response.status_code == 200
        data = response.json()
        assert len(data["sources"]) == 1
        assert "1706.03762" in data["sources"][0]

    def test_ask_agentic_reasoning_steps(self, client, mock_agentic_rag_service):
        """Test that reasoning steps are included in response."""
        mock_agentic_rag_service.ask = AsyncMock(
            return_value={
                "query": "What is deep learning?",
                "answer": "Deep learning is...",
                "sources": [],
                "reasoning_steps": [
                    "Query validation passed",
                    "Retrieved 3 papers",
                    "Graded documents as relevant",
                    "Generated final answer",
                ],
                "retrieval_attempts": 1,
                "rewritten_query": None,
            }
        )

        response = client.post("/api/v1/ask-agentic", json={"query": "What is deep learning?"})

        assert response.status_code == 200
        data = response.json()
        assert len(data["reasoning_steps"]) == 4
        assert "Query validation passed" in data["reasoning_steps"]

    def test_ask_agentic_with_rewritten_query(self, client, mock_agentic_rag_service):
        """Test response when query was rewritten."""
        mock_agentic_rag_service.ask = AsyncMock(
            return_value={
                "query": "ML stuff",
                "answer": "Machine learning...",
                "sources": [],
                "reasoning_steps": ["Query rewritten", "Retrieved papers"],
                "retrieval_attempts": 2,
                "rewritten_query": "What are the key concepts in machine learning?",
            }
        )

        response = client.post("/api/v1/ask-agentic", json={"query": "ML stuff"})

        assert response.status_code == 200
        data = response.json()
        assert data["rewritten_query"] == "What are the key concepts in machine learning?"
        assert data["retrieval_attempts"] == 2

    def test_ask_agentic_custom_model(self, client, mock_agentic_rag_service):
        """Test agentic RAG with custom model parameter."""
        response = client.post("/api/v1/ask-agentic", json={"query": "What is AI?", "model": "llama3.2:3b"})

        assert response.status_code == 200
        # Verify the service was called with the custom model
        mock_agentic_rag_service.ask.assert_called_once()
        call_kwargs = mock_agentic_rag_service.ask.call_args.kwargs
        assert call_kwargs["model"] == "llama3.2:3b"

    def test_ask_agentic_search_mode_hybrid(self, client, mock_agentic_rag_service):
        """Test that search_mode is set correctly for hybrid search."""
        response = client.post("/api/v1/ask-agentic", json={"query": "What is AI?", "use_hybrid": True})

        assert response.status_code == 200
        data = response.json()
        assert data["search_mode"] == "hybrid"

    def test_ask_agentic_search_mode_bm25(self, client, mock_agentic_rag_service):
        """Test that search_mode is set correctly for BM25 search."""
        response = client.post("/api/v1/ask-agentic", json={"query": "What is AI?", "use_hybrid": False})

        assert response.status_code == 200
        data = response.json()
        assert data["search_mode"] == "bm25"
