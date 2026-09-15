Day 3 — AI Review
Build: Gemini/Groq adapter, environment variables, structured JSON response, provider errors.
Prompt:
Implement Day 3. Add an LLM provider abstraction supporting either Gemini or Groq via environment variables. Send Python source plus Bandit findings to the model. Require strict JSON containing summary, risk_level, and issues with severity/category/line/explanation/suggested_fix. Never hard-code keys. Handle timeouts, provider errors, and malformed JSON.
