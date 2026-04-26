---
tags: [priorities, planning, roadmap]
date: 2026-04-26
---

# Current Priorities

## Status: Benchmark Complete ✅

All 855 Phase1+2 runs + 375 synthetic runs complete. Results scored. R report rendered. Docs updated.

---

## Open Items (Paper-Blocking)

> Error taxonomy ✅ closed 2026-04-26. See [[2026-04-26-error-taxonomy-pipeline]].

### 1. Error Taxonomy Analysis ✅ DONE (2026-04-26)
Proposal abstract promises "a systematic error taxonomy for LLM statistical reasoning."  
`evaluation/error_taxonomy.py` exists as dataclass stub only — no analysis pipeline.

**What's needed:**
- Script `scripts/analyze_errors.py` — auto-tag failed runs using `runs.jsonl` heuristics
- Heuristics: `numeric_score=0` → `MATHEMATICAL`; `structure_score<0.3` → `METHOD_SELECTION`; `assumption_score=0` → `ASSUMPTION`; LLM response contains "I cannot" → `HALLUCINATION`
- Output: `experiments/results_v1/error_taxonomy.json` with per-model error type counts
- Add section to master report + website results panel

See [[proposal-gap-error-taxonomy-analysis-missing]].

### 2. User Study ❌ (from proposal — "small-scale user study")
Proposal says: "A small-scale user study with statistics students will assess practical usefulness and trust alignment."  
Timeline: "Early Apr – Mid Apr: Extended benchmarking; robustness analysis; user study."

**What's needed:**
- Survey instrument (Google Form or similar): 5–10 stats students, 3–5 tasks each
- Students attempt tasks → record answers + confidence → compare to LLM outputs
- Metrics: usefulness rating, trust alignment score, error overlap with LLM failures
- Output: user_study_results.json, section in paper §5

Risk: recruitment may be infeasible post-semester. Document as "future work" if so.  
See [[proposal-gap-user-study-not-implemented]].

---

## Phase 3 — New Benchmark Concepts (Important for paper)

### 3. New Task Types (Optional expansion)
Current: 38 types (31 Phase1 + 7 Phase2). Proposal doesn't require expansion — Phase2 already exceeded scope.

Candidates (if time permits):
- Kalman filter (state estimation)
- EM algorithm (mixture models)
- Laplace approximation (posterior approximation)
- Copulas (dependency modeling)
- Extreme value theory

Pattern: [[adding-a-new-task-type-requires-4-changes]].

---

## Phase 4 — Visualization Quality

### 4. Audit Existing Visualizations
15 PNGs + 14 interactive HTMLs exist. Not all directly answer RQ1–RQ5.

**Audit needed:** Map each viz to which RQ it answers. Flag weakest.  
**Potential new charts:**
- RQ3: assumption compliance heatmap by model × task_type
- RQ5: calibration scatter (confidence vs. correctness per model)
- RQ4: perturbation sensitivity by type (rephrase vs. numerical vs. semantic) — cleaner version

---

## Phase 5 — Paper Writing

### 5. Final Report / Paper
Key sections:
- Abstract ← draft from proposal (update with results)
- §2 Methodology ← scoring pipeline, prompting (CoT/PoT/few-shot), LLM-as-Judge
- §3 Results ← RQ1–RQ4 quantitative results (RQ5 calibration pending full analysis)
- §4 Error Analysis ← error taxonomy (pending)
- §5 User Study ← (if conducted) or "future work"
- §6 Discussion ← implications for LLM reliability in statistics
- References ← [[literature/papers_bibliography.md]] — 5 papers already documented

---

## 5-Phase Roadmap Summary (Updated)

| Phase | Deliverable | Status |
|-------|------------|--------|
| 1 | 855-run results.json (all 5 models) | ✅ Complete |
| 2 | 375 synthetic runs + RQ4 analysis | ✅ Complete |
| 3 | New task types benchmarked | ⏳ Optional |
| 4 | Viz audit + RQ-aligned improvements | ⏳ Pending |
| 5 | Error taxonomy + user study + paper | ❌ In progress |
