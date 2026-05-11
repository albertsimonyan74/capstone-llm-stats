---
tags: [integration, gemini, google, api, rate-limits]
date: 2026-04-26
---

# Gemini API Has Free Tier Rate Limits

## Connection Details
- **Class**: `GeminiClient` in `code/models/model_clients.py`
- **Model**: `gemini-2.5-flash`
- **Endpoint**: `generativelanguage.googleapis.com/v1beta`
- **Auth**: `?key=<GEMINI_API_KEY>` query param
- **Env var**: `GEMINI_API_KEY`

## Free Tier Constraints
- **~250 RPD** (requests per day) — hard daily quota
- **RPM** (requests per minute) limit also applies
- Quota resets at **midnight Pacific Time**

## Gemini-Specific Client Settings
```python
_GEMINI_RETRY_WAITS = [10, 20, 40, 80, 160]   # 5 retries, exponential
_GEMINI_SLEEP_S     = 3.0    # default inter-request delay
# Run with --delay 5 for safer free-tier operation
```

## Two Failure Modes
1. **RPM exhaustion** (429 rate limit) — fixable: retry waits + `--delay 5` flag
2. **RPD exhaustion** (daily quota gone) — unfixable until midnight Pacific reset

See [[gemini-daily-quota-exhausted-on-2026-04-24]] for the specific incident.

## Current Status
- Phase 1: 74/136 complete (62 tasks missing — quota hit 2026-04-24)
- Phase 2: 0/35 started
- Resume command:
```bash
python -m llm_runner.run_all_tasks --models gemini          # Phase 1
python -m llm_runner.run_all_tasks --models gemini \
  --tasks data/raw_data/benchmark_v1/tasks_advanced.json --delay 5   # Phase 2
```

## Request Format
Google's proprietary REST format (not OpenAI-compatible):
```json
{
  "contents": [{"role": "user", "parts": [{"text": "<prompt>"}]}],
  "systemInstruction": {"parts": [{"text": "<system prompt>"}]},
  "generationConfig": {"maxOutputTokens": 1024}
}
```
