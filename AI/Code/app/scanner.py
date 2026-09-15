"""
Local static security scanning via Bandit.

Safety rules this module follows (see docs/rules.md):
  - The submitted code is NEVER executed. Bandit performs AST-based static
    analysis only — it parses the file, it does not import or run it.
  - The snippet is written to a private temporary file and always removed
    in a `finally` block, even if Bandit crashes or times out.
  - The subprocess is bounded by a timeout so a pathological input can't
    hang a request indefinitely.
  - Errors (Bandit missing, timeout, malformed output) raise a typed
    ScannerError instead of leaking raw subprocess internals to the caller.
"""

import json
import os
import subprocess
import tempfile
from typing import Any

from app.schemas import ScanFinding, ScanResult

BANDIT_TIMEOUT_SECONDS = 20


class ScannerError(Exception):
    """Raised when the Bandit scan cannot be completed."""


def _upper_or_undefined(value: str | None) -> str:
    return (value or "UNDEFINED").upper()


def _normalize_finding(raw: dict[str, Any]) -> ScanFinding:
    return ScanFinding(
        rule_id=raw.get("test_id", "UNKNOWN"),
        rule_name=raw.get("test_name", "unknown"),
        severity=_upper_or_undefined(raw.get("issue_severity")),
        confidence=_upper_or_undefined(raw.get("issue_confidence")),
        line=raw.get("line_number", 0),
        message=(raw.get("issue_text") or "").strip(),
        more_info=raw.get("more_info"),
    )


def run_bandit_scan(code: str) -> ScanResult:
    """
    Run Bandit against a Python snippet and return normalized findings.

    Raises ScannerError on any failure mode (Bandit not installed, timeout,
    unparseable output) so callers can turn it into a clean HTTP error.
    """
    fd, path = tempfile.mkstemp(suffix=".py", prefix="sentinel_scan_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(code)

        try:
            proc = subprocess.run(
                ["bandit", "-q", "-f", "json", path],
                capture_output=True,
                text=True,
                timeout=BANDIT_TIMEOUT_SECONDS,
            )
        except FileNotFoundError as e:
            raise ScannerError(
                "Bandit is not installed or not on PATH. "
                "Run: pip install bandit (already in requirements.txt — "
                "did you activate your virtualenv?)"
            ) from e
        except subprocess.TimeoutExpired as e:
            raise ScannerError(
                f"Bandit scan exceeded the {BANDIT_TIMEOUT_SECONDS}s timeout."
            ) from e

        # Bandit exit codes: 0 = no issues found, 1 = issues found,
        # >1 = a real error. Both 0 and 1 still print valid JSON to stdout,
        # so we only treat this as an error if stdout isn't parseable.
        try:
            data = json.loads(proc.stdout or "{}")
        except json.JSONDecodeError as e:
            raise ScannerError(
                f"Bandit did not return valid JSON "
                f"(exit code {proc.returncode}): {proc.stderr.strip()[:500]}"
            ) from e

        findings = [_normalize_finding(r) for r in data.get("results", [])]
        totals = data.get("metrics", {}).get("_totals", {})

        return ScanResult(
            tool="bandit",
            findings=findings,
            issue_count=len(findings),
            loc=int(totals.get("loc", 0)),
        )
    finally:
        # Always clean up, whether the scan succeeded, failed, or timed out.
        try:
            os.remove(path)
        except OSError:
            pass
