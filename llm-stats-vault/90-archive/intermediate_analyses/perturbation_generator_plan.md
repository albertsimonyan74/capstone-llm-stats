# Perturbation Generator Plan — Solver Dispatch Map

Generated: 2026-04-30
Total task_types: 38
Total base tasks: 171 (136 Phase 1 + 35 Phase 2)
Source: `data/benchmark_v1/tasks_all.json` (task_type inferred from `task_id` prefix `TYPE_NN`)

---

## Summary by feasibility

| Verdict | Types | Base tasks | Task types |
|---|---:|---:|---|
| `solver_callable` | 18 | 68 | BAYES_FACTOR, BAYES_RISK, BETA_BINOM, BINOM_FLAT, BOX_MULLER, DIRICHLET, DISC_MEDIAN, FISHER_INFO, GAMBLER, GAMMA_POISSON, HPD, JEFFREYS, LOG_ML, MLE_MAP, NORMAL_GAMMA, RANGE_DIST, STATIONARY, UNIFORM_MLE |
| `solver_with_adapter` | 12 | 58 | BAYES_REG, CI_CREDIBLE, MARKOV, MINIMAX, MLE_EFFICIENCY, MSE_COMPARE, OPT_SCALED, ORDER_STAT, PPC, RC_BOUND, REGRESSION, RJMCMC |
| `inline_math` | 1 | 5 | BIAS_VAR |
| `mc_seeded` | 6 | 30 | ABC, GIBBS, HIERARCHICAL, HMC, MH, VB |
| `unknown` | 1 | 10 | CONCEPTUAL (qualitative, no numeric targets — rubric-only) |
| **TOTAL** | **38** | **171** | |

---

## Per-task-type detail

### BETA_BINOM
- **Verdict:** solver_callable
- **Base tasks:** 1 (BETA_BINOM_01) — Tier 1
- **Solver:** `baseline.bayesian.ground_truth.gt_beta_binomial`
- **Signature:** `gt_beta_binomial(alpha: float, beta: float, x: int, n: int, ci_level: float, predictive_k: Optional[int], predictive_m: Optional[int]) -> Dict`
- **Returns:** `posterior_mean`, `ci_lower`, `ci_upper`, `predictive_pmf_k_m`
- **Used in build:** `build_tasks_bayesian.py:86` (`gen_original_tasks`)
- **Perturbation params:** alpha, beta, x, n, ci_level, predictive_k, predictive_m
- **Notes:** Direct call, no adapter.

### GAMMA_POISSON
- **Verdict:** solver_callable
- **Base tasks:** 1 (GAMMA_POISSON_01) — Tier 1
- **Solver:** `baseline.bayesian.ground_truth.gt_gamma_poisson`
- **Signature:** `gt_gamma_poisson(alpha: float, rate: float, counts: List[int], ci_level: float, predictive_y: Optional[int]) -> Dict`
- **Used in build:** `build_tasks_bayesian.py:96`
- **Perturbation params:** alpha, rate, counts, predictive_y

### NORMAL_GAMMA
- **Verdict:** solver_callable
- **Base tasks:** 1 (NORMAL_GAMMA_01) — Tier 1
- **Solver:** `baseline.bayesian.ground_truth.gt_normal_gamma_precision`
- **Signature:** `gt_normal_gamma_precision(mu0, kappa0, alpha0, beta0, data, ci_level) -> Dict`
- **Used in build:** `build_tasks_bayesian.py:106`
- **Perturbation params:** mu0, kappa0, alpha0, beta0, data

### DIRICHLET
- **Verdict:** solver_callable
- **Base tasks:** 1 (DIRICHLET_01) — Tier 1
- **Solver:** `baseline.bayesian.ground_truth.gt_dirichlet_multinomial`
- **Signature:** `gt_dirichlet_multinomial(alpha: List[float], counts: List[int], predictive_counts: Optional[List[int]]) -> Dict`
- **Used in build:** `build_tasks_bayesian.py:116`
- **Perturbation params:** alpha (list), counts (list), predictive_counts (list). Vector lengths must match.

### DISC_MEDIAN
- **Verdict:** solver_callable
- **Base tasks:** 5 — Tier 2
- **Solver:** `baseline.bayesian.bayes_estimators.discrete_posterior_median`
- **Signature:** `discrete_posterior_median(values: List[float], probs: List[float]) -> float`
- **Used in build:** `build_tasks_bayesian.py:144`
- **Perturbation params:** values (sorted), probs (sum to 1)

### UNIFORM_MLE
- **Verdict:** solver_callable
- **Base tasks:** 5 — Tier 2
- **Solver:** `baseline.bayesian.uniform_model.uniform_mle`
- **Signature:** `uniform_mle(data: List[float]) -> float`
- **Used in build:** `build_tasks_bayesian.py:168`
- **Perturbation params:** data

### BINOM_FLAT
- **Verdict:** solver_callable
- **Base tasks:** 5 — Tier 1
- **Solver:** `baseline.bayesian.conjugate_models.binomial_uniform_prior_update`
- **Signature:** `binomial_uniform_prior_update(x: int, n: int) -> BetaBinomialPosterior` (dataclass: `alpha_post`, `beta_post`, `mean()`)
- **Used in build:** `build_tasks_bayesian.py:192`
- **Perturbation params:** x, n. `x <= n`.

### MINIMAX
- **Verdict:** solver_with_adapter
- **Base tasks:** 5 — Tier 3
- **Solver:** `baseline.bayesian.decision_theory.minimax_risk`
- **Signature:** `minimax_risk(estimators: Dict[str, np.ndarray], theta_grid: np.ndarray, loss_fn: Union[str, Callable]) -> Dict`
- **Used in build:** `build_tasks_bayesian.py:227`
- **Adapter:** convert two list-of-floats inputs (`hat1_risks`, `hat2_risks`) to `{"hat1": np.array(...), "hat2": np.array(...)}`. Trivial wrapper.
- **Perturbation params:** theta_grid, hat1_risks, hat2_risks (equal length)

### BAYES_RISK
- **Verdict:** solver_callable
- **Base tasks:** 5 — Tier 2
- **Solver:** `baseline.bayesian.decision_theory.discrete_bayes_risk`
- **Signature:** `discrete_bayes_risk(risk_values: List[float], prior_probs: List[float]) -> float`
- **Used in build:** `build_tasks_bayesian.py:265`
- **Perturbation params:** risk_values, prior_probs (sum to 1)

### BIAS_VAR
- **Verdict:** inline_math
- **Base tasks:** 5 — Tier 3
- **Solver:** none — closed-form analytical formulas hardcoded in build script.
- **Code at `build_tasks_bayesian.py:293-295`:**
  ```python
  bias   = -theta / (n + 1)
  var_d2 = n * theta ** 2 / ((n + 1) ** 2 * (n + 2))
  mse_d2 = 2 * theta ** 2 / ((n + 1) * (n + 2))
  ```
- **Recommendation:** extract into `baseline/frequentist/uniform_estimators.py::bias_variance_decomp_uniform_max(n, theta) -> Dict` (3-line helper). Trivial.
- **Perturbation params:** n, theta

### FISHER_INFO
- **Verdict:** solver_callable
- **Base tasks:** 5 — Tier 3
- **Solver:** `baseline.frequentist.fisher_information.fisher_information`
- **Signature:** `fisher_information(dist: str, theta: float, n: int) -> float`
- **Used in build:** `build_tasks_bayesian.py:334`
- **Perturbation params:** dist ∈ {binomial, poisson, normal} (NOT uniform — raises NotImplementedError), theta, n

### RC_BOUND
- **Verdict:** solver_with_adapter
- **Base tasks:** 5 — Tier 3
- **Solvers:** `fisher_information` + `rao_cramer_bound`
- **Used in build:** `build_tasks_bayesian.py:360-361`
- **Adapter:** `fi = fisher_information(dist, theta, n); rc = rao_cramer_bound(fi)`. Two-line wrapper.
- **Perturbation params:** dist, theta, n

### OPT_SCALED
- **Verdict:** solver_with_adapter
- **Base tasks:** 5 — Tier 4
- **Solver:** `baseline.frequentist.uniform_estimators.optimal_scaled_estimator_uniform`
- **Signature:** `optimal_scaled_estimator_uniform(n: int, theta: float) -> Dict`
- **Used in build:** `build_tasks_bayesian.py:386`
- **Adapter:** result dict has many keys; targets pull `c_opt`, `mse_opt`. Map keys.
- **Perturbation params:** n, theta

### MSE_COMPARE
- **Verdict:** solver_with_adapter
- **Base tasks:** 5 — Tier 4
- **Solver:** same as OPT_SCALED (`optimal_scaled_estimator_uniform`)
- **Used in build:** `build_tasks_bayesian.py:420`
- **Adapter:** pulls `mse_d1`, `mse_d2`, `mse_opt` from same result dict.
- **Perturbation params:** n, theta

### MARKOV
- **Verdict:** solver_with_adapter
- **Base tasks:** 5 — Tier 3
- **Solvers:** `markov_chains.stationary_distribution`, `gambling_ruin_probability`, `n_step_transition`
- **Used in build:** `build_tasks_bayesian.py:498-535` (subtype dispatch)
- **Adapter:** must dispatch on `subtype` ∈ {stationary, stationary_2state, gamblers_ruin, n_step}; targets vary by subtype.
- **Perturbation params:** subtype-dependent. P (stochastic matrix), or (p,i,M), or (P,n,i,j).
- **Notes:** preserve subtype across perturbations to avoid changing target keys.

### ORDER_STAT
- **Verdict:** solver_with_adapter
- **Base tasks:** 5 — Tier 3
- **Solvers:** `order_statistics.order_statistic_pdf` / `min_order_statistic_cdf` / `uniform_range_distribution`
- **Used in build:** `build_tasks_bayesian.py:577-597`
- **Adapter:** dispatch on `subtype` ∈ {pdf, min_cdf, range}.
- **Perturbation params:** subtype-dependent.

### REGRESSION
- **Verdict:** solver_with_adapter
- **Base tasks:** 5 — Tier 3
- **Solvers:** `regression.ols_estimators` + `residual_variance` + `credibility_intervals`
- **Used in build:** `build_tasks_bayesian.py:645-647`
- **Adapter:** call all three; build composite target dict {A_hat, B_hat, s2, B_lower, B_upper}.
- **Perturbation params:** x, y (equal length, n>=3 required for s2)

### BOX_MULLER
- **Verdict:** solver_callable
- **Base tasks:** 5 — Tier 2
- **Solver:** `baseline.frequentist.sampling.box_muller_standard`
- **Signature:** `box_muller_standard(u: float, v: float) -> Tuple[float, float]`
- **Used in build:** `build_tasks_bayesian.py:695`
- **Perturbation params:** U ∈ (0,1), V ∈ (0,1), mu, sigma. Affine scale done inline (`mu + sigma*z`) — trivial.

### HPD
- **Verdict:** solver_callable
- **Base tasks:** 5 — Tier 2
- **Solver:** `baseline.bayesian.intervals.beta_hpd_interval`
- **Signature:** `beta_hpd_interval(alpha: float, beta: float, level: float) -> tuple`
- **Used in build:** `build_tasks_bayesian.py:755`
- **Perturbation params:** alpha, beta, level

### BAYES_FACTOR
- **Verdict:** solver_callable
- **Base tasks:** 5 — Tier 3
- **Solver:** `baseline.bayesian.bayes_factors.bayes_factor_beta_binomial`
- **Signature:** `bayes_factor_beta_binomial(alpha1, beta1, alpha2, beta2, x, n) -> Dict`
- **Used in build:** `build_tasks_bayesian.py:796`
- **Perturbation params:** alpha1, beta1, alpha2, beta2, x, n

### JEFFREYS
- **Verdict:** solver_callable
- **Base tasks:** 5 — Tier 2
- **Solver:** `baseline.bayesian.conjugate_models.jeffreys_update_binomial`
- **Signature:** `jeffreys_update_binomial(x: int, n: int) -> Dict`
- **Used in build:** `build_tasks_bayesian.py:845`
- **Perturbation params:** x, n

### PPC
- **Verdict:** solver_with_adapter
- **Base tasks:** 5 — Tier 3
- **Solver:** `baseline.bayesian.posterior_predictive.posterior_predictive_check_beta_binomial`
- **Signature:** `posterior_predictive_check_beta_binomial(alpha_post, beta_post, n_obs, x_obs, n_rep, seed) -> dict`
- **Used in build:** `build_tasks_bayesian.py:904`
- **Adapter:** uses Monte Carlo with `seed=42`, `n_rep=5000`. Reproducible if seed fixed. p-value depends on x_obs vs replicates.
- **Notes:** mark perturbations with `seed=42, n_rep=5000` so true value is deterministic per (alpha_post, beta_post, n_obs, x_obs).
- **Perturbation params:** alpha_post, beta_post, n_obs, x_obs

### BAYES_REG
- **Verdict:** solver_with_adapter
- **Base tasks:** 5 — Tier 3
- **Solver:** `baseline.bayesian.bayesian_regression.normal_inverse_gamma_regression_update`
- **Signature:** `normal_inverse_gamma_regression_update(X: np.ndarray, y: np.ndarray, mu0: np.ndarray, Lambda0: np.ndarray, a0: float, b0: float) -> Dict`
- **Used in build:** `build_tasks_bayesian.py:980`
- **Adapter:** y data is simulated upstream with `rng = np.random.default_rng(seed); y = a + b*x + rng.normal(0, sigma, n)`. Then `X = column_stack([1, x])`, diffuse prior. Two-step adapter (sim + solve).
- **Perturbation params:** true_a, true_b, x (list), sigma, seed → solver returns `posterior_mean_beta` (intercept_post, slope_post)

### MLE_MAP
- **Verdict:** solver_callable
- **Base tasks:** 5 — Tier 2
- **Solver:** `baseline.bayesian.conjugate_models.mle_vs_map`
- **Signature:** `mle_vs_map(dist: str, prior_params: dict, data) -> Dict`
- **Used in build:** `build_tasks_bayesian.py:1032`
- **Perturbation params:** dist="binomial", prior_params={alpha,beta}, data={x,n}

### CI_CREDIBLE
- **Verdict:** solver_with_adapter
- **Base tasks:** 5 — Tier 2
- **Solver:** `baseline.bayesian.intervals.compare_ci_vs_credible_normal`
- **Signature:** `compare_ci_vs_credible_normal(mu0, tau0_sq, sigma_sq, data, level) -> dict`
- **Used in build:** `build_tasks_bayesian.py:1087`
- **Adapter:** data simulated with `rng = np.random.default_rng(seed); data = true_mean + rng.normal(0, sqrt(sigma_sq), n)`. Two-step (sim + solve).
- **Perturbation params:** mu0, tau0_sq, sigma_sq, true_mean, n, seed

### LOG_ML
- **Verdict:** solver_callable
- **Base tasks:** 5 — Tier 3
- **Solvers:** `bayes_factors.log_marginal_likelihood_beta_binomial` (3 tasks) + `log_marginal_likelihood_gamma_poisson` (2 tasks)
- **Used in build:** `build_tasks_bayesian.py:1150,1157`
- **Adapter (mild):** dispatch on `model` ∈ {beta_binomial, gamma_poisson}.
- **Perturbation params:** model-dependent.

### GAMBLER
- **Verdict:** solver_callable
- **Base tasks:** 3 — Tier 3
- **Solver:** `baseline.bayesian.markov_chains.gambling_ruin_probability`
- **Signature:** `gambling_ruin_probability(p: float, i: int, M: int) -> Dict`
- **Used in build:** `build_tasks_bayesian.py:1201`
- **Perturbation params:** p, i, M (0 < i < M)

### STATIONARY
- **Verdict:** solver_callable
- **Base tasks:** 3 — Tier 3
- **Solver:** `baseline.bayesian.markov_chains.stationary_distribution`
- **Signature:** `stationary_distribution(P: np.ndarray, tol: float) -> np.ndarray`
- **Used in build:** `build_tasks_bayesian.py:1261`
- **Perturbation params:** P (k×k stochastic matrix). Targets `pi_0…pi_{k-1}` — k must match base task to keep target keys.

### RANGE_DIST
- **Verdict:** solver_callable
- **Base tasks:** 3 — Tier 3
- **Solver:** `baseline.frequentist.order_statistics.uniform_range_distribution`
- **Signature:** `uniform_range_distribution(n: int, n_sim: int, seed: int) -> Dict`
- **Used in build:** `build_tasks_bayesian.py:1300`
- **Perturbation params:** n. Returns Beta(n-1, 2) parameters analytically; `verified` is KS-test flag (Monte Carlo).

### MLE_EFFICIENCY
- **Verdict:** solver_with_adapter
- **Base tasks:** 3 — Tier 4
- **Solvers:** `fisher_information` + `rao_cramer_bound` + hardcoded `efficiency_ratio=1.0` and `is_efficient=1.0`
- **Used in build:** `build_tasks_bayesian.py:1346-1347`
- **Adapter:** wrap two solvers; emit constants 1.0 for efficiency_ratio (theoretical for regular exp families).
- **Perturbation params:** dist ∈ {binomial, poisson, normal}, theta, n. Avoid uniform (NotImplementedError).

### CONCEPTUAL
- **Verdict:** unknown (qualitative — no numeric targets, rubric-only scoring)
- **Base tasks:** 10 — Tiers 2, 3
- **Solver:** none. Tasks built via `make_conceptual_task(task_id, tier, difficulty, question, rubric_keys, reference_answer, topic)` at `build_tasks_bayesian.py:1380`.
- **Notes:** numerical perturbation N/A. Rephrase/semantic feasible (LLM rewrites prompt; reference_answer + rubric_keys carry over). Need separate path in generator that bypasses ground-truth recompute.

### GIBBS, MH, HMC, VB, ABC, HIERARCHICAL
- **Verdict:** mc_seeded
- **Base tasks:** 5 each (30 total) — Tiers 2, 3, 4
- **Solvers:** `baseline.bayesian.advanced_methods.{GibbsSampler, MetropolisHastings, HamiltonianMC, VariationalBayes, ABCMethod, HierarchicalBayes}` — class-based, `__init__(params: Dict)` + `solve() -> Dict`. All call `np.random.seed(42)`.
- **Used in build:** `build_tasks_advanced.py:80,128,176,282,338,386`
- **Numerical perturbation feasibility:** PROBLEMATIC. Each solver's "true value" is a seeded Monte Carlo estimate. Re-running with new params + same seed gives a deterministic result, but it is NOT the analytical true value — it is one realisation of a stochastic estimator. Methodologically muddy: a model that disagrees might be closer to the analytical truth than the seeded MC sample.
- **Recommendation:** SKIP numerical perturbation. Rephrase + semantic only.

### RJMCMC (verified 2026-04-30)
- **Verdict:** solver_with_adapter (RECLASSIFIED from mc_seeded after code review)
- **Base tasks:** 5 — Tiers 3, 4
- **Solver:** `baseline.bayesian.advanced_methods.RJMCMC` — class-based; `solve()` is fully analytical despite calling `np.random.seed(42)`. The seed call is dead code (no random sampling occurs). `proposal_std` is "kept for API compat".
- **Used in build:** `build_tasks_advanced.py:233`
- **Code excerpt** (`advanced_methods.py:247-271`):
  ```python
  def solve(self) -> Dict[str, float]:
      np.random.seed(42)            # dead code — no rng calls follow
      y = np.array(self.data)
      mid = len(y) // 2
      y1, y2 = y[:mid], y[mid:]
      log_ml_m1 = self._log_marginal(y)
      log_ml_m2 = self._log_marginal(y1) + self._log_marginal(y2)
      log_bf   = log_ml_m1 - log_ml_m2
      log_bf   = float(np.clip(log_bf, -30.0, 30.0))
      bf       = math.exp(log_bf)
      ...
      return {"posterior_prob_m1": ..., "posterior_prob_m2": ..., "bayes_factor": float(bf)}
  ```
- `_log_marginal` is closed-form (Normal-Normal conjugate marginal likelihood); no random calls.
- **Adapter:** instantiate `RJMCMC({"data": ..., "prior_prob_m1": ..., "proposal_std": ...}).solve()`. `sigma2 = var(data, ddof=1)` and `tau2 = sigma2` are derived in `__init__`.
- **Perturbation params:** data (list[float], len ≥ 2), prior_prob_m1 ∈ (0,1), proposal_std (any float, unused).
- **Numerical perturbation:** FEASIBLE. Output deterministic given inputs.

---

## Recommendations for the perturbation generator

### Task types where numerical perturbation is feasible (no extra work)
**18 task_types, 68 base tasks** (`solver_callable`). Plug straight into a dispatch table:
```python
DISPATCH = {
    "BETA_BINOM":  ("baseline.bayesian.ground_truth", "gt_beta_binomial"),
    "DISC_MEDIAN": ("baseline.bayesian.bayes_estimators", "discrete_posterior_median"),
    # ... 16 more
}
```
Generator flow: LLM proposes new params → call dispatch[task_type](**params) → emit perturbation.

### Task types requiring custom adapters
**11 task_types, 53 base tasks** (`solver_with_adapter`). Adapters by category:
- **Subtype dispatch (2):** MARKOV, ORDER_STAT — branch on `subtype` field; preserve subtype across perturbations to keep target-key shape stable.
- **Two-step (data sim + solve) (2):** BAYES_REG, CI_CREDIBLE — re-run `np.random.default_rng(seed).normal(...)` then call solver. Pass `seed` through perturbation.
- **Combine multiple solvers (4):** RC_BOUND, REGRESSION, MLE_EFFICIENCY, OPT_SCALED/MSE_COMPARE (share solver, differ in target keys).
- **Trivial wrapper (3):** MINIMAX (list→ndarray), PPC (fix seed=42, n_rep=5000), LOG_ML (model dispatch).

Estimated total: ~80 lines of glue across all 11 adapters.

### Task types where math must be extracted from build scripts
**1 task_type, 5 base tasks** (`inline_math` — BIAS_VAR).
- `build_tasks_bayesian.py:293-295` — three closed-form lines.
- **Action:** add `bias_variance_decomp_uniform_max(n, theta) -> Dict` to `baseline/frequentist/uniform_estimators.py`. ~5 lines including docstring. Then promote BIAS_VAR to `solver_callable`.

### Task types where we should skip numerical perturbation
**6 task_types, 30 base tasks** (`mc_seeded`: GIBBS, MH, HMC, VB, ABC, HIERARCHICAL). Generate `rephrase` + `semantic` only.

### Task types with no numeric targets
**1 task_type, 10 base tasks** (CONCEPTUAL). Generate `rephrase` + `semantic` only; carry over `reference_answer` and `rubric_keys` unchanged. Generator needs a `is_conceptual` branch.

### Final perturbation count estimate

Assuming we extract BIAS_VAR (so 126 base tasks) AND promote RJMCMC to numerical (5 more) → 131 numerically-feasible base tasks. Skip numerical for remaining mc_seeded + CONCEPTUAL (40 base tasks):

| Bucket | Base tasks | Pert / task | Perturbations |
|---|---:|---:|---:|
| Numerical-feasible (callable + adapter + extracted + RJMCMC) | 131 | 3 (rephrase/numerical/semantic) | 393 |
| MC-seeded (Phase 2 MCMC, excl. RJMCMC) | 30 | 2 (rephrase/semantic) | 60 |
| Conceptual | 10 | 2 (rephrase/semantic) | 20 |
| **TOTAL perturbations** | **171** | — | **473** |

- Total perturbation runs × 5 models = **2,365 model calls**
- Plus judge calls (1 per run for rubric scoring): ~2,365 judge calls
- Estimated cost (Together-cheap models for judge, mixed for benchmark):
  - Benchmark calls: 2,365 × ~$0.002 avg = ~$4.73
  - Judge calls (Llama-3.3-70B-Instruct-Turbo via Together): 2,365 × ~$0.0006 = ~$1.42
  - **Total estimate: ~$6 (low) to ~$12 (high)** depending on prompt length distribution

If we keep BIAS_VAR as inline_math without extraction:
- Numerical-feasible: 121 × 3 = 363
- Non-numerical: (5 + 35 + 10) × 2 = 100
- Total: 463 (≈same scale).

### Open questions / flagged

1. **CONCEPTUAL** — generator needs separate path. No ground-truth recompute possible. Decide: do we trust the LLM judge against `reference_answer` for the rephrased prompt?
2. **RJMCMC** — RESOLVED 2026-04-30. Verified analytical (Normal-Normal conjugate marginal likelihood, no random calls). Promoted to `solver_with_adapter`; numerical perturbation feasible.
3. **STATIONARY / MARKOV stationary subtype** — perturbation must keep matrix dimension `k` constant or target keys (`pi_0…pi_{k-1}`) won't align across base + perturbation.
4. **DIRICHLET** — vector dimension must match base task (3 categories). Same constraint.
5. **FISHER_INFO / RC_BOUND / MLE_EFFICIENCY** — `dist="uniform"` raises `NotImplementedError`. Generator must constrain `dist ∈ {binomial, poisson, normal}` or reuse base task's dist.

---

## Notes on identification

`tasks_all.json` records do NOT contain a `task_type` field. Phase 2 advanced tasks set `task_type` inside their make_task signature (e.g. `task_type="GIBBS"`), but it is dropped before serialisation in some paths. **Task type was inferred from the `task_id` prefix pattern `^([A-Z_]+?)_(\d+)$`.** Generator should adopt the same regex or be patched to require an explicit `task_type` field at task-build time.
