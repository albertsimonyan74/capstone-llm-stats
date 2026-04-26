# ROADMAP

## Phase 1 — Gemini Completion + Results Pipeline
**Goal:** Get complete 5-model results. Unblock all downstream analysis.
**Covers:** R1, R2

### Plan 1.1 — Resume Gemini Runs
- Resume Phase 1 (62 missing tasks): `python -m llm_runner.run_all_tasks --models gemini`
- Resume Phase 2 (35 tasks): `python -m llm_runner.run_all_tasks --models gemini --tasks data/benchmark_v1/tasks_advanced.json --delay 5`
- Monitor for quota exhaustion; resume next day if hit

### Plan 1.2 — Prune Error Records + Run Scoring
- Identify 58 error records (score=0) in runs.jsonl for Gemini
- Run `python -m experiments.run_benchmark` → populate results.json (855 entries)
- Run `python scripts/summarize_results.py` → refresh results_summary.json
- Verify website LiveResults panel shows 5 models

---

## Phase 2 — RQ4 Synthetic Benchmark
**Goal:** Complete RQ4 perturbation analysis. Enables robustness findings.
**Covers:** R3

### Plan 2.1 — Run Synthetic Benchmark
- Run: `python -m llm_runner.run_all_tasks --models claude chatgpt deepseek mistral --synthetic`
- Run Gemini: `python -m llm_runner.run_all_tasks --models gemini --synthetic --delay 5`
- Verify: 375 new records in runs.jsonl (75 tasks × 5 models)

### Plan 2.2 — Perturbation Comparison Analysis
- Script: `scripts/analyze_perturbations.py`
- Logic: group runs by base_task_id, compare avg score across rephrase/numerical/semantic
- Output: `experiments/results_v1/perturbation_analysis.json` + summary table
- Add analysis section to 08_master_report.Rmd

---

## Phase 3 — New Benchmark Concepts
**Goal:** Expand benchmark with missing statistical concepts for comprehensive coverage.
**Covers:** R6

### Plan 3.1 — Identify + Design New Task Types
- Review existing 38 types vs statistical curriculum
- Candidate concepts: Kalman filter, EM algorithm, Laplace approximation, copulas, extreme value theory
- Design task spec schema + baseline computation for each
- Target: 3–7 new task types, 5 tasks each (15–35 new tasks)

### Plan 3.2 — Generate + Validate Tasks
- Add `gen_<type>_tasks()` to build_tasks_bayesian.py
- Add `_prompt_<type>()` to prompt_builder.py
- Regenerate tasks_all.json; validate with task_validator.py
- Update stats.json, frontend tasks.json, CLAUDE.md

### Plan 3.3 — Benchmark New Tasks
- Run all 5 models on new tasks
- Integrate runs into existing results pipeline
- Refresh results.json + results_summary.json

---

## Phase 4 — Visualization Overhaul
**Goal:** Clear, research-question-aligned visualizations. Fix Open Interactive.
**Covers:** R4, R5

### Plan 4.1 — Fix Open Interactive Button
- Verify current `window.open(viz.interactive, '_blank')` implementation in VizGallery.jsx
- Test in Safari + Chrome + Firefox
- Fix any remaining iframe/popup issues

### Plan 4.2 — Replace Unclear Visualizations
- Audit all 15 PNGs + 14 interactive HTMLs against RQ1–RQ5 mapping
- Identify lowest-value visualizations
- Write new R scripts or modify existing ones for clearer charts
- Candidates: RQ1 accuracy breakdown, RQ3 assumption compliance heatmap, RQ5 calibration scatter
- Re-copy assets to frontend/public/visualizations/

### Plan 4.3 — Update Viz Manifest
- Update visualizations.js with new/replaced charts
- Update descriptions and insights to match actual findings
- Ensure website gallery reflects new assets

---

## Phase 5 — Final Report + Paper Readiness
**Goal:** Publication-ready report with complete 5-model data.
**Covers:** R7, R9

### Plan 5.1 — Final R Report Render
- Update 08_master_report.Rmd: replace "4 complete models" → "5 models"
- Add RQ4 perturbation section
- Add new task types section if Phase 3 completed
- Re-render: `cd report_materials/r_analysis && Rscript run_all.R`
- Verify benchmark_report.html complete with Gemini data

### Plan 5.2 — CLAUDE.md + Docs Update
- Update §9 Known Gaps to reflect completed work
- Update tier counts, model run status table
- Verify all stats match actual runs.jsonl counts

---

## Milestone Summary

| Phase | Key Deliverable | Requirement |
|-------|----------------|-------------|
| 1 | 855-run results.json | R1, R2 |
| 2 | 375 synthetic runs + RQ4 analysis | R3 |
| 3 | New task types benchmarked | R6 |
| 4 | Working viz + clearer charts | R4, R5 |
| 5 | Final report with all 5 models | R7, R9 |
