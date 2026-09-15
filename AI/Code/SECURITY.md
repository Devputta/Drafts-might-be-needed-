# Security Checklist & Design Rationale

This document exists so the security posture of this project is a
deliberate, written decision — not something a reader has to reverse-
engineer from the code. It's organized as: what's covered, what's
explicitly out of scope, and what to do before using this anywhere
beyond a local demo.

## What's covered

**No code execution, anywhere, ever.**
Both the Bandit scan and the LLM review operate on the submitted text as
*text*. Bandit performs AST-based static analysis (`app/scanner.py`) —
it parses the code into a syntax tree; it never imports or runs it. The
LLM review (`app/llm/`) sends the code as a string in a prompt; nothing
in this codebase `eval`s, `exec`s, or subprocess-runs the *submitted*
code. The only subprocess this app ever spawns is `bandit` itself,
against a temp file, with a bounded timeout.

**Bandit subprocess isolation.**
- Submitted code is written to a private temp file (`tempfile.mkstemp`),
  never the working directory.
- The temp file is removed in a `finally` block — verified by
  `tests/test_scanner_hardening.py` for the success path, the timeout
  path, and the "Bandit isn't installed" path.
- The subprocess is bounded by a 20-second timeout
  (`BANDIT_TIMEOUT_SECONDS` in `app/scanner.py`).
- Every Bandit failure mode (not installed, timeout, malformed JSON
  output) raises a typed `ScannerError` and becomes a clean `502` —
  never a raw stack trace or subprocess internals leaked to the caller.

**Request limits and input validation.**
- `code` is capped at `MAX_CODE_CHARS` (50,000 characters —
  `app/schemas.py`), rejected with `422` if exceeded.
- Whitespace-only input is rejected explicitly (`field_validator` in
  `app/schemas.py`), not just empty-string input.
- `language` is validated against an explicit allowlist
  (`SUPPORTED_LANGUAGES = {"python"}`) via one shared helper used by
  both `/scan` and `/review`, so the check can't drift between routes.

**Secret redaction before the LLM call.**
`app/redaction.py` applies a set of regex patterns (AWS access keys,
PEM-format private key blocks, Slack tokens, bearer tokens, and generic
`api_key = "..."` / `password = "..."`-style assignments) to the code
*before* it's sent to Gemini or Groq, and reports what kind of pattern
was found and on which line — never the matched value itself. This is
explicitly **best-effort, not a guarantee**:
- It's pattern matching, not a secret-entropy scanner. Anything that
  doesn't match one of these shapes (a bespoke internal token format, a
  secret with no recognizable prefix, a key split across string
  concatenation) will not be caught.
- **Treat this as a safety net, not a reason to paste real production
  secrets into the review box.** Don't submit code you wouldn't be
  comfortable having a third-party API provider log server-side —
  review Google's and Groq's own data-handling terms for their free
  tiers before relying on this for anything sensitive.
- The *original*, unredacted code is always what Bandit scans — Bandit
  runs entirely on your machine, so redacting before the local scan
  would only cost accuracy for no security benefit.

**Timeouts on every external call.**
Both `GeminiProvider` and `GroqProvider` (`app/llm/gemini.py`,
`app/llm/groq.py`) use a 30-second `httpx` timeout. A hung free-tier API
cannot hang a request indefinitely.

**Graceful degradation instead of leaking internals.**
`/review` never returns a raw `httpx` exception, a raw provider HTTP
body, or a raw `json.JSONDecodeError` to the caller. Every failure mode
is caught and converted into either an HTTP status with a clean `detail`
message, or (for the AI half specifically) a structured `ai_error`
string in a `200` response — see `app/main.py` and
`tests/test_llm_error_handling.py`.

**Safe logging.**
`app/logging_conf.py` and the access-log middleware in `app/main.py` log
method, path, status code, and duration only — never the request body.
Error branches log our own generated messages (e.g. "Bandit scan timed
out"), never `request.code` directly.

**Scoped CORS.**
`allow_origins=["*"]` is enabled specifically because this is a
local, single-user developer tool with no cookies, sessions, or
authentication to protect (a static HTML file opened from disk has a
`null` origin, which only a wildcard reliably matches). This is **not**
a pattern to carry into any deployment that serves real user accounts.

## Known limitations (out of scope for this build)

- **No authentication or authorization.** Anyone who can reach the API
  can call every endpoint. Fine for `127.0.0.1`-only local use; not fine
  for anything reachable from a network.
- **No rate limiting.** A local single-user tool doesn't need it; a
  shared or public deployment would.
- **Redaction is best-effort regex**, not a secret-scanning product —
  see above.
- **The log-safety guarantee has one narrow, documented exception**:
  when a `ProviderError` is raised because the model's raw output wasn't
  valid JSON, the error message includes a truncated fragment of that
  raw output (see `app/llm/base.py::parse_model_json`). Because the
  model was given the user's code, that echoed fragment could in rare
  cases contain a piece of it. Closing this completely would mean
  losing the diagnostic value of the error message; it's flagged here
  instead of hidden.
- **No sandboxing beyond "we never execute the code."** This app relies
  entirely on Bandit's AST-based static analysis being safe by
  construction, and on the LLM providers treating the code as inert
  text. There's no seccomp/container/VM layer on top, because none is
  needed for a tool that never runs the submitted code.
- **This is a demo/portfolio project**, not a hardened multi-tenant
  service. Treat it accordingly.

## Dependency hygiene

`requirements.txt` uses compatible-release ranges (`>=X,<Y`), not exact
pins — reproducible across machines without being brittle against every
patch release, appropriate for a project built incrementally over a
week. Before using this anywhere beyond local experimentation:

1. **Generate a lockfile** with exact versions:
   ```bash
   pip freeze > requirements-lock.txt
   ```
   Commit the lockfile alongside `requirements.txt` and install from it
   in any environment where reproducibility matters more than picking up
   patch releases automatically.

2. **Audit for known vulnerabilities** — free, local, no account needed:
   ```bash
   pip install pip-audit
   pip-audit
   ```
   `pip-audit` checks installed packages against the public PyPI
   Advisory Database. Run it before any real deployment and periodically
   thereafter; it costs nothing and requires no API key.

3. **Re-run the full test suite** (`pytest -v`) after any dependency
   bump — the suite in `tests/` is written specifically so a Bandit or
   `httpx` version bump that changes an error message format, a JSON
   shape, or a rule ID would surface as a failing assertion, not a
   silent behavior change.
