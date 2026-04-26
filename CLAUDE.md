# CLAUDE.md — Ground Truth Reference

This file is the single source of truth for any Claude Code session working on this project. It reflects verified state as of the last full audit. Do not trust comments, docstrings, or prior summaries over this file.

---

## 1. Project Overview

**DS 299 Capstone** — benchmarking LLMs on inferential and Bayesian statistical reasoning. Five research questions (RQ1–RQ5) cover numerical accuracy, method selection, assumption compliance, robustness, and confidence calibration.

- 136 benchmark tasks across 31 task types, 4 tiers, 3 difficulty levels (Phase 1)
- **35 Phase 2 advanced tasks** across 7 computational Bayes types (GIBBS×5, MH×5, HMC×5, RJMCMC×5, VB×5, ABC×5, HIERARCHICAL×5)
- **171 total tasks** in `data/benchmark_v1/tasks_all.json` (136 + 35)
- 5 LLM clients: Claude, Gemini, ChatGPT, DeepSeek, Mistral
- Single canonical scoring weight set: N=0.20, M=0.20, A=0.20, C=0.20, R=0.20 (all five components equal and active)
- MCP server for interactive querying and scoring
- React + FastAPI website for result visualization
- MCMC methods are explicitly **out of scope** (`bayesian_scope.md`) for benchmark tasks; implemented as baseline ground-truth solvers only

---

## 2. How to Run Things

```bash
# Activate virtual environment (Python 3.11)
source .venv/bin/activate

# Regenerate tasks.json from ground-truth computations
python -m baseline.bayesian.build_tasks_bayesian

# Regenerate Phase 2 advanced tasks (35 tasks → tasks_advanced.json)
python -m baseline.bayesian.build_tasks_advanced

# Run benchmark against one or more models (requires API keys in env)
python -m llm_runner.run_all_tasks --models claude gemini chatgpt deepseek mistral

# Run Phase 2 advanced tasks (35 tasks × 5 models = 175 runs)
python -m llm_runner.run_all_tasks --models claude chatgpt deepseek mistral \
    --tasks data/benchmark_v1/tasks_advanced.json
python -m llm_runner.run_all_tasks --models gemini --delay 5 \
    --tasks data/benchmark_v1/tasks_advanced.json

# Dry-run: print prompts without API calls
python llm_runner/run_all_tasks.py --models claude --dry-run --limit 3

# Filter by task type
python llm_runner/run_all_tasks.py --models claude --task-types DISC_MEDIAN MARKOV

# Run RQ4 perturbation benchmark (75 tasks = 25 base × 3 types)
python llm_runner/run_all_tasks.py --models claude gemini --synthetic
python llm_runner/run_all_tasks.py --models claude --synthetic --pert-types numerical
python llm_runner/run_all_tasks.py --models claude --synthetic --dry-run --limit 5

# Regenerate perturbations.json from scratch
python data/synthetic/build_perturbations.py

# Run scoring pipeline (requires experiments/results_v1/runs.jsonl to exist)
python -m experiments.run_benchmark

# Start MCP server
python -m capstone_mcp.server

# Start website backend (FastAPI, port 8000)
cd capstone-website && uvicorn backend.main:app --reload

# Start website frontend (Vite, port 3000)
cd capstone-website/frontend && npm run dev

# Lint
ruff check .

# Run all tests
pytest baseline/frequentist/test_frequentist.py capstone_mcp/test_server.py -v
```

All scripts must be run from the project root so imports resolve.

### Required environment variables

Copy `.env.example` to `.env` and fill in keys. Missing key produces an error record — no exception.

| Variable | Used by |
|---|---|
| `ANTHROPIC_API_KEY` | ClaudeClient |
| `GEMINI_API_KEY` | GeminiClient |
| `OPENAI_API_KEY` | ChatGPTClient |
| `DEEPSEEK_API_KEY` | DeepSeekClient |
| `MISTRAL_API_KEY` | MistralClient |

---

## 3. Architecture Map

```
baseline/
  bayesian/           # Closed-form Bayesian ground-truth computations
    advanced_methods.py        # 7 computational Bayes solvers (Gibbs/MH/HMC/RJMCMC/VB/ABC/Hierarchical)
    build_tasks_advanced.py    # Generate 35 Phase 2 tasks → tasks_advanced.json
  frequentist/        # Frequentist baselines
    test_frequentist.py  # 24 tests for fisher_information + order_statistics
capstone_mcp/
  server.py           # FastMCP server exposing 8 tools
  test_server.py      # 29 tests, all passing
capstone-website/
  frontend/src/       # React + Vite UI (App.jsx, App.css)
    pages/VizGallery.jsx         # Results & Visualizations page (leaderboard + viz gallery)
    data/visualizations.js       # Manifest of 15 R-generated visualizations
    components/ParamTooltip.jsx  # Portal-based tooltip for task parameters
    components/Tooltip/TooltipPortal.jsx  # createPortal tooltip (bypasses modal overflow)
    data/TooltipMap.js           # ~130 Bayesian stat term definitions
  frontend/public/visualizations/
    png/             # 15 static PNGs + 1 GIF (15_bar_race.gif) copied from report_materials
    interactive/     # 14 Plotly HTML files + _files/ subdirs copied from report_materials
  backend/            # FastAPI serving runs.jsonl data
data/
  benchmark_v1/
    tasks.json          # 136 Phase 1 task specs (DO NOT edit — regenerate with build_tasks_bayesian)
    tasks_advanced.json # 35 Phase 2 task specs (DO NOT edit — regenerate with build_tasks_advanced)
    tasks_all.json      # 171 merged tasks (136 + 35, DO NOT edit — regenerate by merging both)
  synthetic/
    perturbations.json      # 75 perturbations: 25 base tasks × 3 types (rephrase/numerical/semantic)
    build_perturbations.py  # Generation script — run to regenerate
evaluation/
  metrics.py          # Formal scoring: weights N=0.60, M=0.20, C=0.00, A=0.20, R=0.00
  task_spec_schema.py # Loads tasks.json → Dict[str, TaskSpec]
  rubrics.py          # Structure/assumption/conceptual rubric key constants
  error_taxonomy.py   # ErrorAnnotation dataclass
experiments/
  run_benchmark.py    # Entry point: loads tasks + runs, scores, writes results
  results_v1/
    runs.jsonl        # Append-only LLM run log (created by run_all_tasks.py)
    results.json      # Scoring output (created by run_benchmark.py)
llm_runner/
  run_all_tasks.py    # CLI benchmark driver
  model_clients.py    # 5 API clients (httpx, no SDKs)
  prompt_builder.py   # build_prompt(task) + parse_answer(response)
  response_parser.py  # full_score(raw_response, task) — runner's scoring path
  logger.py           # log_jsonl() append-only JSONL writer
.env.example          # API key template — copy to .env
literature/           # Background reading
website/              # (older static site, separate from capstone-website/)
```

---

## 4. Baseline Modules

### `baseline/bayesian/conjugate_models.py`
- `beta_binomial_update(alpha, beta, x, n) -> BetaBinomialPosterior`
- `gamma_poisson_update(alpha, rate, counts) -> GammaPoissonPosterior`
- `normal_known_var_update(mu0, tau0_2, sigma2, data) -> NormalKnownVarPosterior`
- `binomial_uniform_prior_update(x, n) -> BetaBinomialPosterior`
- `flat_prior(theta, a, b) -> float`
- `improper_prior_location(mu) -> float`
- `improper_prior_scale(sigma) -> float`
- `posterior_with_flat_prior(x, n) -> Dict`
- `improper_beta_prior_update(s, n) -> Dict`
- `jeffreys_prior_binomial(theta) -> float`
- `jeffreys_prior_poisson(lam) -> float`
- `jeffreys_prior_normal_mean(mu) -> float`
- `jeffreys_update_binomial(x, n) -> Dict`
- `mle_vs_map(...) -> Dict`
- `verify_gamma_additive(...)`, `verify_beta_gamma_connection(...)`, `verify_chi2_additive(...)`

### `baseline/bayesian/normal_gamma.py`
- `NormalGammaPosterior` (dataclass with `.mu_n, .kappa_n, .alpha_n, .beta_n`, derived `.marginal_mean`, `.marginal_var`, `.precision_mean`, `.precision_var`)
- `normal_gamma_update(mu0, kappa0, alpha0, beta0, data) -> NormalGammaPosterior`

### `baseline/bayesian/dirichlet_multinomial.py`
- `dirichlet_multinomial_update(alpha, counts) -> Dict`
- `dirichlet_multinomial_logpmf(counts, alpha) -> float`
- `dirichlet_multinomial_pmf(counts, alpha) -> float`
- `multinomial_pmf(n, k, p) -> float`
- `multinomial_logpmf(n, k, p) -> float`
- `multinomial_sample(n, p, seed) -> List[int]`
- `dirichlet_pdf(p, alpha) -> float`
- `is_uniform_dirichlet(alpha, tol) -> bool`
- `dirichlet_from_gamma(shapes, scales) -> List[float]`

### `baseline/bayesian/posterior_predictive.py`
- `beta_binomial_predictive_pmf(k, m, alpha_post, beta_post) -> float`
- `gamma_poisson_predictive_pmf(y, alpha_post, beta_post) -> float`
- `dirichlet_multinomial_predictive_pmf(counts, alpha_post) -> float`
- `dirichlet_predictive_next(alpha_post) -> List[float]`
- `normal_known_var_predictive_pdf(y_new, mu_n, tau_n2, sigma2) -> float`
- `normal_gamma_predictive_pdf(y_new, mu_n, kappa_n, alpha_n, beta_n) -> float`
- `posterior_predictive_check(...)`, `posterior_predictive_check_beta_binomial(...)`

### `baseline/bayesian/bayes_estimators.py`
- `bayes_estimator_from_beta(alpha, beta, loss) -> BayesEstimator`
- `bayes_estimator_from_gamma_shape_rate(alpha, rate, loss) -> BayesEstimator`
- `bayes_estimator_from_normal(mu, var, loss) -> BayesEstimator`
- `bayes_estimator_from_student_t(loc, scale, df, loss) -> BayesEstimator`
- `beta_median_approx(alpha, beta) -> BayesEstimator`
- `discrete_posterior_median(values, probs) -> float`
- `asymmetric_linear_bayes_estimator(alpha, beta, c_over, c_under) -> BayesEstimator`
- `Loss` enum: `QUADRATIC`, `ABSOLUTE`, `ZERO_ONE`

### `baseline/bayesian/intervals.py`
- `beta_credible_interval(alpha, beta, level=0.95) -> CredibleInterval`
- `gamma_credible_interval(alpha, rate, level=0.95) -> CredibleInterval`
- `normal_credible_interval(mu, var, level=0.95) -> CredibleInterval`
- `hpd_credible_interval(dist, params, level=0.95) -> CredibleInterval`
- `beta_hpd_interval(alpha, beta, level=0.95) -> CredibleInterval`
- `normal_hpd_interval(mu, var, level=0.95) -> CredibleInterval`
- `compare_ci_vs_credible_normal(...) -> Dict`

### `baseline/bayesian/decision_theory.py`
- `bayes_estimator_from_samples(posterior_samples, loss) -> BayesEstimatorResult`
- `mse_risk(theta_true, estimator_values) -> float`
- `analytical_bayes_risk_quadratic(posterior_var) -> float`
- `discrete_bayes_risk(risk_values, prior_probs) -> float`
- `bias_variance_decomposition(theta_true, estimator_values) -> dict`
- `general_risk(loss_fn, theta_true, estimator_values) -> float`
- `minimax_risk(loss_fn, estimators, thetas) -> Dict`

### `baseline/bayesian/ground_truth.py`
- `gt_beta_binomial(alpha, beta, x, n) -> Dict`
- `gt_gamma_poisson(alpha, rate, counts) -> Dict`
- `gt_normal_known_var(mu0, tau0_2, sigma2, data) -> Dict`
- `gt_normal_gamma_precision(mu0, kappa0, alpha0, beta0, data) -> Dict`
- `gt_dirichlet_multinomial(alpha, counts) -> Dict`
- `gt_bayes_estimator_beta(alpha_post, beta_post, loss) -> Dict`
- `gt_bayes_estimator_gamma(alpha_post, rate_post, loss) -> Dict`
- `gt_bayes_estimator_normal(mu, var, loss) -> Dict`
- `gt_bayes_estimator_student_t(loc, scale, df, loss) -> Dict`

### `baseline/frequentist/fisher_information.py`
- `fisher_information(dist, theta, n=1) -> float`
  - Supported: `"binomial"`, `"poisson"`, `"normal"`, `"exponential"`, `"normal_var"`, `"gamma_rate"`
  - **`dist="uniform"` intentionally raises `NotImplementedError`** — Uniform is not a regular exponential family; Fisher information / RC bound do not apply. This is theoretically correct, not a bug.
- `rao_cramer_bound(fisher_info, bias_deriv=0.0) -> float`
- `estimator_bias(estimator_fn, theta, n, n_sim) -> float`
- `is_efficient(estimator_variance, fisher_info, bias_deriv, tol) -> bool`
- `is_exponential_family(dist) -> Dict`
- `log_likelihood_derivative(dist, theta, data) -> float`
- `verify_rao_cramer(dist, theta, n, n_sim) -> Dict`
- `verify_mle_efficiency(dist, theta, n, n_sim) -> Dict`
- `sufficient_statistic(dist) -> Dict`
- `neyman_factorization(dist, statistic) -> Dict`

### `baseline/frequentist/order_statistics.py`

All five order-statistic functions now support `dist="uniform"` (analytical), `dist="exponential"` (analytical CDF/PDF), and `dist="normal"` (via scipy.stats). Pass `params={"rate": float}` for exponential or `params={"mu": float, "sigma": float}` for normal.

- `order_statistic_pdf(y, k, n, dist="uniform", params=None) -> float`
- `min_order_statistic_cdf(x, n, dist="uniform", params=None) -> float`
- `max_order_statistic_cdf(x, n, dist="uniform", params=None) -> float`
- `joint_min_max_density(x, y, n, dist="uniform", params=None) -> float`
- `range_cdf(x, n, dist="uniform", params=None) -> float` — uniform uses analytical formula; others use scipy.integrate.quad
- `uniform_range_distribution(n) -> Dict` — simulation-based verification that R ~ Beta(n-1, 2)

### `baseline/frequentist/regression.py`
- `ols_estimators(x, y) -> Dict[str, float]`
- `residual_variance(x, y) -> float`
- `credibility_intervals(x, y, alpha) -> Dict`

### `baseline/frequentist/sampling.py`
- `box_muller_standard(u, v) -> Tuple[float, float]`
- `box_muller_sample(n, mu, sigma, seed) -> List[float]`
- `verify_box_muller(...) -> Dict`

### `baseline/frequentist/uniform_estimators.py`
- `unbiased_estimator_uniform(data) -> Dict`
- `mle_uniform_analytics(data, theta_true) -> Dict`
- `optimal_scaled_estimator_uniform(n, theta_true) -> Dict`
- `compare_mse(n, theta_true) -> Dict`

---

## 5. Benchmark Tasks

**171 tasks** total across two phases.

### Phase 1: 136 tasks
Stored in `data/benchmark_v1/tasks.json`. **Do not edit manually** — regenerate with `python -m baseline.bayesian.build_tasks_bayesian`.

### Phase 2: 35 advanced computational Bayes tasks
Stored in `data/benchmark_v1/tasks_advanced.json`. **Do not edit manually** — regenerate with `python -m baseline.bayesian.build_tasks_advanced`.

| Task Type | Count | Baseline module | Tolerance |
|---|---|---|---|
| GIBBS | 5 | `advanced_methods.GibbsSampler` | 0.05 |
| MH | 5 | `advanced_methods.MetropolisHastings` | 0.05 |
| HMC | 5 | `advanced_methods.HamiltonianMC` | 0.05 |
| RJMCMC | 5 | `advanced_methods.RJMCMC` | 0.05 |
| VB | 5 | `advanced_methods.VariationalBayes` | 0.10 |
| ABC | 5 | `advanced_methods.ABCMethod` | 0.10 |
| HIERARCHICAL | 5 | `advanced_methods.HierarchicalBayes` | 0.05 |

All Phase 2 solvers call `np.random.seed(42)` in `solve()` for reproducibility. True values are MC estimates (seeded), not analytic — this is intentional for computational methods.

**Merged file:** `data/benchmark_v1/tasks_all.json` (171 tasks = Phase 1 + Phase 2). Regenerate merge:
```bash
python3 -c "
import json
with open('data/benchmark_v1/tasks.json') as f: t1 = json.load(f)
with open('data/benchmark_v1/tasks_advanced.json') as f: t2 = json.load(f)
all_ = t1 + t2
assert len(set(t['task_id'] for t in all_)) == len(all_)
with open('data/benchmark_v1/tasks_all.json', 'w') as f: json.dump(all_, f, indent=2)
print(f'Merged {len(t1)} + {len(t2)} = {len(all_)} tasks')
"
```

### Phase 1 task type breakdown (31 types)

### Task type breakdown (31 types)

| Task Type | Count | Baseline module |
|---|---|---|
| BAYES_FACTOR | 5 | `ground_truth.py` (log marginal likelihood ratio) |
| BAYES_REG | 5 | `conjugate_models.py` (Bayesian linear regression) |
| BAYES_RISK | 5 | `decision_theory.py` |
| BETA_BINOM | 1 | `conjugate_models.py` |
| BIAS_VAR | 5 | `decision_theory.py` |
| BINOM_FLAT | 5 | `conjugate_models.py` |
| BOX_MULLER | 5 | `sampling.py` |
| CI_CREDIBLE | 5 | `intervals.py` |
| CONCEPTUAL | 10 | rubric-only, no numeric targets |
| DIRICHLET | 1 | `dirichlet_multinomial.py` |
| DISC_MEDIAN | 5 | `bayes_estimators.py` |
| FISHER_INFO | 5 | `fisher_information.py` — all tasks use binomial/poisson/normal (no stubs hit) |
| GAMBLER | 3 | Markov chain (gambler's ruin) |
| GAMMA_POISSON | 1 | `conjugate_models.py` |
| HPD | 5 | `intervals.py` |
| JEFFREYS | 5 | `conjugate_models.py` |
| LOG_ML | 5 | marginal likelihood computations |
| MARKOV | 5 | Markov chains |
| MINIMAX | 5 | `decision_theory.py` |
| MLE_EFFICIENCY | 3 | `fisher_information.py` |
| MLE_MAP | 5 | `conjugate_models.py` |
| MSE_COMPARE | 5 | `decision_theory.py` |
| NORMAL_GAMMA | 1 | `normal_gamma.py` |
| OPT_SCALED | 5 | `uniform_estimators.py` |
| ORDER_STAT | 5 | `order_statistics.py` — all tasks use `dist="uniform"` |
| PPC | 5 | `posterior_predictive.py` |
| RANGE_DIST | 3 | `order_statistics.py` — all tasks use `dist="uniform"` |
| RC_BOUND | 5 | `fisher_information.py` |
| REGRESSION | 5 | `regression.py` |
| STATIONARY | 3 | Markov stationary distributions |
| UNIFORM_MLE | 5 | `uniform_estimators.py` |

### Tier breakdown

| Tier | Count | Multiplier |
|---|---|---|
| 1 | 9 | 1.0× |
| 2 | 45 | 1.0× |
| 3 | 69 | 1.0× |
| 4 | 13 | 1.0× |
| 5 | 0 | 1.5× (stress tier — no tasks yet) |

### Difficulty breakdown

| Difficulty | Count |
|---|---|
| basic | 28 |
| intermediate | 82 |
| advanced | 26 |

### Task spec schema (per task in tasks.json)

```json
{
  "task_id": "DISC_MEDIAN_01",
  "tier": 2,
  "difficulty": "basic",
  "inputs": {...},
  "numeric_targets": [{"key": "median", "value": 0.4, "full_credit_tol": 0.01, "zero_credit_scale": 0.10}],
  "required_structure_checks": ["shows_posterior_pmf", "identifies_median"],
  "required_assumption_checks": ["discrete_support_stated"],
  "prompt_template": "..."
}
```

### Perturbation spec schema (per record in perturbations.json)

```json
{
  "task_id": "BINOM_FLAT_01_numerical",
  "base_task_id": "BINOM_FLAT_01",
  "perturbation_type": "numerical",
  "task_type": "BINOM_FLAT",
  "tier": 1,
  "difficulty": "basic",
  "prompt": "...",
  "numeric_targets": [{"key": "alpha_post", "true_value": 6.0, ...}],
  "required_structure_checks": ["..."],
  "required_assumption_checks": ["..."],
  "perturbation_note": "x=5, n=12 instead of x=3, n=10; ..."
}
```

**Perturbation types:**
- `rephrase` — same inputs and answers, reworded prompt (tests prompt sensitivity)
- `numerical` — changed numbers, recomputed ground-truth answers (tests generalisation)
- `semantic` — same math, new real-world framing (tests context robustness)

**Stats:** 75 total = 25 base tasks × 3 types; 25 of each type.
**Runner:** `--synthetic` loads `perturbations.json`; `--pert-types rephrase numerical semantic` filters by type.

---

## 6. Model Clients

File: `llm_runner/model_clients.py`. All clients use `httpx` directly — no vendor SDKs.

| Family name | Class | Exact model string | API key env var | Endpoint |
|---|---|---|---|---|
| `claude` | `ClaudeClient` | `claude-sonnet-4-5` | `ANTHROPIC_API_KEY` | `api.anthropic.com/v1/messages` |
| `gemini` | `GeminiClient` | `gemini-2.5-flash` | `GEMINI_API_KEY` | `generativelanguage.googleapis.com/v1beta` |
| `chatgpt` | `ChatGPTClient` | `gpt-4.1` | `OPENAI_API_KEY` | `api.openai.com/v1/chat/completions` |
| `deepseek` | `DeepSeekClient` | `deepseek-chat` | `DEEPSEEK_API_KEY` | `api.deepseek.com/v1/chat/completions` |
| `mistral` | `MistralClient` | `mistral-large-latest` | `MISTRAL_API_KEY` | `api.mistral.ai/v1/chat/completions` |

**Shared settings:** `_MAX_TOKENS = 1024`, `_TIMEOUT = 60.0s`, `_SLEEP_S = 1.0s` between requests. **Retry logic: up to 3 attempts with waits of 5s / 15s / 30s on 429, connection, and timeout errors. Non-retryable: 400, 401, 403, 404.**

**Gemini-specific rate limit overrides** (`_GEMINI_RETRY_WAITS = [30, 60, 120]`, `_GEMINI_SLEEP_S = 15.0s`): Gemini free tier hits 429 frequently. Two distinct failure modes:
- **Per-minute rate limit** (RPM): fixed by 15s inter-request delay + 30s/60s/120s retry waits.
- **Daily quota exhaustion** (RPD): no retry wait helps — quota resets at midnight Pacific. `gemini-2.5-flash` free tier is ~250 RPD. After 61+ tasks in one session, daily quota may be spent. Resume next day or upgrade to paid tier.

Factory: `get_client(name: str) -> BaseModelClient`

System prompt (same for all models):
> "You are an expert in Bayesian statistics and probability theory. Solve problems step by step, showing all working. Always end your response with your final answer on its own line in the format: ANSWER: <value1>, <value2>, ..."

---

## 7. Scoring Pipeline

### Single canonical scoring path — weights reconciled

Both scoring files now use the same weights. The cross-reference comment in both files reads:
`# Scoring weights must match [other file] — see CLAUDE.md §7`

**Path A — Runner path** (`llm_runner/response_parser.py`):
- Used by `run_all_tasks.py` during live API runs
- `full_score(raw_response: str, task: dict) -> Dict` — first arg must be a string (raw LLM text)
- Weights: **N=0.20, M=0.20, A=0.20, C=0.20, R=0.20** (all five equal)
- Component C — Confidence Calibration: `extract_confidence()` → `confidence_calibration_score(confidence, numeric_score)`
  - Explicit %/X-10 → linguistic hedge/definitive analysis → default 0.5
  - Overconfident-on-wrong penalized 1.5×; underconfident-on-right penalized 0.8×
- Component R — Reasoning Quality: `reasoning_quality_score(text, task_type)`
  - 4 criteria × 0.25: shows work · identifies model · states formula · interprets result
- Rubric-only tasks (CONCEPTUAL): 1.0 × rubric_score
- Tasks with both rubric and numeric: 0.6 × numeric + 0.4 × rubric
- Pass threshold: `final_score >= 0.5`
- Returns: `{"numeric": {...}, "structure": {...}, "assumptions": {...}, "confidence_score": float, "reasoning_score": float, "final_score": float, "pass": bool}`

**Path B — Formal evaluation path** (`evaluation/metrics.py`):
- Used by `experiments/run_benchmark.py` for post-hoc analysis
- `score_all_models(tasks: Dict[str, TaskSpec], runs: List[TaskRun]) -> Tuple[List[TaskScore], List[ModelAggregate]]`
- `WEIGHTS = {"N": 0.20, "M": 0.20, "C": 0.20, "A": 0.20, "R": 0.20}` — all equal
  - C reads `TaskRun.confidence_calib_score` (default 0.5)
  - R reads `TaskRun.reasoning_qual_score` (default 0.5)
- Tier-5 stress multiplier: 1.5× (no tier-5 tasks currently exist)
- Operates on `TaskRun` dataclass objects, not raw responses

### Run record schema (what `run_all_tasks.py` writes to `runs.jsonl`)

```
run_id, timestamp, task_id, task_type, tier, difficulty,
model, model_family, prompt, raw_response,
parsed_values, ground_truth,
numeric_score, structure_score, assumption_score,
confidence_score, reasoning_score,
final_score, pass, answer_found, length_match,
input_tokens, output_tokens, latency_ms, error
```

Note: `runs.jsonl` also contains an old placeholder record with a different schema. Any analysis code must handle schema heterogeneity.

### Result files

- `experiments/results_v1/runs.jsonl` — append-only, one JSON object per line
- `experiments/results_v1/results.json` — output of `run_benchmark.py`; top-level is a **dict** with keys `model_aggregates` (list of ModelAggregate) and `task_scores` (list of TaskScore)

---

## 8. Research Questions

| RQ | Topic | Status |
|---|---|---|
| RQ1 | Numerical accuracy (N score) | Implemented — `numeric_score` in runner, `numerical_score()` in metrics.py |
| RQ2 | Method selection (M score) | Implemented — `structure_score` in runner, `method_structure_score()` in metrics.py |
| RQ3 | Assumption compliance (A score) | Implemented — `assumption_score` in runner, `assumption_compliance_score()` in metrics.py |
| RQ4 | Robustness to prompt variations | **Implemented** — `data/synthetic/perturbations.json` (75 tasks); all 4 models ran synthetic; `scripts/analyze_perturbations.py` → `rq4_analysis.json`; Gemini synthetic in progress |
| RQ5 | Confidence calibration (C score) | **Implemented** — `extract_confidence()` + `confidence_calibration_score()` in `response_parser.py`; C=0.20 active in both scoring paths; `scores/recompute_scores.py` backfilled all existing runs |

---

## 9. Known Gaps and TODOs

### Verified Run Status (audited 2026-04-26)

#### Phase 1+2 (171 tasks combined)

| Model | Runs | Avg Score | Pass Rate | Status |
|---|---|---|---|---|
| claude | 171/171 | 0.679 | 88.9% | ✅ Complete |
| chatgpt | 171/171 | 0.614 | 77.8% | ✅ Complete |
| deepseek | 171/171 | 0.621 | 78.9% | ✅ Complete |
| mistral | 171/171 | 0.632 | 84.8% | ✅ Complete |
| gemini | 171/171 | 0.656 | 81.7% | ✅ Complete (paid tier, 2026-04-26) |

Old Gemini free-tier records were wiped and re-run with paid billing (2026-04-26). No error records remain.

#### Synthetic / RQ4 (75 perturbation tasks)

| Model | Runs | Status |
|---|---|---|
| claude | 75/75 | ✅ Complete |
| chatgpt | 75/75 | ✅ Complete |
| deepseek | 75/75 | ✅ Complete |
| mistral | 75/75 | ✅ Complete |
| gemini | in progress | ⏳ Running 2026-04-26 |

**Scoring components:** All 855 Phase1+2 runs have confidence_score + reasoning_score. No error records remain.

**runs.jsonl record count:** 1155 total (171×5 benchmark + 300 synthetic for 4 models).

**results.json:** Populated with 5 models, 834 task scores (via `run_benchmark.py --no-judge`).
**rq4_analysis.json:** `experiments/results_v1/rq4_analysis.json` — 300 triples, 4 models analyzed.
  - Claude robustness: 0.915 | ChatGPT: 0.931 | DeepSeek: 0.901 | Mistral: 0.925
  - By type: rephrase=0.924, semantic=0.916, numerical=0.913

### CRITICAL (blocks results)
- [ ] **Finish Gemini synthetic** (in progress) — 75 tasks: `python -m llm_runner.run_all_tasks --models gemini --synthetic --delay 2`
- [ ] **Re-run pipeline after Gemini synthetic completes** — `bash scripts/refresh_pipeline.sh --no-judge`

### IMPORTANT (needed for paper)
- [ ] Regenerate R visualizations after results complete: `cd report_materials/r_analysis && Rscript run_all.R`
- [x] Implement RQ4 perturbation comparison analysis — `scripts/analyze_perturbations.py` ✅ written and tested
- [x] Run `python scripts/summarize_results.py` — outputs `results_summary.json` with benchmark/synthetic split
- [x] Interactive HTML: 14 HTML files in `report_materials/r_analysis/interactive/` (7 HTML from scripts 08–14, plus 7 `_files/` subdirs; scripts 01–07 output HTML to `figures/` dir)
- [x] `report_materials/r_analysis/figures/` populated: 15 PNG + 1 GIF + 7 HTML (01–07)
- [x] Master report `report_materials/r_analysis/benchmark_report.html` — **9.3 MB, generated 2026-04-24** (`theme: null` fixed to `theme: flatly` in Rmd YAML)

### NICE TO HAVE
- [ ] Verify `results.json` schema matches what `run_benchmark.py` writes before writing analysis code (DONE for `--no-judge` path — schema verified)
- [ ] Re-render R report with all 5 complete model data (currently has partial Gemini)

### Before first API run (done)
- [x] Set all 5 API key environment variables (copy `.env.example` → `.env`)
- [x] Verify model strings are current: `claude-sonnet-4-5`, `gpt-4.1`, `gemini-2.5-flash`

### Before full benchmark (done)
- [x] Add retry logic + exponential backoff to all 5 clients — DONE (3 attempts, 5s/15s/30s, 429/connect/timeout only); Gemini uses 30s/60s/120s + 15s inter-request delay
- [x] Add resume logic to runner — DONE (`_load_completed()` loads existing (model_family, task_id) pairs at startup; already-completed tasks are skipped)
- [x] Create `data/synthetic/perturbations.json` (75 tasks = 25 base × 3 types) — DONE
- [x] Add `--synthetic` / `--pert-types` flags to `run_all_tasks.py` — DONE

### After results exist (done)
- [x] Implement RQ5 confidence extraction — `extract_confidence()` + `confidence_calibration_score()` in `response_parser.py`; C=0.20 active
- [x] Implement Reasoning Quality (R) scoring — `reasoning_quality_score()` in `response_parser.py`; R=0.20 active
- [x] Recompute all existing run scores with new weights — `scripts/recompute_scores.py` + `scripts/summarize_results.py`

### Resolved
- [x] Build Results & Visualizations page (`VizGallery.jsx`) — leaderboard cards + filter tabs + 15-viz gallery with lightbox/iframe/GIF modals. Assets in `frontend/public/visualizations/`. Manifest in `src/data/visualizations.js`. Added as `id="visualizations"` section in App.jsx and navbar entry.
- [x] Website task modal improvements — stable 2×2 metadata grid with `minHeight:72`, collapsible "TASK INPUTS" section showing `inputs_str` as formatted JSON, GROUND TRUTH parameters wrapped in container div using `ParamTooltip` (portal-based).
- [x] Website live results panel — `LiveResults` component below `AnimatedScoringBars` in `BenchmarkSection`, reads from `results_summary.json`, shows models benchmarked (4/5 + 1 partial), overall avg score, best model (CLAUDE), hardest/easiest task types with glowing cyan-border panel.
- [x] R visualization pipeline — 15 PNG figures generated in `report_materials/r_analysis/figures/` (scripts 01–15). Interactive HTML charts in `report_materials/r_analysis/interactive/` (scripts 08–14). Script 08 fixed: replaced CSS `rgba()` color with hex `#FFFFFF0D` (ggplot2 compatibility). GIF animation in `report_materials/r_analysis/figures/15_bar_race.gif`. **Run from `report_materials/r_analysis/` dir** — outputs go to relative `figures/` and `interactive/` within that dir.
- [x] Tasks page pagination + view mode — perPage selector (9/18/36/72/All, default 18), currentPage state resets on filter change, pagination controls below grid, GROUP BY TYPE toggle in sidebar (grouped mode shows all filtered tasks by task_type, no pagination).
- [x] Removed duplicate leaderboard from `ResultsSection.jsx` — only leaderboard is in `VizGallery.jsx` (Benchmark Visualizations section). `selectedModel` prop removed; heatmap now always shows all models.
- [x] Viz modal improvements (`VizGallery.jsx`) — "Open Interactive" button: non-GIF now calls `window.open(viz.interactive, '_blank')` (Safari iframe blocked). GIF ("View Animation ▶") still opens in-page modal with `<img>`. iframe modal JSX removed. Static lightbox ("View Static") unchanged: 90vw × 85vh PNG lightbox, zIndex 99000/99001, ESC/backdrop close. Scroll lock on `modalOpen`/`showFullImg`. Plotly `_files/` subdirs copied via `cp -r report_materials/r_analysis/interactive/ frontend/public/visualizations/interactive/`.
- [x] Task modal centering fix — root cause: App() root `motion.div` has `filter:'blur(0px)'` which creates permanent CSS stacking context, breaking `position:fixed` for ALL descendants. Fix: lifted `modal`/`setModal` state to `App()`, pass `onOpenModal` prop to `Tasks()`, render AnimatePresence+backdrop+modal box AFTER closing `</motion.div>` in App() return (sibling, not child). TaskModal refactored to content-only (no backdrop/box wrapper). backdrop: `position:fixed; top/left/right/bottom:0; zIndex:99999`. inner box: `maxWidth:640; maxHeight:85vh; padding:28`.
- [x] VizGallery PNG lightbox fix — same filter stacking context root cause as task modal. `fullImg` state (null | src string) lifted to `App()`. `setFullImg` passed as prop: `App→Visualizations→VizGallery→VizCard`. `showFullImg` state + lightbox JSX removed from VizCard. Lightbox rendered in App() return as sibling of root motion.div (outside filter context). ESC handler in App() closes both modal and fullImg. Zoom overlay + "View Static" button call `setFullImg(viz.png)`.
- [x] Portal tooltip system (`TooltipPortal.jsx` + `ParamTooltip.jsx`) — bypasses modal overflow clipping via `createPortal` to `document.body`. Viewport-clamped positioning.
- [x] Expanded `TooltipMap.js` to ~130 Bayesian stat terms.
- [x] Add retry + resume logic — see §6 Shared settings and §9 Before full benchmark
- [x] Update Gemini model string to `gemini-2.5-flash` (was `gemini-1.5-flash`)
- [x] Reconcile scoring weights between `response_parser.py` and `metrics.py` — both now use N=M=A=C=R=0.20; cross-reference comments in both files
- [x] Implement C (Confidence Calibration) + R (Reasoning Quality) in `response_parser.py`; backfill `runs.jsonl` via `scripts/recompute_scores.py`
- [x] Add `MistralClient` to `model_clients.py` — `mistral-large-latest` via `api.mistral.ai`, `MISTRAL_API_KEY`
- [x] Update ChatGPT model from `gpt-4o-mini` to `gpt-4.1`
- [x] Fix stale docstring in `run_all_tasks.py` — now says 136 tasks
- [x] Create `.env.example` with all 5 API key placeholders
- [x] Extend `fisher_information()` to support `"exponential"`, `"normal_var"`, `"gamma_rate"` — uniform intentionally raises `NotImplementedError` (theoretically correct: Uniform is not a regular exponential family)
- [x] Extend `order_statistics.py` to support `"exponential"` and `"normal"` distributions — all 5 functions now accept `params` dict; uniform (analytical) remains the default
- [x] Write 24 tests for frequentist modules: `baseline/frequentist/test_frequentist.py`
- [x] Website cursor nuclear rebuild — moved entirely to vanilla JS IIFE in `index.html` + CSS in `index.css`. No React cursor component. `GlobalCursor.jsx` is a null stub.
- [x] Website tooltip portal rebuild — `src/components/Tooltip/TooltipPortal.jsx` uses `createPortal` to render at `document.body`. Never clipped by modal overflow. `src/components/ParamTooltip.jsx` updated to use portal. `TooltipMap.js` expanded to ~130+ entries (71 actual task keys + extended Bayesian stat vocabulary).
- [x] Website task modal improvements — stable 2×2 metadata grid with `minHeight:72`, collapsible "TASK INPUTS" section showing `inputs_str` as formatted JSON, GROUND TRUTH parameters wrapped in container div using `ParamTooltip` (portal-based).
- [x] Website live results panel — `LiveResults` component below `AnimatedScoringBars` in `BenchmarkSection`, reads from `results_summary.json`, shows models benchmarked (4/5 + 1 partial), overall avg score, best model (CLAUDE), hardest/easiest task types with glowing cyan-border panel.
- [x] R visualization pipeline — 15 PNG + 1 GIF in `report_materials/r_analysis/figures/`; 14 interactive HTML in `report_materials/r_analysis/interactive/`; master report `benchmark_report.html` (9.3 MB) in `report_materials/r_analysis/`. Run from that dir: `cd report_materials/r_analysis && Rscript run_all.R`. Assets copied to `capstone-website/frontend/public/visualizations/`.

---

## 10. Conventions and Rules

### Naming
- Task IDs: `TYPE_NN` e.g. `DISC_MEDIAN_01` (padded 2 digits)
- Model family names (lowercase): `claude`, `gemini`, `chatgpt`, `deepseek`, `mistral`
- Run output: `experiments/results_v1/runs.jsonl` (append-only — never truncate)

### Adding a model client
1. Add class in `llm_runner/model_clients.py` inheriting `BaseModelClient`
2. Set `model` and `model_family` class attributes
3. Implement `query(self, prompt: str, task_id: str) -> Dict[str, Any]`
4. Return dict with keys: `model, model_family, task_id, raw_response, input_tokens, output_tokens, latency_ms, error`
5. Register in `_CLIENTS` dict at bottom of file
6. Add to `--models` choices in `run_all_tasks.py`
7. Add key placeholder to `.env.example`

### Adding a task type
1. Write a `gen_<type>_tasks()` function in `baseline/bayesian/build_tasks_bayesian.py`
2. Add ground-truth computation to `baseline/bayesian/ground_truth.py` if needed
3. Add a `_prompt_<type>()` function in `llm_runner/prompt_builder.py`
4. Register in `_DISPATCH` dict in `prompt_builder.py`
5. Regenerate: `python -m baseline.bayesian.build_tasks_bayesian`

### Scoring weight changes
Weights live in two places — always update both together:
1. `WEIGHTS` dict in `evaluation/metrics.py`
2. The formula comment + `full_score()` in `llm_runner/response_parser.py`

### Import style
- All scripts run from project root. Use absolute imports: `from llm_runner.logger import log_jsonl`
- No relative imports outside of packages

### Test locations
- MCP server tests: `capstone_mcp/test_server.py` (29 tests, all passing)
- Frequentist baseline tests: `baseline/frequentist/test_frequentist.py` (24 tests, all passing)
- No tests exist for `evaluation/`, `baseline/bayesian/`, or `llm_runner/`

---

## 11. Running the Full Benchmark

855 runs total (171 × 5 models). Results append to `runs.jsonl` automatically.
Resume-safe: re-running skips already-completed tasks (checks existing records at startup).

```bash
# Full benchmark — estimated 2-3 hours
python -m llm_runner.run_all_tasks --models claude gemini chatgpt deepseek mistral

# RQ4 synthetic perturbations — run after main benchmark completes
python -m llm_runner.run_all_tasks --models claude gemini chatgpt deepseek mistral --synthetic

# Score all results
python -m experiments.run_benchmark
```

If the run is interrupted, re-run the same command — completed tasks are skipped automatically.
