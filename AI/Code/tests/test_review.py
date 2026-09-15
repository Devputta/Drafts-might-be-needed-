"""
Tests for the /review endpoint.

None of these tests make a real network call. They substitute a fake
LLMProvider via FastAPI's dependency_overrides, which is exactly why
main.py exposes get_llm_provider() as a dependency instead of hardcoding
a provider at import time. This keeps the suite free, fast, and fully
offline — no API key required to verify the app's logic.
"""

from typing import Any

from app.llm.base import LLMProvider, ProviderError
from app.main import app, get_llm_provider
from tests.fixtures import CLEAN_CODE


class FakeGoodProvider(LLMProvider):
    name = "fake-good"

    def review(self, code: str, findings: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "summary": "No significant issues found.",
            "risk_level": "LOW",
            "issues": [],
        }


class FakeFailingProvider(LLMProvider):
    name = "fake-failing"

    def review(self, code: str, findings: list[dict[str, Any]]) -> dict[str, Any]:
        raise ProviderError("simulated provider outage")


class FakeMalformedProvider(LLMProvider):
    name = "fake-malformed"

    def review(self, code: str, findings: list[dict[str, Any]]) -> dict[str, Any]:
        # Missing required fields (risk_level, issues) — should fail
        # AIReviewResult validation, not crash the endpoint.
        return {"summary": "incomplete response"}


class SpyProvider(LLMProvider):
    """Records exactly what code it was called with, for assertions."""

    name = "fake-spy"

    def __init__(self):
        self.received_code: str | None = None

    def review(self, code: str, findings: list[dict[str, Any]]) -> dict[str, Any]:
        self.received_code = code
        return {"summary": "ok", "risk_level": "LOW", "issues": []}


def test_review_returns_scan_and_ai_review_on_success(client):
    app.dependency_overrides[get_llm_provider] = lambda: FakeGoodProvider()

    r = client.post("/review", json={"code": CLEAN_CODE, "language": "python"})

    assert r.status_code == 200
    body = r.json()
    assert body["scan"]["tool"] == "bandit"
    assert body["ai_review"]["risk_level"] == "LOW"
    assert body["ai_review"]["issues"] == []
    assert body["ai_error"] is None
    assert body["redactions"] == []


def test_review_degrades_gracefully_on_provider_error(client):
    app.dependency_overrides[get_llm_provider] = lambda: FakeFailingProvider()

    r = client.post("/review", json={"code": CLEAN_CODE, "language": "python"})

    # The endpoint still returns 200 — the scan succeeded even though the
    # AI call failed. This is the core design decision from Day 3.
    assert r.status_code == 200
    body = r.json()
    assert body["scan"]["tool"] == "bandit"
    assert body["ai_review"] is None
    assert "simulated provider outage" in body["ai_error"]


def test_review_degrades_gracefully_on_malformed_model_output(client):
    app.dependency_overrides[get_llm_provider] = lambda: FakeMalformedProvider()

    r = client.post("/review", json={"code": CLEAN_CODE, "language": "python"})

    assert r.status_code == 200
    body = r.json()
    assert body["ai_review"] is None
    assert body["ai_error"] is not None


def test_review_rejects_non_python_language(client):
    app.dependency_overrides[get_llm_provider] = lambda: FakeGoodProvider()

    r = client.post("/review", json={"code": "1+1", "language": "javascript"})
    assert r.status_code == 400


def test_review_redacts_secret_before_reaching_provider(client):
    """
    Integration test tying Day 6's redaction into the Day 3 /review flow:
    the provider must never see the raw secret, and the response must
    report what was redacted without echoing the secret's value.
    """
    spy = SpyProvider()
    app.dependency_overrides[get_llm_provider] = lambda: spy

    code_with_secret = 'aws_key = "AKIAABCDEFGHIJKLMNOP"\nprint(aws_key)\n'
    r = client.post("/review", json={"code": code_with_secret, "language": "python"})

    assert r.status_code == 200
    body = r.json()

    assert "AKIAABCDEFGHIJKLMNOP" not in spy.received_code
    assert "REDACTED" in spy.received_code
    assert any("AWS Access Key" in item for item in body["redactions"])
    # The response itself must never contain the raw secret either.
    assert "AKIAABCDEFGHIJKLMNOP" not in str(body)
