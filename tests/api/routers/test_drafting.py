from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient

from src import dependencies
from src.main import app
from src.services.drafting.models import DraftingResult, SourceEntry, VerifiedClaim, VerifiedSection
from src.services.drafting.service import DraftingService


@pytest.fixture
def mock_drafting_service():
    """Mock DraftingService for API testing."""
    service = Mock(spec=DraftingService)
    service.draft = AsyncMock(
        return_value=DraftingResult(
            topic="What is machine learning?",
            domain="ai",
            sections=[
                VerifiedSection(
                    title="Section A",
                    description="Covers A",
                    claims=[
                        VerifiedClaim(
                            text="Claim backed by c1", chunk_id="c1", verified=True, source_excerpt="excerpt"
                        ),
                        VerifiedClaim(text="Unsupported claim", chunk_id=None, verified=False),
                    ],
                )
            ],
            sources=[SourceEntry(chunk_id="c1", citation_id="1706.03762", excerpt="excerpt")],
            markdown="# What is machine learning?\n\n## 1. Section A\n",
        )
    )
    return service


@pytest.fixture
def client(mock_drafting_service):
    def override_get_drafting_service():
        return mock_drafting_service

    app.dependency_overrides[dependencies.get_drafting_service] = override_get_drafting_service

    yield TestClient(app)

    app.dependency_overrides.clear()


class TestDraftEndpoint:
    """Tests for POST /api/v1/draft."""

    def test_draft_success(self, client, mock_drafting_service):
        response = client.post(
            "/api/v1/draft",
            json={"topic": "What is machine learning?", "domain": "ai"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["topic"] == "What is machine learning?"
        assert data["domain"] == "ai"
        assert len(data["sections"]) == 1
        assert len(data["sections"][0]["claims"]) == 2
        assert data["sections"][0]["verified_ratio"] == 0.5
        assert data["overall_verified_ratio"] == 0.5
        assert len(data["sources"]) == 1
        assert "# What is machine learning?" in data["markdown"]

        mock_drafting_service.draft.assert_called_once_with(topic="What is machine learning?", domain="ai", model=None)

    def test_draft_missing_topic_returns_422(self, client):
        response = client.post("/api/v1/draft", json={"domain": "ai"})

        assert response.status_code == 422

    def test_draft_empty_topic_returns_422(self, client, mock_drafting_service):
        mock_drafting_service.draft = AsyncMock(side_effect=ValueError("Topic cannot be empty"))

        response = client.post("/api/v1/draft", json={"topic": "   "})

        assert response.status_code == 422

    def test_draft_service_error_returns_500(self, client, mock_drafting_service):
        mock_drafting_service.draft = AsyncMock(side_effect=Exception("LLM unavailable"))

        response = client.post("/api/v1/draft", json={"topic": "Test topic"})

        assert response.status_code == 500
        assert "detail" in response.json()

    def test_draft_defaults_domain_to_ai(self, client, mock_drafting_service):
        response = client.post("/api/v1/draft", json={"topic": "Test topic"})

        assert response.status_code == 200
        mock_drafting_service.draft.assert_called_once_with(topic="Test topic", domain="ai", model=None)

    def test_draft_passes_model_override(self, client, mock_drafting_service):
        response = client.post(
            "/api/v1/draft",
            json={"topic": "Test topic", "domain": "education", "model": "deepseek-v4-pro"},
        )

        assert response.status_code == 200
        mock_drafting_service.draft.assert_called_once_with(
            topic="Test topic", domain="education", model="deepseek-v4-pro"
        )
