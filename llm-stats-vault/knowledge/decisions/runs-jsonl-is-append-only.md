---
tags: [decision, runs, data, append-only, jsonl]
date: 2026-04-26
---

# runs.jsonl Is Append-Only

## Decision
`data/processed_data/results_v1/runs.jsonl` is **never truncated, overwritten, or edited**.  
All new run records are appended by `llm_runner/logger.py`'s `log_jsonl()`.

## Why
- Provides a complete audit trail of all LLM calls including errors
- Re-running the benchmark is safe — resume logic skips already-completed tasks
- Allows retrospective analysis of any run without re-running expensive API calls
- Error records (score=0, error field set) are valuable data — preserve them

## Consequences
1. **Schema heterogeneity**: file contains one old placeholder record with a different schema. Any analysis code must handle this.
2. **Error records persist**: 58 Gemini error records (score=0 from 429 quota hits) remain in the file. They depress Gemini's apparent average. Fix: re-run after quota resets (resume logic will overwrite by task re-execution, NOT delete old records).
3. **Growing file**: ~620+ records currently; will reach ~1230 when complete (171 tasks × 5 models + 375 synthetic).

## How to Apply
- Never run `> runs.jsonl` or any truncation command
- Analysis code: always filter by `(model_family, task_id)` pair; take latest non-error record if duplicates exist
- To fix error records: re-run the model (`run_all_tasks.py` skips already-completed via `_load_completed()`) — BUT `_load_completed()` may already consider errored tasks as "done"

## Related
- [[resume-safe-benchmark-skips-completed-tasks]] — how resume works
- [[gemini-daily-quota-exhausted-on-2026-04-24]] — source of the 58 error records
