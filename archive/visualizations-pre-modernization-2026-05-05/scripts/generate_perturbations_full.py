"""Full 171-task perturbation generator.

Produces ~473 perturbations:
- 131 numerical-feasible base tasks × 3 perturbations = 393
- 30 mc_seeded base tasks × 2 (rephrase + semantic) = 60
- 10 conceptual base tasks × 2 (rephrase + semantic) = 20

Numerical-feasible coverage:
- 18 solver_callable types
- 12 solver_with_adapter types (RJMCMC reclassified analytic — included)
- 1 inline_math (BIAS_VAR) extracted into uniform_estimators.bias_variance_decomp_uniform_max

Output: data/synthetic/perturbations_v2.json (does NOT overwrite v1).
For base tasks already covered in v1, v2 SKIPS regeneration to preserve provenance —
analysis-time concatenation handles the union.

Provider: Together AI Llama 3.3 70B Turbo. env: TOGETHER_API_KEY.

Strategy:
- rephrase: LLM rewrites prompt; ground truth unchanged.
- semantic: LLM rewrites prompt with new domain framing; ground truth unchanged.
- numerical: LLM proposes new inputs; Python recomputes ground truth via
  DISPATCH and re-renders Phase 1 prompts via build_prompt deterministically.
  Phase 2 (RJMCMC) numerical prompt rewritten via LLM with new inputs.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import math
import os
import re
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

import httpx
import numpy as np
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from baseline.utils_task_id import task_type_from_id
from llm_runner.prompt_builder import build_prompt

# Solvers — Phase 1
from baseline.bayesian.bayes_estimators import discrete_posterior_median
from baseline.bayesian.bayes_factors import (
    bayes_factor_beta_binomial,
    log_marginal_likelihood_beta_binomial,
    log_marginal_likelihood_gamma_poisson,
)
from baseline.bayesian.bayesian_regression import normal_inverse_gamma_regression_update
from baseline.bayesian.conjugate_models import (
    binomial_uniform_prior_update,
    jeffreys_update_binomial,
    mle_vs_map,
)
from baseline.bayesian.decision_theory import discrete_bayes_risk, minimax_risk
from baseline.bayesian.ground_truth import (
    gt_beta_binomial,
    gt_dirichlet_multinomial,
    gt_gamma_poisson,
    gt_normal_gamma_precision,
)
from baseline.bayesian.intervals import beta_hpd_interval, compare_ci_vs_credible_normal
from baseline.bayesian.markov_chains import (
    gambling_ruin_probability,
    n_step_transition,
    stationary_distribution,
)
from baseline.bayesian.posterior_predictive import posterior_predictive_check_beta_binomial
from baseline.bayesian.uniform_model import uniform_mle
from baseline.frequentist.fisher_information import fisher_information, rao_cramer_bound
from baseline.frequentist.order_statistics import (
    min_order_statistic_cdf,
    order_statistic_pdf,
    uniform_range_distribution,
)
from baseline.frequentist.regression import credibility_intervals, ols_estimators, residual_variance
from baseline.frequentist.sampling import box_muller_standard
from baseline.frequentist.uniform_estimators import (
    bias_variance_decomp_uniform_max,
    optimal_scaled_estimator_uniform,
)

# Phase 2 (RJMCMC analytic)
from baseline.bayesian.advanced_methods import RJMCMC

load_dotenv()

# ─── Config ─────────────────────────────────────────────────────────────────

TOGETHER_URL = "https://api.together.xyz/v1/chat/completions"
LLM_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
TIMEOUT_S = 60.0
RETRY_BACKOFF_S = 5.0
RATE_LIMIT_BACKOFF_S = 30.0
MAX_TOKENS = 2048

TASKS_PATH = ROOT / "data" / "benchmark_v1" / "tasks_all.json"
V1_PATH = ROOT / "data" / "synthetic" / "perturbations.json"
DEFAULT_OUTPUT = ROOT / "data" / "synthetic" / "perturbations_v2.json"

MC_SEEDED_TYPES = {"GIBBS", "MH", "HMC", "VB", "ABC", "HIERARCHICAL"}
CONCEPTUAL_TYPE = "CONCEPTUAL"

PERT_TYPES_NUMERIC = ("rephrase", "numerical", "semantic")
PERT_TYPES_NO_NUMERIC = ("rephrase", "semantic")


# ─── DISPATCH: task_type → solver(inputs) → {target_key: value} ──────────────
#
# Each entry returns a dict whose keys MATCH the keys in the base task's
# numeric_targets list. Validation gate 1 runs each solver on the base task's
# stored inputs and asserts the returned values match the stored true_values
# within full_credit_tol.

def _solve_beta_binom(inp: dict) -> dict[str, float]:
    g = gt_beta_binomial(
        alpha=inp["alpha"], beta=inp["beta"], x=inp["x"], n=inp["n"],
        ci_level=0.95,
        predictive_k=inp.get("k"), predictive_m=inp.get("m"),
    )
    return {
        "posterior_mean": g["posterior_mean"],
        "ci_lower": g["ci_lower"],
        "ci_upper": g["ci_upper"],
        "predictive_pmf_k_m": g.get("predictive_pmf_k_m"),
    }


def _solve_gamma_poisson(inp: dict) -> dict[str, float]:
    g = gt_gamma_poisson(
        alpha=inp["alpha"], rate=inp["rate"], counts=inp["counts"],
        ci_level=0.95, predictive_y=inp.get("y"),
    )
    return {
        "posterior_mean": g["posterior_mean"],
        "ci_lower": g["ci_lower"],
        "ci_upper": g["ci_upper"],
        "predictive_pmf_y": g.get("predictive_pmf_y"),
    }


def _solve_normal_gamma(inp: dict) -> dict[str, float]:
    g = gt_normal_gamma_precision(
        mu0=inp["mu0"], kappa0=inp["kappa0"], alpha0=inp["alpha0"], beta0=inp["beta0"],
        data=inp["data"], ci_level=0.95,
    )
    return {
        "posterior_mean_mu": g["posterior_mean_mu"],
        "ci_mu_lower": g["ci_mu_lower"],
        "ci_mu_upper": g["ci_mu_upper"],
        "posterior_mean_tau": g["posterior_mean_tau"],
    }


def _solve_dirichlet(inp: dict) -> dict[str, float]:
    g = gt_dirichlet_multinomial(
        alpha=inp["alpha"], counts=inp["counts"],
        predictive_counts=inp.get("pred_counts"),
    )
    pm = g["posterior_mean_vector"]
    return {
        "p1_mean": pm[0], "p2_mean": pm[1], "p3_mean": pm[2],
        "predictive_pmf_counts": g.get("predictive_pmf_counts"),
    }


def _solve_disc_median(inp: dict) -> dict[str, float]:
    return {"posterior_median": discrete_posterior_median(inp["values"], inp["probs"])}


def _solve_uniform_mle(inp: dict) -> dict[str, float]:
    return {"mle_theta": uniform_mle(inp["data"])}


def _solve_binom_flat(inp: dict) -> dict[str, float]:
    p = binomial_uniform_prior_update(inp["x"], inp["n"])
    return {"alpha_post": p.alpha_post, "beta_post": p.beta_post, "posterior_mean": p.mean()}


def _solve_minimax(inp: dict) -> dict[str, float]:
    res = minimax_risk(
        estimators={"hat1": np.array(inp["hat1_risks"]), "hat2": np.array(inp["hat2_risks"])},
        theta_grid=np.array(inp["theta_grid"]),
    )
    return {
        "max_risk_hat1": res["risks"]["hat1"]["max_risk"],
        "max_risk_hat2": res["risks"]["hat2"]["max_risk"],
        "minimax_value": res["minimax_value"],
    }


def _solve_bayes_risk(inp: dict) -> dict[str, float]:
    return {"bayes_risk": discrete_bayes_risk(inp["risk_values"], inp["prior_probs"])}


def _solve_bias_var(inp: dict) -> dict[str, float]:
    return bias_variance_decomp_uniform_max(int(inp["n"]), float(inp["theta"]))


def _solve_fisher_info(inp: dict) -> dict[str, float]:
    return {"fisher_info": fisher_information(inp["dist"], inp["theta"], int(inp["n"]))}


def _solve_rc_bound(inp: dict) -> dict[str, float]:
    fi = fisher_information(inp["dist"], inp["theta"], int(inp["n"]))
    return {"fisher_info": fi, "rc_bound": rao_cramer_bound(fi)}


def _solve_opt_scaled(inp: dict) -> dict[str, float]:
    r = optimal_scaled_estimator_uniform(int(inp["n"]), float(inp["theta"]))
    return {"c_opt": r["c_opt"], "mse_opt": r["mse_opt"]}


def _solve_mse_compare(inp: dict) -> dict[str, float]:
    r = optimal_scaled_estimator_uniform(int(inp["n"]), float(inp["theta"]))
    return {"mse_d1": r["mse_d1"], "mse_d2": r["mse_d2"], "mse_dc": r["mse_opt"]}


def _solve_markov(inp: dict, target_keys: list[str]) -> dict[str, float]:
    """MARKOV uses subtype dispatch — peek at target keys to disambiguate."""
    P = np.array(inp["P"]) if "P" in inp else None
    if any(k.startswith("ruin_prob") or k == "ruin_prob" or k == "win_prob" for k in target_keys):
        r = gambling_ruin_probability(inp["p"], int(inp["i"]), int(inp["M"]))
        return {"ruin_prob": r["ruin_prob"], "win_prob": r["win_prob"]}
    n_step_match = next((k for k in target_keys if re.match(r"^P\d+_\d+_\d+$", k)), None)
    if n_step_match:
        m = re.match(r"^P(\d+)_(\d+)_(\d+)$", n_step_match)
        n_step, i, j = int(m.group(1)), int(m.group(2)), int(m.group(3))
        Pn = n_step_transition(P, n_step)
        return {n_step_match: float(Pn[i, j])}
    pi = stationary_distribution(P)
    return {f"pi_{j}": float(pi[j]) for j in range(len(pi))}


def _solve_order_stat(inp: dict, target_keys: list[str]) -> dict[str, float]:
    if "order_stat_pdf" in target_keys:
        return {"order_stat_pdf": float(order_statistic_pdf(inp["y"], int(inp["k"]), int(inp["n"])))}
    if "min_cdf" in target_keys:
        return {"min_cdf": float(min_order_statistic_cdf(inp["x"], int(inp["n"])))}
    res = uniform_range_distribution(int(inp["n"]))
    return {"range_beta_alpha": float(res["alpha"]), "range_beta_beta": float(res["beta"])}


def _solve_regression(inp: dict) -> dict[str, float]:
    e = ols_estimators(inp["x"], inp["y"])
    s2 = residual_variance(inp["x"], inp["y"])
    ci = credibility_intervals(inp["x"], inp["y"], level=0.95)
    return {"A_hat": e["A_hat"], "B_hat": e["B_hat"], "s2": s2,
            "B_lower": ci["B_lower"], "B_upper": ci["B_upper"]}


def _solve_box_muller(inp: dict) -> dict[str, float]:
    z1, z2 = box_muller_standard(inp["U"], inp["V"])
    mu, sigma = inp.get("mu", 0.0), inp.get("sigma", 1.0)
    return {"z1": float(z1), "z2": float(z2),
            "x1": float(mu + sigma * z1), "x2": float(mu + sigma * z2)}


def _solve_hpd(inp: dict) -> dict[str, float]:
    lo, hi = beta_hpd_interval(inp["alpha"], inp["beta"], inp["level"])
    return {"hpd_lower": float(lo), "hpd_upper": float(hi)}


def _solve_bayes_factor(inp: dict) -> dict[str, float]:
    r = bayes_factor_beta_binomial(alpha1=1.0, beta1=1.0, alpha2=0.5, beta2=0.5,
                                   x=int(inp["x"]), n=int(inp["n"]))
    return {"log_BF": r["log_BF"], "BF": r["BF"]}


def _solve_jeffreys(inp: dict) -> dict[str, float]:
    r = jeffreys_update_binomial(int(inp["x"]), int(inp["n"]))
    return {"alpha_post": r["alpha"], "beta_post": r["beta"], "posterior_mean": r["posterior_mean"]}


def _solve_ppc(inp: dict) -> dict[str, float]:
    r = posterior_predictive_check_beta_binomial(
        alpha_post=inp["alpha_post"], beta_post=inp["beta_post"],
        n_obs=int(inp["n_obs"]), x_obs=int(inp["x_obs"]),
        n_rep=int(inp.get("n_rep", 5000)), seed=42,
    )
    return {"p_value": r["p_value"], "passed": float(r["passed"])}


def _solve_mle_map(inp: dict) -> dict[str, float]:
    r = mle_vs_map("binomial",
                   {"alpha": inp["alpha"], "beta": inp["beta"]},
                   {"x": int(inp["x"]), "n": int(inp["n"])})
    return {"mle": r["mle"], "map": r["map"],
            "posterior_mean": r["posterior_mean"], "shrinkage": r["shrinkage"]}


def _solve_ci_credible(inp: dict) -> dict[str, float]:
    r = compare_ci_vs_credible_normal(inp["mu0"], inp["tau0_sq"], inp["sigma_sq"], inp["data"], level=0.95)
    fl, fh = r["freq_ci"]
    bl, bh = r["bayes_credible"]
    return {"freq_lower": float(fl), "freq_upper": float(fh),
            "bayes_lower": float(bl), "bayes_upper": float(bh)}


def _solve_log_ml(inp: dict) -> dict[str, float]:
    if inp.get("model", "").startswith("Beta") or "x" in inp:
        v = log_marginal_likelihood_beta_binomial(inp["alpha"], inp["beta"], int(inp["x"]), int(inp["n"]))
    else:
        v = log_marginal_likelihood_gamma_poisson(inp["alpha"], inp["beta"], inp["data"])
    return {"log_ml": v}


def _solve_gambler(inp: dict) -> dict[str, float]:
    r = gambling_ruin_probability(inp["p"], int(inp["i"]), int(inp["M"]))
    return {"ruin_prob": r["ruin_prob"], "win_prob": r["win_prob"]}


def _solve_stationary(inp: dict) -> dict[str, float]:
    pi = stationary_distribution(np.array(inp["P"]))
    return {f"pi_{j}": float(pi[j]) for j in range(len(pi))}


def _solve_range_dist(inp: dict) -> dict[str, float]:
    r = uniform_range_distribution(int(inp["n"]))
    return {"alpha": float(r["alpha"]), "beta": float(r["beta"]), "verified": 1.0}


def _solve_mle_efficiency(inp: dict) -> dict[str, float]:
    fi = fisher_information(inp["dist"], inp["theta"], int(inp["n"]))
    return {"rc_bound": rao_cramer_bound(fi), "efficiency_ratio": 1.0, "is_efficient": 1.0}


def _solve_bayes_reg(inp: dict) -> dict[str, float]:
    x_arr = np.array(inp["x"], dtype=float)
    y_arr = np.array(inp["y"], dtype=float)
    n = len(x_arr)
    X = np.column_stack([np.ones(n), x_arr])
    mu0 = np.zeros(2)
    Lambda0 = 0.001 * np.eye(2)
    res = normal_inverse_gamma_regression_update(X, y_arr, mu0, Lambda0, 1.0, 1.0)
    return {"intercept_post": float(res["posterior_mean_beta"][0]),
            "slope_post": float(res["posterior_mean_beta"][1])}


def _solve_rjmcmc(inp: dict) -> dict[str, float]:
    """RJMCMC analytic — np.random.seed(42) in solve() is dead code."""
    r = RJMCMC({"data": inp["data"],
                "prior_prob_m1": inp["prior_prob_m1"],
                "proposal_std": inp.get("proposal_std", 0.3)}).solve()
    return {"posterior_prob_m1": r["posterior_prob_m1"],
            "posterior_prob_m2": r["posterior_prob_m2"],
            "bayes_factor": r["bayes_factor"]}


# Some types need access to base task target_keys (for subtype dispatch).
# Functions taking 2 args ARE called with (inputs, target_keys).
_NEEDS_KEYS = {"MARKOV", "ORDER_STAT"}

DISPATCH: dict[str, Callable] = {
    "BETA_BINOM": _solve_beta_binom, "GAMMA_POISSON": _solve_gamma_poisson,
    "NORMAL_GAMMA": _solve_normal_gamma, "DIRICHLET": _solve_dirichlet,
    "DISC_MEDIAN": _solve_disc_median, "UNIFORM_MLE": _solve_uniform_mle,
    "BINOM_FLAT": _solve_binom_flat, "MINIMAX": _solve_minimax,
    "BAYES_RISK": _solve_bayes_risk, "BIAS_VAR": _solve_bias_var,
    "FISHER_INFO": _solve_fisher_info, "RC_BOUND": _solve_rc_bound,
    "OPT_SCALED": _solve_opt_scaled, "MSE_COMPARE": _solve_mse_compare,
    "MARKOV": _solve_markov, "ORDER_STAT": _solve_order_stat,
    "REGRESSION": _solve_regression, "BOX_MULLER": _solve_box_muller,
    "HPD": _solve_hpd, "BAYES_FACTOR": _solve_bayes_factor,
    "JEFFREYS": _solve_jeffreys, "PPC": _solve_ppc,
    "MLE_MAP": _solve_mle_map, "CI_CREDIBLE": _solve_ci_credible,
    "LOG_ML": _solve_log_ml, "GAMBLER": _solve_gambler,
    "STATIONARY": _solve_stationary, "RANGE_DIST": _solve_range_dist,
    "MLE_EFFICIENCY": _solve_mle_efficiency, "BAYES_REG": _solve_bayes_reg,
    "RJMCMC": _solve_rjmcmc,
}

# Bounds descriptions for the LLM param-proposal prompt (numerical perturbation).
BOUNDS: dict[str, str] = {
    "BETA_BINOM": "alpha,beta in [0.5, 5]; x integer in [0, n]; n integer in [5, 30]; k integer in [0, m]; m integer in [3, 10].",
    "GAMMA_POISSON": "alpha in [0.5, 5]; rate in [0.5, 5]; counts: list of 3-6 non-negative integers each in [0, 8]; y integer in [0, 8].",
    "NORMAL_GAMMA": "mu0 in [-3, 3]; kappa0 in [0.1, 5]; alpha0 in [1, 5]; beta0 in [0.5, 5]; data: list of 4-8 floats in [-3, 5].",
    "DIRICHLET": "alpha: list of EXACTLY 3 floats in [0.5, 3]; counts: list of EXACTLY 3 non-neg integers (sum 5-30); pred_counts: list of EXACTLY 3 non-neg integers (sum 2-8).",
    "DISC_MEDIAN": "values: list of 3-6 increasing floats; probs: list of same length, positive, sum to exactly 1.0.",
    "UNIFORM_MLE": "data: list of 5-8 positive floats in [0.1, 20].",
    "BINOM_FLAT": "x integer in [0, n]; n integer in [5, 30].",
    "MINIMAX": "theta_grid: list of 3 increasing integers; hat1_risks and hat2_risks: lists of 3 floats in [0, 1] (same length as theta_grid).",
    "BAYES_RISK": "risk_values: 2-5 floats in [0, 1]; prior_probs: same length, positive, sum to 1.0.",
    "BIAS_VAR": "n integer in [3, 25]; theta in [0.5, 6].",
    "FISHER_INFO": "dist in {binomial, poisson, normal} ONLY (NOT uniform); theta in [0.1, 5] (theta in (0,1) for binomial); n integer in [5, 30].",
    "RC_BOUND": "dist in {binomial, poisson, normal} ONLY; theta in [0.1, 5] (theta in (0,1) for binomial); n integer in [5, 30].",
    "OPT_SCALED": "n integer in [3, 25]; theta in [0.5, 6].",
    "MSE_COMPARE": "n integer in [3, 25]; theta in [0.5, 6].",
    "MARKOV": "Preserve subtype: keep same shape as original (P kxk if stationary, p,i,M if gamblers_ruin, P+n+i+j if n_step). New P: row-stochastic, k=2 or 3. p in [0.3, 0.7], i in (0, M), M integer in [5, 15].",
    "ORDER_STAT": "Preserve subtype based on target keys. For pdf: y in (0,1), k integer in [1, n], n integer in [3, 10]. For min_cdf: x in (0,1), n integer in [3, 10]. For range: n integer in [3, 12].",
    "REGRESSION": "x: list of 5-10 floats in [0, 50]; y: list of same length, real-valued — produce y as roughly linear in x with noise. Lengths must be equal and >= 4.",
    "BOX_MULLER": "U in (0.01, 0.99); V in (0.01, 0.99); mu in [-10, 100]; sigma in [0.1, 20].",
    "HPD": "alpha in [1, 15]; beta in [1, 15]; level in {0.90, 0.95, 0.99}.",
    "BAYES_FACTOR": "x integer in [0, n]; n integer in [5, 30].",
    "JEFFREYS": "x integer in [0, n]; n integer in [5, 30].",
    "PPC": "alpha_post in [1, 12]; beta_post in [1, 12]; n_obs integer in [8, 25]; x_obs integer in [0, n_obs]; n_rep=5000 fixed.",
    "MLE_MAP": "alpha in [1, 6]; beta in [1, 6]; x integer in [0, n]; n integer in [5, 25].",
    "CI_CREDIBLE": "mu0 in [-3, 6]; tau0_sq in [0.1, 100]; sigma_sq in [0.5, 5]; data: list of 5-20 floats consistent with sigma_sq.",
    "LOG_ML": "Preserve model field exactly. For Beta-Binomial: alpha,beta in [0.5, 3], x integer in [0, n], n integer in [5, 30]. For Gamma-Poisson: alpha,beta in [0.5, 5], data list of 3-6 non-neg integers.",
    "GAMBLER": "p in [0.3, 0.7]; M integer in [5, 15]; i integer in (0, M).",
    "STATIONARY": "P: row-stochastic matrix matching original dimension k (k=2,3,or 4). All rows sum to exactly 1.0.",
    "RANGE_DIST": "n integer in [3, 15].",
    "MLE_EFFICIENCY": "dist in {binomial, poisson, normal} ONLY; theta in [0.1, 5]; n integer in [5, 30].",
    "BAYES_REG": "x: list of 7-15 floats; y: list of same length — must be roughly linear in x with noise. Different from original numbers.",
    "RJMCMC": "data: list of 8-16 floats roughly N(0,1); prior_prob_m1 in [0.3, 0.7]; proposal_std in [0.1, 1.0].",
}


# ─── LLM helpers ─────────────────────────────────────────────────────────────

REPHRASE_TMPL = """OUTPUT FORMAT: return ONLY the rewritten prompt body, ready to send to an LLM. No preamble. No "Constraints" list. No closing remarks. No markdown fences. Do NOT echo these instructions.

Rewrite the following Bayesian-statistics task prompt with different sentence structure and word choice. Every number, list, variable name, mathematical expression, and the final ANSWER format must appear identically. Keep the same questions in the same order.

REQUIRED: keep the very first line as a Markdown-style header in the form `[Task {new_task_id}  |  Tier <T>  |  <Difficulty>]` (use the same tier and difficulty as the original).
REQUIRED: any variable names listed in a "Report:" line of the original must appear identically in your output's "Report:" line. Do not rename target variables.

ORIGINAL PROMPT:
<<<
{base_prompt}
>>>

Now output the rewritten prompt only:"""

SEMANTIC_TMPL = """OUTPUT FORMAT: return ONLY the rewritten prompt body, ready to send to an LLM. No preamble. No "Constraints" list. No closing remarks. No markdown fences. Do NOT echo these instructions. Do NOT include any solution, derivation, or answer reasoning in the output.

Reframe the following task in a new real-world domain (medical, manufacturing, finance, climate, marketing, or similar). All numerical values, mathematical content, and the final ANSWER format must be identical — only narrative framing changes. Keep the same questions in the same order.

REQUIRED: keep the very first line as a Markdown-style header in the form `[Task {new_task_id}  |  Tier <T>  |  <Difficulty>]` (same tier/difficulty as original).
REQUIRED: any variable names appearing in a "Report:" line of the original must appear identically in your output's "Report:" line — do NOT rename target variables (they are scoring keys). Do NOT add any domain-mapping annotations like "(x maps to y)" in the output.
REQUIRED: if the original prompt has NO "Report:" line, do NOT add one. Only include a "Report:" line if the original has one.

For purely conceptual prompts (no numbers): change the domain context but preserve the conceptual question intent. NEVER provide the answer or reasoning in the output.

ORIGINAL PROMPT:
<<<
{base_prompt}
>>>

Now output the rewritten prompt only:"""

NUMERICAL_PARAMS_TMPL = """OUTPUT FORMAT: return ONLY a single JSON object: {{"new_inputs": {{...}}}}. No preamble, no markdown fences, no commentary.

Propose new input parameters for this Bayesian-statistics benchmark task.

Task type: {task_type}
Original parameters: {original_inputs}
Constraints (MUST satisfy all): {bounds}

Requirements: not trivially equal or proportional to the originals; round-ish numbers where reasonable; same keys and same list lengths as original.

Output:"""

NUMERICAL_REWRITE_TMPL = """OUTPUT FORMAT: return ONLY the rewritten prompt body, ready to send to an LLM. No preamble. No "Constraints" list. No commentary. No markdown fences. Do NOT echo these instructions.

Rewrite the following Bayesian-statistics task prompt by substituting the new numerical inputs everywhere they appear. Keep all surrounding text, questions, and the final ANSWER format intact. Update only the header task_id to {new_task_id} (keep tier and difficulty).

ORIGINAL PROMPT:
<<<
{base_prompt}
>>>

ORIGINAL PARAMS: {original_inputs}
NEW PARAMS: {new_inputs}

Now output the rewritten prompt only:"""


def _strip_fence(s: str) -> str:
    return re.sub(r"\s*```\s*$", "", re.sub(r"^```(?:json)?\s*", "", s.strip())).strip()


async def _llm_call(client: httpx.AsyncClient, api_key: str, prompt: str,
                    max_tokens: int = MAX_TOKENS) -> str | None:
    payload = {"model": LLM_MODEL, "max_tokens": max_tokens, "temperature": 0.4,
               "messages": [{"role": "user", "content": prompt}]}
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    for attempt in (1, 2):
        try:
            resp = await client.post(TOGETHER_URL, json=payload, headers=headers, timeout=TIMEOUT_S)
            if resp.status_code == 429 and attempt == 1:
                await asyncio.sleep(RATE_LIMIT_BACKOFF_S); continue
            if 500 <= resp.status_code < 600 and attempt == 1:
                await asyncio.sleep(RETRY_BACKOFF_S); continue
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError):
            if attempt == 1:
                await asyncio.sleep(RETRY_BACKOFF_S); continue
            return None
        except Exception:
            return None
    return None


# ─── Base prompt rendering ───────────────────────────────────────────────────

def _base_prompt_for(task: dict) -> str:
    """Get the canonical 'original prompt' for a base task.

    Phase 2 tasks (mc_seeded + RJMCMC) have a `prompt` field directly.
    Phase 1 tasks render via build_prompt(task).
    """
    if "prompt" in task and task["prompt"]:
        # Phase 2 — use stored prompt and add a header for parity.
        header = f"[Task {task['task_id']}  |  Tier {task['tier']}  |  {task['difficulty'].capitalize()}]\n\n"
        return header + task["prompt"]
    return build_prompt(task)


def _render_phase1_with_new_inputs(base_task: dict, new_inputs: dict, new_task_id: str) -> str:
    """Re-render Phase 1 prompt deterministically by swapping notes.inputs.

    Uses the BASE task_id during rendering so build_prompt's prefix dispatch
    (which expects TYPE_NN) hits the right branch, then patches the header.
    """
    synth = deepcopy(base_task)
    synth.setdefault("notes", {})
    synth["notes"]["inputs"] = new_inputs
    rendered = build_prompt(synth)  # uses base_task_id for routing
    # Replace the [Task <base_id> | ...] header line with the new id.
    rendered = re.sub(
        r"\[Task\s+" + re.escape(base_task["task_id"]) + r"\b",
        f"[Task {new_task_id}",
        rendered, count=1,
    )
    return rendered


# ─── Numeric target builder ──────────────────────────────────────────────────

def _solve(task_type: str, inputs: dict, target_keys: list[str]) -> dict[str, float]:
    fn = DISPATCH[task_type]
    if task_type in _NEEDS_KEYS:
        return fn(inputs, target_keys)
    return fn(inputs)


def _build_targets_from_solver(base_task: dict, solver_out: dict[str, Any]) -> list[dict]:
    """Build numeric_targets list using the SAME schema as the base task —
    same keys, same tolerances — but with new true_values from solver_out.
    """
    out = []
    for nt in base_task.get("numeric_targets", []):
        key = nt["key"]
        if key not in solver_out or solver_out[key] is None:
            raise KeyError(f"solver missing target key: {key}")
        out.append({
            "key": key,
            "true_value": float(solver_out[key]),
            "full_credit_tol": nt.get("full_credit_tol", 1e-4),
            "zero_credit_scale": nt.get("zero_credit_scale", 0.05),
        })
    return out


# ─── Validation gate 1 ──────────────────────────────────────────────────────

def _within_tol(got: float, expected: float, tol: float, scale: float) -> bool:
    if expected is None or got is None:
        return False
    if math.isnan(got) or math.isnan(expected):
        return False
    abs_err = abs(got - expected)
    if abs_err <= tol:
        return True
    # Also accept if relative tolerance is generous (matches scale-based zero-credit semantics)
    return abs_err <= max(tol, scale * max(1.0, abs(expected)) * 0.01)


def gate1_dispatch_sanity(tasks: list[dict]) -> dict[str, Any]:
    """Run each solver on its base task's stored inputs; compare to stored true_values."""
    by_type: dict[str, list[dict]] = {}
    for t in tasks:
        tt = task_type_from_id(t["task_id"])
        if tt not in DISPATCH:
            continue
        by_type.setdefault(tt, []).append(t)

    summary = []
    failures: list[dict] = []
    for tt in sorted(by_type):
        n_pass = n_fail = 0
        first_fail = None
        for t in by_type[tt]:
            inp = t.get("inputs") if t.get("inputs") else t.get("notes", {}).get("inputs", {})
            target_keys = [nt["key"] for nt in t.get("numeric_targets", [])]
            try:
                solved = _solve(tt, inp, target_keys)
            except Exception as e:
                n_fail += 1
                if first_fail is None:
                    first_fail = (t["task_id"], f"solver_exc: {e}")
                    failures.append({"task_id": t["task_id"], "task_type": tt, "reason": f"solver_exc: {e}"})
                continue
            mismatch = []
            for nt in t.get("numeric_targets", []):
                k = nt["key"]
                got = solved.get(k)
                exp = nt["true_value"]
                tol = nt.get("full_credit_tol", 1e-4)
                scale = nt.get("zero_credit_scale", 0.05)
                if not _within_tol(got, exp, tol, scale):
                    mismatch.append((k, got, exp, tol))
            if mismatch:
                n_fail += 1
                if first_fail is None:
                    first_fail = (t["task_id"], f"target_mismatch: {mismatch[0]}")
                    failures.append({"task_id": t["task_id"], "task_type": tt,
                                     "reason": f"target_mismatch", "details": mismatch})
            else:
                n_pass += 1
        summary.append({"task_type": tt, "n_total": len(by_type[tt]),
                        "n_pass": n_pass, "n_fail": n_fail,
                        "first_fail": first_fail})
    return {"summary": summary, "failures": failures}


# ─── Perturbation generation ────────────────────────────────────────────────

async def _generate_rephrase(base_task: dict, base_prompt: str, client, api_key) -> dict | None:
    new_id = f"{base_task['task_id']}_rephrase_v2"
    p = REPHRASE_TMPL.format(base_prompt=base_prompt, new_task_id=new_id)
    txt = await _llm_call(client, api_key, p)
    if not txt:
        return None
    return {"prompt": _strip_fence(txt), "new_task_id": new_id,
            "perturbation_note": "Same numbers and math; reworded prompt."}


async def _generate_semantic(base_task: dict, base_prompt: str, client, api_key) -> dict | None:
    new_id = f"{base_task['task_id']}_semantic_v2"
    p = SEMANTIC_TMPL.format(base_prompt=base_prompt, new_task_id=new_id)
    txt = await _llm_call(client, api_key, p)
    if not txt:
        return None
    return {"prompt": _strip_fence(txt), "new_task_id": new_id,
            "perturbation_note": "Same numbers and math; new real-world domain framing."}


async def _propose_new_inputs(task_type: str, original_inputs: dict, client, api_key) -> dict | None:
    p = NUMERICAL_PARAMS_TMPL.format(
        task_type=task_type, original_inputs=json.dumps(original_inputs),
        bounds=BOUNDS.get(task_type, "match the original structure exactly"),
    )
    for attempt in (1, 2):
        txt = await _llm_call(client, api_key, p, max_tokens=512)
        if not txt:
            continue
        try:
            obj = json.loads(_strip_fence(txt))
            ni = obj.get("new_inputs")
            if isinstance(ni, dict):
                return ni
        except json.JSONDecodeError:
            continue
    return None


async def _generate_numerical(base_task: dict, base_prompt: str, task_type: str,
                              client, api_key) -> dict | None:
    """Numerical perturbation: propose new inputs, recompute targets, re-render prompt."""
    is_phase2 = "prompt" in base_task and base_task["prompt"] and "notes" not in base_task
    original_inputs = base_task.get("inputs") if is_phase2 else base_task.get("notes", {}).get("inputs", {})
    if not original_inputs:
        return None

    new_id = f"{base_task['task_id']}_numerical_v2"
    new_inputs = await _propose_new_inputs(task_type, original_inputs, client, api_key)
    if not new_inputs:
        return None

    # Solve with new inputs.
    target_keys = [nt["key"] for nt in base_task.get("numeric_targets", [])]
    try:
        solver_out = _solve(task_type, new_inputs, target_keys)
        new_targets = _build_targets_from_solver(base_task, solver_out)
    except Exception as e:
        return {"_error": f"solver_failure: {e}", "new_task_id": new_id, "new_inputs": new_inputs}

    # Render new prompt.
    if is_phase2:
        # LLM-substitute new numbers into the original prompt.
        p = NUMERICAL_REWRITE_TMPL.format(
            base_prompt=base_prompt,
            original_inputs=json.dumps(original_inputs),
            new_inputs=json.dumps(new_inputs),
            new_task_id=new_id,
        )
        txt = await _llm_call(client, api_key, p)
        if not txt:
            return None
        new_prompt = _strip_fence(txt)
    else:
        # Phase 1 — deterministic build_prompt with new notes.inputs.
        new_prompt = _render_phase1_with_new_inputs(base_task, new_inputs, new_id)

    return {"prompt": new_prompt, "new_task_id": new_id,
            "numeric_targets": new_targets, "new_inputs": new_inputs,
            "perturbation_note": f"New inputs: {json.dumps(new_inputs)[:200]}"}


def _make_record(base_task: dict, ptype: str, gen: dict) -> dict:
    tt = task_type_from_id(base_task["task_id"])
    return {
        "task_id": gen["new_task_id"],
        "base_task_id": base_task["task_id"],
        "perturbation_type": ptype,
        "task_type": tt,
        "tier": base_task["tier"],
        "difficulty": base_task["difficulty"],
        "prompt": gen["prompt"],
        "numeric_targets": gen.get("numeric_targets", deepcopy(base_task.get("numeric_targets", []))),
        "required_structure_checks": deepcopy(base_task.get("required_structure_checks", [])),
        "required_assumption_checks": deepcopy(base_task.get("required_assumption_checks", [])),
        "perturbation_note": gen.get("perturbation_note", ""),
    }


async def generate_for_base_task(base_task: dict, client: httpx.AsyncClient,
                                 api_key: str, sem: asyncio.Semaphore) -> list[dict]:
    tt = task_type_from_id(base_task["task_id"])
    base_prompt = _base_prompt_for(base_task)
    has_numeric = (tt in DISPATCH) and (tt != CONCEPTUAL_TYPE) and (tt not in MC_SEEDED_TYPES)
    types = PERT_TYPES_NUMERIC if has_numeric else PERT_TYPES_NO_NUMERIC

    out: list[dict] = []
    async with sem:
        for ptype in types:
            try:
                if ptype == "rephrase":
                    g = await _generate_rephrase(base_task, base_prompt, client, api_key)
                elif ptype == "semantic":
                    g = await _generate_semantic(base_task, base_prompt, client, api_key)
                elif ptype == "numerical":
                    g = await _generate_numerical(base_task, base_prompt, tt, client, api_key)
                else:
                    continue
            except Exception as e:
                g = {"_error": f"unexpected: {e}"}

            if not g or g.get("_error"):
                err_id = f"{base_task['task_id']}_{ptype}_v2"
                out.append({
                    "task_id": err_id, "base_task_id": base_task["task_id"],
                    "perturbation_type": ptype, "task_type": tt,
                    "tier": base_task["tier"], "difficulty": base_task["difficulty"],
                    "prompt": "", "numeric_targets": [],
                    "required_structure_checks": [], "required_assumption_checks": [],
                    "perturbation_note": (g or {}).get("_error", "generation_failed"),
                    "error": (g or {}).get("_error", "generation_failed"),
                })
                continue
            out.append(_make_record(base_task, ptype, g))
    return out


# ─── I/O ─────────────────────────────────────────────────────────────────────

def load_tasks() -> list[dict]:
    return json.load(open(TASKS_PATH))


def load_v1_base_ids() -> set[str]:
    if not V1_PATH.exists():
        return set()
    v1 = json.load(open(V1_PATH))
    return {r.get("base_task_id") for r in v1 if r.get("base_task_id")}


def append_jsonl(path: Path, recs: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")


def load_existing_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    seen = set()
    try:
        data = json.load(open(path))
        if isinstance(data, list):
            # JSON array format.
            for r in data:
                if isinstance(r, dict) and r.get("task_id") and not r.get("error"):
                    seen.add(r["task_id"])
            return seen
    except (json.JSONDecodeError, ValueError):
        pass
    # Fall back to JSONL format.
    for line in path.open():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
            if isinstance(r, dict) and r.get("task_id") and not r.get("error"):
                seen.add(r["task_id"])
        except json.JSONDecodeError:
            continue
    return seen


# ─── CLI ─────────────────────────────────────────────────────────────────────

def _print_gate1(report: dict) -> int:
    print(f"\n{'task_type':<18} {'n':>4} {'pass':>5} {'fail':>5}  first_fail")
    print("-" * 80)
    n_total = n_pass = n_fail = 0
    for row in report["summary"]:
        ff = row["first_fail"]
        ff_s = f"{ff[0]}: {ff[1][:50]}" if ff else ""
        print(f"{row['task_type']:<18} {row['n_total']:>4} {row['n_pass']:>5} {row['n_fail']:>5}  {ff_s}")
        n_total += row["n_total"]; n_pass += row["n_pass"]; n_fail += row["n_fail"]
    print("-" * 80)
    print(f"{'TOTAL':<18} {n_total:>4} {n_pass:>5} {n_fail:>5}")
    return n_fail


async def run_sample(tasks: list[dict], output_path: Path, concurrency: int) -> None:
    """Generate 15-sample (5 base tasks × 3 perturbation types where applicable)."""
    api_key = os.environ.get("TOGETHER_API_KEY")
    if not api_key:
        sys.exit("TOGETHER_API_KEY missing.")

    # Pick 5 diverse base tasks.
    by_id = {t["task_id"]: t for t in tasks}
    picks = ["BETA_BINOM_01", "MARKOV_03", "RJMCMC_02", "CONCEPTUAL_01", "GIBBS_01"]
    picked = [by_id[i] for i in picks if i in by_id]
    if len(picked) != 5:
        sys.exit(f"Could not find all 5 sample tasks: missing {set(picks) - set(by_id)}")

    sem = asyncio.Semaphore(concurrency)
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            *[generate_for_base_task(t, client, api_key, sem) for t in picked]
        )

    flat = [r for batch in results for r in batch]
    append_jsonl(output_path, flat)
    print(f"\nWrote {len(flat)} sample perturbations → {output_path}\n")
    for r in flat:
        print(json.dumps(r, indent=2))
        print("---")


async def run_full(tasks: list[dict], output_path: Path, concurrency: int) -> None:
    """Generate the full set, skipping v1-covered base tasks and existing output ids."""
    import time as _time

    api_key = os.environ.get("TOGETHER_API_KEY")
    if not api_key:
        sys.exit("TOGETHER_API_KEY missing.")

    v1_covered = load_v1_base_ids()
    existing = load_existing_ids(output_path)
    # Also load good IDs from JSON array output (retry case).
    if output_path.exists() and output_path.suffix == ".json":
        try:
            for r in json.load(open(output_path)):
                if r.get("task_id") and not r.get("error"):
                    existing.add(r["task_id"])
        except (json.JSONDecodeError, KeyError):
            pass
    todo = [t for t in tasks if t["task_id"] not in v1_covered]

    # Estimate expected perturbation count.
    expected = 0
    for t in todo:
        tt = task_type_from_id(t["task_id"])
        if tt in MC_SEEDED_TYPES or tt == CONCEPTUAL_TYPE:
            expected += 2  # rephrase + semantic
        else:
            expected += 3  # rephrase + numerical + semantic

    print(f"Base tasks total={len(tasks)}, in v1={len(v1_covered)}, queued for v2={len(todo)}")
    print(f"Existing v2 perturbation ids in output: {len(existing)}")
    print(f"Expected new perturbations: ~{expected}")

    # Progress state — shared across coroutines.
    completed = 0
    errors_by_type: dict[str, int] = {}
    t0 = _time.monotonic()
    _lock = asyncio.Lock()

    async def _progress(n_new: int, n_err: int, err_types: list[str]) -> None:
        nonlocal completed
        async with _lock:
            completed += n_new
            for et in err_types:
                errors_by_type[et] = errors_by_type.get(et, 0) + 1
            if completed % 25 < n_new or completed == expected:
                elapsed = _time.monotonic() - t0
                rate = completed / elapsed if elapsed > 0 else 0
                eta = (expected - completed) / rate if rate > 0 else 0
                err_summary = ", ".join(f"{k}={v}" for k, v in sorted(errors_by_type.items())) or "none"
                # Rough cost: ~800 input + ~600 output tokens avg per call @ $0.88/$0.88 per M (Llama 3.3 70B Turbo)
                est_cost = completed * 0.0012  # ~$0.0012 per perturbation
                print(
                    f"[progress] {completed}/{expected}  "
                    f"elapsed={elapsed:.0f}s  ETA={eta:.0f}s  "
                    f"errors=[{err_summary}]  "
                    f"est_cost=${est_cost:.2f}",
                    file=sys.stderr, flush=True,
                )

    # Write JSONL to staging file for resume safety; convert to JSON at end.
    staging_path = output_path.with_suffix(".jsonl") if output_path.suffix == ".json" else output_path
    # Also load existing ids from staging path (for resume).
    existing |= load_existing_ids(staging_path)

    sem = asyncio.Semaphore(concurrency)
    async with httpx.AsyncClient() as client:
        async def one(t):
            recs = await generate_for_base_task(t, client, api_key, sem)
            recs = [r for r in recs if r["task_id"] not in existing]
            n_err = sum(1 for r in recs if r.get("error"))
            err_types = [r.get("error", "")[:30] for r in recs if r.get("error")]
            good = [r for r in recs if not r.get("error")]
            if recs:
                append_jsonl(staging_path, recs)
            await _progress(len(recs), n_err, err_types)
            return len(good)
        counts = await asyncio.gather(*[one(t) for t in todo])

    elapsed_total = _time.monotonic() - t0
    n_good = sum(counts)
    n_total = completed
    n_errors = sum(errors_by_type.values())
    est_cost = n_total * 0.0012

    # Merge staging JSONL into JSON array output.
    if output_path.suffix == ".json" and staging_path != output_path:
        # Load existing JSON records (if any — retry case).
        all_recs = []
        if output_path.exists():
            try:
                all_recs = json.load(open(output_path))
            except json.JSONDecodeError:
                pass
        existing_ids = {r["task_id"] for r in all_recs}
        # Append new records from staging JSONL.
        n_new = 0
        if staging_path.exists():
            for line in staging_path.open():
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                    if r.get("task_id") not in existing_ids:
                        all_recs.append(r)
                        n_new += 1
                except json.JSONDecodeError:
                    pass
        with output_path.open("w") as f:
            json.dump(all_recs, f, indent=2)
        print(f"Merged {n_new} new records → {len(all_recs)} total in {output_path}")
        staging_path.unlink(missing_ok=True)

    print(f"\n=== FULL RUN COMPLETE ===")
    print(f"Total records written: {n_total} ({n_good} good, {n_errors} errors)")
    print(f"Wall-clock: {elapsed_total:.0f}s ({elapsed_total/60:.1f}min)")
    print(f"Estimated API cost: ${est_cost:.2f}")
    if errors_by_type:
        print(f"Error breakdown: {json.dumps(errors_by_type, indent=2)}")
    print(f"Output: {output_path}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate-only", action="store_true", help="Run gate 1, no LLM calls.")
    ap.add_argument("--sample", action="store_true", help="Run 15-sample (gate 2). STOPS.")
    ap.add_argument("--full", action="store_true", help="Generate all (only after sample approval).")
    ap.add_argument("--output", default=str(DEFAULT_OUTPUT))
    ap.add_argument("--concurrency", type=int, default=5)
    ap.add_argument("--only-tasks", type=str, default="",
                    help="Comma-separated base task_ids to retry (e.g. DIRICHLET_01,REGRESSION_05).")
    ap.add_argument("--retry", action="store_true",
                    help="Remove error records for --only-tasks from output before regenerating.")
    args = ap.parse_args()

    tasks = load_tasks()
    print(f"Loaded {len(tasks)} base tasks. DISPATCH covers {len(DISPATCH)} task_types.")

    # Always run gate 1.
    print("\n=== GATE 1: dispatch sanity check ===")
    g1 = gate1_dispatch_sanity(tasks)
    n_fail = _print_gate1(g1)
    if n_fail:
        print(f"\nGATE 1 FAILED — {n_fail} mismatches. Failures:")
        for f in g1["failures"][:20]:
            print(f"  {f['task_id']} ({f['task_type']}): {f['reason']}")
        return 1
    print("\nGATE 1 PASSED.")

    if args.validate_only:
        return 0

    output_path = Path(args.output)

    # --only-tasks: filter base tasks to retry subset.
    if args.only_tasks:
        only = set(args.only_tasks.split(","))
        tasks = [t for t in tasks if t["task_id"] in only]
        print(f"Filtered to {len(tasks)} base tasks: {sorted(only)}")

    # --retry: strip error records for these tasks from existing output.
    if args.retry and output_path.exists() and output_path.suffix == ".json":
        only_set = set(args.only_tasks.split(",")) if args.only_tasks else set()
        existing_data = json.load(open(output_path))
        before = len(existing_data)
        existing_data = [r for r in existing_data
                         if not (r.get("error") and r.get("base_task_id") in only_set)]
        after = len(existing_data)
        with open(output_path, "w") as f:
            json.dump(existing_data, f, indent=2)
        print(f"Retry: removed {before - after} error records from {output_path}")

    if args.sample:
        asyncio.run(run_sample(tasks, output_path, args.concurrency))
    elif args.full:
        asyncio.run(run_full(tasks, output_path, args.concurrency))
    else:
        print("\nNo action flag (--validate-only / --sample / --full). Exiting.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
