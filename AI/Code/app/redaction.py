"""
Best-effort redaction of obvious secret patterns before code is sent to a
third-party LLM API.

Important scope limits, stated plainly rather than implied:
  - This is NOT a secret scanner and NOT a guarantee. It's a last line of
    defense so an accidentally-pasted key doesn't get forwarded to
    Gemini/Groq verbatim — it does not replace not committing secrets in
    the first place, and it will miss anything that doesn't match these
    patterns.
  - The ORIGINAL code — never the redacted version — is what's sent to
    Bandit, because Bandit runs entirely on your machine and redacting
    would only make its line numbers and analysis less accurate for no
    security benefit.
  - Redaction only ever touches what's sent to the LLM provider. It never
    changes what's stored, scanned, or returned to the caller as `scan`.
"""

import re
from dataclasses import dataclass

REDACTED_PLACEHOLDER_TEMPLATE = "«REDACTED:{kind}»"

# Each entry is (human-readable kind, compiled pattern). Order doesn't
# matter for correctness — each pattern is applied to the same original
# text for detection, then applied in sequence for substitution.
_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("AWS Access Key ID", re.compile(r"AKIA[0-9A-Z]{16}")),
    (
        "Private Key Block",
        re.compile(
            r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----"
        ),
    ),
    ("Slack Token", re.compile(r"xox[baprs]-[0-9A-Za-z-]{10,}")),
    ("Bearer Token", re.compile(r"Bearer\s+[A-Za-z0-9\-_.]{10,}")),
    (
        "Hardcoded Secret Assignment",
        re.compile(
            r"(?i)\b(api[_-]?key|secret[_-]?key|access[_-]?token|"
            r"password|passwd|pwd|token)\b\s*[:=]\s*['\"][^'\"\n]{6,}['\"]"
        ),
    ),
]


@dataclass(frozen=True)
class RedactionMatch:
    kind: str
    line: int  # 1-indexed, computed against the ORIGINAL code


def redact_secrets(code: str) -> tuple[str, list[RedactionMatch]]:
    """
    Returns (redacted_code, matches). `matches` records only the *kind* of
    secret found and its line number — never the matched text itself —
    so this function's return value is always safe to log.
    """
    matches: list[RedactionMatch] = []
    redacted = code

    for kind, pattern in _PATTERNS:
        for m in pattern.finditer(code):
            line = code[: m.start()].count("\n") + 1
            matches.append(RedactionMatch(kind=kind, line=line))
        redacted = pattern.sub(REDACTED_PLACEHOLDER_TEMPLATE.format(kind=kind), redacted)

    return redacted, matches
