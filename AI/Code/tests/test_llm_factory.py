"""
Tests for the provider factory and per-provider key handling.

Verifies two things without ever calling a real API:
  1. An unknown LLM_PROVIDER value is rejected immediately (config bug).
  2. A missing API key is NOT rejected at construction time — it's only
     raised when review() is actually called, so the FastAPI dependency
     never crashes the app just because a key hasn't been set yet.
"""

import pytest

from app.config import Settings
from app.llm.base import ProviderError
from app.llm.factory import build_llm_provider
from app.llm.gemini import GeminiProvider
from app.llm.groq import GroqProvider


def test_unknown_provider_name_raises_immediately():
    settings = Settings(llm_provider="not-a-real-provider")
    with pytest.raises(ProviderError):
        build_llm_provider(settings)


def test_gemini_selected_by_provider_name():
    settings = Settings(llm_provider="gemini", gemini_api_key=None)
    provider = build_llm_provider(settings)
    assert isinstance(provider, GeminiProvider)


def test_groq_selected_by_provider_name():
    settings = Settings(llm_provider="groq", groq_api_key=None)
    provider = build_llm_provider(settings)
    assert isinstance(provider, GroqProvider)


def test_gemini_without_key_raises_only_when_called():
    settings = Settings(llm_provider="gemini", gemini_api_key=None)
    provider = build_llm_provider(settings)  # must NOT raise here

    with pytest.raises(ProviderError, match="GEMINI_API_KEY"):
        provider.review("code", [])


def test_groq_without_key_raises_only_when_called():
    settings = Settings(llm_provider="groq", groq_api_key=None)
    provider = build_llm_provider(settings)  # must NOT raise here

    with pytest.raises(ProviderError, match="GROQ_API_KEY"):
        provider.review("code", [])
