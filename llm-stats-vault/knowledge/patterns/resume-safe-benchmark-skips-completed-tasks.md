---
tags: [pattern, benchmark, resume, runner, safety]
date: 2026-04-26
---

# Resume-Safe Benchmark Skips Completed Tasks

## The Pattern
`code/models/run_all_tasks.py` is safe to re-run at any time — it will skip tasks already recorded in `runs.jsonl`.

## How It Works
At startup, `_load_completed()` reads the existing `runs.jsonl` and builds a set of completed `(model_family, task_id)` pairs. Any task with an existing record is skipped.

```python
completed = _load_completed()  # Set[Tuple[str, str]]
for task in tasks:
    if (model_family, task["task_id"]) in completed:
        continue
    # ... run task
```

## Use Cases
1. **Quota exhaustion** — Gemini hits daily RPD limit; resume next day, completed tasks auto-skipped
2. **Network failures** — runner crashes mid-run; restart picks up where it left off
3. **Partial model runs** — run 3 models, add a 4th later without re-running the first 3
4. **Debugging** — `--dry-run` flag prints prompts without API calls, safe to run any time

## Caveat: Error Records
If a task errored (e.g., 429 quota hit) but a record was still written to `runs.jsonl`, `_load_completed()` may consider it "completed" and skip it on resume.  
Consequence: Gemini's 58 error records (score=0) may prevent those tasks from being retried.  
**Verify behavior**: check if `_load_completed()` filters out error records before trusting resume.

## Related Commands
```bash
# Dry run — no API calls, just print prompts
python code/models/run_all_tasks.py --models claude --dry-run --limit 3

# Filter by task type
python code/models/run_all_tasks.py --models claude --task-types DISC_MEDIAN MARKOV

# Resume Gemini after quota reset
python -m llm_runner.run_all_tasks --models gemini
```

## Related
- [[gemini-daily-quota-exhausted-on-2026-04-24]] — why resume matters for Gemini
- [[runs-jsonl-is-append-only]] — the file resume logic reads
