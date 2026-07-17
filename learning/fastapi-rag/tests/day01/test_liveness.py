import importlib
import importlib.util

import fastapi
import pytest
from httpx import ASGITransport, AsyncClient

MISSING_APP_MESSAGE = (
    "Day 1 starts red: create app/main.py and export a FastAPI instance named 'app'."
)


def load_app() -> fastapi.FastAPI:
    try:
        module_spec = importlib.util.find_spec("app.main")
    except ModuleNotFoundError:
        pytest.fail(MISSING_APP_MESSAGE, pytrace=False)
    assert module_spec is not None, MISSING_APP_MESSAGE

    module = importlib.import_module("app.main")
    application = getattr(module, "app", None)
    assert isinstance(application, fastapi.FastAPI), MISSING_APP_MESSAGE
    return application


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_liveness_returns_expected_json_response() -> None:
    application = load_app()

    async with AsyncClient(
        transport=ASGITransport(app=application),
        base_url="http://test",
    ) as client:
        response = await client.get("/api/v1/health/live")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"status": "alive"}


@pytest.mark.anyio
async def test_unknown_path_uses_framework_default_404() -> None:
    application = load_app()

    async with AsyncClient(
        transport=ASGITransport(app=application),
        base_url="http://test",
    ) as client:
        response = await client.get("/api/v1/does-not-exist")

    assert response.status_code == 404


def test_openapi_describes_liveness_contract() -> None:
    openapi = load_app().openapi()

    assert openapi["info"]["title"] == "FastAPI RAG Learning API"
    assert openapi["info"]["version"] == "0.1.0"

    operation = openapi["paths"]["/api/v1/health/live"]["get"]
    assert operation["summary"] == "Check liveness"
    assert "200" in operation["responses"]
