from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from src.main import app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Async backend for testing."""
    return "asyncio"


@pytest.fixture
async def client():
    """HTTP client for API testing with mocked services."""
    # Mock database startup and session to prevent real connections
    with (
        patch("src.db.interfaces.postgresql.PostgreSQLDatabase.startup") as mock_startup,
        patch("src.db.interfaces.postgresql.PostgreSQLDatabase.get_session") as mock_get_session,
        patch("src.services.opensearch.factory.make_opensearch_client") as mock_os,
        patch("src.services.arxiv.factory.make_arxiv_client") as mock_arxiv,
        patch("src.services.pdf_parser.factory.make_pdf_parser_service") as mock_pdf,
        patch("src.services.ollama.client.OllamaClient") as mock_ollama,
        patch("src.repositories.paper.PaperRepository.get_by_arxiv_id") as mock_get_by_id,
    ):
        # Mock startup to do nothing
        mock_startup.return_value = None

        # Mock get_session to return a mock session
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_get_session.return_value.__exit__.return_value = None

        # Mock repository methods to return None (not found) by default
        mock_get_by_id.return_value = None

        # Set up other mock return values
        mock_os.return_value = AsyncMock()
        mock_arxiv.return_value = AsyncMock()
        mock_pdf.return_value = AsyncMock()
        mock_ollama.return_value = AsyncMock()

        async with LifespanManager(app) as manager:
            async with AsyncClient(transport=ASGITransport(app=manager.app), base_url="http://test") as client:
                yield client
