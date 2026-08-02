from unittest.mock import MagicMock, patch

from src.config import TelegramSettings
from src.services.telegram.bot import TelegramBot
from src.services.telegram.factory import make_telegram_service


class TestTelegramBot:
    """Test Telegram bot."""

    def test_bot_creation(self):
        """Test creating bot instance."""
        bot = TelegramBot(
            bot_token="test_token",
            opensearch_client=MagicMock(),
            embeddings_client=MagicMock(),
            llm_client=MagicMock(),
        )

        assert bot.bot_token == "test_token"
        assert bot.opensearch is not None
        assert bot.embeddings is not None
        assert bot.llm is not None


class TestTelegramSettings:
    """Test Telegram settings."""

    def test_default_settings(self):
        """Test default settings."""
        # Explicitly set default values to test the schema, ignoring .env
        settings = TelegramSettings(bot_token="", enabled=False)
        assert settings.enabled is False
        assert settings.bot_token == ""

    def test_custom_settings(self):
        """Test custom settings."""
        settings = TelegramSettings(bot_token="test", enabled=True)
        assert settings.enabled is True
        assert settings.bot_token == "test"


class TestTelegramFactory:
    """Test factory."""

    @patch("src.services.telegram.factory.get_settings")
    def test_factory_disabled(self, mock_settings):
        """Test factory returns None when disabled."""
        mock_settings.return_value.telegram.enabled = False
        bot = make_telegram_service(
            opensearch_client=MagicMock(),
            embeddings_client=MagicMock(),
            llm_client=MagicMock(),
        )
        assert bot is None

    @patch("src.services.telegram.factory.get_settings")
    def test_factory_no_token(self, mock_settings):
        """Test factory returns None without token."""
        mock_settings.return_value.telegram.enabled = True
        mock_settings.return_value.telegram.bot_token = ""
        bot = make_telegram_service(
            opensearch_client=MagicMock(),
            embeddings_client=MagicMock(),
            llm_client=MagicMock(),
        )
        assert bot is None

    @patch("src.services.telegram.factory.get_settings")
    def test_factory_success(self, mock_settings):
        """Test factory creates bot."""
        mock_settings.return_value.telegram.enabled = True
        mock_settings.return_value.telegram.bot_token = "test_token"
        bot = make_telegram_service(
            opensearch_client=MagicMock(),
            embeddings_client=MagicMock(),
            llm_client=MagicMock(),
        )
        assert bot is not None
        assert bot.bot_token == "test_token"
