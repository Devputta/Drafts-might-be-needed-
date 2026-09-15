# 2-Minute Demo Script

A timed script for recording a short screen capture (Loom, QuickTime,
OBS — anything free) for a portfolio or a job application. Total runtime
target: **~2 minutes**. Practice once before recording; don't script the
narration word-for-word, just hit these beats.

---

**0:00 – 0:15 — The problem**
> "Code review tools either need a paid SaaS subscription, or they're
> pure static analysis with no understanding of *why* something matters.
> This combines both, for free: a local security scanner plus an AI
> review, running entirely on your own machine."

Show the terminal with `uvicorn app.main:app --reload` already running.

**0:15 – 0:35 — The setup, briefly**
> "One FastAPI backend, one HTML dashboard, no build step, no database.
> The only external dependency is a free-tier LLM key — Gemini or Groq,
> your choice, swapped with one environment variable."

Quickly show `.env` with `LLM_PROVIDER=gemini` and a redacted key (don't
show the real key on screen).

**0:35 – 1:15 — The live demo**
1. Open `frontend/index.html` in the browser.
2. Point out the pre-filled vulnerable snippet (`subprocess.call(cmd, shell=True)`).
3. Click **Run review**. Narrate while it loads:
   > "This is hitting a local Bandit scan — completely free, completely
   > offline — and a free-tier LLM call at the same time."
4. When results appear, walk through:
   - The risk banner and its summary.
   - The Bandit finding (`B602`, shell-injection risk) with its severity badge.
   - The AI issue below it — same vulnerability, explained in plain
     English, with a concrete suggested fix.

**1:15 – 1:35 — The graceful degradation (optional, if time allows)**
> "If the AI call fails for any reason — rate limit, no key configured,
> whatever — the scan still comes back. Watch."

Temporarily clear the API key in `.env`, restart the server, run the same
review, and show the amber "AI review unavailable" notice next to the
still-intact Bandit results.

**1:35 – 1:55 — The engineering, not just the feature**
> "Everything here is tested — 40-plus tests covering Bandit failure
> modes, provider timeouts, malformed model output, oversized input — all
> running offline, no API key needed for CI."

Show `pytest -v` passing in a terminal, or the green GitHub Actions badge
on the repo.

**1:55 – 2:00 — Close**
> "Built over seven scoped days, from a FastAPI skeleton to a hardened,
> tested, portfolio-ready tool — entirely on free-tier infrastructure."

---

## Recording checklist

- [ ] Backend running (`uvicorn app.main:app --reload --port 8000`)
- [ ] `.env` has a real key for the primary take; a second short take
      with the key removed, for the graceful-degradation beat
- [ ] Browser zoomed enough that text is readable in a recording
      (125–150% zoom works well for most screen sizes)
- [ ] Terminal font size bumped up before recording
- [ ] No real secrets, API keys, or private repo names visible on screen
- [ ] `pytest -v` output ready in a second terminal tab, pre-run once so
      Python's first-import overhead doesn't stall on camera
