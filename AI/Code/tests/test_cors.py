"""
Day 5 needs the dashboard (a static HTML file) to call the API
cross-origin. This test confirms CORS is actually configured, rather than
discovering it's missing only when the browser silently blocks the fetch.
"""


def test_cors_allows_cross_origin_requests(client):
    r = client.get("/health", headers={"Origin": "null"})
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") == "*"
