---
tags: [pattern, scoring, weights, sync, critical]
date: 2026-04-26
---

# Scoring Weights Must Be Updated in Two Files

## The Pattern
The benchmark has two scoring implementations that must stay in sync. When changing scoring weights, **always update both files simultaneously**:

1. `llm_runner/response_parser.py` — Path A (live runner)
2. `evaluation/metrics.py` — Path B (formal evaluation)

Both files contain the same NMACR weights (literature-derived, sole
canonical scheme since Approach A 2026-05-03):
```python
# evaluation/metrics.py
NMACR_WEIGHTS = {"A": 0.30, "R": 0.25, "M": 0.20, "C": 0.15, "N": 0.10}

# llm_runner/response_parser.py
W_N = 0.10  # Numerical Accuracy
W_M = 0.20  # Method Structure
W_A = 0.30  # Assumption Compliance
W_C = 0.15  # Confidence Calibration
W_R = 0.25  # Reasoning Quality
```

## How to Verify Sync
Both files have a cross-reference comment:
- In `response_parser.py`: `# Scoring weights must match evaluation/metrics.py — see CLAUDE.md §7`
- In `metrics.py`: `# Scoring weights must match llm_runner/response_parser.py — see CLAUDE.md §7`

## Why This Is a Risk
If weights diverge:
- Live runs (Path A) produce different scores than post-hoc analysis (Path B)
- `runs.jsonl` contains Path A scores; `results.json` uses Path B
- The two data sources will disagree, corrupting all comparative analysis

## What Happened Before (History)
- C and R weights were 0.00 in both files before confidence calibration was implemented
- N was previously 0.60 — reduced to 0.20 when C and R were activated
- All scoring weights were equal at 0.20 each from 2026-04-26 to 2026-05-03
- Approach A (2026-05-03) migrated runtime weights to the literature-derived
  scheme that Phase 1B (2026-05-01) had been applying post-hoc; verified
  byte-identical regeneration of canonical surfaces. See
  [audit/recompute_log.md §"Phase 1.6 — Approach A"](../../../audit/recompute_log.md)
- All existing runs were backfilled via `scripts/recompute_scores.py`

## How to Apply
1. Change WEIGHTS in `evaluation/metrics.py`
2. Change the same values in `llm_runner/response_parser.py`
3. Run `scripts/recompute_scores.py` to backfill existing runs.jsonl records
4. Re-run `python -m experiments.run_benchmark` to refresh results.json

## Related
- [[dual-scoring-paths-exist-for-separation-of-concerns]] — why two paths exist
- [[scoring-pipeline]] — full weight details
- [[all-scoring-weights-are-equal-at-0.20]] — the current decision
