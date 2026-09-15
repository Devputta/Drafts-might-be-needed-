"""
Selects the active provider based on `LLM_PROVIDER` in the environment.
This is the only place that needs to change to add a third provider.
"""

from app.config import Settings
from app.llm.base import LLMProvider, ProviderError
from app.llm.gemini import GeminiProvider
from app.llm.groq import GroqProvider

_DEFAULT_GEMINI_MODEL = "gemini-1.5-flash"
_DEFAULT_GROQ_MODEL = "llama-3.1-8b-instant"


def build_llm_provider(settings: Settings) -> LLMProvider:
    provider_name = (settings.llm_provider or "").strip().lower()

    if provider_name == "gemini":
        return GeminiProvider(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model or _DEFAULT_GEMINI_MODEL,
        )
    if provider_name == "groq":
        return GroqProvider(
            api_key=settings.groq_api_key,
            model=settings.groq_model or _DEFAULT_GROQ_MODEL,
        )

    # An unrecognized provider name is a configuration mistake, not a
    # transient per-request condition — surfacing it loudly at request
    # time (via a 500, see main.py) is correct here, unlike a missing key.
    raise ProviderError(
        f"Unknown LLM_PROVIDER '{settings.llm_provider}'. "
        "Set it to 'gemini' or 'groq' in your .env file."
    )
