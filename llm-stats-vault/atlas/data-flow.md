---
tags: [atlas, data-flow, pipeline, files]
date: 2026-04-26
---

# Data Flow

## Full Pipeline

```
1. TASK GENERATION
   build_tasks_bayesian.py            →  tasks.json          (136 Phase 1 tasks)
   build_tasks_advanced.py            →  tasks_advanced.json (35 Phase 2 tasks)
   [manual merge]                     →  tasks_all.json      (171 total)
   generate_perturbations_full.py     →  perturbations_all.json
                                          (473 = 75 hand-authored + 398 LLM-generated)

2. BENCHMARK RUN
   run_all_tasks.py --models <name>
     loads tasks_all.json (or perturbations_all.json with --synthetic)
     calls model API via httpx
     response_parser.full_score() → component scores
     log_jsonl() → appends record to runs.jsonl

3. POST-HOC SCORING
   run_benchmark.py
     loads tasks_all.json → Dict[task_id, TaskSpec]
     loads runs.jsonl → List[TaskRun]
     [optional] llm_judge.py fallback for failed extraction
     metrics.score_all_models() → TaskScore + ModelAggregate
     writes results.json

4. SUMMARY REFRESH
   summarize_results.py
     reads results.json
     writes results_summary.json (website LiveResults data)

5. WEBSITE DISPLAY
   FastAPI backend (port 8000) reads runs.jsonl directly
   React frontend reads:
     results_summary.json  → LiveResults panel
     stats.json           → benchmark stats
     tasks.json           → task browser
     visualizations.js    → viz gallery manifest
```

## Key File Locations

| File | Path | Status (2026-04-26) |
|------|------|---------------------|
| Phase 1 tasks | `data/raw_data/benchmark_v1/tasks.json` | ✅ 136 tasks |
| Phase 2 tasks | `data/raw_data/benchmark_v1/tasks_advanced.json` | ✅ 35 tasks |
| All tasks | `data/raw_data/benchmark_v1/tasks_all.json` | ✅ 171 tasks |
| Synthetic | `data/raw_data/synthetic/perturbations_all.json` | ✅ 473 perturbations (75 hand-authored + 398 LLM-generated; v1 file deprecated 2026-05-04) |
| Run log | `data/processed_data/results_v1/runs.jsonl` | ⚠️ ~620+ (Gemini incomplete) |
| Results | `data/processed_data/results_v1/results.json` | ❌ EMPTY |
| Website data | `capstone-website/frontend/src/data/` | ⚠️ 4 models only |
| R PNGs | `report_materials/r_analysis/figures/` | ✅ 15 PNGs + 1 GIF |
| R HTML | `report_materials/r_analysis/interactive/` | ✅ 14 Plotly HTMLs |
| Master report | `report_materials/r_analysis/benchmark_report.html` | ✅ 9.3 MB (4 models) |

## Run Record Schema (runs.jsonl)

```json
{
  "run_id": "...",
  "timestamp": "...",
  "task_id": "BINOM_FLAT_01",
  "task_type": "BINOM_FLAT",
  "tier": 1,
  "difficulty": "basic",
  "model": "claude-sonnet-4-5",
  "model_family": "claude",
  "prompt": "...",
  "raw_response": "...",
  "parsed_values": [7.0, 5.0, 0.583],
  "ground_truth": [...],
  "numeric_score": 0.95,
  "structure_score": 1.0,
  "assumption_score": 1.0,
  "confidence_score": 0.8,
  "reasoning_score": 0.75,
  "final_score": 0.9,
  "pass": true,
  "answer_found": true,
  "length_match": true,
  "input_tokens": 210,
  "output_tokens": 380,
  "latency_ms": 2100,
  "error": null
}
```

**Schema caveat**: runs.jsonl contains one old placeholder record with different schema.
Analysis code must handle heterogeneous records.

## Merging Task Files

```bash
python3 -c "
import json
with open('data/raw_data/benchmark_v1/tasks.json') as f: t1 = json.load(f)
with open('data/raw_data/benchmark_v1/tasks_advanced.json') as f: t2 = json.load(f)
all_ = t1 + t2
assert len(set(t['task_id'] for t in all_)) == len(all_)
with open('data/raw_data/benchmark_v1/tasks_all.json', 'w') as f: json.dump(all_, f, indent=2)
print(f'Merged {len(t1)} + {len(t2)} = {len(all_)} tasks')
"
```
