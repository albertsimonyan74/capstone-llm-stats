---
tags: [session, user-study, deployment, vercel, render]
date: 2026-04-27
---

# Session: User Study + Production Deployment

## What Was Done

### 1. User Study — Backend (user_study.py)
Created `capstone-website/backend/user_study.py`:
- 5 async httpx callers (`call_claude`, `call_gpt4`, `call_gemini`, `call_deepseek`, `call_mistral`)
- All use raw httpx — no vendor SDKs (consistent with existing `llm_runner/model_clients.py`)
- Vision support: Claude, GPT-4.1, Gemini accept base64 images; DeepSeek + Mistral return early with `vision_not_supported`
- `asyncio.gather` for parallel execution
- In-memory rate limiter: 10 req/hr per IP (`_rate_store` dict)
- Vote persistence: `backend/data/user_study_results.json` (append-only)
- 3 endpoints: `POST /api/user-study`, `POST /api/user-study/vote`, `GET /api/user-study/results`
- SYSTEM_PROMPT: Bayesian stats expert, educational, graduate-level

### 2. User Study — Frontend (UserStudy.jsx)
Created `capstone-website/frontend/src/pages/UserStudy.jsx`:
- Textarea input + image attach with preview (file input hidden, triggered by button)
- `VITE_API_URL` env var for API base (empty string = relative path in prod)
- 5 skeleton loading cards during fetch (pulse animation)
- 5 ResponseCard components: model color, initials badge, latency, scrollable response text
- Text-only indicator for DeepSeek/Mistral when image attached
- VotePanel: click model button → select winner → optional reason textarea → submit
- AggregateStats: lazy-loaded CSS bar chart from `GET /api/user-study/results`
- Wired into App.jsx between Visualizations and About; `{ id: 'user-study', label: 'User Study' }` in Navbar

### 3. Backend Integration Fixes
- `main.py`: `from user_study import router` → try `backend.user_study` first, fallback to `user_study`
- CORS: `FRONTEND_URL` env var; falls back to `["*"]` when unset (avoids `allow_credentials + *` conflict)
- `BASE_DIR`: reads `DATA_ROOT` env var; falls back to `Path(__file__).parent.parent.parent` (project root for local dev)
- Added `GET /` health-check route
- Dropped unused `Query` import

### 4. Production Deployment — Render (backend)
- `backend/render.yaml` created with 5 API key env var slots + FRONTEND_URL
- `backend/Dockerfile` fixed:
  - Was: `COPY main.py .` only → `user_study.py` absent in container
  - Fixed: `COPY main.py user_study.py ./`
  - Added: `COPY static_data/ ./static_data/` + `ENV DATA_ROOT=/app/static_data`
- `backend/static_data/` bundled: `tasks_all.json` (184K) + `runs.jsonl` (4.4M)
- `.gitignore` exception: `!capstone-website/backend/static_data/**` to un-ignore runs.jsonl
- Root `BASE_DIR` resolved to `/` in Docker (3 parent levels from `/app/main.py`) → fixed with DATA_ROOT

### 5. Production Deployment — Vercel (frontend)
- `frontend/vercel.json`: rewrites `/api/(.*)` → `https://capstone-llm-stats.onrender.com/api/$1`
- `frontend/UserStudy.jsx`: `API_BASE = import.meta.env.VITE_API_URL || ''`
- `VITE_API_URL` set in Vercel env (not sensitive — it's a public URL)
- Deployed via `npx vercel --prod` after `vercel login`

## Production URLs
- **Frontend:** https://capstone-llm-stats.vercel.app
- **Backend:** https://capstone-llm-stats.onrender.com
- Both verified: `/api/status` → 200, 171 tasks, 1230 runs

## Known Behavior
- Render free tier cold-start: ~30s delay after 15 min idle
- User Study votes stored in Render container's `data/user_study_results.json` — ephemeral (reset on redeploy)
- VITE_API_URL baked at build time by Vite (not runtime-configurable)

## Key Files Changed
- `capstone-website/backend/user_study.py` — NEW
- `capstone-website/backend/main.py` — router, CORS, DATA_ROOT, root route
- `capstone-website/backend/Dockerfile` — user_study.py + static_data copy
- `capstone-website/backend/render.yaml` — NEW
- `capstone-website/backend/static_data/` — NEW (tasks_all.json + runs.jsonl)
- `capstone-website/frontend/src/pages/UserStudy.jsx` — NEW
- `capstone-website/frontend/src/App.jsx` — UserStudy import + section
- `capstone-website/frontend/src/components/Navbar.jsx` — User Study nav entry
- `capstone-website/frontend/vercel.json` — NEW
- `.gitignore` — static_data exception
