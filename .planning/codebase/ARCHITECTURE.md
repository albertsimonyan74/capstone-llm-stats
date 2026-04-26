<!-- refreshed: 2026-04-26 -->
# Architecture

**Analysis Date:** 2026-04-26

## System Overview

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       BENCHMARK PIPELINE (offline)                          │
│                                                                             │
│  baseline/bayesian/          baseline/frequentist/                          │
│  build_tasks_bayesian.py  →  ground_truth.py  →  tasks.json (136 tasks)    │
│  build_tasks_advanced.py  →  advanced_methods.py → tasks_advanced.json      │
│                                                  → tasks_all.json (171)     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ task specs (JSON)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LLM RUNNER  (llm_runner/)                           │
│                                                                             │
│  run_all_tasks.py  →  prompt_builder.py  →  model_clients.py (5 clients)   │
│                    ←  raw_response                                           │
│                    →  response_parser.py  →  full_score() [N+M+A+C+R]      │
│                    →  logger.py  →  runs.jsonl (append-only)                │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ runs.jsonl
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                   POST-HOC SCORING  (experiments/)                          │
│                                                                             │
│  run_benchmark.py  →  evaluation/task_spec_schema.py                        │
│                    →  evaluation/metrics.py  →  score_all_models()          │
│                    →  results.json                                           │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ results.json + runs.jsonl
                          ┌────────────┴──────────────┐
                          ▼                           ▼
         ┌─────────────────────────┐   ┌─────────────────────────────────┐
         │   MCP SERVER            │   │   WEBSITE                       │
         │   capstone_mcp/         │   │   capstone-website/             │
         │   server.py (8 tools)   │   │   backend/main.py (FastAPI)     │
         │   FastMCP / stdio       │   │   frontend/src/ (React + Vite)  │
         └─────────────────────────┘   └─────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | Key Files |
|-----------|----------------|-----------|
| Baseline (Bayesian) | Closed-form ground-truth computation for all 31 Phase 1 task types | `baseline/bayesian/ground_truth.py`, `conjugate_models.py`, `decision_theory.py`, `intervals.py`, `bayes_estimators.py`, `posterior_predictive.py`, `normal_gamma.py`, `dirichlet_multinomial.py` |
| Baseline (Advanced) | Monte Carlo ground-truth for 7 Phase 2 computational Bayes types | `baseline/bayesian/advanced_methods.py` |
| Baseline (Frequentist) | Fisher information, order statistics, regression, sampling baselines | `baseline/frequentist/fisher_information.py`, `order_statistics.py`, `regression.py`, `sampling.py`, `uniform_estimators.py` |
| Task Builders | Generate JSON task files from baseline computations | `baseline/bayesian/build_tasks_bayesian.py`, `baseline/bayesian/build_tasks_advanced.py`, `data/synthetic/build_perturbations.py` |
| LLM Runner | CLI driver that sends tasks to LLM APIs, scores responses, appends to runs.jsonl | `llm_runner/run_all_tasks.py` |
| Prompt Builder | Constructs human-readable prompts from task dicts; dispatches by task type | `llm_runner/prompt_builder.py` |
| Model Clients | 5 httpx-based API clients (no vendor SDKs) | `llm_runner/model_clients.py` |
| Response Parser (Path A) | Live scoring during benchmark runs; `full_score()` computes N+M+A+C+R | `llm_runner/response_parser.py` |
| Evaluation Metrics (Path B) | Post-hoc formal scoring from TaskRun dataclass objects | `evaluation/metrics.py` |
| Experiments | Orchestrates post-hoc analysis; loads tasks+runs, calls metrics, writes results.json | `experiments/run_benchmark.py` |
| MCP Server | FastMCP stdio server exposing 8 tools for interactive benchmark access | `capstone_mcp/server.py`, `capstone_mcp/tools/` |
| FastAPI Backend | REST API serving tasks, runs, leaderboard, and results to the React frontend | `capstone-website/backend/main.py` |
| React Frontend | Single-page application for result visualization | `capstone-website/frontend/src/` |

## Pattern Overview

**Overall:** Research pipeline — offline data generation → API batch execution → dual scoring paths → visualization

**Key Characteristics:**
- Tasks are generated once by baseline computations and stored as static JSON; they are never computed at query time
- The benchmark runner and the formal evaluator are two separate scoring paths that use the same weight constants (N=M=A=C=R=0.20) — both paths must stay in sync
- `runs.jsonl` is append-only; resume safety is implemented by scanning completed (model_family, task_id) pairs at startup
- All Python scripts assume CWD = project root; absolute imports only

## Layers

**Baseline Layer:**
- Purpose: Compute analytically-correct ground truth values that define what the correct answer is for each task
- Location: `baseline/bayesian/`, `baseline/frequentist/`
- Contains: Statistical computation modules (conjugate updates, decision theory, MCMC solvers)
- Depends on: scipy, numpy, standard Python
- Used by: Task builders (`build_tasks_bayesian.py`, `build_tasks_advanced.py`)

**Data Layer:**
- Purpose: Static task specifications and run logs
- Location: `data/benchmark_v1/`, `data/synthetic/`, `experiments/results_v1/`
- Contains: `tasks.json` (136), `tasks_advanced.json` (35), `tasks_all.json` (171), `perturbations.json` (75), `runs.jsonl`, `results.json`
- Generated: Never edit task JSON files manually — regenerate with builder scripts
- Used by: Runner, evaluator, MCP server, FastAPI backend

**Runner Layer:**
- Purpose: Execute live API calls against all 5 LLM providers, parse responses, score on the fly, append records to `runs.jsonl`
- Location: `llm_runner/`
- Contains: `run_all_tasks.py` (CLI driver), `model_clients.py` (5 clients), `prompt_builder.py` (31 task type handlers), `response_parser.py` (scoring), `logger.py`
- Depends on: `data/benchmark_v1/tasks.json`, LLM API keys in `.env`
- Used by: Run from CLI; produces `experiments/results_v1/runs.jsonl`

**Evaluation Layer:**
- Purpose: Formal post-hoc scoring using typed dataclasses; produces `results.json`
- Location: `evaluation/`, `experiments/`
- Contains: `metrics.py` (scoring functions + dataclasses), `task_spec_schema.py` (loads tasks), `rubrics.py`, `error_taxonomy.py`, `run_benchmark.py` (entry point)
- Depends on: `runs.jsonl` + `tasks_all.json`
- Used by: Run manually after benchmark is complete

**Interface Layer:**
- Purpose: Expose benchmark data for interactive use and web display
- Location: `capstone_mcp/`, `capstone-website/`
- Contains: MCP server (8 tools, stdio transport) and React + FastAPI website
- Depends on: `tasks_all.json`, `runs.jsonl`, `results.json`

## Data Flow

### Primary Benchmark Run (end-to-end)

1. **Generate tasks** — `python -m baseline.bayesian.build_tasks_bayesian` → writes `data/benchmark_v1/tasks.json` (136 tasks)
2. **Generate advanced tasks** — `python -m baseline.bayesian.build_tasks_advanced` → writes `data/benchmark_v1/tasks_advanced.json` (35 tasks)
3. **Merge** — manual one-liner merges both into `data/benchmark_v1/tasks_all.json` (171 tasks)
4. **Load tasks** — `run_all_tasks.py:_load_tasks()` reads tasks JSON into list of dicts
5. **Check resume state** — `_load_completed()` scans existing `runs.jsonl`; returns set of `(model_family, task_id)` pairs to skip
6. **For each model × task** — `get_client(family)` returns the appropriate `BaseModelClient`
7. **Build prompt** — `build_prompt(task)` dispatches to one of 31 `_prompt_<type>()` functions in `prompt_builder.py`; returns formatted string
8. **Query LLM** — `client.query(prompt, task_id)` sends HTTP POST with retry logic; returns `{raw_response, input_tokens, output_tokens, latency_ms, error}`
9. **Score response** — `full_score(raw_response, task)` computes five components:
   - **N** (Numerical): `parse_answer()` extracts values after `ANSWER:` line; compares to `numeric_targets` with relative tolerance
   - **M** (Method/Structure): keyword-match against `required_structure_checks`
   - **A** (Assumption): keyword-match against `required_assumption_checks`
   - **C** (Confidence Calibration): `extract_confidence()` → `confidence_calibration_score()`
   - **R** (Reasoning Quality): regex patterns for 4 criteria × 0.25
   - Final: `0.20*N + 0.20*M + 0.20*A + 0.20*C + 0.20*R` (or rubric-only for CONCEPTUAL tasks)
10. **Append to JSONL** — `log_jsonl(output_path, record)` appends one JSON object per run to `experiments/results_v1/runs.jsonl`

### Post-Hoc Scoring (Path B)

1. `experiments/run_benchmark.py:main()` loads `tasks_all.json` via `evaluation/task_spec_schema.py:load_tasks_from_json()` → `Dict[str, TaskSpec]`
2. Reads `runs.jsonl` line by line via `load_runs_jsonl()`; skips error records and unknown task_ids; constructs `TaskRun` dataclass objects
3. Optionally applies LLM-as-Judge fallback via `evaluation/llm_judge.py` (for records where parsing failed)
4. `score_all_models(tasks, runs)` from `evaluation/metrics.py` groups runs by `(model_name, task_id)`, calls `score_task_with_perturbations()` per group
5. `aggregate_model_scores()` computes normalized scores by tier and difficulty
6. Writes `experiments/results_v1/results.json` — a dict with `model_aggregates` list and `task_scores` list

### RQ4 Perturbation Run

1. `data/synthetic/build_perturbations.py` generates `perturbations.json` (75 records = 25 base tasks × 3 perturbation types: rephrase/numerical/semantic)
2. `run_all_tasks.py --synthetic` loads `perturbations.json` instead of `tasks.json`; perturbation records carry pre-built prompts (no `build_prompt()` call needed)
3. Records are scored and appended to the same `runs.jsonl`

### Website Data Flow

1. FastAPI backend (`capstone-website/backend/main.py`) reads from `data/benchmark_v1/tasks_all.json` and `experiments/results_v1/runs.jsonl` on each request — no caching
2. Endpoints: `/api/tasks`, `/api/task/{task_id}`, `/api/results/summary`, `/api/leaderboard`, `/api/results/by_type`, `/api/status`
3. React frontend bundles static copies of key data files at build time: `src/data/tasks.json`, `src/data/results_summary.json`, `src/data/stats.json`
4. Visualizations are pre-generated R/Plotly files served as static assets from `frontend/public/visualizations/`

## Scoring Architecture — Two Parallel Paths

Both paths use **identical weights**: `N=0.20, M=0.20, A=0.20, C=0.20, R=0.20`

| | Path A (Runner) | Path B (Formal) |
|-|-----------------|-----------------|
| File | `llm_runner/response_parser.py` | `evaluation/metrics.py` |
| Called by | `run_all_tasks.py` during live runs | `experiments/run_benchmark.py` post-hoc |
| Input | `raw_response: str`, `task: dict` | `TaskRun` dataclass objects |
| Entry point | `full_score(raw_response, task) -> Dict` | `score_all_models(tasks, runs) -> Tuple` |
| Scoring | Inline keyword matching + regex | Checklist matching on pre-populated flags |
| Output | Score dict appended to `runs.jsonl` | `TaskScore` / `ModelAggregate` dataclasses → `results.json` |

**Critical rule:** Any change to scoring weights must be applied in both `evaluation/metrics.py:WEIGHTS` and `llm_runner/response_parser.py:W_N/W_M/W_A/W_C/W_R`.

## Key Abstractions

**TaskSpec (`evaluation/metrics.py`):**
- Purpose: Typed representation of a task for post-hoc scoring
- Fields: `task_id`, `tier`, `difficulty`, `required_structure_checks`, `required_assumption_checks`, `numeric_targets: List[NumericTarget]`
- Loaded by: `evaluation/task_spec_schema.py:load_tasks_from_json()`

**TaskRun (`evaluation/metrics.py`):**
- Purpose: Typed representation of one LLM execution result
- Fields: `model_name`, `task_id`, `run_id`, `extracted_numbers`, `structure_flags`, `assumption_flags`, `confidence_calib_score`, `reasoning_qual_score`
- Created by: `experiments/run_benchmark.py:load_runs_jsonl()`

**NumericTarget (`evaluation/metrics.py`):**
- Purpose: A single ground-truth value with tolerance bands
- Fields: `key`, `true_value`, `full_credit_tol`, `zero_credit_scale`
- Source: `numeric_targets` array in task JSON

**BaseModelClient (`llm_runner/model_clients.py`):**
- Purpose: Abstract base for all 5 LLM API clients
- Contract: `query(prompt: str, task_id: str) -> Dict` with keys `model, model_family, task_id, raw_response, input_tokens, output_tokens, latency_ms, error`
- Retry logic: 3 attempts, 5s/15s/30s waits on 429/connect/timeout; Gemini uses 30s/60s/120s + 15s inter-request delay

## Entry Points

**Benchmark runner:**
- Location: `llm_runner/run_all_tasks.py:main()` (also invokable as `python -m llm_runner.run_all_tasks`)
- Triggers: CLI with `--models`, `--tasks`, `--output`, `--task-types`, `--limit`, `--dry-run`, `--synthetic`, `--pert-types`, `--delay`
- Responsibilities: Load tasks, check resume state, iterate model × task, call prompt builder, call LLM client, score, log

**Post-hoc evaluator:**
- Location: `experiments/run_benchmark.py:main()` (also invokable as `python -m experiments.run_benchmark`)
- Triggers: Manual CLI invocation after runs complete
- Responsibilities: Load tasks + runs, optionally apply LLM judge, score all, write `results.json`

**MCP server:**
- Location: `capstone_mcp/server.py` (invokable as `python -m capstone_mcp.server`)
- Transport: stdio (FastMCP)
- Triggers: Claude Code MCP integration or direct subprocess

**FastAPI backend:**
- Location: `capstone-website/backend/main.py`
- Start: `uvicorn backend.main:app --reload` from `capstone-website/` directory
- Port: 8000

**React frontend:**
- Location: `capstone-website/frontend/`
- Start: `npm run dev` from `capstone-website/frontend/` directory
- Port: 3000 (Vite dev server)

## Architectural Constraints

- **Working directory:** All Python scripts must be run from project root — absolute imports rely on this (e.g., `from llm_runner.logger import log_jsonl`)
- **No vendor SDKs:** All 5 LLM clients use `httpx` directly — no `anthropic`, `openai`, or `google-generativeai` packages
- **Append-only log:** `experiments/results_v1/runs.jsonl` must never be truncated; resume logic depends on scanning it at startup
- **Task JSON immutability:** `data/benchmark_v1/tasks.json`, `tasks_advanced.json`, and `tasks_all.json` must never be edited manually — always regenerate with builder scripts
- **Dual scoring sync:** Weights defined in both `evaluation/metrics.py:WEIGHTS` and `llm_runner/response_parser.py` must stay identical
- **Seeded reproducibility:** All Phase 2 advanced method solvers call `np.random.seed(42)` in `solve()`; ground truth values are MC estimates, not analytic
- **Schema heterogeneity:** `runs.jsonl` contains an old placeholder record with a different schema; all analysis code must handle this

## Anti-Patterns

### Editing task JSON files directly
**What happens:** A developer edits `data/benchmark_v1/tasks.json` by hand to fix a typo or adjust a tolerance.
**Why it's wrong:** The file is the output of `build_tasks_bayesian.py`. Manual edits are lost the next time the builder runs, and introduce inconsistency between the JSON and the baseline computation.
**Do this instead:** Edit the relevant `gen_<type>_tasks()` function in `baseline/bayesian/build_tasks_bayesian.py` and re-run `python -m baseline.bayesian.build_tasks_bayesian`.

### Changing weights in only one scoring file
**What happens:** `WEIGHTS` in `evaluation/metrics.py` is updated but `W_N/W_M/W_A/W_C/W_R` in `llm_runner/response_parser.py` is not (or vice versa).
**Why it's wrong:** Path A (live runs) and Path B (post-hoc) produce different scores, making comparison meaningless. The cross-reference comment in both files exists specifically to prevent this.
**Do this instead:** Always update both files together. See CLAUDE.md §7 and §10 for the canonical process.

### Running scripts from a subdirectory
**What happens:** `cd llm_runner && python run_all_tasks.py`
**Why it's wrong:** All imports use project-root-relative paths (`from llm_runner.logger import ...`). Running from a subdirectory causes `ModuleNotFoundError`.
**Do this instead:** Always run from the project root: `python -m llm_runner.run_all_tasks` or `python llm_runner/run_all_tasks.py` with CWD at project root.

### Truncating runs.jsonl to fix errors
**What happens:** Gemini error records (score=0) are deleted from `runs.jsonl` to clean up stats.
**Why it's wrong:** The resume logic in `_load_completed()` considers only records with `raw_response` AND no `error` as complete. Truncating the file does not break resumption, but it invalidates historical audit trails.
**Do this instead:** Leave error records in place. Filter them out in analysis code using `if obj.get("error"): continue` (as `run_benchmark.py` already does).

## Error Handling

**Strategy:** Non-fatal errors — API failures are recorded as error records in `runs.jsonl` with score=0; the runner continues to the next task.

**Patterns:**
- Missing API key: produces an error record (`error` field populated); no exception raised to the caller
- HTTP 429: retried up to 3× with exponential backoff; if all retries fail, logged as error record
- HTTP 400/401/403/404: not retried; logged immediately as error record
- JSON decode errors in `runs.jsonl`: silently skipped by all readers
- Unknown `task_id` in `runs.jsonl`: silently skipped by `run_benchmark.py:load_runs_jsonl()`

## Cross-Cutting Concerns

**Logging:** `llm_runner/logger.py:log_jsonl()` — single function, append-only writes to JSONL; no log framework used elsewhere
**Validation:** `evaluation/task_validator.py` exists but is not called in the main pipeline; task JSON validated implicitly by schema loading
**Authentication:** API keys loaded from `.env` via `python-dotenv` at the top of `run_all_tasks.py`; missing key produces an error record per task, not a startup crash

---

*Architecture analysis: 2026-04-26*
