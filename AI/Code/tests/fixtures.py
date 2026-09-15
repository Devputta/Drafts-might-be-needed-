"""
Shared code samples for tests. Centralized so `test_scanner.py`,
`test_review.py`, and the Day 6 hardening tests all exercise the exact
same inputs instead of subtly-different copies drifting apart over time.
"""

CLEAN_CODE = "def add(a: int, b: int) -> int:\n    return a + b\n"

# Deliberately vulnerable: shell=True on subprocess is a classic
# command-injection risk. Bandit flags this as B602
# (subprocess_popen_with_shell_equals_true).
VULNERABLE_CODE = "import subprocess\n\ndef run(cmd):\n    subprocess.call(cmd, shell=True)\n"

HARDCODED_PASSWORD_CODE = 'password = "hunter2super_secret"\n'
