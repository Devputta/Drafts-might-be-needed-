"""
Google Gemini adapter (free tier via Google AI Studio).

Get a free key, no card required: https://aistudio.google.com/app/apikey
"""

from typing import Any

import httpx

from app.llm.base import LLMProvider, ProviderError, parse_model_json
from app.llm.prompt import REVIEW_SYSTEM_INSTRUCTIONS, build_user_prompt

REQUEST_TIMEOUT_SECONDS = 30
API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self, api_key: str | None, model: str):
        # Deliberately does NOT raise here. A missing key is a per-request
        # condition we want to surface as a graceful `ai_error` in the API
        # response, not a hard crash when the app boots or when the
        # dependency is constructed.
        self._api_key = api_key
        self._model = model

    def review(self, code: str, findings: list[dict[str, Any]]) -> dict[str, Any]:
        if not self._api_key:
            raise ProviderError(
                "GEMINI_API_KEY is not set. Get a free key at "
                "https://aistudio.google.com/app/apikey and add it to .env "
                "as GEMINI_API_KEY, then restart the server."
            )

        url = f"{API_BASE}/{self._model}:generateContent"
        payload = {
            "system_instruction": {"parts": [{"text": REVIEW_SYSTEM_INSTRUCTIONS}]},
            "contents": [
                {"role": "user", "parts": [{"text": build_user_prompt(code, findings)}]}
            ],
            "generationConfig": {
                "temperature": 0.1,
                "response_mime_type": "application/json",
            },
        }

        try:
            resp = httpx.post(
                url,
                params={"key": self._api_key},
                json=payload,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except httpx.TimeoutException as e:
            raise ProviderError(
                f"Gemini request timed out after {REQUEST_TIMEOUT_SECONDS}s."
            ) from e
        except httpx.HTTPError as e:
            raise ProviderError(f"Gemini request failed: {e}") from e

        if resp.status_code != 200:
            raise ProviderError(
                f"Gemini returned HTTP {resp.status_code}: {resp.text[:500]}"
            )

        try:
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as e:
            raise ProviderError(
                f"Unexpected Gemini response shape (fields missing): {e}"
            ) from e

        return parse_model_json(text)
