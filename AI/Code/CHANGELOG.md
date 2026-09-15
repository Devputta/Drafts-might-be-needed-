# Changelog

This project was built incrementally over seven scoped days, each with a
narrow, testable deliverable rather than one large drop. See
`prompts/day-N.md` for the exact brief given at each stage.

## [1.0.0] — Day 7: Portfolio Release
- Rewrote `README.md` as a portfolio-ready document: problem statement,
  architecture diagram, API examples, security model summary,
  limitations, roadmap.
- Added `DEMO_SCRIPT.md` (2-minute walkthrough script) and
  `RELEASE_CHECKLIST.md`.
- Added `demo/sample_review_response.json` — a real, schema-valid example
  response for reference without needing a live API key.
- Added `.github/workflows/tests.yml` — free CI on GitHub Actions, runs
  the fully offline test suite on every push.
- Added `LICENSE` (MIT).
- Bumped app version to `1.0.0`.

## [0.6.0] — Day 6: Testing & Hardening
- Added `tests/conftest.py` (shared `client` fixture, guaranteed
  dependency-override cleanup) and `tests/fixtures.py` (shared code
  samples).
- Added `app/redaction.py` — best-effort secret redaction before code is
  sent to the LLM provider; wired into `/review` and reported via a new
  `redactions` field on `ReviewResponse`.
- Added `app/logging_conf.py` and an access-log middleware that logs
  method/path/status/duration only — never the request body.
- Added hardening tests: `test_scanner_hardening.py` (Bandit failure
  modes), `test_llm_error_handling.py` (provider failure modes,
  parametrized across Gemini and Groq), `test_redaction.py`.
- Added `SECURITY.md` and `requirements-dev.txt` (optional `pip-audit`).

## [0.5.0] — Day 5: Dashboard
- Added `frontend/index.html` — a single-file HTML/Tailwind dashboard
  with severity-grouped findings, suggested fixes, and loading/error
  states.
- Added `CORSMiddleware` to the API so the dashboard can call it
  cross-origin.

## [0.4.0] — Day 4: API Contract
- Added real request limits (`MAX_CODE_CHARS`), a whitespace-only-code
  validator, and one shared `_require_supported_language()` helper used
  by both endpoints.
- Added OpenAPI `summary`/`description`/`examples` on every route and
  field.
- Added `test_api_contract.py`.

## [0.3.0] — Day 3: AI Review
- Added the `app/llm/` provider abstraction (`LLMProvider`,
  `ProviderError`, shared prompt, Gemini and Groq adapters, factory).
- Added `POST /review`, combining the Bandit scan with the LLM review and
  degrading gracefully (HTTP 200 + `ai_error`) when the AI call fails.
- Added `test_review.py`, `test_llm_factory.py`.

## [0.2.0] — Day 2: Local Security Scanner
- Added `app/scanner.py` — safe Bandit subprocess integration: temp file,
  timeout, cleanup, typed `ScannerError`.
- Added `POST /scan` and `app/schemas.py`.
- Added `test_scanner.py`.

## [0.1.0] — Day 1: Foundation
- Initial FastAPI app, `/health`, centralized `app/config.py` settings,
  `.env.example`, `.gitignore`.
