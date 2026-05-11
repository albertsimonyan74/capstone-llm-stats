# llm_runner/prompt_builder.py
"""
Builds human-readable prompts from task dicts (tasks.json schema) and
parses LLM responses back into numeric values.

Supports all 31 task types in the benchmark:
  BAYES_FACTOR, BAYES_REG, BAYES_RISK, BETA_BINOM, BIAS_VAR,
  BINOM_FLAT, BOX_MULLER, CI_CREDIBLE, CONCEPTUAL, DIRICHLET,
  DISC_MEDIAN, FISHER_INFO, GAMBLER, GAMMA_POISSON, HPD,
  JEFFREYS, LOG_ML, MARKOV, MINIMAX, MLE_EFFICIENCY, MLE_MAP,
  MSE_COMPARE, NORMAL_GAMMA, OPT_SCALED, ORDER_STAT, PPC,
  RANGE_DIST, RC_BOUND, REGRESSION, STATIONARY, UNIFORM_MLE
"""
from __future__ import annotations

import re
from typing import Any, Dict, List

# ── Shared preamble / footer ──────────────────────────────────────────────────

_REASONING_INSTRUCTION = (
    "Show your step-by-step reasoning before giving the final answer."
)

_ANSWER_INSTRUCTION_SINGLE = (
    "Your final answer must be on the last line in this exact format:\n"
    "ANSWER: <value>\n"
    "Round to 4 decimal places."
)

_ANSWER_INSTRUCTION_MULTI = (
    "Your final answer must be on the last line in this exact format:\n"
    "ANSWER: <v1>, <v2>, ...\n"
    "List values in the order requested. Round each to 4 decimal places."
)

def _footer(multi: bool = False) -> str:
    instr = _ANSWER_INSTRUCTION_MULTI if multi else _ANSWER_INSTRUCTION_SINGLE
    return f"\n{_REASONING_INSTRUCTION}\n\n{instr}"


def _fmt_list(lst: list, dp: int = 4) -> str:
    """Format a list of numbers inline, e.g. [1.2, 3.4] → '1.2, 3.4'."""
    return ", ".join(str(round(v, dp)) if isinstance(v, float) else str(v) for v in lst)


def _fmt_matrix(mat: list) -> str:
    """Format a 2-D list as a readable matrix string."""
    rows = ["  [" + ", ".join(f"{v:.4f}" for v in row) + "]" for row in mat]
    return "[\n" + "\n".join(rows) + "\n]"


# ── Per-topic prompt builders ─────────────────────────────────────────────────

def _prompt_beta_binom(inp: Dict[str, Any]) -> str:
    alpha, beta, x, n = inp["alpha"], inp["beta"], inp["x"], inp["n"]
    k, m = inp.get("k"), inp.get("m")
    body = (
        f"You observe x = {x} successes in n = {n} Bernoulli trials.\n"
        f"The prior on the success probability θ is Beta(α={alpha}, β={beta}).\n\n"
        f"(a) State the posterior distribution of θ given the data.\n"
        f"(b) Compute the posterior mean of θ.\n"
        f"(c) Compute the 95% equal-tailed credible interval for θ.\n"
    )
    if k is not None and m is not None:
        body += (
            f"(d) Compute P(X_new = {k} | data) where X_new ~ Binomial({m}, θ) "
            f"(posterior predictive).\n\n"
            f"Report: posterior_mean, ci_lower, ci_upper, predictive_pmf_k_m"
        )
        return body + _footer(multi=True)
    return body + _footer(multi=True)


def _prompt_gamma_poisson(inp: Dict[str, Any]) -> str:
    alpha, rate = inp["alpha"], inp["rate"]
    counts, y = inp["counts"], inp.get("y")
    n = len(counts)
    sum_x = sum(counts)
    body = (
        f"You observe n = {n} Poisson counts: {counts}  (sum = {sum_x}).\n"
        f"The prior on the rate λ is Gamma(α={alpha}, rate={rate}).\n\n"
        f"(a) State the posterior distribution of λ given the data.\n"
        f"(b) Compute the posterior mean of λ.\n"
        f"(c) Compute the 95% equal-tailed credible interval for λ.\n"
    )
    if y is not None:
        body += (
            f"(d) Compute the posterior predictive probability P(Y_new = {y} | data),\n"
            f"    where Y_new | λ ~ Poisson(λ).\n\n"
            f"Report: posterior_mean, ci_lower, ci_upper, predictive_pmf_y"
        )
    return body + _footer(multi=True)


def _prompt_normal_gamma(inp: Dict[str, Any]) -> str:
    mu0, k0, a0, b0 = inp["mu0"], inp["kappa0"], inp["alpha0"], inp["beta0"]
    data = inp["data"]
    n = len(data)
    xbar = round(sum(data) / n, 4)
    body = (
        f"You observe n = {n} data points from a Normal distribution with unknown mean μ "
        f"and unknown precision τ = 1/σ²:\n"
        f"  data = {data}  (x̄ = {xbar})\n\n"
        f"Prior: (μ, τ) ~ Normal-Gamma(μ₀={mu0}, κ₀={k0}, α₀={a0}, β₀={b0})\n"
        f"  where κ₀ controls prior strength on the mean, and β₀ is the rate parameter.\n\n"
        f"(a) State the posterior Normal-Gamma parameters (μₙ, κₙ, αₙ, βₙ).\n"
        f"(b) Compute the posterior mean of μ.\n"
        f"(c) Compute the posterior mean of τ.\n"
        f"(d) Compute the 95% marginal credible interval for μ (Student-t marginal).\n\n"
        f"Report: posterior_mean_mu, ci_mu_lower, ci_mu_upper, posterior_mean_tau"
    )
    return body + _footer(multi=True)


def _prompt_dirichlet(inp: Dict[str, Any]) -> str:
    alpha, counts = inp["alpha"], inp["counts"]
    pred = inp.get("pred_counts")
    K = len(alpha)
    total = sum(counts)
    body = (
        f"You observe counts {counts} (total = {total}) from {K} categories.\n"
        f"The prior on the category probabilities (θ₁, …, θ_{K}) is "
        f"Dirichlet(α = {alpha}).\n\n"
        f"(a) State the posterior Dirichlet distribution.\n"
        f"(b) Compute the posterior mean vector (E[θ₁|data], …, E[θ_{K}|data]).\n"
    )
    if pred:
        body += (
            f"(c) Compute the posterior predictive probability "
            f"P(X_new = {pred} | data).\n\n"
            f"Report: p1_mean, p2_mean, p3_mean, predictive_pmf_counts"
        )
    return body + _footer(multi=True)


def _prompt_disc_median(inp: Dict[str, Any]) -> str:
    values, probs = inp["values"], inp["probs"]
    body = (
        f"A discrete random variable θ takes the following values and probabilities:\n\n"
        f"  Values:        {values}\n"
        f"  Probabilities: {probs}\n\n"
        f"Find the posterior median of θ.\n"
        f"(The posterior median is the smallest value v such that P(θ ≤ v) ≥ 0.5.)\n\n"
        f"Show the cumulative distribution step by step.\n\n"
        f"Report: posterior_median"
    )
    return body + _footer(multi=False)


def _prompt_uniform_mle(inp: Dict[str, Any]) -> str:
    data = inp["data"]
    n = len(data)
    body = (
        f"You observe n = {n} i.i.d. draws from Uniform(0, θ):\n"
        f"  data = {data}\n\n"
        f"Derive the Maximum Likelihood Estimator (MLE) for θ.\n"
        f"State why the MLE is the maximum order statistic X_(n) = max(data).\n\n"
        f"Report: mle_theta"
    )
    return body + _footer(multi=False)


def _prompt_binom_flat(inp: Dict[str, Any]) -> str:
    x, n = inp["x"], inp["n"]
    body = (
        f"You observe x = {x} successes in n = {n} Bernoulli trials.\n"
        f"The prior on θ is Uniform(0, 1) = Beta(1, 1)  (a flat / diffuse prior).\n\n"
        f"(a) State the posterior distribution Beta(α_post, β_post).\n"
        f"(b) Compute α_post and β_post.\n"
        f"(c) Compute the posterior mean E[θ | data] = α_post / (α_post + β_post).\n\n"
        f"Report: alpha_post, beta_post, posterior_mean"
    )
    return body + _footer(multi=True)


def _prompt_minimax(inp: Dict[str, Any]) -> str:
    theta_grid = inp["theta_grid"]
    h1 = inp["hat1_risks"]
    h2 = inp["hat2_risks"]
    body = (
        f"Two estimators δ₁ and δ₂ have the following risk values R(δ, θ) "
        f"at θ ∈ {theta_grid}:\n\n"
        f"  R(δ₁, θ): {h1}\n"
        f"  R(δ₂, θ): {h2}\n\n"
        f"The minimax estimator minimises the maximum risk max_θ R(δ, θ).\n\n"
        f"(a) Compute max_θ R(δ₁, θ).\n"
        f"(b) Compute max_θ R(δ₂, θ).\n"
        f"(c) Identify the minimax estimator and state its minimax value.\n\n"
        f"Report: max_risk_hat1, max_risk_hat2, minimax_value"
    )
    return body + _footer(multi=True)


def _prompt_bayes_risk(inp: Dict[str, Any]) -> str:
    risks, probs = inp["risk_values"], inp["prior_probs"]
    K = len(probs)
    body = (
        f"An estimator δ has risk values R(δ, θᵢ) at {K} parameter values,\n"
        f"with a discrete prior π(θᵢ):\n\n"
        f"  Risk values R(δ, θᵢ): {risks}\n"
        f"  Prior probabilities π(θᵢ): {probs}\n\n"
        f"Compute the Bayes risk:\n"
        f"  B(δ) = Σᵢ R(δ, θᵢ) · π(θᵢ)\n\n"
        f"Report: bayes_risk"
    )
    return body + _footer(multi=False)


def _prompt_bias_var(inp: Dict[str, Any]) -> str:
    n, theta = inp["n"], inp["theta"]
    body = (
        f"Consider n = {n} i.i.d. draws X₁, …, X_n from Uniform(0, θ = {theta}).\n"
        f"Let d₂ = max(X₁, …, X_n) be the MLE estimator for θ.\n\n"
        f"Using the analytical formulas:\n"
        f"  Bias(d₂)     = -θ / (n + 1)\n"
        f"  Var(d₂)      = n·θ² / [(n+1)²·(n+2)]\n"
        f"  MSE(d₂)      = 2·θ² / [(n+1)·(n+2)]\n\n"
        f"(a) Compute Bias(d₂).\n"
        f"(b) Compute Var(d₂).\n"
        f"(c) Compute MSE(d₂) and verify MSE = Bias² + Var.\n\n"
        f"Report: bias, var_d2, mse_d2"
    )
    return body + _footer(multi=True)


def _prompt_fisher_info(inp: Dict[str, Any]) -> str:
    dist, theta, n = inp["dist"], inp["theta"], inp["n"]
    formulas = {
        "binomial": "I_n(θ) = n / [θ(1 − θ)]  (Bernoulli observations)",
        "poisson":  "I_n(θ) = n / θ  (Poisson(λ=θ) observations)",
        "normal":   "I_n(θ) = n / σ²  (Normal(μ=θ, σ²=1) → I_n(θ) = n)",
    }
    formula_hint = formulas.get(dist, f"standard formula for {dist}")
    body = (
        f"Compute the Fisher information I_n(θ) for n = {n} i.i.d. observations\n"
        f"from a {dist.capitalize()} distribution with parameter θ = {theta}.\n\n"
        f"Recall: {formula_hint}\n\n"
        f"Report: fisher_info"
    )
    return body + _footer(multi=False)


def _prompt_rc_bound(inp: Dict[str, Any]) -> str:
    dist, theta, n = inp["dist"], inp["theta"], inp["n"]
    body = (
        f"For n = {n} i.i.d. observations from a {dist.capitalize()} distribution\n"
        f"with parameter θ = {theta}:\n\n"
        f"(a) Compute the Fisher information I_n(θ).\n"
        f"(b) Compute the Rao-Cramér lower bound on the variance of any unbiased estimator:\n"
        f"    RC = (1 + b'(θ))² / I_n(θ)   with b'(θ) = 0 for unbiased estimators.\n\n"
        f"Report: fisher_info, rc_bound"
    )
    return body + _footer(multi=True)


def _prompt_opt_scaled(inp: Dict[str, Any]) -> str:
    n, theta = inp["n"], inp["theta"]
    body = (
        f"For n = {n} i.i.d. draws from Uniform(0, θ = {theta}),\n"
        f"consider the scaled estimator d_c = c · max(X₁, …, X_n).\n\n"
        f"(a) Find the optimal constant c* that minimises MSE(d_c) with respect to c.\n"
        f"    Show that c* = (n + 2) / (n + 1).\n"
        f"(b) Compute MSE(d_c*) = θ² / (n + 1)².\n\n"
        f"Report: c_opt, mse_opt"
    )
    return body + _footer(multi=True)


def _prompt_mse_compare(inp: Dict[str, Any]) -> str:
    n, theta = inp["n"], inp["theta"]
    body = (
        f"For n = {n} i.i.d. draws from Uniform(0, θ = {theta}), compare three estimators:\n\n"
        f"  d₁ = 2 · X̄  (unbiased, uses sample mean)\n"
        f"  d₂ = max(Xᵢ)  (MLE, biased)\n"
        f"  d_c = c* · max(Xᵢ)  with c* = (n+2)/(n+1)  (optimal scaled)\n\n"
        f"Using closed-form MSE formulas:\n"
        f"  MSE(d₁) = θ² / (3n)\n"
        f"  MSE(d₂) = 2θ² / [(n+1)(n+2)]\n"
        f"  MSE(d_c*) = θ² / (n+1)²\n\n"
        f"(a) Compute MSE(d₁), MSE(d₂), and MSE(d_c*).\n"
        f"(b) Rank the estimators by MSE.\n\n"
        f"Report: mse_d1, mse_d2, mse_dc"
    )
    return body + _footer(multi=True)


def _prompt_markov(inp: Dict[str, Any], topic: str) -> str:
    if topic == "markov_stationary" or topic == "markov_stationary_2state":
        P = inp["P"]
        K = len(P)
        mat_str = _fmt_matrix(P)
        body = (
            f"A Markov chain on {K} states has transition matrix:\n"
            f"P = {mat_str}\n\n"
            f"Find the stationary distribution π = (π₀, π₁, …) satisfying:\n"
            f"  π · P = π   and   Σᵢ πᵢ = 1\n\n"
            f"Report: " + ", ".join(f"pi_{i}" for i in range(K))
        )
        return body + _footer(multi=(K > 1))

    elif topic == "gamblers_ruin":
        p, i, M = inp["p"], inp["i"], inp["M"]
        q = round(1 - p, 6)
        formula = (
            "P(ruin | start=i) = (M − i) / M"
            if abs(p - 0.5) < 1e-9
            else "P(ruin | start=i) = [(q/p)^i − (q/p)^M] / [1 − (q/p)^M]"
        )
        body = (
            f"A gambler starts with fortune i = {i}.\n"
            f"At each step they win £1 with probability p = {p} or lose £1 with "
            f"probability q = {q}.\n"
            f"The game ends when fortune reaches 0 (ruin) or M = {M} (win).\n\n"
            f"Using the gambler's ruin formula:\n"
            f"  {formula}\n\n"
            f"(a) Compute the probability of ruin.\n"
            f"(b) Compute the probability of winning.\n\n"
            f"Report: ruin_prob, win_prob"
        )
        return body + _footer(multi=True)

    else:  # markov_n_step
        P = inp["P"]
        n_steps, i_idx, j_idx = inp["n"], inp["i"], inp["j"]
        mat_str = _fmt_matrix(P)
        body = (
            f"A Markov chain has transition matrix:\n"
            f"P = {mat_str}\n\n"
            f"Compute the {n_steps}-step transition probability P^{n_steps}[{i_idx}, {j_idx}]\n"
            f"(the probability of being in state {j_idx} after {n_steps} steps, "
            f"starting from state {i_idx}).\n\n"
            f"Use the Chapman-Kolmogorov equation or direct matrix multiplication.\n\n"
            f"Report: P{n_steps}_{i_idx}_{j_idx}"
        )
        return body + _footer(multi=False)


def _prompt_order_stat(inp: Dict[str, Any], topic: str) -> str:
    if topic == "order_statistic_pdf":
        y, k, n = inp["y"], inp["k"], inp["n"]
        body = (
            f"Let X₁, …, X_{n} be i.i.d. Uniform[0, 1] random variables.\n"
            f"Let X_({k}) denote the {k}-th order statistic (the {k}-th smallest value).\n\n"
            f"The PDF of X_({k}) is:\n"
            f"  g_({k})(y) = n! / [(k−1)! (n−k)!] · y^(k−1) · (1−y)^(n−k)\n"
            f"           = Beta(k={k}, n−k+1={n-k+1}).pdf(y)\n\n"
            f"Evaluate g_({k})(y = {y}).\n\n"
            f"Report: order_stat_pdf"
        )
        return body + _footer(multi=False)

    elif topic == "min_order_statistic_cdf":
        x, n = inp["x"], inp["n"]
        body = (
            f"Let X₁, …, X_{n} be i.i.d. Uniform[0, 1] random variables.\n"
            f"Let X_(1) = min(X₁, …, X_{n}) be the minimum order statistic.\n\n"
            f"The CDF of X_(1) is:\n"
            f"  F_(1)(x) = 1 − (1 − x)^n\n\n"
            f"Evaluate F_(1)(x = {x}) with n = {n}.\n\n"
            f"Report: min_cdf"
        )
        return body + _footer(multi=False)

    else:  # uniform_range_distribution
        n = inp["n"]
        body = (
            f"Let X₁, …, X_{n} be i.i.d. Uniform[0, 1] random variables.\n"
            f"The range R = X_({n}) − X_(1) = max(Xᵢ) − min(Xᵢ) follows a Beta distribution.\n\n"
            f"(a) State the parameters α and β of the Beta distribution that R follows.\n"
            f"    Hint: R ~ Beta(n−1, 2).\n"
            f"(b) Give the values of α and β for n = {n}.\n\n"
            f"Report: range_beta_alpha, range_beta_beta"
        )
        return body + _footer(multi=True)


def _prompt_regression(inp: Dict[str, Any]) -> str:
    x, y = inp["x"], inp["y"]
    n = len(x)
    import numpy as np
    xa, ya = np.array(x), np.array(y)
    sum_x  = round(float(xa.sum()), 4)
    sum_y  = round(float(ya.sum()), 4)
    sum_x2 = round(float((xa**2).sum()), 4)
    sum_xy = round(float((xa * ya).sum()), 4)
    xbar   = round(float(xa.mean()), 4)
    body = (
        f"You have n = {n} data points for a simple linear regression Y = A + B·x + ε,\n"
        f"where ε ~ N(0, σ²) i.i.d.\n\n"
        f"Summary statistics:\n"
        f"  n        = {n}\n"
        f"  Σxᵢ      = {sum_x}    (x̄ = {xbar})\n"
        f"  Σyᵢ      = {sum_y}\n"
        f"  Σxᵢ²     = {sum_x2}\n"
        f"  Σxᵢyᵢ    = {sum_xy}\n\n"
        f"(a) Compute the OLS estimators:\n"
        f"    B̂ = [Σxᵢyᵢ − n·x̄·ȳ] / [Σxᵢ² − n·x̄²]  =  Sxy / Sxx\n"
        f"    Â = ȳ − B̂·x̄\n"
        f"(b) Compute the residual variance  s² = SSR / (n−2),\n"
        f"    where SSR = Σ(yᵢ − Â − B̂·xᵢ)².\n"
        f"(c) Compute the 95% confidence interval for B using the t-distribution\n"
        f"    with df = n−2:  B̂ ± t_{{n-2, 0.025}} · se(B̂),\n"
        f"    where se(B̂) = √(s² / Sxx).\n\n"
        f"Report: A_hat, B_hat, s2, B_lower, B_upper"
    )
    return body + _footer(multi=True)


def _prompt_gambler(inp: Dict[str, Any]) -> str:
    p, i, M = inp["p"], inp["i"], inp["M"]
    q = round(1 - p, 6)
    if abs(p - 0.5) < 1e-9:
        formula = "P(ruin | start=i) = (M − i) / M  [fair game, p = 0.5]"
    else:
        formula = "P(ruin | start=i) = [(q/p)^i − (q/p)^M] / [1 − (q/p)^M]"
    body = (
        f"A gambler starts with fortune i = {i} and plays until reaching 0 (ruin)\n"
        f"or M = {M} (win). Each bet is won with probability p = {p} (lost with q = {q}).\n\n"
        f"Using the Gambler's Ruin formula:\n"
        f"  {formula}\n\n"
        f"(a) Compute the probability of ruin.\n"
        f"(b) Compute the probability of winning (= 1 − ruin_prob).\n\n"
        f"Report: ruin_prob, win_prob"
    )
    return body + _footer(multi=True)


def _prompt_stationary(inp: Dict[str, Any]) -> str:
    P = inp["P"]
    K = len(P)
    mat_str = _fmt_matrix(P)
    body = (
        f"A Markov chain on {K} states has transition matrix:\n"
        f"P = {mat_str}\n\n"
        f"Find the stationary distribution π = (π₀, π₁, …, π_{K-1}) by solving\n"
        f"the linear system  π · P = π  with  Σᵢ πᵢ = 1.\n\n"
        f"Show each step of the linear system solution.\n\n"
        f"Report: " + ", ".join(f"pi_{i}" for i in range(K))
    )
    return body + _footer(multi=True)


def _prompt_range_dist(inp: Dict[str, Any]) -> str:
    n = inp["n"]
    body = (
        f"For a sample of size n = {n} from Uniform[0, 1], the sample range\n"
        f"R = max(Xᵢ) − min(Xᵢ) follows a Beta distribution.\n\n"
        f"(a) State the parameters α and β of this Beta distribution.\n"
        f"    Hint: R ~ Beta(n−1, 2).\n"
        f"(b) Confirm whether the distribution is verified (1 = yes, 0 = no).\n\n"
        f"Report: alpha, beta, verified"
    )
    return body + _footer(multi=True)


def _prompt_mle_efficiency(inp: Dict[str, Any]) -> str:
    dist, theta, n = inp["dist"], inp["theta"], inp["n"]
    body = (
        f"For the {dist.capitalize()} distribution with parameter θ = {theta}\n"
        f"and sample size n = {n}, the MLE is known to be efficient.\n\n"
        f"Compute:\n"
        f"  (1) The Fisher information I(θ) for a single observation.\n"
        f"  (2) The Rao-Cramér lower bound  RC = 1 / (n · I(θ)).\n"
        f"  (3) The simulated MLE variance (use standard results or simulate).\n"
        f"  (4) The efficiency ratio = (simulated MLE variance) / RC bound.\n"
        f"Report whether the MLE is efficient (ratio within 5% of 1.0 → 1, else → 0).\n\n"
        f"Report: rc_bound, efficiency_ratio, is_efficient"
    )
    return body + _footer(multi=True)


def _prompt_hpd(inp: Dict[str, Any]) -> str:
    alpha, beta = inp["alpha"], inp["beta"]
    level = inp.get("level", 0.95)
    pct = int(round(level * 100))
    body = (
        f"The posterior distribution is Beta(α = {alpha}, β = {beta}).\n\n"
        f"Find the {pct}% Highest Posterior Density (HPD) credible interval.\n\n"
        f"Note: for skewed distributions, the HPD interval is SHORTER than the\n"
        f"equal-tail interval — show why this is the case here.\n\n"
        f"Report: hpd_lower, hpd_upper"
    )
    return body + _footer(multi=True)


def _prompt_jeffreys(inp: Dict[str, Any]) -> str:
    x, n = inp["x"], inp["n"]
    body = (
        f"Using the Jeffreys prior for the Binomial model — Beta(0.5, 0.5) —\n"
        f"with x = {x} successes in n = {n} trials:\n\n"
        f"(a) State the posterior distribution Beta(α_post, β_post).\n"
        f"(b) Compute α_post = x + 0.5 and β_post = n − x + 0.5.\n"
        f"(c) Compute the posterior mean = α_post / (α_post + β_post).\n\n"
        f"Report: alpha_post, beta_post, posterior_mean"
    )
    return body + _footer(multi=True)


def _prompt_ppc(inp: Dict[str, Any]) -> str:
    a, b = inp["alpha_post"], inp["beta_post"]
    n_obs, x_obs = inp["n_obs"], inp["x_obs"]
    body = (
        f"A Beta({a}, {b}) posterior was fitted on Binomial data with n = {n_obs} trials.\n"
        f"A posterior predictive check is run using x_obs = {x_obs} as the test observation.\n\n"
        f"Compute the Bayesian p-value  P(T(y_rep) ≥ T_obs)  where T is the observed count,\n"
        f"by sampling from the posterior predictive distribution.\n\n"
        f"State whether the model passes  (p between 0.05 and 0.95 → 1, else → 0).\n\n"
        f"Report: p_value, passed"
    )
    return body + _footer(multi=True)


def _prompt_mle_map(inp: Dict[str, Any]) -> str:
    x, n, alpha, beta = inp["x"], inp["n"], inp["alpha"], inp["beta"]
    prior_mean = round(alpha / (alpha + beta), 6)
    body = (
        f"Binomial model: x = {x} successes in n = {n} trials.\n"
        f"Prior: Beta(α = {alpha}, β = {beta})  (prior mean = {prior_mean}).\n\n"
        f"Compute:\n"
        f"  (1) MLE = x / n\n"
        f"  (2) MAP = (x + α − 1) / (n + α + β − 2)\n"
        f"  (3) Posterior mean = (x + α) / (n + α + β)\n"
        f"  (4) Shrinkage = (MLE − MAP) / (MLE − prior_mean)\n\n"
        f"Show all working.\n\n"
        f"Report: mle, map, posterior_mean, shrinkage"
    )
    return body + _footer(multi=True)


def _prompt_ci_credible(inp: Dict[str, Any]) -> str:
    mu0     = inp["mu0"]
    tau0_sq = inp["tau0_sq"]
    sigma_sq = inp["sigma_sq"]
    n        = inp["n"]
    data     = inp["data"]
    x_bar    = round(sum(data) / len(data), 4)
    body = (
        f"You have n = {n} observations from Normal(μ, σ² = {sigma_sq}) with\n"
        f"sample mean x̄ = {x_bar:.4f}.\n"
        f"Prior on μ: Normal(μ₀ = {mu0}, τ₀² = {tau0_sq}).\n\n"
        f"(1) Compute the 95% frequentist confidence interval for μ:\n"
        f"    x̄ ± 1.96 · σ / √n\n"
        f"(2) Compute the 95% Bayesian credible interval for μ using the posterior\n"
        f"    Normal(μₙ, τₙ²) where:\n"
        f"    τₙ² = 1 / (1/τ₀² + n/σ²)\n"
        f"    μₙ = τₙ² · (μ₀/τ₀² + n·x̄/σ²)\n\n"
        f"Show both intervals and explain any difference.\n\n"
        f"Report: freq_lower, freq_upper, bayes_lower, bayes_upper"
    )
    return body + _footer(multi=True)


def _prompt_log_ml(inp: Dict[str, Any]) -> str:
    alpha, beta = inp["alpha"], inp["beta"]
    model = inp.get("model", "Beta-Binomial")
    if "x" in inp:
        # Beta-Binomial variant
        x, n = inp["x"], inp["n"]
        body = (
            f"For a Beta({alpha}, {beta}) prior with x = {x} successes in n = {n}\n"
            f"Binomial trials, compute the log marginal likelihood:\n\n"
            f"  log p(x | α, β) = log B(α+x, β+n−x) − log B(α, β)\n\n"
            f"where B(a, b) = Γ(a)·Γ(b) / Γ(a+b) is the Beta function.\n\n"
            f"Report: log_ml"
        )
    else:
        # Gamma-Poisson variant
        data = inp["data"]
        n, sum_x = len(data), sum(data)
        body = (
            f"For a Gamma(α = {alpha}, β = {beta}) prior on the Poisson rate λ,\n"
            f"with n = {n} observations summing to {sum_x}  (data = {data}),\n"
            f"compute the log marginal likelihood:\n\n"
            f"  log p(data | α, β) = log Γ(α + Σxᵢ) − log Γ(α)\n"
            f"                     + α·log β − (α + Σxᵢ)·log(β + n)\n"
            f"                     − Σ log(xᵢ!)\n\n"
            f"Report: log_ml"
        )
    return body + _footer(multi=False)


def _parse_beta_params(s: str):
    """Parse 'Beta(a, b)' → (float, float)."""
    m = re.search(r'Beta\(([^,]+),\s*([^)]+)\)', s, re.IGNORECASE)
    if m:
        return float(m.group(1).strip()), float(m.group(2).strip())
    return 1.0, 1.0


def _prompt_bayes_factor(inp: Dict[str, Any]) -> str:
    x, n = inp["x"], inp["n"]
    a1, b1 = _parse_beta_params(inp.get("M1", "Beta(1,1)"))
    a2, b2 = _parse_beta_params(inp.get("M2", "Beta(0.5,0.5)"))
    body = (
        f"Compare two models for Binomial data with x = {x} successes in n = {n} trials:\n\n"
        f"  M₁: Beta({a1}, {b1}) prior\n"
        f"  M₂: Beta({a2}, {b2}) prior\n\n"
        f"Compute the Bayes factor BF₁₂ = p(x|M₁) / p(x|M₂) using the\n"
        f"log marginal likelihood formula:\n"
        f"  log p(x|M) = log B(α+x, β+n−x) − log B(α, β)\n"
        f"  BF₁₂ = exp(log p(x|M₁) − log p(x|M₂))\n\n"
        f"Report: log_BF, BF"
    )
    return body + _footer(multi=True)


def _prompt_bayes_reg(inp: Dict[str, Any]) -> str:
    x_vals = inp["x"]
    y_vals = inp["y"]
    n = len(x_vals)
    body = (
        f"Bayesian linear regression with Normal-Inverse-Gamma conjugate prior.\n"
        f"Data: n = {n} observations.\n"
        f"  x values: {x_vals}\n"
        f"  y values: {[round(v, 4) for v in y_vals]}\n\n"
        f"Prior: μ₀ = 0, Λ₀ = 0.01·I, a₀ = 1, b₀ = 1  (diffuse prior).\n\n"
        f"Find the posterior mean of the intercept and slope coefficients.\n\n"
        f"Report: intercept_post, slope_post"
    )
    return body + _footer(multi=True)


def _prompt_conceptual(task: dict) -> str:
    question = task.get("question", "")
    return (
        f"{question}\n\n"
        f"Explain your reasoning step by step, addressing all key concepts.\n\n"
        f"{_REASONING_INSTRUCTION}"
    )


def _prompt_box_muller(inp: Dict[str, Any]) -> str:
    U, V = inp["U"], inp["V"]
    mu, sigma = inp.get("mu", 0.0), inp.get("sigma", 1.0)
    body = (
        f"Using the Box-Muller transform, generate two independent standard normal values\n"
        f"from U = {U} and V = {V}  (both drawn from Uniform(0, 1)).\n\n"
        f"Formulas:\n"
        f"  z₁ = √(−2·ln(U)) · cos(2π·V)\n"
        f"  z₂ = √(−2·ln(U)) · sin(2π·V)\n\n"
        f"(a) Compute z₁ and z₂.\n"
    )
    if mu != 0.0 or sigma != 1.0:
        body += (
            f"(b) Scale to Normal(μ={mu}, σ={sigma}):\n"
            f"    x₁ = {mu} + {sigma}·z₁\n"
            f"    x₂ = {mu} + {sigma}·z₂\n\n"
            f"Report: z1, z2, x1, x2"
        )
    else:
        body += "\nReport: z1, z2"
    return body + _footer(multi=True)


# ── Dispatch table ────────────────────────────────────────────────────────────

def _get_prefix(task_id: str) -> str:
    """Extract the task type prefix from a task_id like 'BETA_BINOM_01'."""
    parts = task_id.rsplit("_", 1)
    return parts[0] if len(parts) == 2 and parts[1].isdigit() else task_id


def build_prompt(task: dict) -> str:
    """
    Build a human-readable prompt string for the given task dict.

    Args:
        task: A single task dict from tasks.json.

    Returns:
        A prompt string ready to send to an LLM.
    """
    task_id: str = task["task_id"]
    notes: dict = task.get("notes", {})
    inp: dict = notes.get("inputs", {})
    topic: str = notes.get("topic", "")
    prefix = _get_prefix(task_id)

    header = f"[Task {task_id}  |  Tier {task['tier']}  |  {task['difficulty'].capitalize()}]\n\n"

    if prefix == "BETA_BINOM":
        body = _prompt_beta_binom(inp)
    elif prefix == "GAMMA_POISSON":
        body = _prompt_gamma_poisson(inp)
    elif prefix == "NORMAL_GAMMA":
        body = _prompt_normal_gamma(inp)
    elif prefix == "DIRICHLET":
        body = _prompt_dirichlet(inp)
    elif prefix == "DISC_MEDIAN":
        body = _prompt_disc_median(inp)
    elif prefix == "UNIFORM_MLE":
        body = _prompt_uniform_mle(inp)
    elif prefix == "BINOM_FLAT":
        body = _prompt_binom_flat(inp)
    elif prefix == "MINIMAX":
        body = _prompt_minimax(inp)
    elif prefix == "BAYES_RISK":
        body = _prompt_bayes_risk(inp)
    elif prefix == "BIAS_VAR":
        body = _prompt_bias_var(inp)
    elif prefix == "FISHER_INFO":
        body = _prompt_fisher_info(inp)
    elif prefix == "RC_BOUND":
        body = _prompt_rc_bound(inp)
    elif prefix == "OPT_SCALED":
        body = _prompt_opt_scaled(inp)
    elif prefix == "MSE_COMPARE":
        body = _prompt_mse_compare(inp)
    elif prefix == "MARKOV":
        body = _prompt_markov(inp, topic)
    elif prefix == "ORDER_STAT":
        body = _prompt_order_stat(inp, topic)
    elif prefix == "REGRESSION":
        body = _prompt_regression(inp)
    elif prefix == "BOX_MULLER":
        body = _prompt_box_muller(inp)
    elif prefix == "GAMBLER":
        body = _prompt_gambler(inp)
    elif prefix == "STATIONARY":
        body = _prompt_stationary(inp)
    elif prefix == "RANGE_DIST":
        body = _prompt_range_dist(inp)
    elif prefix == "MLE_EFFICIENCY":
        body = _prompt_mle_efficiency(inp)
    elif prefix == "HPD":
        body = _prompt_hpd(inp)
    elif prefix == "JEFFREYS":
        body = _prompt_jeffreys(inp)
    elif prefix == "PPC":
        body = _prompt_ppc(inp)
    elif prefix == "MLE_MAP":
        body = _prompt_mle_map(inp)
    elif prefix == "CI_CREDIBLE":
        body = _prompt_ci_credible(inp)
    elif prefix == "LOG_ML":
        body = _prompt_log_ml(inp)
    elif prefix == "BAYES_FACTOR":
        body = _prompt_bayes_factor(inp)
    elif prefix == "BAYES_REG":
        body = _prompt_bayes_reg(inp)
    elif prefix == "CONCEPTUAL":
        body = _prompt_conceptual(task)
    else:
        # Fallback: generic prompt from notes
        target_keys = [nt["key"] for nt in task.get("numeric_targets", [])]
        body = (
            f"Task topic: {topic}\n\n"
            f"Inputs: {inp}\n\n"
            f"Compute the following quantities: {', '.join(target_keys)}.\n\n"
            f"Report: {', '.join(target_keys)}"
        )
        body += _footer(multi=len(target_keys) > 1)

    return header + body


# ── parse_answer ──────────────────────────────────────────────────────────────

def parse_answer(response: str) -> List[float]:
    """
    Extract numeric values from the 'ANSWER: ...' line of an LLM response.

    Searches the last occurrence of a line starting with 'ANSWER:' and
    parses comma-separated floats.

    Args:
        response: Full response string from an LLM.

    Returns:
        List of floats extracted from the ANSWER line.
        Returns [] if no ANSWER line is found or parsing fails.
    """
    # Find last ANSWER: line (case-insensitive)
    pattern = re.compile(r"^\s*ANSWER\s*:\s*(.+)$", re.IGNORECASE | re.MULTILINE)
    matches = pattern.findall(response)
    if not matches:
        return []
    last_match = matches[-1].strip()
    # Parse comma-separated numbers; handle optional spaces
    try:
        return [float(v.strip()) for v in last_match.split(",") if v.strip()]
    except ValueError:
        return []


# ── format_numeric_targets ────────────────────────────────────────────────────

def format_numeric_targets(task: dict) -> List[float]:
    """
    Return the ground-truth values from task['numeric_targets'] as a flat list.

    The order matches the order they appear in the task dict, which corresponds
    to the order expected by parse_answer when reconstructing from the ANSWER line.

    Args:
        task: A single task dict from tasks.json.

    Returns:
        List of floats — one per numeric target, in declaration order.
    """
    return [float(nt["true_value"]) for nt in task.get("numeric_targets", [])]


# ── CLI test ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    tasks = json.load(open("data/raw_data/benchmark_v1/tasks.json"))
    for task in tasks[:3]:
        print(f"\n{'='*60}")
        print(f"Task: {task['task_id']}")
        print(build_prompt(task))
        print(f"Ground truth: {format_numeric_targets(task)}")
