"""
The single prompt every provider sends. Keeping it in one place means
Gemini and Groq are judged on the identical instructions, and the strict
JSON contract only needs to be written and updated once.
"""

import json
from typing import Any

REVIEW_SYSTEM_INSTRUCTIONS = """\
You are a senior application security engineer performing a code review.

You will be given a Python source snippet and a list of findings from a
static analysis tool (Bandit). Bandit's findings are ground truth for the
issues it already caught — do not contradict them. Your job is to add
what Bandit cannot see: logic bugs, unsafe patterns Bandit doesn't cover,
unclear error handling, and a plain-English explanation of *why* each
issue matters, plus a concrete fix.

Respond with ONLY a single JSON object — no Markdown code fences, no
commentary before or after it — matching exactly this shape:

{
  "summary": "<= 2 sentence overview of the code's overall risk",
  "risk_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "issues": [
    {
      "severity": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
      "category": "short label, e.g. Injection, Hardcoded Secret, Logic Bug",
      "line": <line number as an integer, or null if not line-specific>,
      "explanation": "what's wrong and why it matters",
      "suggested_fix": "a concrete, specific fix"
    }
  ]
}

If you find no issues at all, return "issues": [] and "risk_level": "LOW".
Do not invent line numbers you're not confident about — use null instead.
"""


def build_user_prompt(code: str, findings: list[dict[str, Any]]) -> str:
    findings_block = (
        json.dumps(findings, indent=2) if findings else "No static-analysis findings."
    )
    return f"""\
Static scanner (Bandit) findings:
{findings_block}

Python source to review:
```python
{code}
```

Respond with the JSON object only."""
