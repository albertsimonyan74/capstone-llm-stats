# REQUIREMENTS

## Table Stakes (must ship)

### R1 — Gemini Completion
- Resume Phase 1: 62 missing tasks (`python -m llm_runner.run_all_tasks --models gemini`)
- Resume Phase 2: 35 tasks (`python -m llm_runner.run_all_tasks --models gemini --tasks data/benchmark_v1/tasks_advanced.json --delay 5`)
- After completion: prune/annotate 58 error records in runs.jsonl
- Acceptance: gemini row in results shows 171/171 runs, avg_score > 0 (no error-inflated zeros)

### R2 — Results Pipeline
- `python -m experiments.run_benchmark` produces non-empty results.json
- results.json contains all 5 models × 171 tasks = 855 task_scores entries
- `scripts/summarize_results.py` refreshes results_summary.json (read by website LiveResults panel)
- Acceptance: results.json has model_aggregates with 5 entries, task_scores with 855 entries

### R3 — RQ4 Synthetic Benchmark
- Run 75 perturbations × 5 models = 375 runs
- Command: `python -m llm_runner.run_all_tasks --models claude chatgpt deepseek mistral gemini --synthetic`
- Implement perturbation comparison analysis: per base_task_id, compare score[rephrase] vs score[numerical] vs score[semantic]
- Acceptance: 375 runs in runs.jsonl, analysis script produces per-type score table

### R4 — Open Interactive Fix
- Current bug: "Open Interactive" button opens Plotly HTML in iframe; Safari blocks cross-origin iframes
- Fix: change button to `window.open(viz.interactive, '_blank')` for all non-GIF viz
- Already done for VizGallery per CLAUDE.md §9 — verify it's actually working in browser
- Acceptance: clicking "Open Interactive" opens Plotly chart in new tab in all browsers

### R5 — Visualization Improvements
- Identify which of the 15 existing PNGs are unclear or low-information
- Replace/supplement with clearer alternatives that directly answer RQ1–RQ5
- Specific improvements needed: [to be determined in planning phase]
- Acceptance: each visualization has a clear takeaway directly mapping to a research question

## Important (needed for paper)

### R6 — New Benchmark Concepts
- Identify statistical concepts not yet covered in 38 task types
- Generate tasks using existing pipeline (build_tasks_bayesian.py pattern)
- Run benchmark on new tasks (all 5 models)
- Integrate into tasks_all.json, update stats.json and website
- Acceptance: new task types documented in CLAUDE.md, tasks generated, runs complete

### R7 — Final Report Render
- Re-render 08_master_report.Rmd with complete data (all 5 models, all 171 tasks)
- Update all hardcoded "4 complete models" references to "5 models"
- Acceptance: benchmark_report.html generated with Gemini data included

## Nice to Have

### R8 — Testing Coverage
- Add tests for evaluation/metrics.py (scoring weight contract, aggregation math)
- Add tests for llm_runner/response_parser.py (parse_and_score, extract_confidence)
- Acceptance: pytest passes, coverage > 60% for these modules

### R9 — CLAUDE.md Update
- Update Known Gaps §9 after each completed phase
- Acceptance: CLAUDE.md reflects final project state accurately
