"""
Centralized logging configuration.

The one rule every logging call in this app follows: never log a request
body, submitted source code, or an API key. The access-log middleware in
main.py logs method/path/status/duration only — nothing from the payload.
Error branches in main.py log our own generated messages (e.g. "Bandit
scan timed out"), never `request.code` directly.

One caveat worth stating rather than hiding: a ProviderError message can
occasionally include a short, truncated fragment of the *model's* raw
output when it fails to parse as JSON (see app/llm/base.py). Because the
model was given the user's code, that echoed fragment could in rare cases
contain a snippet of it. This is a known, narrow limitation — see
SECURITY.md — not something this logging setup can fully close without
losing the diagnostic value of the error message entirely.
"""

import logging
import sys


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stdout,
    )
