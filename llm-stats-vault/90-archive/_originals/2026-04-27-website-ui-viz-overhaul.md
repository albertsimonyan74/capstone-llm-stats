---
tags: [session, website, ui, visualizations]
date: 2026-04-27
---

# Session: Website UI + Visualization Overhaul

## What Was Done

### 1. Emoji Removal (App.jsx)
Replaced all emoji icons site-wide with monoline SVG icons:
- **Pipeline steps** (6): grid, chat bubble, triangle-nodes, bar chart, refresh arrows, crosshair magnifier
- **About findings** (4): podium/rank, downtrend, warning triangle, shuffle arrows
- Removed `✅` from RQS status string

### 2. TierLadder Redesign (App.jsx)
Complete rebuild of the difficulty ladder component:
- Proportional scale bar at top showing all 4 tiers by task count
- Tier badges now have 4-dot difficulty indicators
- Animated progress bar per row
- Expanded panel now shows: detail text + KEY CHALLENGES (3 bullets per tier) + TASK TYPES chips (tier-specific, accurate)
- Old bug: expanded section showed first 3 items from TASK_TYPE_TOOLTIPS for every tier (same 3 always) — fixed with `TIER_TASK_EXAMPLES` const

### 3. Benchmark Visualizations Overhaul (visualizations.js + VizGallery.jsx)

**Removed 5 vizs** (redundant/too technical for ordinary users):
- `model_table` — table as static image is not useful; leaderboard covers it
- `ecdf` — jargon-heavy (ECDF)
- `correlation` — technical, redundant
- `treemap` — redundant with tier ladder info
- `difficulty_scatter` — redundant with difficulty_line

**Featured 2×2 grid** (KEY VISUALIZATIONS section above gallery):
1. Performance Heatmap (`01_model_heatmap`)
2. Score Distributions (`03_distributions`)
3. Tier Breakdown → `pass_rate` (`13_pass_rate`)
4. Best & Worst Task Types → `failure_analysis` (`05_failure_analysis`)

**All descriptions/insights rewritten** in plain language for ordinary users.

**Fixed broken "Open Interactive" button** for error taxonomy cards (`interactive: null`) — was calling `window.open(null, '_blank')`. Now shows dimmed "Static only" placeholder.

**Added `FEATURED_IDS` export** to visualizations.js.

### 4. Removed Results Section
- Deleted `<Results/>` and its `<SectionDivider/>` from App.jsx
- Removed "Results" nav link from Navbar.jsx
- The 4 tabbed vizs (Heatmap, Distribution, Tier Breakdown, Best/Worst) in ResultsSection.jsx were redundant with VizGallery

Nav order now: Overview → How It Works → Models → Tasks → Visualizations → About

### 5. Fixed Gemini Missing from Featured Viz PNGs

Root cause: 3 R scripts hardcoded 4-model factor levels and "Gemini excluded" subtitles even after Gemini completed on 2026-04-26.

Fixed scripts:
- `01_model_heatmap.R`: factor levels + subtitle + caption + `models_ordered`
- `03_distributions.R`: factor levels (ridges + plotly) + caption + `models_ord`
- `05_failure_analysis.R`: factor levels (Panel B) + caption + plotly PALETTE slice

Regenerated PNGs/HTMLs and copied to `capstone-website/frontend/public/visualizations/`.
`13_pass_rate.R` already included Gemini — no change needed.

## Key Files Changed
- `capstone-website/frontend/src/App.jsx` — emoji→SVG, TierLadder rebuild, removed Results section
- `capstone-website/frontend/src/components/Navbar.jsx` — removed "Results" entry
- `capstone-website/frontend/src/data/visualizations.js` — 18→12 vizs, featured IDs, plain descriptions
- `capstone-website/frontend/src/pages/VizGallery.jsx` — featured strip, null interactive fix, description on all cards
- `report_materials/r_analysis/01_model_heatmap.R` — Gemini fix
- `report_materials/r_analysis/03_distributions.R` — Gemini fix
- `report_materials/r_analysis/05_failure_analysis.R` — Gemini fix

## Build Status
`npm run build` passes clean.
