"""
Shared pytest fixtures.

The `client` fixture is the one every test file should use instead of
building its own module-level `TestClient(app)`. Centralizing it here
does two things a hand-rolled per-file client can't guarantee:
  1. `app.dependency_overrides` is cleared both before AND after every
     test, so a fake LLM provider set in one test can never leak into
     the next test by accident, regardless of import order.
  2. If the app's construction ever needs a test-only tweak (e.g. a
     different settings object), there's exactly one place to make it.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    app.dependency_overrides.clear()
    yield TestClient(app)
    app.dependency_overrides.clear()
