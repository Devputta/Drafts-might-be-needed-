# Release Checklist

Run through this before pushing the repo public or sharing it as a
portfolio piece.

## Secrets & hygiene
- [ ] `.env` is **not** committed (`git status` shows it untracked; check
      `.gitignore` includes it)
- [ ] `git log -p` (or `git log --all -- .env`) confirms no earlier commit
      ever included a real `.env` or a real API key
- [ ] `.env.example` contains no real values, only placeholders
- [ ] No API keys, tokens, or personal paths appear in `DEMO_SCRIPT.md` or
      any committed screenshots

## Correctness
- [ ] `pip install -r requirements.txt` succeeds in a clean virtualenv
- [ ] `pytest -v` passes completely — **no real API key required**, every
      LLM-dependent test uses a fake provider
- [ ] `uvicorn app.main:app --reload --port 8000` boots without errors
- [ ] `curl http://127.0.0.1:8000/health` returns `200`
- [ ] `frontend/index.html` successfully calls `/review` end-to-end with
      a real (even if free-tier) API key configured
- [ ] `/docs` (Swagger UI) loads and every route shows a description

## Dependency hygiene (see `SECURITY.md`)
- [ ] `pip freeze > requirements-lock.txt` generated at least once, for a
      known-good reproducible install (optional, but recommended before
      calling anything a "release")
- [ ] `pip install -r requirements-dev.txt && pip-audit` run with no
      unresolved high-severity findings

## Documentation
- [ ] `README.md` setup steps followed literally, on a machine that
      hasn't run this project before, start to finish
- [ ] `SECURITY.md` reviewed for accuracy against the current code
- [ ] `CHANGELOG.md` entry added for this release
- [ ] Screenshots/demo assets captured (see checklist in `README.md`)
- [ ] `LICENSE` author name filled in

## GitHub-specific (if publishing there)
- [ ] Repository description and topics set (`fastapi`, `security`,
      `bandit`, `llm`, `code-review`, etc.)
- [ ] `.github/workflows/tests.yml` passes on the actual pushed branch —
      check the Actions tab, not just local `pytest`
- [ ] Repo is public (or intentionally private, if that's the goal)
- [ ] README renders correctly on GitHub — check the Mermaid diagram
      actually renders (GitHub supports Mermaid natively in Markdown; a
      typo in the diagram syntax will silently show as a code block
      instead of a rendered diagram)

## Final sanity pass
- [ ] Clone the repo fresh into a new directory and follow the README
      from a cold start — this catches "works on my machine" gaps that
      editing in place won't
- [ ] Confirm the free-tier LLM key used for testing hasn't hit its rate
      limit mid-demo (see the note in `README.md` about free-tier limits
      changing over time)
