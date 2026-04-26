# STATE

## Project
DS 299 Capstone — LLM Bayesian Benchmark (Completion Phase)

## Current Phase
Phase 1 — Gemini Completion + Results Pipeline

## Status
- Codebase map: DONE (.planning/codebase/ — 7 docs)
- Research gap closures: DONE (bc470f1 — llm_judge, task_validator, fewshot, PoT, bibliography)
- Phase 1 benchmark (4 models): DONE (136+35=171 tasks each)
- Gemini Phase 1: PARTIAL (74/136 done, 62 missing — quota)
- Gemini Phase 2: NOT STARTED (0/35)
- RQ4 synthetic: NOT STARTED (0/375)
- results.json: EMPTY
- Open Interactive: verify needed
- Visualizations: need overhaul

## Run Status (as of 2026-04-26)
| Model | Phase 1 | Phase 2 | Synthetic |
|-------|---------|---------|-----------|
| claude | 136/136 ✅ | 35/35 ✅ | 0/75 |
| chatgpt | 136/136 ✅ | 35/35 ✅ | 0/75 |
| mistral | 136/136 ✅ | 35/35 ✅ | 0/75 |
| deepseek | 136/136 ✅ | 35/35 ✅ | 0/75 |
| gemini | 74/136 ❌ | 0/35 ❌ | 0/75 |

## Key Files
- tasks: data/benchmark_v1/tasks_all.json (171 tasks)
- runs: experiments/results_v1/runs.jsonl (~620+ records)
- results: experiments/results_v1/results.json (EMPTY)
- website: capstone-website/ (FastAPI + React)
- R report: report_materials/r_analysis/benchmark_report.html

## Next Action
Resume Gemini Phase 1:
```bash
source .venv/bin/activate
python -m llm_runner.run_all_tasks --models gemini
```
Then Phase 2:
```bash
python -m llm_runner.run_all_tasks --models gemini --tasks data/benchmark_v1/tasks_advanced.json --delay 5
```
