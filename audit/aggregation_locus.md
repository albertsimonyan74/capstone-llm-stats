# Aggregation Locus — where NMACR weights live

## Canonical authoritative implementations (two paths, must stay in sync)

### Path A — live runner
[llm_runner/response_parser.py:24-28](llm_runner/response_parser.py#L24-L28)

```python
W_N = 0.20  # Numerical Accuracy
W_M = 0.20  # Method Structure
W_A = 0.20  # Assumption Compliance
W_C = 0.20  # Confidence Calibration
W_R = 0.20  # Reasoning Quality
```

Used by `full_score()` at [llm_runner/response_parser.py:439](llm_runner/response_parser.py#L439). Combines with the `0.6·numeric + 0.4·rubric` blend for numeric+rubric tasks; CONCEPTUAL tasks score on rubric only.

### Path B — post-hoc analysis
[evaluation/metrics.py:31](evaluation/metrics.py#L31)

```python
WEIGHTS: Dict[str, float] = {"N": 0.20, "M": 0.20, "C": 0.20, "A": 0.20, "R": 0.20}
```

Applied at [evaluation/metrics.py:171-175](evaluation/metrics.py#L171-L175):
```python
WEIGHTS["N"] * cs.N + WEIGHTS["M"] * cs.M + WEIGHTS["C"] * cs.C
+ WEIGHTS["A"] * cs.A + WEIGHTS["R"] * cs.R
```

## Downstream consumer
[scripts/recompute_scores.py](scripts/recompute_scores.py) — wraps Path A (`full_score()`) to recompute v1 `runs.jsonl` from stored `raw_response`. No NMACR knobs of its own.

## Stored per-run scores
- [experiments/results_v1/runs.jsonl](experiments/results_v1/runs.jsonl) — fields `numeric_score`, `structure_score`, `assumption_score`, `confidence_score`, `reasoning_score`, `final_score`. 1230 records.
- [experiments/results_v2/perturbation_runs.jsonl](experiments/results_v2/perturbation_runs.jsonl) — same schema, 2365 records.
- [experiments/results_v2/llm_judge_scores_full.jsonl](experiments/results_v2/llm_judge_scores_full.jsonl) — judge dimensions `method_structure.score`, `assumption_compliance.score`, `reasoning_quality.score`, `reasoning_completeness.score`. 1230 records. Judge does NOT score N or C — keyword path remains canonical for those.

## Decision for Phase 1B
Phase 1B does NOT modify Path A or Path B (they remain at 0.20 each — locked for run-time scoring continuity and v1 reproducibility). Instead, build a new wrapper script `scripts/recompute_nmacr.py` that:
- Reads stored per-dimension scores from runs.jsonl + llm_judge_scores_full.jsonl
- Recomputes aggregate under literature-derived weights `A=0.30 R=0.25 M=0.20 C=0.15 N=0.10`
- Emits `experiments/results_v2/nmacr_scores_v2.jsonl` as the single source of truth for downstream analyses

## Out-of-scope file (untouched per task constraint)
- [evaluation/llm_judge.py](evaluation/llm_judge.py)
- [evaluation/llm_judge_rubric.py](evaluation/llm_judge_rubric.py)
