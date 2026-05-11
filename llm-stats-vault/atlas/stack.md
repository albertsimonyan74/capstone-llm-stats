---
tags: [atlas, stack, dependencies, runtime]
date: 2026-04-26
---

# Technology Stack

## Python (Backend + Runner)
- **Python 3.11** — runtime via `.venv/`
- **FastAPI** — REST API for website backend (port 8000)
- **httpx** — all 5 LLM API clients (no vendor SDKs — see [[httpx-used-directly-no-vendor-sdks]])
- **anthropic** — used only by `code/analysis/llm_judge.py` + `code/analysis/task_validator.py`
  - Not in venv by default — `pip install anthropic` if missing (see [[anthropic-module-not-in-venv]])
- **numpy / scipy** — Bayesian baseline ground-truth computations
- **FastMCP** — MCP server framework (`code/capstone_mcp/server.py`)
- **ruff** — linting (`ruff check .`)
- **pytest** — testing (53 tests: 24 frequentist + 29 MCP)

## Frontend
- **React 19** + **Vite 8** + **Node 25**
- No state management library — `useState` / `useEffect` only
- Custom portal tooltip system: `TooltipPortal.jsx` + `ParamTooltip.jsx`
- Cursor: vanilla JS IIFE in `index.html` (removed from React due to stacking context issues)
- See [[css-filter-stacking-context-breaks-fixed-modals]] for why modals are siblings not children

## R Pipeline
- **R 4.3.2**
- **ggplot2** — static PNG charts (scripts 01–15)
- **plotly** — interactive HTML charts (scripts 08–14)
- **ggridges** — density/ridgeline plots (script 03)
- **gganimate** — bar race GIF animation (script 15)
- **rmarkdown** — master report (`benchmark_report.html`, 9.3 MB)
- **gt** — publication-quality table (script 06)
- Run: `cd code/visualization && Rscript run_all.R`

## Model Endpoints

| Family | Model String | Endpoint |
|--------|-------------|----------|
| `claude` | `claude-sonnet-4-5` | `api.anthropic.com/v1/messages` |
| `gemini` | `gemini-2.5-flash` | `generativelanguage.googleapis.com/v1beta` |
| `chatgpt` | `gpt-4.1` | `api.openai.com/v1/chat/completions` |
| `deepseek` | `deepseek-chat` | `api.deepseek.com/v1/chat/completions` |
| `mistral` | `mistral-large-latest` | `api.mistral.ai/v1/chat/completions` |

DeepSeek and Mistral use OpenAI-compatible API format.

## API Client Settings (all models)
- `_MAX_TOKENS = 1024`
- `_TIMEOUT = 60.0s`
- `_SLEEP_S = 1.0s` between requests
- Retry waits: `[5, 15, 30]` seconds (3 attempts total)
- Non-retryable status codes: 400, 401, 403, 404

## Gemini-Specific Overrides
- `_GEMINI_RETRY_WAITS = [10, 20, 40, 80, 160]` — 5 retries, exponential
- `_GEMINI_SLEEP_S = 3.0s` default (pass `--delay 5` for 5s to be safe on free tier)
- Free tier limit: ~250 RPD (requests per day)
- See [[gemini-api-has-free-tier-rate-limits]] and [[gemini-daily-quota-exhausted-on-2026-04-24]]

## Environment Setup
```bash
cp .env.example .env   # fill in API keys
source .venv/bin/activate
```
Required env vars: `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `MISTRAL_API_KEY`

Missing key → error record logged, no exception thrown.
