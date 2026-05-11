---
tags: [integration, deepseek, api]
date: 2026-04-26
---

# DeepSeek Has Worst Speed-Accuracy Tradeoff

## Connection Details
- **Class**: `DeepSeekClient` in `code/models/model_clients.py`
- **Model**: `deepseek-chat`
- **Endpoint**: `api.deepseek.com/v1/chat/completions`
- **Auth**: `Authorization: Bearer <DEEPSEEK_API_KEY>`
- **Env var**: `DEEPSEEK_API_KEY`

## Request Format
OpenAI-compatible — same structure as ChatGPT client.

## Performance (Phase 1)
- **Avg score**: 0.615
- **Pass rate**: 100/136 = 74%
- **Latency**: highest and most variable of all models
- Speed-accuracy tradeoff: worst among all 5 models (latency/accuracy scatter)
- Tier 4 pass rate: 38% (lowest — Claude is 69%)

## Notes
- API is OpenAI-compatible, making the client trivial to implement
- Despite high latency, pass rate (74%) is slightly above ChatGPT (72%)
