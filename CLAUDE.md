# CLAUDE.md

Single source of truth. Overrides comments, docstrings, and prior summaries.

---

## Project

DS 299 Capstone — benchmarking LLMs on Bayesian/inferential statistical reasoning (RQ1–RQ5).

- **171 tasks**: 136 Phase 1 (31 types) + 35 Phase 2 (7 computational Bayes types)
- **5 models**: claude, gemini, chatgpt, deepseek, mistral
- **Scoring**: NMACR literature-derived weights `A=0.30, R=0.25, M=0.20, C=0.15, N=0.10` (two paths — keep in sync). Defense: `evaluation/metrics.py` docstring (10-paper trail).
- **Stack**: Python 3.11 + FastMCP | React + Vite | FastAPI | httpx (no vendor SDKs)
- MCMC out of scope for benchmark tasks; used as ground-truth solvers only

---

## Commands

Run all from project root.

```bash
source .venv/bin/activate

# Task generation (DO NOT edit output files manually)
python -m baseline.bayesian.build_tasks_bayesian        # → tasks.json (136)
python -m baseline.bayesian.build_tasks_advanced        # → tasks_advanced.json (35)
python3 -c "
import json
t1=json.load(open('data/raw_data/benchmark_v1/tasks.json'))
t2=json.load(open('data/raw_data/benchmark_v1/tasks_advanced.json'))
all_=t1+t2
assert len(set(t['task_id'] for t in all_))==len(all_)
json.dump(all_,open('data/raw_data/benchmark_v1/tasks_all.json','w'),indent=2)
"  # → tasks_all.json (171)

# Benchmark runs
python -m llm_runner.run_all_tasks --models claude gemini chatgpt deepseek mistral
python -m llm_runner.run_all_tasks --models claude --dry-run --limit 3
python -m llm_runner.run_all_tasks --models claude --task-types DISC_MEDIAN MARKOV
python -m llm_runner.run_all_tasks --models claude gemini --synthetic
python -m llm_runner.run_all_tasks --models claude --synthetic --pert-types numerical
python scripts/generate_perturbations_full.py          # regenerate perturbations_all.json (canonical, 473 perturbations)

# Scoring & analysis
python -m experiments.run_benchmark
python scripts/analyze_errors.py                        # E1–E9 taxonomy, up to 100 LLM calls
python scripts/analyze_errors.py --no-llm               # rule-based only
python scripts/analyze_perturbations.py                 # RQ4 → rq4_analysis.json
python scripts/summarize_results.py                     # → results_summary.json

# Services
python -m capstone_mcp.server                           # MCP server
cd capstone-website && uvicorn backend.main:app --reload  # FastAPI :8000
cd capstone-website/frontend && npm run dev             # Vite :3000

# R visualizations (run from report_materials/r_analysis/)
Rscript run_all.R                                       # 18 scripts → figures/ + interactive/

# Quality
ruff check .
pytest baseline/frequentist/test_frequentist.py capstone_mcp/test_server.py -v
```

---

## Environment Variables

Copy `.env.example` → `.env`. Missing key → error record (no exception).

| Variable | Model |
|---|---|
| `ANTHROPIC_API_KEY` | claude |
| `GEMINI_API_KEY` | gemini |
| `OPENAI_API_KEY` | chatgpt |
| `DEEPSEEK_API_KEY` | deepseek |
| `MISTRAL_API_KEY` | mistral |

---

## Model Clients

`llm_runner/model_clients.py` — all use `httpx`, no vendor SDKs.

| Family | Model string | Env var |
|---|---|---|
| `claude` | `claude-sonnet-4-5` | `ANTHROPIC_API_KEY` |
| `gemini` | `gemini-2.5-flash` | `GEMINI_API_KEY` |
| `chatgpt` | `gpt-4.1` | `OPENAI_API_KEY` |
| `deepseek` | `deepseek-chat` | `DEEPSEEK_API_KEY` |
| `mistral` | `mistral-large-latest` | `MISTRAL_API_KEY` |

**Shared**: `_MAX_TOKENS=1024`, `_TIMEOUT=60s`, `_SLEEP_S=1s`. Retry: 3 attempts, 5s/15s/30s on 429/connect/timeout. Non-retryable: 4xx.

**Gemini**: `_GEMINI_RETRY_WAITS=[30,60,120]`, `_GEMINI_SLEEP_S=15s`. Two failure modes: RPM (fixable with delays) vs RPD daily quota (~250 free tier) — quota resets midnight Pacific, no retry helps.

**System prompt** (all models): `"You are an expert in Bayesian statistics and probability theory. Solve problems step by step, showing all working. Always end your response with your final answer on its own line in the format: ANSWER: <value1>, <value2>, ..."`

---

## Scoring

Two paths — **weights must match both files** (`evaluation/metrics.py` and `llm_runner/response_parser.py`):

`NMACR_WEIGHTS = A=0.30, R=0.25, M=0.20, C=0.15, N=0.10` (literature-derived; sole canonical scheme since Approach A, 2026-05-03). Defense in `evaluation/metrics.py` docstring cites Du 2025, Boye & Moell 2025, Yamauchi 2025, ReasonBench 2025, Wei 2022, Chen 2022, Bishop 2006, Nagarkar 2026, FermiEval 2025, Liu 2025. Full literature trail in `llm-stats-vault/90-archive/audit/methodology_continuity.md` §"NMACR weighting".

**Path A** (`response_parser.py`) — live runner:
- `full_score(raw_response: str, task: dict) -> Dict`
- CONCEPTUAL tasks: `1.0 × rubric_score`
- Tasks with numeric + rubric: `0.6 × numeric + 0.4 × rubric`
- Pass threshold: `final_score >= 0.5`
- C: `extract_confidence()` → overconfident-on-wrong penalized 1.5×, underconfident-on-right 0.8×
- R: 4 criteria × 0.25 (shows work / identifies model / states formula / interprets result)

**Path B** (`evaluation/metrics.py`) — post-hoc:
- `score_all_models(tasks, runs)` operates on `TaskRun` dataclass objects
- C/R read from `confidence_calib_score` / `reasoning_qual_score` fields (default 0.5)
- Tier-5 multiplier: 1.5× (no tier-5 tasks exist)

**`runs.jsonl` schema**:
```
run_id, timestamp, task_id, task_type, tier, difficulty,
model, model_family, prompt, raw_response,
parsed_values, ground_truth,
numeric_score, structure_score, assumption_score,
confidence_score, reasoning_score,
final_score, pass, answer_found, length_match,
input_tokens, output_tokens, latency_ms, error
```
Note: file contains one old placeholder record with different schema — handle heterogeneity.

**Result files**:
- `data/processed_data/results_v1/runs.jsonl` — append-only, never truncate
- `data/processed_data/results_v1/results.json` — dict: `model_aggregates` + `task_scores`

---

## Tasks

**Phase 1** (`data/raw_data/benchmark_v1/tasks.json`): 136 tasks, 31 types. Do not edit — regenerate.

**Phase 2** (`data/raw_data/benchmark_v1/tasks_advanced.json`): 35 tasks. Do not edit — regenerate.

| Type | Count | Tolerance |
|---|---|---|
| GIBBS, MH, HMC, RJMCMC, HIERARCHICAL | 5 each | 0.05 |
| VB, ABC | 5 each | 0.10 |

Phase 2 solvers use `np.random.seed(42)` — true values are seeded MC estimates, not analytic.

**Task spec schema**:
```json
{
  "task_id": "DISC_MEDIAN_01",
  "tier": 2,
  "difficulty": "basic",
  "inputs": {...},
  "numeric_targets": [{"key": "median", "value": 0.4, "full_credit_tol": 0.01, "zero_credit_scale": 0.10}],
  "required_structure_checks": ["shows_posterior_pmf"],
  "required_assumption_checks": ["discrete_support_stated"],
  "prompt_template": "..."
}
```

**Perturbations** (`data/raw_data/synthetic/perturbations_all.json`, 473 records covering all 171 base tasks): `rephrase` (same math, reworded) / `numerical` (changed numbers, recomputed) / `semantic` (same math, new framing). Composition: 75 hand-authored seed records + 398 LLM-generated v2 records (v2 ids end with `_v2`). Regenerate with `python scripts/generate_perturbations_full.py`.

**v1 perturbation deprecation (2026-05-04, Phase 1.8).** The legacy `data/raw_data/synthetic/perturbations.json` (75 hand-authored records) is deprecated as a data source — its records are preserved verbatim inside `perturbations_all.json`. The file is RETAINED on disk because 5 consumer scripts (`scripts/krippendorff_agreement.py`, `keyword_vs_judge_agreement.py`, `combined_pass_flip_analysis.py`, `calibration_analysis.py`, `recompute_downstream.py`), `capstone-website/backend/main.py`, and the R pipeline use it as the canonical list of v1-pert task_ids to filter out of `runs.jsonl` (Strategy C). Future cleanup: refactor consumers to derive the v1 list from `perturbations_all.json` (suffix-match `task_id` not ending in `_v2`), then delete `perturbations.json`. Generator `data/raw_data/synthetic/build_perturbations.py` is no longer the canonical generator — `scripts/generate_perturbations_full.py` is. See `llm-stats-vault/90-archive/audit/recompute_log.md` §"Phase 1.8".

---

## Key Gotchas

- `fisher_information(dist="uniform")` **intentionally raises `NotImplementedError`** — Uniform is not a regular exponential family. Not a bug.
- `runs.jsonl` is **append-only** — never truncate or overwrite.
- Task JSON files (`tasks.json`, `tasks_advanced.json`, `tasks_all.json`) — **never edit manually**.
- All scripts **must run from project root** for imports to resolve.
- Scoring weights **must be updated in both** `evaluation/metrics.py` and `llm_runner/response_parser.py`.
- Website: root `motion.div` has `filter:'blur(0px)'` → creates CSS stacking context → breaks `position:fixed` for descendants. Modals/lightboxes must be rendered as siblings outside that div.

---

## Conventions

**Naming**:
- Task IDs: `TYPE_NN` (e.g. `DISC_MEDIAN_01`, padded 2 digits)
- Model family names lowercase: `claude`, `gemini`, `chatgpt`, `deepseek`, `mistral`

**Imports**: absolute only (`from llm_runner.logger import log_jsonl`). No relative imports outside packages.

**Tests**: `capstone_mcp/test_server.py` (29), `baseline/frequentist/test_frequentist.py` (24). No tests for `evaluation/`, `baseline/bayesian/`, `llm_runner/`.

**Adding a model client**:
1. Subclass `BaseModelClient` in `llm_runner/model_clients.py`
2. Set `model`, `model_family` attrs; implement `query(prompt, task_id) -> Dict`
3. Return keys: `model, model_family, task_id, raw_response, input_tokens, output_tokens, latency_ms, error`
4. Register in `_CLIENTS`; add to `--models` choices; add key to `.env.example`

**Adding a task type**:
1. `gen_<type>_tasks()` in `baseline/bayesian/build_tasks_bayesian.py`
2. Ground-truth fn in `baseline/bayesian/ground_truth.py` if needed
3. `_prompt_<type>()` in `llm_runner/prompt_builder.py`; register in `_DISPATCH`
4. Regenerate: `python -m baseline.bayesian.build_tasks_bayesian`

**User Study hardening** (`capstone-website/backend/user_study.py`):
- Concurrency: `asyncio.Semaphore(3)` — max 3 parallel 5-model fan-outs (15 in-flight LLM calls)
- Per-model timeout: 60s (`TIMEOUT = 60.0`)
- Rate limits: 10/hour + 3/minute per IP on `POST /api/user-study`; 30/hour per IP on `POST /api/user-study/vote`
- Atomic JSON writes: `_atomic_write_json()` writes to `.tmp` then `os.replace()` — crash-safe on all 5 paths
- Partial-failure tolerance: `return_exceptions=True` on gather; returns 200 with up to 4 working models; raises 502 only if all 5 fail
