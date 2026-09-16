"""
Shared request/response models — the API contract.

Day 4 scope: real request limits (not just a large arbitrary max_length),
explicit Python-only validation with a clear rejection message, and
OpenAPI-facing descriptions/examples so /docs is actually useful to a
consumer who has never read this source file.
"""

from pydantic import BaseModel, Field, field_validator

# Generous enough for a real code review, small enough to keep Bandit fast
# and free-tier LLM calls comfortably within their token limits. Chosen
# deliberately rather than left at an arbitrary round number: most
# free-tier LLM context windows handle this many characters of source
# plus prompt overhead without truncation.
MAX_CODE_CHARS = 50_000

# Languages supported for static analysis and AI review.
# Python uses Bandit; JavaScript/TypeScript use ESLint; others may be added.
SUPPORTED_LANGUAGES = {"python", "javascript", "typescript", "go", "ruby", "java", "php"}


class ScanRequest(BaseModel):
    """Request body shared by both /scan and /review."""

    code: str = Field(
        ...,
        min_length=1,
        max_length=MAX_CODE_CHARS,
        description=(
            "Python source code to analyze. Limited to "
            f"{MAX_CODE_CHARS:,} characters — large enough for a real "
            "file, small enough to keep the scan fast and any LLM call "
            "within its free-tier token limits."
        ),
        examples=["def add(a, b):\n    return a + b\n"],
    )
    language: str = Field(
        default="python",
        description=(
            "Source language. Only 'python' is supported in this MVP; "
            "any other value is rejected with a 400."
        ),
        examples=["python"],
    )

    @field_validator("code")
    @classmethod
    def _reject_blank_code(cls, value: str) -> str:
        # min_length=1 already blocks "", but not "   " — a string of pure
        # whitespace passes length checks and produces a useless scan.
        if not value.strip():
            raise ValueError("code must not be empty or whitespace-only.")
        return value

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "code": "import subprocess\n\n"
                    "def run(cmd):\n    subprocess.call(cmd, shell=True)\n",
                    "language": "python",
                }
            ]
        }
    }


class ScanFinding(BaseModel):
    """A single normalized Bandit finding."""

    rule_id: str = Field(description="Bandit test ID, e.g. 'B602'.")
    rule_name: str = Field(
        description="Bandit test name, e.g. 'subprocess_popen_with_shell_equals_true'."
    )
    severity: str = Field(description="LOW | MEDIUM | HIGH | UNDEFINED")
    confidence: str = Field(description="LOW | MEDIUM | HIGH | UNDEFINED")
    line: int = Field(description="1-indexed line number in the submitted snippet.")
    message: str = Field(description="Bandit's human-readable description of the issue.")
    more_info: str | None = Field(
        default=None, description="Link to Bandit's documentation for this rule, if available."
    )


class ScanResult(BaseModel):
    """Response body for /scan, and the `scan` field of /review."""

    tool: str = Field(description="Always 'bandit' for this MVP.")
    findings: list[ScanFinding]
    issue_count: int = Field(description="Convenience count; equals len(findings).")
    loc: int = Field(description="Lines of code Bandit actually analyzed.")


class AIIssue(BaseModel):
    """A single issue surfaced by the LLM review."""

    severity: str = Field(description="LOW | MEDIUM | HIGH | CRITICAL")
    category: str = Field(
        description="Short label, e.g. 'Injection', 'Hardcoded Secret', 'Logic Bug'."
    )
    line: int | None = Field(
        default=None,
        description="Line number if the model is confident of one; null otherwise.",
    )
    explanation: str = Field(description="What's wrong and why it matters.")
    suggested_fix: str = Field(description="A concrete, specific fix.")


class AIReviewResult(BaseModel):
    """The LLM's structured review, present only when the provider call succeeds."""

    summary: str = Field(description="<=2 sentence overview of the code's overall risk.")
    risk_level: str = Field(description="LOW | MEDIUM | HIGH | CRITICAL")
    issues: list[AIIssue]


class ReviewResponse(BaseModel):
    """
    Response body for /review.

    `ai_review` and `ai_error` are mutually exclusive: exactly one is set,
    never both, never neither. `scan` is always present and always
    trustworthy even when the AI half fails entirely — Bandit runs
    locally and never depends on provider uptime, rate limits, or an API
    key being configured.
    """

    scan: ScanResult
    ai_review: AIReviewResult | None = Field(
        default=None,
        description="Set when the LLM provider call succeeded and returned a valid schema.",
    )
    ai_error: str | None = Field(
        default=None,
        description=(
            "Set when the LLM provider call failed for any reason (missing "
            "key, timeout, provider error, malformed model output). The "
            "scan above is still valid and complete."
        ),
    )
    redactions: list[str] = Field(
        default_factory=list,
        description=(
            "Best-effort secret patterns (e.g. 'AWS Access Key ID on line 4') "
            "redacted from the code before it was sent to the LLM provider. "
            "Never includes the actual secret value. Empty if none were found. "
            "This is not a guarantee — see SECURITY.md."
        ),
    )
