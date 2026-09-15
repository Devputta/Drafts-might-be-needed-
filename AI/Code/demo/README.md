# Demo fixtures

`sample_review_response.json` is a hand-crafted, schema-valid example of
what `POST /review` returns — not a live API capture, since this repo
ships with no API key by default. It's the exact response you'd get for
this input, sent to `/review` with `{"language": "python"}`:

```python
import subprocess

def run_backup(cmd):
    subprocess.call(cmd, shell=True)
```

Field names and types match `app/schemas.py` exactly (`ScanResult`,
`AIReviewResult`, `AIIssue`, `ReviewResponse`) — useful as a reference for
building a second frontend, writing a client SDK, or just seeing the
shape without running the server. If you have a free Gemini or Groq key
configured, running the same snippet through the real `/review` endpoint
should return something structurally identical, though the AI's exact
wording will vary between calls and between providers.
