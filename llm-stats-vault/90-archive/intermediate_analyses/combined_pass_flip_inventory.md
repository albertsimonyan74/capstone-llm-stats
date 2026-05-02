# Combined Pass-Flip Inventory (Phase 1.5)

Pre-flight inventory for `combined_pass_flip_analysis.py`. Documents which file
holds keyword vs judge scores for the base population vs the perturbation
population, and the field names used.

## File-by-file

| Population | Score type | File | Field for assumption_compliance |
|------------|------------|------|---------------------------------|
| Base       | Keyword    | `experiments/results_v1/runs.jsonl` | `assumption_score` (top-level float in [0,1]) |
| Base       | LLM judge  | `experiments/results_v2/llm_judge_scores_full.jsonl` | `assumption_compliance.score` (nested object) |
| Perturbation | Keyword  | `experiments/results_v2/perturbation_runs.jsonl` | `assumption_score` (top-level float in [0,1]) |
| Perturbation | LLM judge | `experiments/results_v2/perturbation_judge_scores.jsonl` | `assumption_compliance.score` (nested object) |

## Field-name notes

- Keyword files share the **same** schema for the assumption dimension
  (`assumption_score`, top-level numeric).
- Judge files share the **same** schema (nested `assumption_compliance.score`),
  matching the existing `keyword_vs_judge_agreement.py` script.
- Run-IDs are field `run_id` in all four files. Format: UUID4 string.

## Run counts

| File | Records | Errors |
|------|---------|--------|
| `runs.jsonl` (base) | 1,230 | 0 |
| `llm_judge_scores_full.jsonl` | 1,230 | 0 |
| `perturbation_runs.jsonl` | 2,365 | 0 |
| `perturbation_judge_scores.jsonl` | 2,365 | 0 |

Run-ID intersection (per population): 100% match.
Run-ID overlap **between** base and perturbation: **0** (no collisions, as
expected — each run has a fresh UUID).

## Eligibility filter (required_assumption_checks > 0)

Canonical task-spec sources:

- Base task specs: `data/benchmark_v1/tasks_all.json` (171 tasks)
- Perturbation task specs: `data/synthetic/perturbations.json` (75 tasks)

For perturbations, eligibility inherits from the base task. The perturbation
runs already carry `base_task_id` field (which correctly handles the `_v2`
suffix sometimes present), so we use it directly rather than regex-stripping.

## Binarization rule

Both keyword and judge scores in [0, 1]. Threshold:
- score >= 0.5 -> PASS (1)
- score <  0.5 -> FAIL (0)

Pass-flip = keyword PASS and judge FAIL (poster headline metric).
Inverse-flip = keyword FAIL and judge PASS.

## Perturbation-type counts

- rephrase: 855
- semantic: 855
- numerical: 655

(Numerical is short by ~200 because some base tasks have no meaningful
numerical perturbation, e.g. CONCEPTUAL tasks.)
