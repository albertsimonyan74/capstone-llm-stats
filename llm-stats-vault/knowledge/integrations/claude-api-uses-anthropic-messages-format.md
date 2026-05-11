---
tags: [integration, claude, anthropic, api]
date: 2026-04-26
---

# Claude API Uses Anthropic Messages Format

## Connection Details
- **Class**: `ClaudeClient` in `code/models/model_clients.py`
- **Model**: `claude-sonnet-4-5`
- **Endpoint**: `api.anthropic.com/v1/messages`
- **Auth**: `x-api-key` header + `anthropic-version: 2023-06-01`
- **Env var**: `ANTHROPIC_API_KEY`

## Request Format
Anthropic messages API (NOT OpenAI-compatible):
```json
{
  "model": "claude-sonnet-4-5",
  "max_tokens": 1024,
  "system": "<system prompt>",
  "messages": [{"role": "user", "content": "<prompt>"}]
}
```

## Performance (Phase 1)
- **Avg score**: 0.696 (highest of all models)
- **Pass rate**: 117/136 = 86%
- **Latency**: moderate (mid-range among all models)
- Best at: numerical accuracy (63.1%), assumption compliance (65.6%)

## Also Used as Evaluator
`code/analysis/llm_judge.py` and `code/analysis/task_validator.py` use `claude-sonnet-4-6`
via the `anthropic` Python SDK (not httpx) — separate from the benchmark client.  
The `anthropic` package must be installed separately in `.venv`.  
See [[anthropic-module-not-in-venv]].

## Related
- [[scoring-pipeline]] — how scores are computed
- [[httpx-used-directly-no-vendor-sdks]] — why no SDK for benchmark client
