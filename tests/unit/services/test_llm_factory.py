"""Unit tests for LLM client factory."""

import pytest
from unittest.mock import MagicMock, patch

from src.services.llm_factory import make_llm_client
from src.services.minimax.client import MiniMaxClient
from src.services.ollama.client import OllamaClient


class TestMakeLLMClient:
    """Tests for LLM client factory function."""

    def setup_method(self):
        """Clear lru_cache before each test."""
        make_llm_client.cache_clear()

    def test_default_provider_is_ollama(self):
        """Test that default provider returns OllamaClient."""
        mock_settings = MagicMock()
        mock_settings.llm_provider = "ollama"
        mock_settings.ollama_host = "http://localhost:11434"
        mock_settings.ollama_timeout = 300
        mock_settings.ollama_model = "llama3.2:1b"

        with patch("src.services.llm_factory.get_settings", return_value=mock_settings):
            client = make_llm_client()
            assert isinstance(client, OllamaClient)

    def test_minimax_provider(self):
        """Test that minimax provider returns MiniMaxClient."""
        mock_settings = MagicMock()
        mock_settings.llm_provider = "minimax"
        mock_settings.minimax_api_key = "test-key"
        mock_settings.minimax_model = "MiniMax-M3"
        mock_settings.minimax_base_url = "https://api.minimax.io/v1"
        mock_settings.minimax_timeout = 300

        with patch("src.services.llm_factory.get_settings", return_value=mock_settings):
            make_llm_client.cache_clear()
            client = make_llm_client()
            assert isinstance(client, MiniMaxClient)

    def test_minimax_without_api_key_raises(self):
        """Test that missing API key raises ValueError."""
        mock_settings = MagicMock()
        mock_settings.llm_provider = "minimax"
        mock_settings.minimax_api_key = ""

        with patch("src.services.llm_factory.get_settings", return_value=mock_settings):
            make_llm_client.cache_clear()
            with pytest.raises(ValueError, match="MINIMAX_API_KEY is required"):
                make_llm_client()

    def test_case_insensitive_provider(self):
        """Test that provider name is case-insensitive."""
        mock_settings = MagicMock()
        mock_settings.llm_provider = "MiniMax"
        mock_settings.minimax_api_key = "test-key"
        mock_settings.minimax_model = "MiniMax-M3"
        mock_settings.minimax_base_url = "https://api.minimax.io/v1"
        mock_settings.minimax_timeout = 300

        with patch("src.services.llm_factory.get_settings", return_value=mock_settings):
            make_llm_client.cache_clear()
            client = make_llm_client()
            assert isinstance(client, MiniMaxClient)

    def test_unknown_provider_defaults_to_ollama(self):
        """Test that unknown provider falls back to Ollama."""
        mock_settings = MagicMock()
        mock_settings.llm_provider = "unknown"
        mock_settings.ollama_host = "http://localhost:11434"
        mock_settings.ollama_timeout = 300
        mock_settings.ollama_model = "llama3.2:1b"

        with patch("src.services.llm_factory.get_settings", return_value=mock_settings):
            make_llm_client.cache_clear()
            client = make_llm_client()
            assert isinstance(client, OllamaClient)
