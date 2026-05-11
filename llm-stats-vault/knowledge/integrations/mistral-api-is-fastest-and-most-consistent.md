---
tags: [integration, mistral, api]
date: 2026-04-26
---

# Mistral API Is Fastest and Most Consistent

## Connection Details
- **Class**: `MistralClient` in `code/models/model_clients.py`
- **Model**: `mistral-large-latest`
- **Endpoint**: `api.mistral.ai/v1/chat/completions`
- **Auth**: `Authorization: Bearer <MISTRAL_API_KEY>`
- **Env var**: `MISTRAL_API_KEY`

## Request Format
OpenAI-compatible — same structure as ChatGPT client.

## Performance (Phase 1)
- **Avg score**: 0.635 (2nd highest after Claude)
- **Pass rate**: 110/136 = 81%
- **Latency**: fastest and most consistent (along with ChatGPT)
- 2nd place overall — strong generalist performance

## Notes
- Added to project after initial 4-model design (Claude/ChatGPT/DeepSeek/Gemini)
- OpenAI-compatible API makes client trivial
- `mistral-large-latest` is a moving target model string — always resolves to latest large model
