# Aggregation Locus — where NMACR weights live

## Single canonical path (post Approach A, 2026-05-03)

NMACR aggregation is one operation, performed against literature-derived
weights, with the canonical constants duplicated across two consumer
files (per CLAUDE.md §7). Per-dimension extraction lives in
`llm_runner/response_parser.py`; aggregation uses the same weights in
both the live runner and the post-hoc evaluator.

### Locked weights (literature-derived)
```
A 0.30   ← Du 2025, Boye & Moell 2025, Yamauchi 2025
R 0.25   ← Yamauchi 2025, Boye & Moell 2025, ReasonBench 2025
M 0.20   ← Wei 2022, Chen 2022, Bishop 2006
C 0.15   ← Nagarkar 2026, FermiEval 2025, Multi-Answer 2026
N 0.10   ← Liu 2025, Boye & Moell 2025
```
Sum = 1.00. See [`audit/methodology_continuity.md`](methodology_continuity.md)
§"NMACR weighting" for the full literature defense.

### Runtime aggregation — live runner
[llm_runner/response_parser.py:24-29](llm_runner/response_parser.py#L24-L29)

```python
W_N = 0.10  # Numerical Accuracy
W_M = 0.20  # Method Structure
W_A = 0.30  # Assumption Compliance
W_C = 0.15  # Confidence Calibration
W_R = 0.25  # Reasoning Quality
```

Used by `full_score()` at [llm_runner/response_parser.py:435](llm_runner/response_parser.py#L435).
Combines with the `0.6·numeric + 0.4·rubric` blend for numeric+rubric
tasks; CONCEPTUAL tasks score on rubric only.

### Post-hoc aggregation — formal evaluator
[evaluation/metrics.py:38-46](evaluation/metrics.py#L38-L46)

```python
NMACR_WEIGHTS: Dict[str, float] = {
    "A": 0.30,
    "R": 0.25,
    "M": 0.20,
    "C": 0.15,
    "N": 0.10,
}
WEIGHTING_SCHEME = "literature_v1"
WEIGHTS = NMACR_WEIGHTS  # backwards-compat alias
```

Applied at [evaluation/metrics.py:185-191](evaluation/metrics.py#L185-L191):
```python
NMACR_WEIGHTS["N"] * cs.N + NMACR_WEIGHTS["M"] * cs.M
+ NMACR_WEIGHTS["C"] * cs.C + NMACR_WEIGHTS["A"] * cs.A
+ NMACR_WEIGHTS["R"] * cs.R
```

### Downstream consumer
[scripts/recompute_scores.py](../scripts/recompute_scores.py) — wraps the
live `full_score()` to recompute `runs.jsonl` from stored `raw_response`.
No NMACR knobs of its own.

## Stored per-run scores
- [experiments/results_v1/runs.jsonl](../experiments/results_v1/runs.jsonl)
  — fields `numeric_score`, `structure_score`, `assumption_score`,
  `confidence_score`, `reasoning_score`, `final_score`. 1230 records.
  `final_score` is literature-weighted post-Approach-A; pre-Approach-A
  records were equal-weighted (a regenerator pass via
  `scripts/recompute_scores.py` would normalise the historical values).
- [experiments/results_v2/perturbation_runs.jsonl](../experiments/results_v2/perturbation_runs.jsonl)
  — same schema, 2365 records.
- [experiments/results_v2/llm_judge_scores_full.jsonl](../experiments/results_v2/llm_judge_scores_full.jsonl)
  — judge dimensions `method_structure.score`, `assumption_compliance.score`,
  `reasoning_quality.score`, `reasoning_completeness.score`. 1230 records.
  Judge does NOT score N or C — keyword path remains canonical for those.
- [experiments/results_v2/nmacr_scores_v2.jsonl](../experiments/results_v2/nmacr_scores_v2.jsonl)
  — literature-weighted aggregate per run; 3595 records (1230 base +
  2365 perturbation). The single source of truth for downstream analyses
  (bootstrap CI, robustness, per-dim calibration).

## Historical note — pre-Approach-A dual-path design
Before 2026-05-03, runtime scoring used equal weights (0.20 each) and
the literature-weighted aggregate was produced post-hoc by
`scripts/recompute_nmacr.py`. That script is preserved at
`llm-stats-vault/90-archive/superseded_scripts/recompute_nmacr.py` as a
regression-test reference. Approach A consolidated both paths to use
literature weights at the source. See
[`audit/recompute_log.md`](recompute_log.md) §"Phase 1.6 — Approach A".

## Out-of-scope file (untouched per task constraint)
- [evaluation/llm_judge.py](../evaluation/llm_judge.py)
- [evaluation/llm_judge_rubric.py](../evaluation/llm_judge_rubric.py)
