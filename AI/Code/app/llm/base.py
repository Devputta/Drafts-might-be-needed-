"""
Provider-agnostic interface every LLM backend implements.

Design intent: `main.py` and the tests should never know or care whether
Gemini or Groq is behind `LLMProvider.review()`. Swapping providers is a
one-line change in `.env` (`LLM_PROVIDER=gemini` or `LLM_PROVIDER=groq`),
never a code change.
"""

import json
from abc import ABC, abstractmethod
from typing import Any


class ProviderError(Exception):
    """
    Raised for any provider-side failure: missing API key, network/timeout
    error, non-2xx response, or output that isn't valid JSON. Callers
    (main.py) catch this one exception type and decide how to degrade —
    they never need to know which specific thing went wrong underneath.
    """


class LLMProvider(ABC):
    name: str

    @abstractmethod
    def review(self, code: str, findings: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Send `code` and the normalized Bandit `findings` to the model and
        return the parsed JSON response as a plain dict matching the
        strict review schema (summary / risk_level / issues).

        Must raise ProviderError — never let a raw httpx or json exception
        escape — on any failure.
        """
        raise NotImplementedError


def parse_model_json(raw_text: str) -> dict[str, Any]:
    """
    Parse the model's text output as JSON, defensively stripping Markdown
    code fences if the model added them despite being told not to.

    Shared by every provider so "the model wrapped its JSON in ```json```"
    is handled in exactly one place.
    """
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").strip()
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ProviderError(
            f"Model did not return valid JSON ({e}). "
            f"Raw output (truncated): {cleaned[:300]!r}"
        ) from e
