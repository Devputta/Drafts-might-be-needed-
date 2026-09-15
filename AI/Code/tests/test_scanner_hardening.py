"""
Day 6 hardening: exercise every failure mode of run_bandit_scan() directly
(not through the API), by monkeypatching subprocess.run. This is the
level at which "Bandit isn't installed", "Bandit hangs", and "Bandit's
output isn't valid JSON" actually need to be proven safe.
"""

import os
import subprocess

import pytest

from app.scanner import ScannerError, run_bandit_scan


def test_missing_bandit_binary_raises_scanner_error(monkeypatch):
    def _boom(*args, **kwargs):
        raise FileNotFoundError("no such file: bandit")

    monkeypatch.setattr(subprocess, "run", _boom)

    with pytest.raises(ScannerError, match="not installed"):
        run_bandit_scan("x = 1\n")


def test_bandit_timeout_raises_scanner_error(monkeypatch):
    def _boom(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="bandit", timeout=20)

    monkeypatch.setattr(subprocess, "run", _boom)

    with pytest.raises(ScannerError, match="timeout"):
        run_bandit_scan("x = 1\n")


def test_malformed_bandit_output_raises_scanner_error(monkeypatch):
    class _FakeCompletedProcess:
        returncode = 1
        stdout = "this is not json"
        stderr = "bandit crashed somehow"

    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: _FakeCompletedProcess())

    with pytest.raises(ScannerError, match="valid JSON"):
        run_bandit_scan("x = 1\n")


def test_temp_file_is_cleaned_up_even_when_bandit_times_out(monkeypatch):
    """
    The temp file must be removed in the `finally` block regardless of
    which exception path is taken — this proves it for the timeout path
    specifically, since a hung/killed process is the case most likely to
    leave debris behind in a naive implementation.
    """
    captured = {}

    def _spy(cmd, **kwargs):
        captured["path"] = cmd[-1]  # ["bandit", "-q", "-f", "json", <path>]
        raise subprocess.TimeoutExpired(cmd="bandit", timeout=20)

    monkeypatch.setattr(subprocess, "run", _spy)

    with pytest.raises(ScannerError):
        run_bandit_scan("x = 1\n")

    assert captured.get("path"), "expected the temp file path to have been captured"
    assert not os.path.exists(captured["path"])


def test_temp_file_is_cleaned_up_on_success():
    """Sanity check on the happy path too, not just the failure paths."""
    import tempfile

    captured = {}
    real_mkstemp = tempfile.mkstemp

    def _spy_mkstemp(*args, **kwargs):
        fd, path = real_mkstemp(*args, **kwargs)
        captured["path"] = path
        return fd, path

    tempfile.mkstemp = _spy_mkstemp
    try:
        run_bandit_scan("x = 1\n")
    finally:
        tempfile.mkstemp = real_mkstemp

    assert captured.get("path")
    assert not os.path.exists(captured["path"])
