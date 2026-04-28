---
tags: [priorities, planning, roadmap]
date: 2026-04-27
---

# Current Priorities

## Status: Benchmark Complete ✅ · Website Live ✅

All 855 Phase1+2 runs + 375 synthetic runs complete. Results scored. R report rendered. Website deployed.

**Production URLs:**
- Frontend: https://capstone-llm-stats.vercel.app
- Backend: https://capstone-llm-stats.onrender.com

---

## Open Items (Paper-Blocking)

> Error taxonomy ✅ closed 2026-04-26. See [[2026-04-26-error-taxonomy-pipeline]].
> User Study website feature ✅ closed 2026-04-27. See [[2026-04-27-user-study-and-deployment]].

### 1. Error Taxonomy Analysis ✅ DONE (2026-04-26)
See [[proposal-gap-error-taxonomy-analysis-missing]].

### 2. User Study ✅ DONE — live interactive (2026-04-27)
Implemented as interactive website feature (not Google Form):
- Users submit Bayesian stats questions + optional image
- All 5 models respond in parallel (real API calls via httpx)
- User votes for best explanation
- Aggregate vote results displayed (CSS bar chart)
- Live at: https://capstone-llm-stats.vercel.app → scroll to "User Study"
- Vote data stored in Render container (ephemeral — resets on redeploy)

**For paper §5:** Can cite this as "interactive web-based user study" and report vote distribution once data accumulates. Note: votes are ephemeral on Render free tier — export `data/user_study_results.json` before any redeploy if votes need to be preserved.

See [[2026-04-27-user-study-and-deployment]].

---

## Phase 3 — New Benchmark Concepts (Optional)

### 3. New Task Types (Optional expansion)
Current: 38 types (31 Phase1 + 7 Phase2). Proposal doesn't require expansion.

Candidates (if time permits):
- Kalman filter (state estimation)
- EM algorithm (mixture models)
- Laplace approximation (posterior approximation)
- Copulas (dependency modeling)
- Extreme value theory

Pattern: [[adding-a-new-task-type-requires-4-changes]].

---

## Phase 4 — Visualization Quality ✅ DONE (2026-04-27)

### 4. Website Viz Overhaul ✅ DONE (initial)
- Trimmed 18 → 12 visualizations
- Featured 2×2 strip above gallery
- All descriptions plain language
- Fixed Gemini missing from 3 R-generated PNGs
- Removed redundant Results section + navbar entry
- Emoji → monoline SVGs
- TierLadder rebuilt with tier-specific examples and challenges

See [[2026-04-27-website-ui-viz-overhaul]].

### 4b. Website UI Overhaul Part 2 ✅ DONE (2026-04-28)
All 10 items complete. See [[2026-04-28-ui-overhaul-part2]].

Commit 84fa12a pushed → Vercel auto-deploying.

---

## Phase 5 — Paper Writing

### 5. Final Report / Paper
Key sections:
- Abstract ← draft from proposal (update with results)
- §2 Methodology ← scoring pipeline, prompting (CoT/PoT/few-shot), LLM-as-Judge
- §3 Results ← RQ1–RQ4 quantitative results (RQ5 calibration pending full analysis)
- §4 Error Analysis ← error taxonomy (done — E1-E9, 143 failures)
- §5 User Study ← interactive web study live; cite vote distribution from production
- §6 Discussion ← implications for LLM reliability in statistics
- References ← [[literature/papers_bibliography.md]] — 5 papers documented

---

## 5-Phase Roadmap Summary (Updated 2026-04-27)

| Phase | Deliverable | Status |
|-------|------------|--------|
| 1 | 855-run results.json (all 5 models) | ✅ Complete |
| 2 | 375 synthetic runs + RQ4 analysis | ✅ Complete |
| 3 | New task types benchmarked | ⏳ Optional |
| 4 | Viz audit + website deployment | ✅ Complete |
| 5 | Error taxonomy + user study + paper | ⏳ In progress (§5 live, paper remaining) |
