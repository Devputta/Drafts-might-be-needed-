from tests.fixtures import CLEAN_CODE, HARDCODED_PASSWORD_CODE, VULNERABLE_CODE


def test_scan_clean_code_reports_no_findings(client):
    r = client.post("/scan", json={"code": CLEAN_CODE, "language": "python"})
    assert r.status_code == 200
    body = r.json()
    assert body["tool"] == "bandit"
    assert body["issue_count"] == 0
    assert body["findings"] == []


def test_scan_flags_shell_true_subprocess_call(client):
    r = client.post("/scan", json={"code": VULNERABLE_CODE, "language": "python"})
    assert r.status_code == 200
    body = r.json()
    assert body["issue_count"] >= 1

    # Bandit's exact rule ID for shell=True subprocess calls is B602, but we
    # assert loosely on the B60x family so a Bandit version bump doesn't
    # break this test on a rule-ID technicality.
    rule_ids = {f["rule_id"] for f in body["findings"]}
    assert any(rid.startswith("B60") for rid in rule_ids), rule_ids

    severities = {f["severity"] for f in body["findings"]}
    assert severities.issubset({"LOW", "MEDIUM", "HIGH", "UNDEFINED"})


def test_scan_flags_hardcoded_password(client):
    r = client.post(
        "/scan", json={"code": HARDCODED_PASSWORD_CODE, "language": "python"}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["issue_count"] >= 1


def test_scan_rejects_non_python_language(client):
    r = client.post("/scan", json={"code": "print(1)", "language": "javascript"})
    assert r.status_code == 400


def test_scan_rejects_empty_code(client):
    r = client.post("/scan", json={"code": "", "language": "python"})
    # Pydantic min_length=1 validation failure
    assert r.status_code == 422


def test_scan_response_includes_line_numbers(client):
    r = client.post("/scan", json={"code": VULNERABLE_CODE, "language": "python"})
    body = r.json()
    for finding in body["findings"]:
        assert isinstance(finding["line"], int)
        assert finding["line"] > 0
