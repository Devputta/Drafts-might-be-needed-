"""
Day 6 hardening: exercise every failure mode of the LLM adapters directly
(not through a fake provider), by monkeypatching httpx.post. This proves
that a timeout, a non-2xx response, an unexpected response shape, and
malformed model JSON all become a clean ProviderError — for BOTH
providers, so neither one is more fragile than the other.
"""

import httpx
import pytest

from app.llm.base import ProviderError
from app.llm.gemini import GeminiProvider
from app.llm.groq import GroqProvider


class _FakeResponse:
    def __init__(self, status_code=200, json_data=None, text=""):
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text

    def json(self):
        return self._json_data


def _raise(exc):
    def _inner(*args, **kwargs):
        raise exc

    return _inner


GEMINI_GOOD_SHAPE = lambda text: {  # noqa: E731
    "candidates": [{"content": {"parts": [{"text": text}]}}]
}
GROQ_GOOD_SHAPE = lambda text: {"choices": [{"message": {"content": text}}]}  # noqa: E731


@pytest.mark.parametrize(
    "provider_cls,key_env_name,good_shape",
    [
        (GeminiProvider, "GEMINI_API_KEY", GEMINI_GOOD_SHAPE),
        (GroqProvider, "GROQ_API_KEY", GROQ_GOOD_SHAPE),
    ],
)
class TestProviderFailureModes:
    def test_missing_key_raises_before_any_http_call(self, monkeypatch, provider_cls, key_env_name, good_shape):
        monkeypatch.setattr(httpx, "post", _raise(AssertionError("should not call the network")))
        provider = provider_cls(api_key=None, model="test-model")
        with pytest.raises(ProviderError, match=key_env_name):
            provider.review("code", [])

    def test_timeout_becomes_provider_error(self, monkeypatch, provider_cls, key_env_name, good_shape):
        monkeypatch.setattr(httpx, "post", _raise(httpx.TimeoutException("timed out")))
        provider = provider_cls(api_key="fake-key", model="test-model")
        with pytest.raises(ProviderError, match="timed out"):
            provider.review("code", [])

    def test_non_200_becomes_provider_error(self, monkeypatch, provider_cls, key_env_name, good_shape):
        monkeypatch.setattr(
            httpx, "post", lambda *a, **kw: _FakeResponse(status_code=429, text="rate limited")
        )
        provider = provider_cls(api_key="fake-key", model="test-model")
        with pytest.raises(ProviderError, match="429"):
            provider.review("code", [])

    def test_unexpected_response_shape_becomes_provider_error(
        self, monkeypatch, provider_cls, key_env_name, good_shape
    ):
        monkeypatch.setattr(
            httpx, "post", lambda *a, **kw: _FakeResponse(status_code=200, json_data={"nothing": "useful"})
        )
        provider = provider_cls(api_key="fake-key", model="test-model")
        with pytest.raises(ProviderError):
            provider.review("code", [])

    def test_malformed_model_json_becomes_provider_error(
        self, monkeypatch, provider_cls, key_env_name, good_shape
    ):
        monkeypatch.setattr(
            httpx,
            "post",
            lambda *a, **kw: _FakeResponse(status_code=200, json_data=good_shape("not json at all")),
        )
        provider = provider_cls(api_key="fake-key", model="test-model")
        with pytest.raises(ProviderError, match="valid JSON"):
            provider.review("code", [])

    def test_markdown_fenced_json_is_parsed_successfully(
        self, monkeypatch, provider_cls, key_env_name, good_shape
    ):
        """
        Models sometimes wrap JSON in ```json fences despite instructions
        not to. parse_model_json() strips this defensively — confirm the
        adapters actually benefit from that, not just the shared helper
        in isolation.
        """
        fenced = '```json\n{"summary": "ok", "risk_level": "LOW", "issues": []}\n```'
        monkeypatch.setattr(
            httpx, "post", lambda *a, **kw: _FakeResponse(status_code=200, json_data=good_shape(fenced))
        )
        provider = provider_cls(api_key="fake-key", model="test-model")
        result = provider.review("code", [])
        assert result == {"summary": "ok", "risk_level": "LOW", "issues": []}
