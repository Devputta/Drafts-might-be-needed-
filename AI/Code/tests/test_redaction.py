from app.redaction import redact_secrets


def test_clean_code_is_unaffected():
    code = "def add(a, b):\n    return a + b\n"
    redacted, matches = redact_secrets(code)
    assert redacted == code
    assert matches == []


def test_aws_access_key_is_redacted():
    code = 'aws_key = "AKIAABCDEFGHIJKLMNOP"\n'
    redacted, matches = redact_secrets(code)
    assert "AKIAABCDEFGHIJKLMNOP" not in redacted
    assert any(m.kind == "AWS Access Key ID" for m in matches)


def test_private_key_block_is_redacted():
    code = (
        "key = '''\n"
        "-----BEGIN RSA PRIVATE KEY-----\n"
        "MIIEpAIBAAKCAQEA1234567890abcdef\n"
        "-----END RSA PRIVATE KEY-----\n"
        "'''\n"
    )
    redacted, matches = redact_secrets(code)
    assert "MIIEpAIBAAKCAQEA1234567890abcdef" not in redacted
    assert any(m.kind == "Private Key Block" for m in matches)


def test_bearer_token_is_redacted():
    code = 'headers = {"Authorization": "Bearer sk-abcdefghijklmnopqrstuvwxyz"}\n'
    redacted, matches = redact_secrets(code)
    assert "sk-abcdefghijklmnopqrstuvwxyz" not in redacted
    assert any(m.kind == "Bearer Token" for m in matches)


def test_hardcoded_password_assignment_is_redacted():
    code = 'password = "hunter2super_secret"\n'
    redacted, matches = redact_secrets(code)
    assert "hunter2super_secret" not in redacted
    assert any(m.kind == "Hardcoded Secret Assignment" for m in matches)


def test_slack_token_is_redacted():
    code = 'SLACK_TOKEN = "xoxb-1234567890-abcdefghijklmnop"\n'
    redacted, matches = redact_secrets(code)
    assert "xoxb-1234567890-abcdefghijklmnop" not in redacted
    assert any(m.kind == "Slack Token" for m in matches)


def test_matches_report_line_numbers_not_secret_values():
    code = 'x = 1\ny = 2\napi_key = "sk-verysecretvalue123456"\n'
    _, matches = redact_secrets(code)
    assert len(matches) == 1
    assert matches[0].line == 3
    # The dataclass itself must never carry the raw secret text.
    assert "sk-verysecretvalue123456" not in str(matches[0])


def test_redacted_code_preserves_surrounding_structure():
    code = 'def connect():\n    token = "Bearer abcdefghij1234567890"\n    return token\n'
    redacted, _ = redact_secrets(code)
    assert "def connect():" in redacted
    assert "return token" in redacted
    assert "REDACTED" in redacted
