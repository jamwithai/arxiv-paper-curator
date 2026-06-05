"""Integration tests for MiniMax LLM provider.

These tests verify MiniMax API connectivity and basic functionality.
They require MINIMAX_API_KEY to be set in the environment.
"""

import os

import pytest

from src.services.minimax.client import MiniMaxClient


def _get_minimax_client():
    """Create a MiniMax client for integration testing."""
    from unittest.mock import MagicMock

    api_key = os.environ.get("MINIMAX_API_KEY", "")
    if not api_key:
        pytest.skip("MINIMAX_API_KEY not set, skipping integration test")

    settings = MagicMock()
    settings.minimax_api_key = api_key
    settings.minimax_model = "MiniMax-M3"
    settings.minimax_base_url = "https://api.minimax.io/v1"
    settings.minimax_timeout = 60
    return MiniMaxClient(settings)


@pytest.mark.asyncio
async def test_minimax_health_check():
    """Test MiniMax API health check."""
    client = _get_minimax_client()
    result = await client.health_check()
    assert result["status"] == "healthy"
    assert result["provider"] == "minimax"


@pytest.mark.asyncio
async def test_minimax_generate():
    """Test basic text generation with MiniMax API."""
    client = _get_minimax_client()
    result = await client.generate(
        model="MiniMax-M3",
        prompt="What is 2+2? Reply with just the number.",
        temperature=0.01,
    )
    assert result is not None
    assert "response" in result
    assert len(result["response"]) > 0
    assert "4" in result["response"]
    assert result["usage_metadata"]["total_tokens"] > 0


@pytest.mark.asyncio
async def test_minimax_get_langchain_model():
    """Test LangChain model creation for MiniMax."""
    client = _get_minimax_client()
    model = client.get_langchain_model(model="MiniMax-M3", temperature=0.5)
    assert model is not None
    assert model.model_name == "MiniMax-M3"
    assert model.temperature == 0.5

    # Test invocation
    response = await model.ainvoke("What is 1+1? Reply with just the number.")
    assert response is not None
    assert hasattr(response, "content")
    assert "2" in response.content
