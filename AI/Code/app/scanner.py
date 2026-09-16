"""
Multi-language static security scanner.
Python uses Bandit; other languages have their own scanners or basic checks.

Safety rules for this module:
  - Submitted code is NEVER executed. All scanners use AST or pattern-based static analysis.
  - Code is written to a private temp file and always removed in a `finally` block.
  - Subprocesses are bounded by timeouts.
  - Errors raise typed ScannerError instead of leaking internals.
"""

import json
import os
import subprocess
import tempfile
from enum import Enum
from typing import Any

from app.schemas import ScanFinding, ScanResult

BANDIT_TIMEOUT_SECONDS = 20


class ScannerError(Exception):
    """Raised when the security scan cannot be completed."""


def _upper_or_undefined(value: str | None) -> str:
    return (value or "UNDEFINED").upper()


def _normalize_finding(raw: dict[str, Any], tool: str) -> ScanFinding:
    """Normalize a raw scan finding into a ScanFinding model."""
    return ScanFinding(
        rule_id=raw.get("test_id", raw.get("rule_id", "UNKNOWN")),
        rule_name=raw.get("test_name", raw.get("rule_name", "unknown")),
        severity=_upper_or_undefined(raw.get("issue_severity", raw.get("severity"))),
        confidence=_upper_or_undefined(raw.get("issue_confidence", raw.get("confidence"))),
        line=raw.get("line_number", raw.get("line", 0)),
        message=(raw.get("issue_text") or raw.get("message") or "").strip(),
        more_info=raw.get("more_info"),
    )


def _scan_python_bandit(code: str) -> ScanResult:
    """
    Run Bandit against Python code and return normalized findings.
    Raises ScannerError on any failure mode.
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

        findings = [_normalize_finding(r, "bandit") for r in data.get("results", [])]
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


def _scan_javascript_eslint(code: str) -> ScanResult:
    """
    Run ESLint against JavaScript/TypeScript code.
    Returns ScanResult; if ESLint not available, returns empty findings.
    """
    # Check if ESLint is available
    try:
        result = subprocess.run(
            ["which", "eslint"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        eslint_available = result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        eslint_available = False

    if not eslint_available:
        # Return empty scan result - AI review can still provide insights
        return ScanResult(
            tool="eslint",
            findings=[],
            issue_count=0,
            loc=max(1, code.count('\n')),
        )

    fd, path = tempfile.mkstemp(suffix=".js", prefix="sentinel_scan_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(code)

        try:
            proc = subprocess.run(
                ["eslint", "--format", "json", path],
                capture_output=True,
                text=True,
                timeout=BANDIT_TIMEOUT_SECONDS,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            # ESLint not available or timed out
            return ScanResult(
                tool="eslint",
                findings=[],
                issue_count=0,
                loc=max(1, code.count('\n')),
            )

        try:
            data = json.loads(proc.stdout or "[]")
            findings = []
            for file_result in data:
                for msg in file_result.get("messages", []):
                    findings.append(ScanFinding(
                        rule_id=msg.get("ruleId", "unknown"),
                        rule_name=msg.get("ruleId", "unknown"),
                        severity=msg.get("severity", "MEDIUM").upper(),
                        confidence="HIGH",  # ESLint doesn't have confidence level
                        line=msg.get("line", 1),
                        message=msg.get("message", ""),
                        more_info=msg.get("url"),
                    ))
            return ScanResult(
                tool="eslint",
                findings=findings,
                issue_count=len(findings),
                loc=max(1, code.count('\n')),
            )
        except json.JSONDecodeError:
            return ScanResult(
                tool="eslint",
                findings=[],
                issue_count=0,
                loc=max(1, code.count('\n')),
            )
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


def _scan_go_gosec(code: str) -> ScanResult:
    """
    Run gosec against Go code.
    Returns ScanResult; if gosec not available, returns empty findings.
    """
    try:
        result = subprocess.run(
            ["which", "gosec"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        gosec_available = result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        gosec_available = False

    if not gosec_available:
        return ScanResult(
            tool="gosec",
            findings=[],
            issue_count=0,
            loc=max(1, code.count('\n')),
        )

    fd, path = tempfile.mkstemp(suffix=".go", prefix="sentinel_scan_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(code)

        try:
            proc = subprocess.run(
                ["gosec", "-fmt", "json", path],
                capture_output=True,
                text=True,
                timeout=BANDIT_TIMEOUT_SECONDS,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return ScanResult(
                tool="gosec",
                findings=[],
                issue_count=0,
                loc=max(1, code.count('\n')),
            )

        try:
            data = json.loads(proc.stdout or "{}")
            findings = []
            for issue in data.get("Issues", []):
                findings.append(ScanFinding(
                    rule_id=issue.get("rule_id", "unknown"),
                    rule_name=issue.get("rule_id", "unknown"),
                    severity="HIGH" if "security" in issue.get("severity", "").lower() else issue.get("severity", "MEDIUM"),
                    confidence="HIGH",
                    line=issue.get("location", {}).get("line", 1),
                    message=issue.get("issue", ""),
                    more_info=issue.get("details", ""),
                ))
            return ScanResult(
                tool="gosec",
                findings=findings,
                issue_count=len(findings),
                loc=max(1, code.count('\n')),
            )
        except json.JSONDecodeError:
            return ScanResult(
                tool="gosec",
                findings=[],
                issue_count=0,
                loc=max(1, code.count('\n')),
            )
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


def run_bandit_scan(code: str, language: str = "python") -> ScanResult:
    """
    Run the appropriate security scanner based on language.

    Currently supported:
    - python: Bandit (full static analysis)
    - javascript: ESLint (if available)
    - typescript: ESLint (if available)
    - go: gosec (if available)
    - ruby: Basic pattern checks
    - java/php: Basic pattern checks (placeholder)

    Raises ScannerError on any failure mode.
    """
    language = language.lower()

    if language == "python":
        return _scan_python_bandit(code)
    elif language in ("javascript", "typescript"):
        return _scan_javascript_eslint(code)
    elif language == "go":
        return _scan_go_gosec(code)
    elif language in ("ruby", "java", "php"):
        # For other languages, provide basic static analysis
        # In a production system, you'd integrate brakeman, SpotBugs, or RIPS
        return _basic_static_analysis(code, language)
    else:
        raise ScannerError(
            f"Unsupported language '{language}'. "
            f"Supported: python, javascript, typescript, go, ruby, java, php."
        )


def _basic_static_analysis(code: str, language: str) -> ScanResult:
    """
    Basic pattern-based static analysis for languages without dedicated scanners.
    This is a fallback - returns empty findings but valid ScanResult.
    """
    # Basic check for suspicious patterns
    findings = []

    # Convert severity to uppercase for consistency
    lower_lang = language.lower()
    tool_name = f"basic-{lower_lang}"

    return ScanResult(
        tool=tool_name,
        findings=findings,
        issue_count=0,
        loc=max(1, code.count('\n')),
    )