---
tags: [decision, scoring, weights, evaluation]
date: 2026-04-26
---

# All Scoring Weights Are Equal at 0.20

## Decision
`WEIGHTS = {"N": 0.20, "M": 0.20, "C": 0.20, "A": 0.20, "R": 0.20}`

Each of the five components (Numerical, Method, Assumption, Confidence, Reasoning) contributes equally to the final score.

## Why
- Avoids arbitrary prioritization of one research question over another
- Each component maps directly to one RQ (N→RQ1, M→RQ2, A→RQ3, C→RQ5, R→RQ2)
- Equal weighting is the defensible default for a capstone benchmark without domain-expert calibration data
- Previously some weights (C, R) were 0.00 — updated to 0.20 when confidence calibration (RQ5) and reasoning quality were implemented

## How to Apply
- When changing weights: update **both** files — see [[scoring-weights-must-be-updated-in-two-files]]
- Current state: reconciled and identical in both `llm_runner/response_parser.py` and `evaluation/metrics.py`
- Cross-reference comment in both files: `# Scoring weights must match [other file] — see CLAUDE.md §7`

## Current Weight History
| Component | Old Weight | Current Weight | Change |
|-----------|-----------|----------------|--------|
| N (Numerical) | 0.60 | 0.20 | ↓ reduced |
| M (Method) | 0.20 | 0.20 | unchanged |
| A (Assumption) | 0.20 | 0.20 | unchanged |
| C (Confidence) | 0.00 | 0.20 | ↑ activated |
| R (Reasoning) | 0.00 | 0.20 | ↑ activated |

Old scores in `runs.jsonl` were backfilled via `scripts/recompute_scores.py`.

---

## Update — 2026-05-02

Phase 1B introduced an additional **post-hoc literature-derived weighting**
in `scripts/recompute_nmacr.py` that produced a different aggregate score
for analysis purposes. At that point the two paths coexisted by design.

---

## RESOLVED — 2026-05-03 (Approach A)

This decision is **superseded**. Equal weighting is no longer canonical.

The literature-derived NMACR scheme (A=0.30, R=0.25, M=0.20, C=0.15, N=0.10)
is now the **sole canonical scheme** and is applied at runtime in both
`evaluation/metrics.py` and `llm_runner/response_parser.py`.

Approach A (2026-05-03) consolidated the dual-path design: runtime
aggregation now uses the same literature-derived weights that
`scripts/recompute_nmacr.py` had been producing post-hoc. Verification
confirmed byte-identical regeneration of all canonical surfaces
(`bootstrap_ci.json`, `robustness_v2.json`, `nmacr_scores_v2.jsonl`).

The post-hoc script is preserved at
`llm-stats-vault/90-archive/superseded_scripts/recompute_nmacr.py` as a
regression-test reference. See:
- [`audit/aggregation_locus.md`](../../../audit/aggregation_locus.md) — single canonical path
- [`audit/recompute_log.md`](../../../audit/recompute_log.md) §"Phase 1.6 — Approach A"
- [`audit/methodology_continuity.md`](../../../audit/methodology_continuity.md) §"NMACR weighting"

This note is preserved in place (rather than archived) so future readers
see the historical decision and its resolution in one location.

