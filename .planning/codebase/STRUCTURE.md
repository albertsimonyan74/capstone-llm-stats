# Codebase Structure

**Analysis Date:** 2026-04-26

## Directory Layout

```
capstone-llm-stats/                  # Project root (all scripts run from here)
├── baseline/                        # Statistical ground-truth computation
│   ├── bayesian/                    # Closed-form + computational Bayesian solvers
│   │   ├── conjugate_models.py      # Beta-Binomial, Gamma-Poisson, Normal updates
│   │   ├── normal_gamma.py          # Normal-Gamma conjugate model
│   │   ├── dirichlet_multinomial.py # Dirichlet-Multinomial model
│   │   ├── posterior_predictive.py  # Posterior predictive distributions
│   │   ├── bayes_estimators.py      # Bayes estimators under quadratic/absolute/0-1 loss
│   │   ├── intervals.py             # Credible intervals + HPD intervals
│   │   ├── decision_theory.py       # MSE risk, Bayes risk, minimax, bias-variance
│   │   ├── ground_truth.py          # gt_*() functions — entry points for task builders
│   │   ├── bayes_factors.py         # Log marginal likelihood + Bayes factors
│   │   ├── bayesian_regression.py   # Bayesian linear regression
│   │   ├── markov_chains.py         # Markov chain utilities
│   │   ├── uniform_model.py         # Uniform distribution model utilities
│   │   ├── advanced_methods.py      # Phase 2: Gibbs/MH/HMC/RJMCMC/VB/ABC/Hierarchical
│   │   ├── build_tasks_bayesian.py  # Generates tasks.json (136 Phase 1 tasks)
│   │   ├── build_tasks_advanced.py  # Generates tasks_advanced.json (35 Phase 2 tasks)
│   │   └── utils.py                 # Shared utilities
│   └── frequentist/                 # Frequentist statistical baselines
│       ├── fisher_information.py    # Fisher info + Rao-Cramér bound
│       ├── order_statistics.py      # Order statistic PDFs/CDFs (uniform/exp/normal)
│       ├── regression.py            # OLS, residual variance, credibility intervals
│       ├── sampling.py              # Box-Muller transform
│       ├── uniform_estimators.py    # MLE + unbiased estimators for Uniform(0,θ)
│       └── test_frequentist.py      # 24 pytest tests for frequentist modules
│
├── data/                            # Static data files (generated — do not edit)
│   ├── benchmark_v1/
│   │   ├── tasks.json               # 136 Phase 1 task specs (DO NOT edit manually)
│   │   ├── tasks_advanced.json      # 35 Phase 2 task specs (DO NOT edit manually)
│   │   └── tasks_all.json           # 171 merged tasks (DO NOT edit manually)
│   └── synthetic/
│       ├── perturbations.json       # 75 RQ4 perturbation tasks (25 base × 3 types)
│       └── build_perturbations.py   # Regenerates perturbations.json from scratch
│
├── llm_runner/                      # Benchmark execution layer
│   ├── run_all_tasks.py             # CLI driver — main entry point for running benchmarks
│   ├── model_clients.py             # 5 httpx API clients (Claude/Gemini/ChatGPT/DeepSeek/Mistral)
│   ├── prompt_builder.py            # build_prompt() + parse_answer() for all 31 task types
│   ├── prompt_builder_fewshot.py    # Few-shot prompt variant
│   ├── prompt_builder_pot.py        # Program-of-Thought prompt variant
│   ├── response_parser.py           # full_score() — live scoring (Path A)
│   └── logger.py                    # log_jsonl() — append-only JSONL writer
│
├── evaluation/                      # Formal post-hoc scoring layer
│   ├── metrics.py                   # Dataclasses + score_all_models() (Path B)
│   ├── task_spec_schema.py          # load_tasks_from_json() → Dict[str, TaskSpec]
│   ├── rubrics.py                   # Rubric key constants for structure/assumption checks
│   ├── error_taxonomy.py            # ErrorAnnotation dataclass
│   ├── llm_judge.py                 # LLM-as-Judge fallback for extraction failures
│   └── task_validator.py            # Task spec validation (not called in main pipeline)
│
├── experiments/                     # Post-hoc analysis orchestration
│   ├── run_benchmark.py             # Entry point: load tasks+runs → score → results.json
│   └── results_v1/
│       ├── runs.jsonl               # Append-only LLM run log (created by run_all_tasks.py)
│       └── results.json             # Scoring output (created by run_benchmark.py)
│
├── capstone_mcp/                    # MCP server for interactive benchmark access
│   ├── server.py                    # FastMCP server definition (8 tools, stdio transport)
│   ├── test_server.py               # 29 pytest tests for MCP tools
│   └── tools/
│       ├── tasks.py                 # get_task(), list_tasks() implementations
│       ├── scoring.py               # score_response(), run_single_task() implementations
│       └── results.py               # get_results(), get_summary(), compare_models(), get_failures()
│
├── capstone-website/                # Research website
│   ├── backend/
│   │   └── main.py                  # FastAPI app (port 8000) — serves tasks, runs, leaderboard
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── App.jsx              # Root component; owns modal/fullImg state; renders all sections
│   │   │   ├── App.css              # Global styles
│   │   │   ├── main.jsx             # React entry point
│   │   │   ├── index.css            # Global CSS + vanilla JS cursor (IIFE in index.html)
│   │   │   ├── components/
│   │   │   │   ├── Navbar.jsx       # Navigation bar
│   │   │   │   ├── GlobeBackground.jsx  # Animated globe background
│   │   │   │   ├── NeuralNetwork.jsx    # Neural network animation
│   │   │   │   ├── ParamTooltip.jsx     # Tooltip wrapper using portal
│   │   │   │   ├── GlobalCursor.jsx     # Null stub (cursor is vanilla JS in index.html)
│   │   │   │   └── Tooltip/
│   │   │   │       └── TooltipPortal.jsx  # createPortal tooltip (bypasses modal overflow)
│   │   │   ├── pages/
│   │   │   │   ├── ResultsSection.jsx   # Benchmark results section (scoring bars, live results)
│   │   │   │   └── VizGallery.jsx       # Leaderboard + 15-visualization gallery
│   │   │   └── data/
│   │   │       ├── tasks.json           # Static copy of task list for frontend bundle
│   │   │       ├── stats.json           # Benchmark stats shown on hero section
│   │   │       ├── results_summary.json # Pre-computed results for LiveResults component
│   │   │       ├── visualizations.js    # Manifest of 15 R-generated visualizations
│   │   │       └── TooltipMap.js        # ~130 Bayesian stat term definitions
│   │   └── public/
│   │       └── visualizations/
│   │           ├── png/             # 15 static PNGs + 1 GIF (bar race animation)
│   │           └── interactive/     # 14 Plotly HTML files + _files/ dependency subdirs
│   └── nginx/                       # Nginx config for production deployment
│
├── scripts/                         # Utility scripts
│   ├── recompute_scores.py          # Backfill confidence_score+reasoning_score in runs.jsonl
│   └── summarize_results.py         # Regenerates results_summary.json for the website
│
├── report_materials/                # Research report artifacts
│   └── r_analysis/
│       ├── benchmark_report.html    # Master R Markdown report (9.3 MB, Flatly theme)
│       ├── run_all.R                # Runs all 15 R visualization scripts
│       ├── figures/                 # 15 PNG + 1 GIF (15_bar_race.gif)
│       ├── interactive/             # 14 Plotly HTML + _files/ subdirs
│       └── data/                    # R analysis data files
│
├── literature/                      # Background reading (PDFs, notes)
├── website/                         # Older static site (separate from capstone-website/)
├── .claude/
│   └── skills/
│       └── ui-ux-pro-max/           # UI/UX skill definitions
├── .planning/
│   └── codebase/                    # Codebase map documents (written by /gsd-map-codebase)
├── .env.example                     # API key template — copy to .env and fill in
├── .env                             # API keys (never committed)
├── CLAUDE.md                        # Single source of truth for all project state
├── bayesian_scope.md                # Defines scope of MCMC (out-of-scope for tasks)
├── pyproject.toml                   # Python project config (ruff lint settings)
└── .venv/                           # Python 3.11 virtual environment
```

## Directory Purposes

**`baseline/bayesian/`:**
- Purpose: All closed-form Bayesian ground-truth computations used to generate task answers
- Contains: 16 Python modules covering conjugate models, decision theory, MCMC solvers
- Key files: `ground_truth.py` (aggregates all `gt_*()` functions), `advanced_methods.py` (Phase 2 computational Bayes), `build_tasks_bayesian.py` (generates tasks.json)
- Generated by: No other code — this IS the source of truth

**`baseline/frequentist/`:**
- Purpose: Frequentist statistical computations for task types involving Fisher information, order statistics, regression, and uniform estimation
- Contains: 5 computation modules + 1 test file
- Key files: `fisher_information.py`, `order_statistics.py`
- Note: `dist="uniform"` intentionally raises `NotImplementedError` in `fisher_information()` — this is theoretically correct behavior

**`data/benchmark_v1/`:**
- Purpose: The canonical task specifications that define the benchmark
- Contains: 3 JSON files (never edit manually)
- Generated: `tasks.json` by `build_tasks_bayesian.py`; `tasks_advanced.json` by `build_tasks_advanced.py`; `tasks_all.json` by manual merge script

**`data/synthetic/`:**
- Purpose: RQ4 perturbation tasks testing LLM robustness to prompt variations
- Contains: `perturbations.json` (75 tasks) + `build_perturbations.py` (regeneration script)
- Perturbation types: `rephrase` (same math, reworded), `numerical` (new numbers, recomputed answers), `semantic` (new real-world framing)

**`llm_runner/`:**
- Purpose: All code needed to run the benchmark against live LLM APIs
- Contains: CLI driver, 5 API clients, prompt builder, response parser, logger
- Module boundary: This layer reads task JSON and writes to `runs.jsonl` — it does not import from `evaluation/`

**`evaluation/`:**
- Purpose: Formal scoring types and functions for post-hoc analysis
- Contains: Dataclasses (`TaskSpec`, `TaskRun`, `ComponentScores`, `TaskScore`, `ModelAggregate`), scoring functions, schema loader
- Module boundary: This layer is imported by `experiments/run_benchmark.py`; it does not import from `llm_runner/`

**`experiments/results_v1/`:**
- Purpose: Runtime output of the benchmark pipeline
- Contains: `runs.jsonl` (append-only, one JSON object per LLM call) and `results.json` (post-hoc scoring output)
- Warning: `runs.jsonl` contains schema heterogeneity — an old placeholder record exists with a different field set

**`capstone_mcp/`:**
- Purpose: MCP server enabling interactive access to benchmark data from Claude Code
- Contains: `server.py` (8 tool definitions), `tools/` (implementations), `test_server.py` (29 tests)
- Transport: stdio via FastMCP; configure as MCP server in Claude Code settings

**`capstone-website/`:**
- Purpose: Research showcase website with task browser and result visualizations
- Contains: FastAPI backend + React/Vite frontend
- Note: The frontend bundles static copies of key data files (`tasks.json`, `results_summary.json`) — these must be regenerated with `scripts/summarize_results.py` after new runs

**`scripts/`:**
- Purpose: One-off utility scripts for data maintenance
- Contains: `recompute_scores.py` (backfills C+R scores in runs.jsonl), `summarize_results.py` (regenerates `results_summary.json`)

**`report_materials/r_analysis/`:**
- Purpose: R-based visualization pipeline for the research paper
- Run from this directory: `cd report_materials/r_analysis && Rscript run_all.R`
- Output: 15 PNG + 1 GIF in `figures/`, 14 interactive Plotly HTML in `interactive/`
- Assets are copied to `capstone-website/frontend/public/visualizations/` for the website

## Key File Locations

**Entry Points:**
- `llm_runner/run_all_tasks.py` — CLI benchmark runner (primary entry point)
- `experiments/run_benchmark.py` — post-hoc scoring pipeline
- `capstone_mcp/server.py` — MCP server
- `capstone-website/backend/main.py` — FastAPI web backend
- `capstone-website/frontend/src/main.jsx` — React app entry point

**Configuration:**
- `.env.example` — API key template (copy to `.env` before first run)
- `CLAUDE.md` — ground truth reference for all project state
- `pyproject.toml` — Python project config and ruff settings
- `capstone-website/frontend/vite.config.js` — Vite build config
- `capstone-website/nginx/` — Nginx production config

**Core Scoring:**
- `llm_runner/response_parser.py` — `full_score()`, `extract_confidence()`, `reasoning_quality_score()` (Path A)
- `evaluation/metrics.py` — `score_all_models()`, `WEIGHTS` dict, all dataclasses (Path B)

**Ground Truth:**
- `baseline/bayesian/ground_truth.py` — `gt_*()` functions called by task builders
- `baseline/bayesian/advanced_methods.py` — Phase 2 MCMC/VB/ABC solvers

**Task Data:**
- `data/benchmark_v1/tasks_all.json` — 171 tasks (primary source for runners and evaluators)
- `data/synthetic/perturbations.json` — 75 perturbation tasks for RQ4

**Run Logs:**
- `experiments/results_v1/runs.jsonl` — append-only run log (source of truth for all actual LLM outputs)
- `experiments/results_v1/results.json` — post-hoc scoring output (regenerated by `run_benchmark.py`)

**Frontend Data (static copies, must be kept in sync):**
- `capstone-website/frontend/src/data/tasks.json` — task list for task browser
- `capstone-website/frontend/src/data/results_summary.json` — leaderboard data for LiveResults component
- `capstone-website/frontend/src/data/stats.json` — hero section stats
- `capstone-website/frontend/src/data/visualizations.js` — manifest of 15 R visualizations

**Tests:**
- `baseline/frequentist/test_frequentist.py` — 24 tests for frequentist modules
- `capstone_mcp/test_server.py` — 29 tests for MCP tools

## Naming Conventions

**Files:**
- Python modules: `snake_case.py`
- React components: `PascalCase.jsx`
- Data files: `snake_case.json` or `snake_case.js`
- Test files: `test_<module>.py` (co-located with the module being tested)

**Directories:**
- Python packages: `snake_case/`
- Website sub-apps use hyphens: `capstone-website/`

**Task IDs:**
- Format: `TYPE_NN` with zero-padded 2-digit number, e.g. `DISC_MEDIAN_01`, `BETA_BINOM_03`
- Perturbation task IDs append the type: `BINOM_FLAT_01_numerical`

**Model family names (always lowercase in code and data):**
- `claude`, `gemini`, `chatgpt`, `deepseek`, `mistral`

**Score keys in runs.jsonl:**
- `numeric_score`, `structure_score`, `assumption_score`, `confidence_score`, `reasoning_score`, `final_score`

## Where to Add New Code

**New task type (add to Phase 1 benchmark):**
1. Write `gen_<TYPE>_tasks()` in `baseline/bayesian/build_tasks_bayesian.py`
2. Add ground-truth function in `baseline/bayesian/ground_truth.py` if needed
3. Add `_prompt_<TYPE>()` in `llm_runner/prompt_builder.py`
4. Register in `_DISPATCH` dict in `llm_runner/prompt_builder.py`
5. Add structure/assumption keyword patterns in `llm_runner/response_parser.py:_STRUCTURE_KEYWORDS` / `_ASSUMPTION_KEYWORDS`
6. Regenerate: `python -m baseline.bayesian.build_tasks_bayesian`
7. Merge: update `tasks_all.json` using the merge snippet in CLAUDE.md §5

**New LLM model client:**
1. Add class in `llm_runner/model_clients.py` inheriting `BaseModelClient`
2. Set `model` and `model_family` class attributes
3. Implement `query(self, prompt: str, task_id: str) -> Dict[str, Any]`
4. Register in `_CLIENTS` dict at bottom of `model_clients.py`
5. Add to `--models` choices in `llm_runner/run_all_tasks.py`
6. Add placeholder to `.env.example`

**New React page or major section:**
- Implementation: `capstone-website/frontend/src/pages/`
- Register in `capstone-website/frontend/src/App.jsx` (add section + navbar entry)

**New React component:**
- Implementation: `capstone-website/frontend/src/components/`
- Tooltip-enabled components: use `ParamTooltip` from `components/ParamTooltip.jsx` with terms from `data/TooltipMap.js`

**New Bayesian stat term for tooltips:**
- Add to `capstone-website/frontend/src/data/TooltipMap.js` (currently ~130 entries)

**New FastAPI endpoint:**
- Add to `capstone-website/backend/main.py`

**New MCP tool:**
1. Implement in `capstone_mcp/tools/` (tasks.py, scoring.py, or results.py)
2. Register with `@mcp.tool()` decorator in `capstone_mcp/server.py`
3. Add test in `capstone_mcp/test_server.py`

**New utility script (data maintenance):**
- Location: `scripts/`

## Special Directories

**`.venv/`:**
- Purpose: Python 3.11 virtual environment
- Generated: Yes (`python -m venv .venv`)
- Committed: No

**`capstone-website/frontend/node_modules/`:**
- Purpose: npm dependencies for React/Vite frontend
- Generated: Yes (`npm install`)
- Committed: No

**`capstone-website/frontend/dist/`:**
- Purpose: Vite production build output
- Generated: Yes (`npm run build`)
- Committed: No (but Plotly `_files/` subdirs for interactive charts are built into `public/` before build)

**`capstone-website/frontend/public/visualizations/`:**
- Purpose: Pre-generated static visualization assets served directly by Vite
- Contains: `png/` (15 PNG + 1 GIF) and `interactive/` (14 Plotly HTML + `_files/` subdirs)
- Generated: Copied from `report_materials/r_analysis/figures/` and `interactive/`
- Committed: Yes (static assets needed for the website)

**`report_materials/r_analysis/figures/` and `interactive/`:**
- Purpose: Source of R-generated visualizations; copied to frontend public dir
- Generated: Yes (`cd report_materials/r_analysis && Rscript run_all.R`)
- Committed: Yes (source figures committed to repo)

**`.planning/codebase/`:**
- Purpose: Codebase map documents generated by `/gsd-map-codebase`
- Generated: Yes (by GSD commands)
- Committed: Yes

---

*Structure analysis: 2026-04-26*
