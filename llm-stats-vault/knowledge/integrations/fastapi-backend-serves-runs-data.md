---
tags: [integration, fastapi, backend, api]
date: 2026-04-26
---

# FastAPI Backend Serves Runs Data

## Connection Details
- **File**: `capstone-website/backend/main.py`
- **Framework**: FastAPI
- **Port**: 8000
- **Start**: `cd capstone-website && uvicorn backend.main:app --reload`

## What It Serves
- Reads `data/processed_data/results_v1/runs.jsonl` directly
- Provides endpoints consumed by the React frontend
- Also serves data for the leaderboard and task browser

## Notes
- Backend must be running separately from the frontend (port 8000)
- Frontend Vite dev server runs on port 3000
- CORS configured for local development
- `runs.jsonl` schema is heterogeneous — backend must handle old placeholder record

## Related
- [[react-frontend-uses-vite]] — frontend that consumes this backend
- [[runs-jsonl-is-append-only]] — the file this backend reads
