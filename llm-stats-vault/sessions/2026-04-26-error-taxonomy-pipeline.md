---
tags: [session, log, error-taxonomy, analysis, pipeline, proposal-gap]
date: 2026-04-26
---

# Session Log: Error Taxonomy Analysis Pipeline

## Date
2026-04-26

## Context
This session closed the paper-blocking proposal gap: "systematic error taxonomy for LLM statistical reasoning" (from abstract). Also updated vault from stale state (Gemini incomplete → all complete).

## What Was Accomplished

### 1. Vault Update (stale → current)
- `index.md`: run status updated to all 5 models complete (1230 records)
- `current-priorities.md`: Phase 1/2/5 complete; new priorities = error taxonomy + user study + paper
- Created [[proposal-gap-user-study-not-implemented]] — knowledge note
- Created [[proposal-gap-error-taxonomy-analysis-missing]] — knowledge note

### 2. Proposal Cross-Reference (from PDF)
Confirmed two unimplemented deliverables from proposal abstract:
- "systematic error taxonomy" → **now implemented**
- "small-scale user study (n=5-10 statistics students)" → **deferred to future work**

All other proposal items confirmed complete:
- RQ1-5 ✅, CoT/PoT/Few-shot ✅, LLM-as-Judge ✅, TaskValidator ✅, Bibliography ✅

### 3. scripts/analyze_errors.py (NEW)
Hybrid rule-based + LLM-as-Judge error tagging pipeline.

**8 error categories (E1-E9):**
| Code | Name | Count |
|------|------|-------|
| E3 | Assumption Violation | 119 |
| E7 | Truncation (token limit) | 93 |
| E5 | Overconfidence | 85 |
| E6 | Conceptual Confusion | 56 |
| E2 | Method Selection | 18 |
| E4 | Format Failure | 15 |
| E8 | Hallucination | (LLM-tagged ambiguous) |
| E9 | Unclassified | 1 |

Total: 143 failed runs / 855 benchmark runs = 16.7% failure rate

**Critical bug fixed:** `float(0.0 or 1.0) = 1.0` — `or 1.0` fallback incorrectly overrode zero assumption scores. Fixed with `_f(val)` helper that checks `is not None` instead of truthiness.

**LLM usage:** Used for E8/E9/isolated-E3 cases only (1-50 calls max). Avoids over-relying on expensive calls.

Output: `data/error_taxonomy_results.json`

### 4. report_materials/r_analysis/16_error_taxonomy.R (NEW)
3 visualizations:
- `16a_error_distribution.png` — bar chart, all error types by count
- `16b_error_by_model_heatmap.png` — model × error type heatmap
- `16c_error_by_task_type.png` — top 12 task types stacked by error category

Added to `run_all.R` registry (now 16 scripts, was 15).

### 5. 08_master_report.Rmd (MODIFIED)
Two new sections added:
- `# Error Taxonomy Analysis` — 8-category table, kable summary, 3 figures, key findings
- `# Limitations and Future Work` — E7 token limit fix advice, user study future work, Phase 3 scope

Re-rendered successfully: `benchmark_report.html` (9.4 MB).

### 6. Website Updated
- `visualizations.js`: 3 new viz cards in new "Error Analysis" filter tab (18 total categories now)
- 3 PNGs copied to `capstone-website/frontend/public/visualizations/png/`

### 7. CLAUDE.md Updated
- `scripts/analyze_errors.py` added to §2 How to Run Things
- `data/error_taxonomy_results.json` added to §3 Architecture Map
- IMPORTANT section: error taxonomy marked ✅ with findings
- R pipeline: updated to "18 scripts (00-16 + Rmd)"

## Errors and Fixes

| Error | Root Cause | Fix |
|-------|-----------|-----|
| E3 never appears in distribution | `float(0.0 or 1.0) = 1.0` — `or 1.0` fallback is falsy-based | Replaced with `_f(val)` checking `val is not None` |
| Unused imports `os`, `sys` | Copy-paste from prior template | Removed |

## Git Commit
`4069e36` — `feat: complete error taxonomy analysis pipeline` (18 files changed)

## Key Findings (for paper §4)
1. **E7 Truncation dominates mechanically** — 93 failures from hitting 1024-token cap. REGRESSION and BAYES_REG (multi-output tasks) always exceed limit. Fix: set `max_tokens=2048` for tasks with ≥4 numeric targets.
2. **E3 Assumption Violation most common semantically** — 119 cases across all models. Models proceed without stating iid, conjugacy, or distributional assumptions.
3. **Claude most reliable** (19/171 failures = 11%). ChatGPT worst (38/171 = 22%).
4. **Gemini has disproportionate E4 Format Failures** (6/24 failures) — formatting inconsistency not seen in other models.

## Remaining Open Items (Priority Order)
1. Paper draft — §4 Error Analysis now has data; §3 Results ready; §2 Methodology complete
2. User study — recruit or mark future work formally in paper (already in Rmd)
3. Viz audit — map 18 PNGs to RQs, replace weakest
4. Phase 3 new task types — optional, beyond proposal scope
