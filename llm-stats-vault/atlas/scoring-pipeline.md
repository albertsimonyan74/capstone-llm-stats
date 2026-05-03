---
tags: [atlas, scoring, evaluation, weights, metrics]
date: 2026-04-26
---

# Scoring Pipeline

## Single Canonical Scheme — Literature-Derived NMACR

**Critical rule**: [[scoring-weights-must-be-updated-in-two-files]]  
Both paths use the literature-derived NMACR scheme (sole canonical scheme
since Approach A 2026-05-03):

| Dim | Weight | Citations |
|-----|--------|-----------|
| A | 0.30 | Du 2025, Boye & Moell 2025, Yamauchi 2025 |
| R | 0.25 | Yamauchi 2025, Boye & Moell 2025, ReasonBench 2025 |
| M | 0.20 | Wei 2022, Chen 2022, Bishop 2006 |
| C | 0.15 | Nagarkar 2026, FermiEval 2025, Multi-Answer 2026 |
| N | 0.10 | Liu 2025, Boye & Moell 2025 |

Pre-Approach-A history: from 2026-04-26 to 2026-05-03 the runtime paths
used equal weights (0.20 each) and the literature-weighted aggregate
was produced post-hoc by `scripts/recompute_nmacr.py`. Approach A
consolidated to one scheme. See
[audit/aggregation_locus.md](../../audit/aggregation_locus.md).

### Live runner
- File: `llm_runner/response_parser.py`
- Entry: `full_score(raw_response: str, task: dict) -> Dict`
- Called by `run_all_tasks.py` during API runs
- Scores written to each record in `runs.jsonl`

### Formal evaluator (post-hoc on TaskRun objects)
- File: `evaluation/metrics.py`
- Entry: `score_all_models(tasks: Dict[str, TaskSpec], runs: List[TaskRun])`
- Called by `experiments/run_benchmark.py`
- Operates on `TaskRun` dataclass objects (not raw strings)
- Output: `experiments/results_v1/results.json`

## Five Scoring Components

| Component | Key | Weight | Live runner source | Formal evaluator source |
|-----------|-----|--------|--------------------|--------------------------|
| Numerical Accuracy | N | 0.10 | `parse_answer()` extracts floats | `TaskRun.extracted_numbers` |
| Method/Structure | M | 0.20 | structure keyword checks | `TaskRun.structure_flags` |
| Assumption Compliance | A | 0.30 | assumption keyword checks | `TaskRun.assumption_flags` |
| Confidence Calibration | C | 0.15 | `extract_confidence()` | `TaskRun.confidence_calib_score` |
| Reasoning Quality | R | 0.25 | `reasoning_quality_score()` | `TaskRun.reasoning_qual_score` |

## Numerical Scoring Formula

```
for each numeric_target in task:
    abs_err = |predicted - true_value|
    z = max(zero_credit_scale, full_credit_tol)
    if abs_err <= full_credit_tol:  s = 1.0
    else:                           s = 1.0 - (abs_err / z)
    score = clamp(s, 0.0, 1.0)
N_score = mean(all target scores)
```

## Confidence Calibration (C)
`extract_confidence()` parse priority:
1. Explicit `%` or `X/10` notation
2. Linguistic hedges / definitive language
3. Default: 0.5

Penalty rules:
- Overconfident when wrong → penalized **1.5×**
- Underconfident when right → penalized **0.8×**

## Reasoning Quality (R)
Four criteria, each worth 0.25:
1. Shows step-by-step work
2. Identifies the statistical model/distribution
3. States the relevant formula
4. Interprets the final result in context

## Special Scoring Cases
- **CONCEPTUAL tasks** (no numeric targets): `final = 1.0 × rubric_score`
- **Tasks with both numeric + rubric**: `final = 0.6 × numeric + 0.4 × rubric`
- **Pass threshold**: `final_score >= 0.5`

## Tier Multipliers

| Tier | Multiplier | Current Task Count |
|------|-----------|-------------------|
| 1 | 1.0× | 9 |
| 2 | 1.0× | 58 (inc. Phase 2) |
| 3 | 1.0× | 84 (inc. Phase 2) |
| 4 | 1.0× | 20 (inc. Phase 2) |
| 5 | **1.5×** | 0 (stress tier — reserved) |

## LLM-as-Judge Fallback
Triggers in `run_benchmark.py` when:
- `parsed_values = []` (extraction failed → N=0)
- `structure_score < 0.3` (weak structure)

Judge: `evaluation/llm_judge.py` → calls `claude-sonnet-4-6`  
Flag: `--no-judge` disables (faster, less accurate)  
Results tagged: `judge_assisted = True` in run record  
See [[llm-as-judge-fallback-for-failed-extraction]].

## Current Results State (2026-04-26)
- `results.json` is **EMPTY** — `run_benchmark.py` has never completed successfully
- Gemini has 58 error records (score=0) from quota hits — depresses averages
- 4 complete models: Claude (0.696), Mistral (0.635), DeepSeek (0.615), ChatGPT (0.612)
