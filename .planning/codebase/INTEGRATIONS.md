# External Integrations

**Analysis Date:** 2026-04-26

## Overview

Five external LLM APIs are the core integrations — all called via direct HTTP with `httpx` (no vendor SDKs). The MCP server exposes the benchmark internally to Claude Code. Google Fonts is the only frontend CDN dependency. No cloud storage, databases, or auth providers are used.

---

## LLM APIs

All clients live in `llm_runner/model_clients.py`. They share a common base class `BaseModelClient` and use `httpx.post()` with retry/backoff logic.

**Shared settings across all clients:**
- `_MAX_TOKENS = 1024`
- `_TIMEOUT = 60.0s`
- `_SLEEP_S = 1.0s` between requests
- Retry: 3 attempts, waits `[5s, 15s, 30s]` on 429 / connection / timeout errors
- Non-retryable: HTTP 400, 401, 403, 404

---

### Anthropic Claude

- Model: `claude-sonnet-4-5`
- Endpoint: `https://api.anthropic.com/v1/messages`
- Auth: `x-api-key` header with `ANTHROPIC_API_KEY`
- Required header: `anthropic-version: 2023-06-01`
- Client class: `ClaudeClient` in `llm_runner/model_clients.py`
- Response path: `data["content"][0]["text"]`
- Token usage: `data["usage"]["input_tokens"]` / `output_tokens`

---

### Google Gemini

- Model: `gemini-2.5-flash`
- Endpoint: `https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}`
- Auth: API key as URL query parameter (`?key=`)
- Client class: `GeminiClient` in `llm_runner/model_clients.py`
- Response path: `data["candidates"][0]["content"]["parts"][0]["text"]`
- Token usage: `data["usageMetadata"]["promptTokenCount"]` / `candidatesTokenCount`
- Rate limit overrides: retry waits `[10s, 20s, 40s, 80s, 160s]` (5 retries), inter-request delay 3.0s (overridable via `--delay`)
- Known constraint: free tier ~250 RPD daily quota; quota resets midnight Pacific. After exhaustion, all retries fail — must wait until next day or upgrade tier.
- Generation config: `maxOutputTokens: 4096`, `thinkingBudget: 0`

---

### OpenAI ChatGPT

- Model: `gpt-4.1`
- Endpoint: `https://api.openai.com/v1/chat/completions`
- Auth: `Authorization: Bearer {OPENAI_API_KEY}`
- Client class: `ChatGPTClient` in `llm_runner/model_clients.py`
- Request format: OpenAI chat completions (system + user messages)
- Response path: `data["choices"][0]["message"]["content"]`
- Token usage: `data["usage"]["prompt_tokens"]` / `completion_tokens`

---

### DeepSeek

- Model: `deepseek-chat`
- Endpoint: `https://api.deepseek.com/v1/chat/completions`
- Auth: `Authorization: Bearer {DEEPSEEK_API_KEY}`
- Client class: `DeepSeekClient` in `llm_runner/model_clients.py`
- Request format: OpenAI-compatible (identical to ChatGPT format)
- Response path: `data["choices"][0]["message"]["content"]`
- Token usage: `data["usage"]["prompt_tokens"]` / `completion_tokens`

---

### Mistral

- Model: `mistral-large-latest`
- Endpoint: `https://api.mistral.ai/v1/chat/completions`
- Auth: `Authorization: Bearer {MISTRAL_API_KEY}`
- Client class: `MistralClient` in `llm_runner/model_clients.py`
- Request format: OpenAI-compatible (identical to ChatGPT/DeepSeek format)
- Response path: `data["choices"][0]["message"]["content"]`
- Token usage: `data["usage"]["prompt_tokens"]` / `completion_tokens`

---

## MCP Server (Internal Tool Integration)

- Framework: `mcp.server.fastmcp.FastMCP`
- Server name: `"Capstone LLM Benchmark"`
- Transport: stdio (`mcp.run(transport="stdio")`)
- Entry point: `python -m capstone_mcp.server`
- Config: registered as MCP server in Claude Code settings (`.claude/settings.local.json`)
- Exposes 8 tools: `get_task`, `list_tasks`, `score_response`, `get_results`, `get_summary`, `compare_models`, `get_failures`, `run_single_task`
- Source: `capstone_mcp/server.py`

---

## Data Storage

**Benchmark data (local files, no external DB):**
- `data/benchmark_v1/tasks.json` — 136 Phase 1 task specs
- `data/benchmark_v1/tasks_advanced.json` — 35 Phase 2 task specs
- `data/benchmark_v1/tasks_all.json` — 171 merged tasks (read by FastAPI backend)
- `data/synthetic/perturbations.json` — 75 RQ4 perturbation tasks

**Run results (append-only JSONL):**
- `experiments/results_v1/runs.jsonl` — one JSON object per LLM run, written by `llm_runner/logger.py`
- `experiments/results_v1/results.json` — scoring output from `experiments/run_benchmark.py`

**Frontend static data:**
- `capstone-website/frontend/src/data/results_summary.json` — pre-computed summary for LiveResults component
- `capstone-website/frontend/src/data/stats.json` — aggregate stats displayed on site
- `capstone-website/frontend/src/data/tasks.json` — task data for frontend Tasks page
- `capstone-website/frontend/src/data/visualizations.js` — manifest of 15 visualization assets

**File storage (local):**
- `capstone-website/frontend/public/visualizations/png/` — 15 PNGs + 1 GIF (bar race animation)
- `capstone-website/frontend/public/visualizations/interactive/` — 14 Plotly HTML files + `_files/` subdirs

---

## Frontend External Services

**Google Fonts (CDN):**
- Loaded in `capstone-website/frontend/index.html` via `<link>` tag
- Fonts: `Inter` (weights 400–800) and `Space Mono` (weights 400, 700)
- Preconnect: `https://fonts.googleapis.com` and `https://fonts.gstatic.com`
- No API key required

---

## Authentication & Identity

**Auth provider:** None — no user authentication in any layer.

**LLM API keys:** Environment variable only. Missing key causes the client to return an error record (no exception raised). Keys are never logged or written to `runs.jsonl`.

---

## Monitoring & Observability

**Error tracking:** None — no Sentry or similar service.

**Logging:** Run logs written to `experiments/results_v1/runs.jsonl` via `llm_runner/logger.py` (`log_jsonl()` — append-only JSONL). Errors captured in the `error` field of each run record.

**Console output:** Each client prints progress to stdout during benchmark runs (e.g., `Querying claude on TASK_ID...`).

---

## CI/CD & Deployment

**CI Pipeline:** None detected — no GitHub Actions, CircleCI, or similar configuration files.

**Deployment target:** Docker Compose (inferred from two Dockerfiles + nginx config). No cloud provider config detected.
- Frontend: `capstone-website/frontend/Dockerfile` — Node 20 build → nginx:alpine on port 80
- Backend: `capstone-website/backend/Dockerfile` — python:3.11-slim, uvicorn on port 8000

---

## Environment Configuration

**Required environment variables (copy `.env.example` → `.env`):**

| Variable | Used by | Client class |
|---|---|---|
| `ANTHROPIC_API_KEY` | Claude LLM client | `ClaudeClient` |
| `GEMINI_API_KEY` | Gemini LLM client | `GeminiClient` |
| `OPENAI_API_KEY` | ChatGPT LLM client | `ChatGPTClient` |
| `DEEPSEEK_API_KEY` | DeepSeek LLM client | `DeepSeekClient` |
| `MISTRAL_API_KEY` | Mistral LLM client | `MistralClient` |

**Secrets location:** `.env` file at project root (not committed — listed in `.gitignore`). Template at `.env.example`.

**Missing key behavior:** Each client checks `os.environ.get(KEY)` at instantiation. If `None`, `query()` returns an error record with `error: "KEY_NAME not set"` — no exception, no crash.

---

## Webhooks & Callbacks

**Incoming:** None.

**Outgoing:** None — LLM API calls are request/response only, no webhooks configured.

---

## Inter-Service Communication (Website)

**Frontend → Backend API:**
- Dev: Vite proxy (`/api` → `http://localhost:8000`) configured in `capstone-website/frontend/vite.config.js`
- Prod: nginx reverse proxy (`/api/` → `http://backend:8000/api/`) in `capstone-website/frontend/nginx.conf`
- CORS: FastAPI middleware allows all origins (`allow_origins=["*"]`)

**FastAPI endpoints:**
- `GET /api/status` — benchmark status
- `GET /api/tasks` — filterable task list (tier, category, task_type, search)
- `GET /api/task/{task_id}` — single task with generated prompt
- `GET /api/results/summary` — per-model aggregate scores
- `GET /api/leaderboard` — ranked model list
- `GET /api/results/by_type` — scores grouped by task type

---

*Integration audit: 2026-04-26*
