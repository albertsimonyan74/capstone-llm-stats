---
tags: [decision, tasks, generation, data-integrity]
date: 2026-04-26
---

# tasks.json Is Generated — Never Edit Manually

## Decision
Three task JSON files are generated artifacts, not source-of-truth edits:
- `data/raw_data/benchmark_v1/tasks.json` — Phase 1, 136 tasks
- `data/raw_data/benchmark_v1/tasks_advanced.json` — Phase 2, 35 tasks
- `data/raw_data/benchmark_v1/tasks_all.json` — merged 171 tasks

## Why
- Ground-truth values are computed by baseline Python modules (`conjugate_models.py`, `advanced_methods.py`, etc.)
- Manual edits would create numeric_targets that don't match actual ground-truth computations
- Regeneration from source is fast and deterministic (Phase 2 uses `np.random.seed(42)`)
- Any task structure change must go through the generation pipeline to stay consistent

## Regeneration Commands
```bash
# Phase 1 (136 tasks)
python -m baseline.bayesian.build_tasks_bayesian

# Phase 2 (35 advanced tasks)
python -m baseline.bayesian.build_tasks_advanced

# Merge (171 tasks)
python3 -c "
import json
with open('data/raw_data/benchmark_v1/tasks.json') as f: t1 = json.load(f)
with open('data/raw_data/benchmark_v1/tasks_advanced.json') as f: t2 = json.load(f)
all_ = t1 + t2
assert len(set(t['task_id'] for t in all_)) == len(all_)
with open('data/raw_data/benchmark_v1/tasks_all.json', 'w') as f: json.dump(all_, f, indent=2)
"
```

## Adding New Tasks
See [[adding-a-new-task-type-requires-4-changes]] — must go through generation pipeline.

## Related
- [[data-flow]] — where these files fit in the pipeline
