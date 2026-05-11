---
tags: [decision, httpx, api-client, dependencies]
date: 2026-04-26
---

# httpx Used Directly — No Vendor SDKs

## Decision
All 5 LLM API clients in `code/models/model_clients.py` use `httpx` for direct HTTP calls.  
No Anthropic SDK, OpenAI SDK, or Mistral SDK installed in the project venv (except `anthropic` package for judge/validator use).

## Why
- Reduces dependency surface — one HTTP library vs 5 vendor SDKs
- Avoids SDK version incompatibilities across providers
- All 5 providers expose REST APIs; raw HTTP is sufficient
- DeepSeek and Mistral are OpenAI-compatible — same request format, no SDK needed
- Gives full control over retry logic, timeouts, and request headers

## Trade-offs
- **Con**: Must manually maintain API format when providers change their schemas
- **Con**: No automatic SDK-level retry/circuit-breaker (but custom retry is implemented)
- **Pro**: Single dependency for all 5 providers, no version lock-in

## Exception: LLM Judge and Validator
`code/analysis/llm_judge.py` and `code/analysis/task_validator.py` use the `anthropic` Python SDK  
because they need streaming/async features not worth reimplementing.  
The `anthropic` package is NOT in the default `requirements.txt` — install separately:  
`pip install anthropic`  
See [[anthropic-module-not-in-venv]].

## How to Apply
- Adding new model client: inherit `BaseModelClient`, implement `query()` using httpx
- Follow the retry pattern: `_call_with_retry()` in `model_clients.py`
- See [[adding-a-new-task-type-requires-4-changes]] for full client addition checklist
