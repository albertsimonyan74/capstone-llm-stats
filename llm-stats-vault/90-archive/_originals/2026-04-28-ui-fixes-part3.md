---
tags: [session, website, fixes, ui]
date: 2026-04-28
commit: 2f6fdf0
---

# Session: UI Fixes Part 3 (2026-04-28c)

## Tasks Completed ✅

### 1. Model Token Display — Verified & Enhanced
- Confirmed: Gemini client hardcodes `maxOutputTokens: 4096` (NOT `_MAX_TOKENS=1024` like others)
- Confirmed from runs.jsonl: Gemini avg=1729, max=4096 — all others avg~700-811, max=1024
- Updated MODELS array: added `avgOutputTokens` field for all 5 models from actual runs
- Updated model detail panel: renamed "MAX TOKENS" → "TOKEN LIMIT (BENCHMARK)" + added "AVG OUTPUT TOKENS" row
- Added note to Gemini strengths explaining it used 4096 cap (not 1024) — only model with different limit

### 2. Tier Difficulty Ladder — Font Size Fix
- Detail description text: `fontSize: 13` → `fontSize: 15`, `lineHeight: 1.8`
- KEY CHALLENGES label: `fontSize: 9` → `fontSize: 10`
- Challenge items: `fontSize: 10` → `fontSize: 12`
- TASK TYPES label: `fontSize: 9` → `fontSize: 10`
- Task type badges: `fontSize: 9` → `fontSize: 10`

### 3. Benchmark Viz Buttons — Fixed
**Root cause: Vercel `cleanUrls: true` (default) strips `.html` extension → 404 → catch-all serves `index.html` (React SPA) instead of the Plotly interactive.**
- Fix: added `"cleanUrls": false` to `vercel.json`

**GIF animation "Animated visualization" text — no actual GIF:**
- Root cause: img shows alt text while loading; no loading feedback
- Fix: added `gifLoading` + `gifError` states, loading spinner (CSS spin animation), `onLoad`/`onError` handlers, opacity 0→1 transition on load, error message with file path

### 4. Answer Divergence Tolerance — Fixed
- Old: string normalization with `.toFixed(2)` — fails near x.xx5 boundary (0.001 diff → different string)
- New: `extractFirstNum()` parses first float from answer string; `clusterNumeric()` sorts + chains groups where consecutive diff ≤ `NUMERIC_TOLERANCE = 0.005`; falls back to string normalization for non-numeric answers
- Models within 0.005 of each other now correctly show as consensus

### 5. Vote Storage Clarification
- Added info bar below AggregateStats in UserStudy section:
  - `backend/data/user_study_results.json` — JSON array, one record per vote
  - `backend/data/vote_memory.json` — aggregated stats for research paper

## Deployment
- Commit: `2f6fdf0`
- Pushed to `main` → Vercel (frontend) and Render (backend) auto-deploying
- No backend code changed this session

## Notes
- Vote data is ephemeral on Render free tier — export `user_study_results.json` before redeploy
- Interactive HTML files exist in `public/visualizations/interactive/` — verified sizes 6K-231K — all committed and present in dist
