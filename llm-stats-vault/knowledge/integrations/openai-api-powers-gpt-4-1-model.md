---
tags: [integration, openai, chatgpt, api]
date: 2026-04-26
---

# OpenAI API Powers GPT-4.1 Model

## Connection Details
- **Class**: `ChatGPTClient` in `code/models/model_clients.py`
- **Model**: `gpt-4.1` (upgraded from `gpt-4o-mini` in earlier runs)
- **Endpoint**: `api.openai.com/v1/chat/completions`
- **Auth**: `Authorization: Bearer <OPENAI_API_KEY>`
- **Env var**: `OPENAI_API_KEY`

## Request Format
Standard OpenAI chat completions format:
```json
{
  "model": "gpt-4.1",
  "max_tokens": 1024,
  "messages": [
    {"role": "system", "content": "<system prompt>"},
    {"role": "user", "content": "<prompt>"}
  ]
}
```

## Performance (Phase 1)
- **Avg score**: 0.612
- **Pass rate**: 98/136 = 72%
- **Latency**: fast and consistent
- Best at: structure score (93.6%) — highest method compliance of all models
- Weakness: numeric accuracy

## Notes
- Updated from `gpt-4o-mini` to `gpt-4.1` during project — old records in `runs.jsonl` used the old model
- DeepSeek and Mistral also use OpenAI-compatible format (same request structure, different endpoints)
