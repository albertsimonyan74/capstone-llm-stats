# Phase 1 — Project Inventory (read-only)

Generated 2026-05-10. Repo root: `/Users/albertsimonyan/Desktop/capstone-llm-stats`. Git: `main`.

Total tracked content (excluding `.venv`, `node_modules`, `.git`): ~280 MB on disk; project itself (excluding website `node_modules`/`.venv`/`literature` PDFs): ~90 MB.

---

## 1. Top-level tree (depth 1) with sizes + classification

| Size  | Path                       | Classification     | One-line description |
|-------|----------------------------|--------------------|----------------------|
| 12K   | `CLAUDE.md`                | [KEEP-CORE]        | Project source-of-truth (commands, weights, schemas). |
| 8K    | `bayesian_scope.md`        | [KEEP-REFERENCE]   | Original scope/RQ doc. Dated, but useful for paper background. |
| 4K    | `requirements.txt`         | [KEEP-CORE]        | Python deps. |
| 4K    | `.env.example`             | [KEEP-CORE]        | Env var template (5 API keys). No secrets. |
| 4K    | `.env`                     | [KEEP-CORE]        | Local API keys (gitignored). **Flag**: contains live keys. |
| 4K    | `.gitignore`               | [KEEP-CORE]        | Standard. |
| 0B    | `.Rhistory`                | [STALE]            | Empty R history file. Junk. |
| 16K   | `.DS_Store`                | [STALE]            | macOS junk. Three more under `poster/` and `poster/figures/`. |
| 108K  | `capstone_mcp/`            | [KEEP-CORE]        | FastMCP server + tools (results/scoring/tasks). 29 tests. |
| 128K  | `evaluation/`              | [KEEP-CORE]        | Metrics, judge, rubrics, error taxonomy, validators. |
| 248K  | `llm_runner/`              | [KEEP-CORE]        | Five model clients (httpx), prompt builders, runner, parser, logger. |
| 660K  | `scripts/`                 | [KEEP-CORE] mostly | Analysis pipeline (3 rankings, calibration, krippendorff, perturbations, robustness). A few [STALE] one-offs. |
| 708K  | `baseline/`                | [KEEP-CORE]        | Bayesian/frequentist task generators + ground-truth solvers. |
| 2.1M  | `data/`                    | [KEEP-CORE] mostly | Tasks (171), perturbations. Some [STALE] v1 perturbation artifacts. |
| 2.5M  | `llm-stats-vault/`         | [KEEP-REFERENCE]   | Obsidian session/notes vault. Self-contained, mostly markdown. (Now includes the moved `audit/` under `90-archive/audit/` — see note below.) |

> `archive/` removed 2026-05-10; snapshot at `cleanup/pre_deletion_archive_snapshot_2026-05-10.tar.gz`.
> `audit/` moved 2026-05-10 → `llm-stats-vault/90-archive/audit/`; pre-move snapshot at `cleanup/pre_audit_migration_snapshot_2026-05-10.tar.gz`.
| 28M   | `poster/`                  | [KEEP-CORE]        | Poster LaTeX + figures + scripts. Headline narrative source for paper. |
| 34M   | `experiments/`             | [KEEP-CORE] mostly | `results_v1/` + `results_v2/` JSONLs (raw + scored). Two `runs.jsonl` backups [STALE]. |
| 76M   | `literature/`              | [KEEP-REFERENCE]   | Lecture PDFs + 4 textbooks. Big but small footprint via `.gitignore`. |
| 87M   | `report_materials/`        | [KEEP-CORE] mostly | R analysis pipeline (18 scripts) + figures + interactive HTML. |
| 338M  | `capstone-website/`        | [KEEP-REFERENCE]   | Vite/React frontend + FastAPI backend. Not part of paper. Heavy. |
| —     | `.venv/`                   | [STALE for repo]   | Local Python env. Already gitignored. |
| —     | `.git/`                    | [KEEP-CORE]        | Git history. Preserve. |
| —     | `.pytest_cache/`           | [STALE]            | Test cache. |
| —     | `.ruff_cache/`             | [STALE]            | Ruff cache. |
| —     | `.vercel/`                 | [KEEP-REFERENCE]   | Vercel project link. Used for site deploys, not paper. |
| —     | `.claude/`                 | [KEEP-REFERENCE]   | Claude skill config. Local tooling. |
| —     | `.planning/`               | [KEEP-REFERENCE]   | GSD planning artifacts (codebase intel). |

---

## 2. Second-level breakdown (key directories)

### `baseline/` — task generators + solvers
- `bayesian/` — 19 modules: `build_tasks_bayesian.py` (81K, generates 136 Phase 1 tasks), `build_tasks_advanced.py` (21K, 35 Phase 2 tasks), `advanced_methods.py` (Gibbs/MH/HMC/RJMCMC/HIERARCHICAL/VB/ABC), conjugate models, posterior predictive, decision theory, intervals, Bayes factors, regression. **All [KEEP-CORE]** — these define the benchmark.
- `frequentist/` — Fisher info, order stats, regression, sampling, uniform estimators. 24 tests. **[KEEP-CORE]** — used by some baselines.
- `__pycache__/` — **[STALE]**.

### `capstone_mcp/`
- `server.py`, `__main__.py`, `tools/{tasks,scoring,results}.py`, `test_server.py` (29 tests). **[KEEP-CORE]**.

### `data/`
- `benchmark_v1/{tasks.json (136), tasks_advanced.json (35), tasks_all.json (171)}` — generated; do not edit. **[KEEP-CORE]**.
- `synthetic/perturbations_all.json` (784K, **canonical 473 records**) — **[KEEP-CORE]**.
- `synthetic/perturbations.json` (112K, 75 hand-authored v1) — **[KEEP-REFERENCE]**: per CLAUDE.md, kept on disk because 5 consumer scripts + website + R pipeline use it as the canonical v1-id filter (Strategy C). Future cleanup planned.
- `synthetic/perturbations_v2.json` (660K, 398 LLM-generated v2) — **[UNCLEAR]**: subsumed by `perturbations_all.json` but unclear if any script reads it directly. Verify before archiving.
- `synthetic/perturbations_v2_sample.jsonl` (20K) — **[STALE]** sample/preview file.
- `synthetic/build_perturbations.py` — **[KEEP-REFERENCE]**: superseded by `scripts/generate_perturbations_full.py` per CLAUDE.md but listed there as the v1 generator.
- `data/error_taxonomy_results.json` — **[UNCLEAR]**: top-level orphan; possibly superseded by `data/processed_data/results_v2/error_taxonomy_v2.json`.
- `data/README.md` — **[KEEP-REFERENCE]**.

### `evaluation/`
- `metrics.py` (Path B scoring), `llm_judge.py`, `llm_judge_rubric.py` (uses OpenAI for assumption-compliance — but CLAUDE.md says external Llama 3.3 70B judge; verify), `error_taxonomy.py`, `rubrics.py`, `task_spec_schema.py`, `task_validator.py`. **[KEEP-CORE]**.
- **Flag**: `llm_judge_rubric.py` matched `OPENAI_API_KEY` grep — confirm whether this is the live judge code path, or stale.

### `experiments/`
- `run_benchmark.py`, `runs_jsonl_adapter.py`, `__init__.py`. **[KEEP-CORE]**.
- `results_v1/`:
  - `runs.jsonl` (4.4M, append-only). **[KEEP-CORE]**.
  - `runs.jsonl.bak_20260426_211605` (3.4M). **[STALE]** backup.
  - `runs.jsonl.pre_tier1_20260503_195517` (4.4M). **[STALE]** backup.
  - `results.json` (380K). **[KEEP-CORE]**.
  - `rq4_analysis.json` (128K). **[KEEP-CORE]**.
- `results_v2/` (20 files, ~24M) — calibration, krippendorff, robustness, error taxonomy v2, judge scores full + sample, perturbation runs + scores, NMACR scores, self-consistency runs + calibration, tolerance sensitivity, top disagreements. **All [KEEP-CORE]** — these are the paper's numerical results.

### `llm_runner/`
- `model_clients.py` (5 clients: claude/gemini/chatgpt/deepseek/mistral, all httpx).
- `run_all_tasks.py`, `prompt_builder.py`, `prompt_builder_fewshot.py`, `prompt_builder_pot.py`, `response_parser.py` (Path A scoring), `logger.py`. **[KEEP-CORE]**.

### `scripts/` — analysis pipeline
**[KEEP-CORE]**: `analyze_errors.py`, `analyze_perturbations.py`, `bootstrap_ci.py`, `calibration_analysis.py`, `combined_pass_flip_analysis.py`, `dimension_leaderboard.py`, `disagreement_by_perttype.py`, `error_taxonomy.py`, `generate_perturbations_full.py`, `keyword_degradation_check.py`, `keyword_vs_judge_agreement.py`, `krippendorff_agreement.py`, `plot_self_consistency_calibration.py`, `recompute_downstream.py`, `recompute_scores.py`, `refresh_pipeline.sh`, `robustness_analysis.py`, `score_perturbations.py`, `self_consistency_full.py`, `summarize_results.py`, `three_rankings_figure.py`, `tolerance_sensitivity.py`, `rank_shift.py`, `tolerance_sensitivity.py`.
**[UNCLEAR]**: `dedup_runs.py` (one-shot? Or kept as utility?), `inspect_judge_strictness.py` (diagnostic), `generate_group_a_figures.py` (figure-generation specific to "group A"), `site_palette.py` (looks like website helper).

### `poster/`
- `main.tex`, `poster.html` (372K), `literature_comparison.tex`, `figures/` (14 PNG/SVG, 2.1M), `scripts/` (14 figure-generation scripts), `assets/` (472K), `web-visuals/` (17M, includes `node_modules` for puppeteer-style capture). **[KEEP-CORE]** for the paper (figure source).
- `tex/` — empty dir.
- `IMG_9619.heic` (1.7M), `AUA_ML_RGB_ENG.webp`, `b7f387de8c767a6fd688a825217c69fc.webp`, `https_bayes-benchmark_vercel_app_.{png,svg}`, `Poster General rules.pdf`, `How to prepare a poster By Dr. Sarvazyan.pdf` (6.2M) — **[KEEP-REFERENCE]** (poster prep collateral, not paper).
- `DESIGN_AUDIT.md`, `SCRAPE_PLAN.md`, `WEBSITE_SCRAPE.md`, `README.md` — **[KEEP-REFERENCE]**.

### `report_materials/`
- `r_analysis/` (18 R scripts, `run_all.R`, `08_master_report.Rmd`, plus `figures/` + `interactive/` HTML, `data/{benchmark_clean.csv,.rds}`, 87M total). **[KEEP-CORE]** — these are the figure-source for the paper.
- `figures/` — PNG outputs (a1–a6, agreement, calibration, dimension leaderboard, robustness, etc.). **[KEEP-CORE]**.
- `poster_qr.png`, `poster_qr_labeled.png` — **[KEEP-REFERENCE]**.

### `llm-stats-vault/`  (Obsidian)
- `00-home/` (3 md), `40-literature/` (bibtex, citation-map, papers/, textbooks/), `90-archive/` (originals, audit, audit_history, experiments, intermediate_analyses, legacy_flask_website, phase_1c_superseded, proposal_provenance, sprint-history-aggregated, superseded_scripts), `atlas/` (4 md), `inbox/`, `knowledge/` (5 sub: business/debugging/decisions/integrations/patterns), `sessions/` (3 md). **[KEEP-REFERENCE]** — meta-notes, source for paper introduction motivations.

### `literature/`
- 44 PDFs: lecture notes 2–40 + 4 textbooks. **[KEEP-REFERENCE]**. Already gitignored.

### `capstone-website/`
- `backend/` (FastAPI: `main.py`, `user_study.py`, `v2_routes.py`, `data/{user_study_results.json, vote_memory.json}`, `static_data/` (7.3M, bundles `experiments/` + `data/` + `llm-stats-vault/` for Render Docker). **[KEEP-REFERENCE]** for paper.
- `frontend/` (Vite/React: `src/`, `public/`, `dist/` (68M built), `node_modules/` (196M), `package.json`, `vite.config.js`, `vercel.json`). **[KEEP-REFERENCE]**. Reproducible from `npm install`.

### `logs/`
- `self_consistency_full.log`. **[KEEP-REFERENCE]**.

---

## 3. Specific flags

### Files >50 MB
| Size  | Path                                    |
|-------|-----------------------------------------|
| 22M   | `literature/Bayesian Statistics.pdf`    |
| 17M   | `literature/Pattern Recognition and ML.pdf` |
| 15M   | `literature/Book-3.pdf`                 |

(No single file > 50 MB. Two cumulative directories large: `capstone-website/frontend/node_modules` 196M, `capstone-website/frontend/dist` 68M, `capstone-website/frontend/public` 66M.)

### Junk dirs (remove or gitignore)
- 12 `__pycache__/` dirs (in `experiments/`, `baseline/`, `llm_runner/`, `scripts/`, `evaluation/`, `capstone_mcp/`, `capstone-website/backend/`, `poster/scripts/`, `capstone_mcp/tools/`, `baseline/{frequentist,bayesian}/`, plus `.venv/...`).
- `.DS_Store` × 3 (`./`, `./poster/`, `./poster/figures/`).
- `.Rhistory` (empty).
- `.pytest_cache/`, `.ruff_cache/`.
- No `.ipynb_checkpoints/`. No top-level `node_modules/` other than `capstone-website/frontend/node_modules/` and `poster/web-visuals/node_modules/`.

### Duplicate / near-duplicate files
| Files | Notes |
|-------|-------|
| `data/processed_data/results_v1/runs.jsonl`, `runs.jsonl.bak_20260426_211605`, `runs.jsonl.pre_tier1_20260503_195517` | 3 versions; only canonical needed. Backups [STALE]. |
| `data/processed_data/results_v1/runs.jsonl` ↔ `llm-stats-vault/90-archive/audit/tier1_baseline_20260503_195141/runs.jsonl` | Audit baseline snapshot. [KEEP-REFERENCE]. |
| `data/processed_data/results_v1/runs.jsonl` ↔ `capstone-website/backend/static_data/data/processed_data/results_v1/runs.jsonl` | Deliberate Render Docker bundle (per `.gitignore` un-ignore rule). [KEEP-CORE for site]. |
| `data/raw_data/synthetic/perturbations.json` (75) + `perturbations_v2.json` (398) ↔ `perturbations_all.json` (473) | `_all` is canonical superset. v1 retained for filtering (per CLAUDE.md). v2 file's necessity unclear. |
| `data/raw_data/synthetic/perturbations_v2_sample.jsonl` | Sample/preview only. [STALE]. |
| `data/error_taxonomy_results.json` (top-level) ↔ `data/processed_data/results_v2/error_taxonomy_v2.json` | Possibly superseded. [UNCLEAR]. |
| `archive/visualizations-pre-modernization-2026-05-05/scripts/{error_taxonomy.py, self_consistency_full.py, generate_perturbations_full.py}` ↔ `scripts/{same names}` | Archived snapshot. [KEEP-REFERENCE] (already in archive/). |
| Poster figures `*.png` and `*.svg` ↔ `report_materials/figures/*.png` | Different aesthetics (poster vs report). Both [KEEP-CORE]. |
| Frontend `dist/visualizations/` (66M) ↔ `public/visualizations/` (66M) | Build output vs source. `dist/` rebuildable. |

### Secrets / API keys (flag — NOT printing)
- `.env` (project root): contains live API keys for 5 providers. Gitignored. **Verify never committed before re-org.**
- `.env.example`: template only, no secrets.
- `llm_runner/model_clients.py`, `capstone_mcp/server.py`, `evaluation/llm_judge_rubric.py`, `capstone_mcp/tools/scoring.py`, `capstone-website/backend/{user_study.py, render.yaml}` — all reference env vars (`os.environ`/`getenv`); no hardcoded keys (grep of `sk-`, `AIza` matched only English text like "task-score").
- Note: `evaluation/llm_judge_rubric.py` references `OPENAI_API_KEY`. CLAUDE.md states the judge is external Llama 3.3 70B. Resolve before paper write-up — the judge codepath must be confirmed.

### Stale / superseded artifacts
- `runs.jsonl.bak_*`, `runs.jsonl.pre_tier1_*` — old backups; safe to archive after Phase 2 review.
- `.Rhistory` (empty) — delete.
- `.pytest_cache/`, `.ruff_cache/`, `__pycache__/` (12 dirs) — delete from repo, gitignore covers `__pycache__` already.
- `.DS_Store` (×3) — delete; not in `.gitignore` for non-root locations.
- `data/raw_data/synthetic/perturbations_v2_sample.jsonl` — sample preview, looks orphaned.
- `data/raw_data/synthetic/build_perturbations.py` — deprecated per CLAUDE.md (canonical generator now in `scripts/`).
- `archive/visualizations-pre-*` — already archived; leave in place but plan to move under `archive/` in new layout.

### Unclear (need user input before classifying)
- `data/raw_data/synthetic/perturbations_v2.json` — superseded by `_all` but unclear if read by any script. Will grep in Phase 2.
- `data/error_taxonomy_results.json` (top-level orphan) — vs v2 in `experiments/`.
- `evaluation/llm_judge_rubric.py` — current vs stale judge code path (CLAUDE.md says Llama 3.3 70B; this file references OpenAI).
- `scripts/{dedup_runs.py, inspect_judge_strictness.py, generate_group_a_figures.py, site_palette.py}` — one-shot diagnostics or kept utilities?
- `capstone-website/` — keep in repo, archive, or split into separate repo? Not part of paper but referenced by it.
- `poster/IMG_9619.heic`, `AUA_ML_RGB_ENG.webp`, `b7f387de8c767a6fd688a825217c69fc.webp` — random-named poster prep images; ambiguous.

---

## 4. Headline numbers

- **Code**: ~1.8M total in `baseline/`, `evaluation/`, `llm_runner/`, `scripts/`, `capstone_mcp/`.
- **Data**: 171 tasks, 473 perturbations, ~24M v2 results JSONL, ~4.4M v1 `runs.jsonl`.
- **Figures**: ~14 poster figures (PNG+SVG), ~25 R-pipeline figures (PNG+HTML), `dist/` 68M built site assets.
- **Notes**: ~50 markdown files in `llm-stats-vault/90-archive/audit/`, vault, `.planning/`, `cleanup/`.

End of inventory. Awaiting confirmation before Phase 2.
