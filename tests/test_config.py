"""Tests for configuration management."""

from src.config import Settings


def test_settings_from_env(monkeypatch):
    """Test loading settings from environment variables."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
    monkeypatch.setenv("MIN_SCORE_THRESHOLD", "75.0")

    settings = Settings()
    assert settings.openai_api_key == "test-key-123"
    assert settings.min_score_threshold == 75.0


def test_settings_defaults():
    """Test default configuration values."""
    settings = Settings(openai_api_key="dummy-key")

    assert settings.model_name == "gpt-4o-mini"
    assert settings.min_score_threshold == 70.0
    assert settings.experience_weight == 0.3
    assert settings.skills_weight == 0.3
    assert settings.education_weight == 0.2
    assert settings.projects_weight == 0.2


def test_question_config():
    """Test question generation configuration."""
    settings = Settings(openai_api_key="dummy-key")

    assert settings.num_questions == 5
    assert settings.question_difficulty == "medium"
    assert settings.include_coding_questions is True
