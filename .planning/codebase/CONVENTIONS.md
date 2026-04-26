# CONVENTIONS

## Overview
DS 299 Capstone — code conventions derived from CLAUDE.md §10 and codebase audit.

---

## Naming

### Task IDs
`TYPE_NN` — uppercase type prefix, zero-padded 2-digit index.
Examples: `DISC_MEDIAN_01`, `GIBBS_03`, `CONCEPTUAL_10`

### Model family names (lowercase strings)
`claude`, `gemini`, `chatgpt`, `deepseek`, `mistral`
Used as dict keys, `--models` CLI values, and JSONL `model_family` field.

### Files
- Python: `snake_case.py`
- React: `PascalCase.jsx` for components, `camelCase.js` for data/utils
- Data files: `snake_case.json` / `snake_case.jsonl`
- R scripts: `NN_descriptive_name.R` (zero-padded prefix)

### Variables
- Ground truth values: `true_value` (not `answer`, `gt`, `expected`)
- Scoring keys: `numeric_score`, `structure_score`, `assumption_score`, `confidence_score`, `reasoning_score`, `final_score`
- Model run record fields: `model_family` (not `model_name` in JSONL; `model_name` used in metrics.py TaskRun)

---

## Import Style

All scripts run from project root. **Absolute imports only** — no relative imports outside packages.

```python
# Correct
from llm_runner.logger import log_jsonl
from evaluation.metrics import TaskRun, score_all_models

# Wrong
from .logger import log_jsonl
```

---

## Code Patterns

### Adding a model client
1. Class in `llm_runner/model_clients.py` inheriting `BaseModelClient`
2. Set `model` and `model_family` class attributes
3. Implement `query(self, prompt, task_id) -> Dict`
4. Return: `{model, model_family, task_id, raw_response, input_tokens, output_tokens, latency_ms, error}`
5. Register in `_CLIENTS` dict
6. Add to `--models` choices in `run_all_tasks.py`
7. Add key placeholder to `.env.example`

### Adding a task type
1. `gen_<type>_tasks()` in `baseline/bayesian/build_tasks_bayesian.py`
2. Ground-truth computation in `baseline/bayesian/ground_truth.py`
3. `_prompt_<type>()` in `llm_runner/prompt_builder.py`
4. Register in `_DISPATCH` dict in `prompt_builder.py`
5. Regenerate: `python -m baseline.bayesian.build_tasks_bayesian`

### Scoring weight changes
Two files must stay in sync — always update both together:
- `WEIGHTS` dict in `evaluation/metrics.py`
- Formula comment + `full_score()` in `llm_runner/response_parser.py`
Current weights: N=M=A=C=R=0.20 (all equal)

### Task spec schema (tasks.json)
```json
{
  "task_id": "TYPE_NN",
  "tier": 1-4,
  "difficulty": "basic|intermediate|advanced",
  "inputs": {...},
  "numeric_targets": [{"key": "name", "true_value": 0.0, "full_credit_tol": 0.01, "zero_credit_scale": 0.10}],
  "required_structure_checks": ["check_name"],
  "required_assumption_checks": ["check_name"],
  "prompt": "..."
}
```
Phase 1 tasks use `notes.inputs` + `notes.topic`; Phase 2 tasks use top-level `inputs` + `prompt` + `category="computational_bayes"`.

---

## File Organization Rules

- `data/benchmark_v1/tasks.json` — Phase 1 (136 tasks). **Do not edit manually.**
- `data/benchmark_v1/tasks_advanced.json` — Phase 2 (35 tasks). **Do not edit manually.**
- `data/benchmark_v1/tasks_all.json` — Merged 171 tasks. **Do not edit manually.**
- `experiments/results_v1/runs.jsonl` — append-only, never truncate
- All baseline computation in `baseline/` — no ML, no approximations, closed-form only (except Phase 2 MCMC solvers which seed at 42)

---

## Error Handling

- API clients: retry on 429/connect/timeout (3 attempts, 5s/15s/30s waits). Non-retryable: 400/401/403/404.
- Missing API key → error record written to JSONL (no exception raised)
- Missing task in JSONL → silently skipped in `load_runs_jsonl()`
- Error records in JSONL have `"error": "<msg>"` field → skipped by scoring pipeline

---

## Comments

Default: no comments. Add only when WHY is non-obvious.
Exception: cross-reference comment in both scoring files:
`# Scoring weights must match [other file] — see CLAUDE.md §7`

---

## Summary
Strict naming (task IDs, model families), absolute imports, dual-file weight sync, append-only JSONL, never-edit generated task files.
