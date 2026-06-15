"""Configuration management using pydantic-settings."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration (支持OpenAI兼容接口，如阿里云通义千问)
    openai_api_key: str
    openai_base_url: str = "https://api.openai.com/v1"  # 可配置为兼容接口
    openai_model: str = "gpt-4o-mini"

    # Scoring Configuration
    min_score_threshold: float = 70.0
    experience_weight: float = 0.3
    skills_weight: float = 0.3
    education_weight: float = 0.2
    projects_weight: float = 0.2

    # Question Generation Configuration
    num_questions: int = 5
    question_difficulty: str = "medium"
    include_coding_questions: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance (singleton pattern)."""
    return Settings()
