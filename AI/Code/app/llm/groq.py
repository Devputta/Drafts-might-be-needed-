"""
Groq adapter (free tier, OpenAI-compatible chat completions API).

Get a free key, no card required: https://console.groq.com/keys
"""

from typing import Any

import httpx

from app.llm.base import LLMProvider, ProviderError, parse_model_json
from app.llm.prompt import REVIEW_SYSTEM_INSTRUCTIONS, build_user_prompt

REQUEST_TIMEOUT_SECONDS = 30
API_URL = "https://api.groq.com/openai/v1/chat/completions"


class GroqProvider(LLMProvider):
    name = "groq"

    def __init__(self, api_key: str | None, model: str):
        # Same rationale as GeminiProvider: don't raise in __init__, so a
        # missing key surfaces as a graceful ai_error, not a server crash.
        self._api_key = api_key
        self._model = model

    def review(self, code: str, findings: list[dict[str, Any]]) -> dict[str, Any]:
        if not self._api_key:
            raise ProviderError(
                "GROQ_API_KEY is not set. Get a free key at "
                "https://console.groq.com/keys and add it to .env as "
                "GROQ_API_KEY, then restart the server."
            )

        payload = {
            "model": self._model,
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": REVIEW_SYSTEM_INSTRUCTIONS},
                {"role": "user", "content": build_user_prompt(code, findings)},
            ],
        }
        headers = {"Authorization": f"Bearer {self._api_key}"}

        try:
            resp = httpx.post(
                API_URL, json=payload, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS
            )
        except httpx.TimeoutException as e:
            raise ProviderError(
                f"Groq request timed out after {REQUEST_TIMEOUT_SECONDS}s."
            ) from e
        except httpx.HTTPError as e:
            raise ProviderError(f"Groq request failed: {e}") from e

        if resp.status_code != 200:
            raise ProviderError(
                f"Groq returned HTTP {resp.status_code}: {resp.text[:500]}"
            )

        try:
            data = resp.json()
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            raise ProviderError(
                f"Unexpected Groq response shape (fields missing): {e}"
            ) from e

        return parse_model_json(text)
