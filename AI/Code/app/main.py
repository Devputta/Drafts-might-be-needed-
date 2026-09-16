"""
AI Code Review & Security Sentinel.

Day 1: FastAPI skeleton, /health, environment configuration.
Day 2: local Bandit security scan via /scan.
Day 3: free-tier LLM review (Gemini or Groq) combined with the Bandit
       scan via /review.
Day 4: hardened API contract — real request limits, a single shared
       language-validation path, OpenAPI descriptions/examples on every
       route, and documented error responses.
Day 5: local dashboard (frontend/index.html) + CORS to support it.
Day 6 (this pass): secret redaction before code reaches the LLM, a safe
       access-log middleware, and centralized logging config.
"""

import logging
import time

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app.config import get_settings
from app.llm.base import LLMProvider, ProviderError
from app.llm.factory import build_llm_provider
from app.logging_conf import configure_logging
from app.redaction import redact_secrets
from app.scanner import ScannerError, run_bandit_scan
from app.schemas import (
    AIReviewResult,
    ReviewResponse,
    ScanRequest,
    ScanResult,
    SUPPORTED_LANGUAGES,
)

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger("sentinel")
access_logger = logging.getLogger("sentinel.access")

TAGS_METADATA = [
    {"name": "ops", "description": "Health and liveness — zero external dependencies."},
    {
        "name": "scan",
        "description": "Local, deterministic static analysis via Bandit. Always free, "
        "always offline.",
    },
    {
        "name": "review",
        "description": "Bandit scan combined with a free-tier LLM review. The scan half "
        "never fails for external reasons; the AI half degrades gracefully "
        "if the provider is unavailable.",
    },
]

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Local-first code review assistant that combines a deterministic "
        "security scanner (Bandit) with a free-tier LLM review (Gemini or "
        "Groq). No paid services required — see /docs for the full "
        "request/response contract."
    ),
    openapi_tags=TAGS_METADATA,
)

# The Day 5 dashboard is a static HTML file, opened either directly from
# disk (an "origin" of "null") or from a lightweight local static server
# on a different port than the API. Either way, the browser treats it as
# cross-origin. Wide-open CORS is appropriate here specifically because
# this is a local, single-user developer tool with no cookies or session
# auth to protect — it should NOT be copied as-is into an app that serves
# real user accounts or handles credentials.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Access logging, deliberately minimal: method, path, status, duration.

    Never logs the request body. That's the whole point — the body is
    where submitted source code and (before Day 6's redaction) secrets
    live, and neither belongs in a log file. See app/logging_conf.py for
    the one known, narrow exception (truncated model output inside a
    ProviderError message).
    """
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    access_logger.info(
        "%s %s -> %s (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


def get_llm_provider() -> LLMProvider:
    """
    FastAPI dependency that builds the active LLM provider from settings.

    Using a dependency (instead of a module-level singleton) means tests
    can swap in a fake provider with `app.dependency_overrides` and never
    touch the network — the whole test suite stays free and offline.
    """
    return build_llm_provider(get_settings())


def _require_supported_language(language: str) -> None:
    """
    Single source of truth for the Python-only MVP restriction, used by
    both /scan and /review so the check and its error message can't drift
    apart between endpoints.
    """
    if language.lower() not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported language '{language}'. This MVP supports: "
                f"{', '.join(sorted(SUPPORTED_LANGUAGES))}."
            ),
        )


@app.get(
    "/health",
    tags=["ops"],
    summary="Liveness/readiness probe",
    response_description="App metadata confirming the process is up.",
)
def health() -> dict:
    """
    Returns basic app metadata so you can confirm — from the browser, curl,
    or a monitoring tool — that the process is up and which environment
    it's running in. Intentionally has zero external dependencies: if this
    endpoint is slow or fails, the problem is the app process itself, not
    Bandit or the LLM provider.
    """
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
    }


@app.get("/", tags=["ops"], summary="Landing response")
def root() -> dict:
    """Friendly landing response so hitting the base URL isn't a 404."""
    return {
        "message": f"{settings.app_name} is running.",
        "docs": "/docs",
        "health": "/health",
    }


@app.post(
    "/scan",
    response_model=ScanResult,
    tags=["scan"],
    summary="Run a local Bandit security scan",
    responses={
        400: {"description": "Unsupported `language` value."},
        422: {"description": "Request body failed validation (empty/blank/oversized code)."},
        502: {"description": "Bandit itself failed to run (not installed, timed out, bad output)."},
    },
)
def scan(request: ScanRequest) -> ScanResult:
    """
    Run a local, static security scan over a code snippet.

    Python uses Bandit (AST-based, never executes code). Other languages use
    ESLint (JavaScript/TypeScript), gosec (Go), or basic pattern matching.
    The code is **never executed**. This endpoint has no external network
    dependency, so it's free to call as often as you like. No redaction
    applies here: the code never leaves your machine.
    """
    _require_supported_language(request.language)

    try:
        return run_bandit_scan(request.code, request.language)
    except ScannerError as e:
        logger.warning("Scanner failed: %s", e)
        raise HTTPException(status_code=502, detail=str(e))


@app.post(
    "/review",
    response_model=ReviewResponse,
    tags=["review"],
    summary="Run the Bandit scan plus a free-tier LLM review",
    responses={
        400: {"description": "Unsupported `language` value."},
        422: {"description": "Request body failed validation (empty/blank/oversized code)."},
        502: {"description": "Bandit itself failed to run — the one hard failure mode here."},
    },
)
def review(
    request: ScanRequest,
    provider: LLMProvider = Depends(get_llm_provider),
) -> ReviewResponse:
    """
    Run the local Bandit scan **and** the free-tier LLM review together.

    Design choice: the Bandit scan is always trustworthy and always free,
    since it's a local subprocess. The LLM call is the one thing that can
    fail for reasons outside this app's control — no key configured, rate
    limit, provider outage, or the model returning malformed JSON. Rather
    than fail the whole request when only the AI half breaks, this
    endpoint always returns HTTP 200 with the scan intact and degrades the
    AI portion into an `ai_error` string. The scan you paid nothing for
    still comes back.

    Before the code is sent to the LLM provider, obvious secret patterns
    (AWS keys, private key blocks, bearer tokens, hardcoded password/API
    key assignments) are redacted — see app/redaction.py. This is
    best-effort, not a guarantee; the `redactions` field in the response
    tells you exactly what kind of pattern was found and on which line,
    without ever echoing the secret value back. The original,
    unredacted code is what Bandit scans, since Bandit never leaves this
    machine.
    """
    _require_supported_language(request.language)

    try:
        scan_result = run_bandit_scan(request.code, request.language)
    except ScannerError as e:
        # Unlike the AI call, a broken local scanner IS a hard failure —
        # there's no meaningful response without it.
        logger.warning("Scanner failed: %s", e)
        raise HTTPException(status_code=502, detail=str(e))

    redacted_code, redaction_matches = redact_secrets(request.code)
    redaction_summary = [f"{m.kind} on line {m.line}" for m in redaction_matches]
    if redaction_matches:
        logger.info("Redacted %d potential secret(s) before LLM call.", len(redaction_matches))

    try:
        raw_findings = [f.model_dump() for f in scan_result.findings]
        raw_review = provider.review(redacted_code, raw_findings)
        ai_review = AIReviewResult(**raw_review)
        return ReviewResponse(
            scan=scan_result,
            ai_review=ai_review,
            ai_error=None,
            redactions=redaction_summary,
        )
    except ProviderError as e:
        logger.warning("LLM provider call failed: %s", e)
        return ReviewResponse(
            scan=scan_result,
            ai_review=None,
            ai_error=str(e),
            redactions=redaction_summary,
        )
    except (ValidationError, TypeError) as e:
        logger.warning("LLM output failed schema validation: %s", e)
        return ReviewResponse(
            scan=scan_result,
            ai_review=None,
            ai_error=f"Model output didn't match the required schema: {e}",
            redactions=redaction_summary,
        )
