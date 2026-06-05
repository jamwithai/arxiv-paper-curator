"""Unit tests for MiniMax LLM client."""

import json

import pytest
from unittest.mock import AsyncMock, MagicMock, Mock, patch

from src.services.minimax.client import (
    MiniMaxClient,
    MINIMAX_MODELS,
    _clamp_temperature,
    _strip_think_tags,
)
from src.exceptions import MiniMaxConnectionError, MiniMaxException, MiniMaxTimeoutError


@pytest.fixture
def minimax_settings():
    """Create mock settings for MiniMax client."""
    settings = MagicMock()
    settings.minimax_api_key = "test-api-key"
    settings.minimax_model = "MiniMax-M3"
    settings.minimax_base_url = "https://api.minimax.io/v1"
    settings.minimax_timeout = 300
    return settings


@pytest.fixture
def minimax_client(minimax_settings):
    """Create a MiniMax client with mock settings."""
    return MiniMaxClient(minimax_settings)


class TestClampTemperature:
    """Tests for temperature clamping utility."""

    def test_zero_temperature_clamped(self):
        assert _clamp_temperature(0.0) == 0.01

    def test_negative_temperature_clamped(self):
        assert _clamp_temperature(-0.5) == 0.01

    def test_valid_temperature_unchanged(self):
        assert _clamp_temperature(0.5) == 0.5

    def test_max_temperature(self):
        assert _clamp_temperature(1.0) == 1.0

    def test_over_max_clamped(self):
        assert _clamp_temperature(1.5) == 1.0

    def test_small_positive_unchanged(self):
        assert _clamp_temperature(0.01) == 0.01


class TestStripThinkTags:
    """Tests for think tag stripping utility."""

    def test_strip_think_tags(self):
        text = "<think>some reasoning</think>The answer is 42."
        assert _strip_think_tags(text) == "The answer is 42."

    def test_no_think_tags(self):
        text = "The answer is 42."
        assert _strip_think_tags(text) == "The answer is 42."

    def test_multiline_think_tags(self):
        text = "<think>\nstep 1\nstep 2\n</think>\nFinal answer."
        assert _strip_think_tags(text) == "Final answer."

    def test_empty_think_tags(self):
        text = "<think></think>Hello"
        assert _strip_think_tags(text) == "Hello"


class TestMiniMaxClientInit:
    """Tests for MiniMax client initialization."""

    def test_client_initialization(self, minimax_client, minimax_settings):
        assert minimax_client.api_key == "test-api-key"
        assert minimax_client.default_model == "MiniMax-M3"
        assert minimax_client.base_url == "https://api.minimax.io/v1"

    def test_models_list(self):
        assert "MiniMax-M3" in MINIMAX_MODELS
        assert "MiniMax-M2.7" in MINIMAX_MODELS
        assert "MiniMax-M2.7-highspeed" in MINIMAX_MODELS
        assert MINIMAX_MODELS[0] == "MiniMax-M3"


class TestGetLangchainModel:
    """Tests for get_langchain_model method."""

    def test_returns_chat_openai(self, minimax_client):
        model = minimax_client.get_langchain_model()
        assert model is not None
        assert model.model_name == "MiniMax-M3"

    def test_custom_model(self, minimax_client):
        model = minimax_client.get_langchain_model(model="MiniMax-M2.7-highspeed")
        assert model.model_name == "MiniMax-M2.7-highspeed"

    def test_temperature_clamped(self, minimax_client):
        model = minimax_client.get_langchain_model(temperature=0.0)
        assert model.temperature == 0.01

    def test_valid_temperature(self, minimax_client):
        model = minimax_client.get_langchain_model(temperature=0.7)
        assert model.temperature == 0.7


class TestHealthCheck:
    """Tests for health check method."""

    @pytest.mark.asyncio
    async def test_health_check_success(self, minimax_client):
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("httpx.AsyncClient") as mock_async_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_async_client.return_value = mock_client

            result = await minimax_client.health_check()

            assert result["status"] == "healthy"
            assert result["provider"] == "minimax"

    @pytest.mark.asyncio
    async def test_health_check_failure(self, minimax_client):
        mock_response = MagicMock()
        mock_response.status_code = 401

        with patch("httpx.AsyncClient") as mock_async_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_async_client.return_value = mock_client

            with pytest.raises(MiniMaxException):
                await minimax_client.health_check()


class TestListModels:
    """Tests for list_models method."""

    @pytest.mark.asyncio
    async def test_list_models(self, minimax_client):
        models = await minimax_client.list_models()
        assert len(models) == 3
        assert models[0]["id"] == "MiniMax-M3"
        assert models[1]["id"] == "MiniMax-M2.7"
        assert models[2]["id"] == "MiniMax-M2.7-highspeed"
        assert models[0]["provider"] == "minimax"


class TestGenerate:
    """Tests for generate method."""

    @pytest.mark.asyncio
    async def test_generate_success(self, minimax_client):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Hello world"}}],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15,
            },
        }

        with patch("httpx.AsyncClient") as mock_async_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_async_client.return_value = mock_client

            result = await minimax_client.generate(
                model="MiniMax-M3",
                prompt="Say hello",
            )

            assert result["response"] == "Hello world"
            assert result["usage_metadata"]["total_tokens"] == 15

    @pytest.mark.asyncio
    async def test_generate_strips_think_tags(self, minimax_client):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "<think>reasoning</think>Answer"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        }

        with patch("httpx.AsyncClient") as mock_async_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_async_client.return_value = mock_client

            result = await minimax_client.generate(
                model="MiniMax-M3",
                prompt="Test",
            )

            assert result["response"] == "Answer"

    @pytest.mark.asyncio
    async def test_generate_api_error(self, minimax_client):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        with patch("httpx.AsyncClient") as mock_async_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_async_client.return_value = mock_client

            with pytest.raises(MiniMaxException):
                await minimax_client.generate(
                    model="MiniMax-M3",
                    prompt="Test",
                )

    @pytest.mark.asyncio
    async def test_generate_removes_unsupported_params(self, minimax_client):
        """Test that response_format and format params are removed."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "OK"}}],
            "usage": {"prompt_tokens": 5, "completion_tokens": 1, "total_tokens": 6},
        }

        with patch("httpx.AsyncClient") as mock_async_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_async_client.return_value = mock_client

            result = await minimax_client.generate(
                model="MiniMax-M3",
                prompt="Test",
                format={"type": "json"},
                response_format={"type": "json_object"},
            )

            assert result["response"] == "OK"
            # Verify the unsupported params were not sent in the request
            call_args = mock_client.post.call_args
            payload = call_args[1]["json"]
            assert "format" not in payload
            assert "response_format" not in payload


class TestGenerateRagAnswer:
    """Tests for generate_rag_answer method."""

    @pytest.mark.asyncio
    async def test_generate_rag_answer(self, minimax_client):
        chunks = [
            {"arxiv_id": "2301.01234", "chunk_text": "Transformers are neural networks."},
            {"arxiv_id": "2301.05678", "chunk_text": "Attention is key."},
        ]

        with patch.object(minimax_client, "generate", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = {
                "response": "Transformers use attention mechanisms.",
            }

            result = await minimax_client.generate_rag_answer(
                query="What are transformers?",
                chunks=chunks,
            )

            assert "answer" in result
            assert result["answer"] == "Transformers use attention mechanisms."
            assert len(result["sources"]) == 2
            assert len(result["citations"]) == 2


class TestGenerateRagAnswerStream:
    """Tests for generate_rag_answer_stream method."""

    @pytest.mark.asyncio
    async def test_stream_rag_answer(self, minimax_client):
        chunks = [
            {"arxiv_id": "2301.01234", "chunk_text": "Test content."},
        ]

        async def mock_stream(*args, **kwargs):
            yield {"response": "Hello ", "done": False}
            yield {"response": "world!", "done": False}
            yield {"done": True}

        with patch.object(minimax_client, "generate_stream", side_effect=mock_stream):
            collected = []
            async for chunk in minimax_client.generate_rag_answer_stream(
                query="Test query",
                chunks=chunks,
            ):
                collected.append(chunk)

            assert len(collected) == 3
            assert collected[0]["response"] == "Hello "
            assert collected[2]["done"] is True
