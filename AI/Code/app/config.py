"""
Centralized application configuration.

All environment-driven values live here so the rest of the app never calls
os.getenv() directly. This keeps configuration auditable in one place and
makes it trivial to see exactly what the app needs to run.

Nothing here requires a paid service. LLM provider keys are optional at
Day 1 — they'll be required starting Day 3 when the AI review endpoint
is wired up.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # General
    app_name: str = "AI Code Review & Security Sentinel"
    app_version: str = "1.0.0"
    app_env: str = Field(default="development")
    log_level: str = Field(default="INFO")

    # LLM provider config (used from Day 3 onward)
    llm_provider: str = Field(default="gemini")  # "gemini" or "groq"
    gemini_api_key: str | None = None
    gemini_model: str | None = None
    groq_api_key: str | None = None
    groq_model: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings accessor.

    Using lru_cache means the .env file is parsed once per process, not on
    every request — cheap, predictable, and easy to override in tests via
    get_settings.cache_clear().
    """
    return Settings()
