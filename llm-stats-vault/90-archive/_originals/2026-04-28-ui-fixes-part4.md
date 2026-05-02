---
tags: [session, website, fixes, ui, vote-persistence]
date: 2026-04-28
---

# Session: UI Fixes Part 4 (2026-04-28d)

## Tasks Completed ✅

### 1. Tier Difficulty Ladder — Text Even Bigger
- Detail text: `fontSize:15` → `fontSize:17`, `lineHeight:1.8` → `lineHeight:1.85`, margin bump
- KEY CHALLENGES label: `fontSize:10` → `fontSize:11`, marginBottom 6→8
- Challenge items: `fontSize:12` → `fontSize:14`
- TASK TYPES label: `fontSize:10` → `fontSize:11`, marginBottom 6→8
- Task badges: `fontSize:10` → `fontSize:11`, padding bump

### 2. Model Output Layout — Full-Width Stacked
- Response grid: `display:grid, gridTemplateColumns: repeat(auto-fill, minmax(300px, 1fr))`
  → `display:flex, flexDirection:column`
- Each model box now full-width, stacked vertically

### 3. "Open Interactive" + "View Animation" — Fixed (root cause: files not in git)
- Interactive HTML files (14) and `_files/` dirs were excluded by root `.gitignore` (`interactive/` rule)
- GIF was excluded by `**/*.gif` rule
- Fix: Added negation exceptions to `.gitignore`:
  ```
  !capstone-website/frontend/public/visualizations/interactive/
  !capstone-website/frontend/public/visualizations/interactive/**
  !capstone-website/frontend/public/visualizations/png/15_bar_race.gif
  ```
- Committed all files (~56MB) so Vercel can serve them

### 4. Vote Storage Info Bar — Removed
- Removed the "💾 VOTES SAVED TO backend/data/..." dev-info div from UserStudy.jsx
- Was added as debugging info last session, not intended for production

### 5. Vote Persistence — Supabase Integration
- Root cause: Render free tier ephemeral filesystem → votes lost on redeploy
- Added optional Supabase PostgreSQL integration to `backend/user_study.py`:
  - `SUPABASE_URL` + `SUPABASE_KEY` env vars → USE_SUPABASE=True
  - `_supabase_insert(table, record)` — async httpx POST
  - `_supabase_fetch_all(table)` — async httpx GET, ordered by id
  - `/api/user-study/vote` → inserts to both `votes` and `questions` tables via Supabase
  - `/api/user-study/results` → fetches live from Supabase when configured
  - Falls back to file-based storage when env vars absent
- No new Python packages needed (uses httpx already present)

**To activate:** Create free project at supabase.com, run this SQL:
```sql
CREATE TABLE votes (id BIGSERIAL PRIMARY KEY, data JSONB NOT NULL, created_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE questions (id BIGSERIAL PRIMARY KEY, data JSONB NOT NULL, created_at TIMESTAMPTZ DEFAULT NOW());
```
Then set `SUPABASE_URL` and `SUPABASE_KEY` in Render environment variables.

## Deployment
- Files committed to main
- Vercel auto-deploys (frontend changes + interactive HTML files now tracked)
- Render auto-deploys (backend user_study.py with Supabase support)
- Vote persistence requires manual Supabase setup (see above)

## Notes
- Interactive HTML files total ~56MB but all individual files < 5MB — within GitHub limits
- `_files/` dirs contain plotly-main-2.11.1 (~4MB each) × 14 HTMLs = most of the 56MB
- Supabase free tier: 500MB DB, unlimited API calls, no time limit
