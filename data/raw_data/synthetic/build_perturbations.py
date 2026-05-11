#!/usr/bin/env python3
"""
Generate data/raw_data/synthetic/perturbations.json — 75 perturbations (25 base tasks × 3 types).

Perturbation types:
  rephrase   — identical inputs/answers, reworded prompt
  numerical  — changed numbers, recomputed ground-truth answers
  semantic   — identical math, new real-world framing

Run from project root:
  python data/raw_data/synthetic/build_perturbations.py
"""
from __future__ import annotations

import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

_FOOTER_SINGLE = (
    "\nShow your step-by-step reasoning before giving the final answer.\n\n"
    "Your final answer must be on the last line in this exact format:\n"
    "ANSWER: <value>\n"
    "Round to 4 decimal places."
)
_FOOTER_MULTI = (
    "\nShow your step-by-step reasoning before giving the final answer.\n\n"
    "Your final answer must be on the last line in this exact format:\n"
    "ANSWER: <v1>, <v2>, ...\n"
    "List values in the order requested. Round each to 4 decimal places."
)

def tgt(key, val, tol=1e-4, scale=0.05):
    return {"key": key, "true_value": val,
            "full_credit_tol": tol, "zero_credit_scale": scale}


# ─────────────────────────────────────────────────────────────────────────────
# Load base tasks metadata
# ─────────────────────────────────────────────────────────────────────────────

_TASKS_PATH = os.path.join(os.path.dirname(__file__), "..", "benchmark_v1", "tasks.json")
_base = {t["task_id"]: t for t in json.load(open(_TASKS_PATH))}


def _base_checks(task_id):
    t = _base[task_id]
    return (
        t.get("required_structure_checks", []),
        t.get("required_assumption_checks", []),
        t["tier"],
        t["difficulty"],
    )


def _task_type(task_id: str) -> str:
    parts = task_id.rsplit("_", 1)
    return parts[0] if len(parts) == 2 and parts[1].isdigit() else task_id


# ─────────────────────────────────────────────────────────────────────────────
# Build perturbation records
# ─────────────────────────────────────────────────────────────────────────────

records = []


def add(base_id, ptype, prompt, targets, note):
    sc, ac, tier, diff = _base_checks(base_id)
    records.append({
        "task_id": f"{base_id}_{ptype}",
        "base_task_id": base_id,
        "perturbation_type": ptype,
        "task_type": _task_type(base_id),
        "tier": tier,
        "difficulty": diff,
        "prompt": prompt,
        "numeric_targets": targets,
        "required_structure_checks": sc,
        "required_assumption_checks": ac,
        "perturbation_note": note,
    })


# ══════════════════════════════════════════════════════════════════════════════
# 1. BINOM_FLAT_01  (x=3, n=10, flat prior → α=4, β=8, mean=1/3)
# ══════════════════════════════════════════════════════════════════════════════
BF01_TARGETS_BASE = [
    tgt("alpha_post", 4.0, 1e-6), tgt("beta_post", 8.0, 1e-6),
    tgt("posterior_mean", 1/3, 1e-4),
]

add("BINOM_FLAT_01", "rephrase",
    "[Task BINOM_FLAT_01_rephrase  |  Tier 1  |  Basic]\n\n"
    "A coin is flipped n = 10 times and heads is observed x = 3 times.\n"
    "Assume no prior knowledge about the bias θ, modelled as a "
    "Uniform(0, 1) = Beta(1, 1) prior.\n\n"
    "(a) Derive the posterior distribution of θ after observing the data.\n"
    "(b) Compute the posterior mean of θ.\n\n"
    "Report: alpha_post, beta_post, posterior_mean" + _FOOTER_MULTI,
    BF01_TARGETS_BASE,
    "Same numbers, coin-flip framing instead of generic Bernoulli trials.")

add("BINOM_FLAT_01", "numerical",
    "[Task BINOM_FLAT_01_numerical  |  Tier 1  |  Basic]\n\n"
    "You observe x = 5 successes in n = 12 Bernoulli trials.\n"
    "The prior on θ is Uniform(0, 1) = Beta(1, 1)  (a flat / diffuse prior).\n\n"
    "(a) State the posterior distribution of θ given the data.\n"
    "(b) Compute the posterior mean.\n\n"
    "Report: alpha_post, beta_post, posterior_mean" + _FOOTER_MULTI,
    [tgt("alpha_post", 6.0, 1e-6), tgt("beta_post", 8.0, 1e-6),
     tgt("posterior_mean", 6/14, 1e-4)],
    "x=5, n=12 instead of x=3, n=10; posterior Beta(6,8), mean=3/7.")

add("BINOM_FLAT_01", "semantic",
    "[Task BINOM_FLAT_01_semantic  |  Tier 1  |  Basic]\n\n"
    "A quality-control engineer tests n = 10 manufactured items and finds "
    "x = 3 defective. Prior belief about the defect rate θ is "
    "Uniform(0, 1) = Beta(1, 1).\n\n"
    "(a) State the posterior distribution of θ given the inspection data.\n"
    "(b) Compute the posterior mean defect rate.\n\n"
    "Report: alpha_post, beta_post, posterior_mean" + _FOOTER_MULTI,
    BF01_TARGETS_BASE,
    "Manufacturing defect-rate framing; identical inputs and answers.")


# ══════════════════════════════════════════════════════════════════════════════
# 2. BINOM_FLAT_02  (x=7, n=10, flat prior → α=8, β=4, mean=2/3)
# ══════════════════════════════════════════════════════════════════════════════
BF02_TARGETS_BASE = [
    tgt("alpha_post", 8.0, 1e-6), tgt("beta_post", 4.0, 1e-6),
    tgt("posterior_mean", 2/3, 1e-4),
]

add("BINOM_FLAT_02", "rephrase",
    "[Task BINOM_FLAT_02_rephrase  |  Tier 1  |  Basic]\n\n"
    "In n = 10 independent Bernoulli trials with unknown success probability θ, "
    "x = 7 successes are recorded.\n"
    "A non-informative flat prior Beta(1, 1) is placed on θ.\n\n"
    "(a) Identify the posterior distribution.\n"
    "(b) Give the posterior mean.\n\n"
    "Report: alpha_post, beta_post, posterior_mean" + _FOOTER_MULTI,
    BF02_TARGETS_BASE,
    "Same numbers, different sentence structure.")

add("BINOM_FLAT_02", "numerical",
    "[Task BINOM_FLAT_02_numerical  |  Tier 1  |  Basic]\n\n"
    "You observe x = 9 successes in n = 15 Bernoulli trials.\n"
    "The prior on θ is Uniform(0, 1) = Beta(1, 1).\n\n"
    "(a) State the posterior distribution of θ.\n"
    "(b) Compute the posterior mean.\n\n"
    "Report: alpha_post, beta_post, posterior_mean" + _FOOTER_MULTI,
    [tgt("alpha_post", 10.0, 1e-6), tgt("beta_post", 7.0, 1e-6),
     tgt("posterior_mean", 10/17, 1e-4)],
    "x=9, n=15; posterior Beta(10,7), mean=10/17≈0.5882.")

add("BINOM_FLAT_02", "semantic",
    "[Task BINOM_FLAT_02_semantic  |  Tier 1  |  Basic]\n\n"
    "A physician observes x = 7 patients out of n = 10 who respond to a new "
    "treatment. Prior belief about the response rate θ is fully diffuse: "
    "Beta(1, 1).\n\n"
    "(a) State the posterior distribution of θ.\n"
    "(b) Compute the posterior mean response rate.\n\n"
    "Report: alpha_post, beta_post, posterior_mean" + _FOOTER_MULTI,
    BF02_TARGETS_BASE,
    "Clinical-trial framing; identical inputs and answers.")


# ══════════════════════════════════════════════════════════════════════════════
# 3. BETA_BINOM_01  (α=2,β=2,x=6,n=10,k=3,m=5)
# ══════════════════════════════════════════════════════════════════════════════
BB01_TARGETS_BASE = [
    tgt("posterior_mean", 0.5714285714285714, 1e-4),
    tgt("ci_lower", 0.31577760291406304, 1e-3),
    tgt("ci_upper", 0.807767558198712, 1e-3),
    tgt("predictive_pmf_k_m", 0.29411764705882354, 1e-4),
]

add("BETA_BINOM_01", "rephrase",
    "[Task BETA_BINOM_01_rephrase  |  Tier 1  |  Basic]\n\n"
    "An experiment has x = 6 successes in n = 10 Bernoulli trials.\n"
    "Prior: θ ~ Beta(α = 2, β = 2).\n\n"
    "(a) Write down the posterior distribution.\n"
    "(b) Find the posterior mean of θ.\n"
    "(c) Compute the 95% equal-tailed credible interval for θ.\n"
    "(d) Find P(X_new = 3 | data) where X_new ~ Binomial(5, θ) "
    "(posterior predictive).\n\n"
    "Report: posterior_mean, ci_lower, ci_upper, predictive_pmf_k_m" + _FOOTER_MULTI,
    BB01_TARGETS_BASE,
    "Same problem, passive-voice / restructured sentences.")

add("BETA_BINOM_01", "numerical",
    "[Task BETA_BINOM_01_numerical  |  Tier 1  |  Basic]\n\n"
    "You observe x = 4 successes in n = 8 Bernoulli trials.\n"
    "The prior on the success probability θ is Beta(α = 3, β = 3).\n\n"
    "(a) State the posterior distribution of θ given the data.\n"
    "(b) Compute the posterior mean of θ.\n"
    "(c) Compute the 95% equal-tailed credible interval for θ.\n"
    "(d) Compute P(X_new = 2 | data) where X_new ~ Binomial(5, θ).\n\n"
    "Report: posterior_mean, ci_lower, ci_upper, predictive_pmf_k_m" + _FOOTER_MULTI,
    [tgt("posterior_mean", 0.5, 1e-4),
     tgt("ci_lower", 0.251345, 1e-3),
     tgt("ci_upper", 0.748655, 1e-3),
     tgt("predictive_pmf_k_m", 0.274510, 1e-4)],
    "α=3,β=3,x=4,n=8,k=2,m=5; symmetric posterior Beta(7,7).")

add("BETA_BINOM_01", "semantic",
    "[Task BETA_BINOM_01_semantic  |  Tier 1  |  Basic]\n\n"
    "A marketing analyst models click-through rates. In n = 10 ad impressions, "
    "x = 6 clicks are recorded. A prior Beta(2, 2) reflects mild belief in a "
    "moderate click rate.\n\n"
    "(a) State the posterior distribution of the click rate θ.\n"
    "(b) Compute the posterior mean.\n"
    "(c) Compute the 95% equal-tailed credible interval.\n"
    "(d) Find P(X_new = 3 clicks in 5 future impressions | data).\n\n"
    "Report: posterior_mean, ci_lower, ci_upper, predictive_pmf_k_m" + _FOOTER_MULTI,
    BB01_TARGETS_BASE,
    "Click-through rate framing; identical inputs and answers.")


# ══════════════════════════════════════════════════════════════════════════════
# 4. DISC_MEDIAN_01  (values=[1..5], probs=[0.1,0.2,0.3,0.25,0.15] → median=3)
# ══════════════════════════════════════════════════════════════════════════════
DM01_TARGETS_BASE = [tgt("posterior_median", 3.0, 1e-6)]

add("DISC_MEDIAN_01", "rephrase",
    "[Task DISC_MEDIAN_01_rephrase  |  Tier 2  |  Intermediate]\n\n"
    "A discrete posterior over θ assigns probabilities:\n"
    "  θ = 1: 0.10,  θ = 2: 0.20,  θ = 3: 0.30,  θ = 4: 0.25,  θ = 5: 0.15\n\n"
    "Determine the posterior median — the smallest value m such that "
    "P(θ ≤ m) ≥ 0.5.\n\n"
    "Report: posterior_median" + _FOOTER_SINGLE,
    DM01_TARGETS_BASE,
    "Same discrete distribution, ask via cumulative definition.")

add("DISC_MEDIAN_01", "numerical",
    "[Task DISC_MEDIAN_01_numerical  |  Tier 2  |  Intermediate]\n\n"
    "A discrete random variable θ takes the following values and probabilities:\n"
    "  Values:        [1, 2, 3, 4, 5]\n"
    "  Probabilities: [0.15, 0.35, 0.20, 0.20, 0.10]\n\n"
    "Find the Bayes estimator under absolute-error loss — i.e. the posterior median.\n\n"
    "Report: posterior_median" + _FOOTER_SINGLE,
    [tgt("posterior_median", 2.0, 1e-6)],
    "Probs [0.15,0.35,0.20,0.20,0.10]; cum=[0.15,0.50,...] → median=2.")

add("DISC_MEDIAN_01", "semantic",
    "[Task DISC_MEDIAN_01_semantic  |  Tier 2  |  Intermediate]\n\n"
    "A Bayesian model assigns posterior probabilities over five possible "
    "temperature anomaly levels (°C):\n"
    "  Level 1 (0.1°C): prob = 0.10\n"
    "  Level 2 (0.5°C): prob = 0.20\n"
    "  Level 3 (1.0°C): prob = 0.30\n"
    "  Level 4 (1.5°C): prob = 0.25\n"
    "  Level 5 (2.0°C): prob = 0.15\n\n"
    "The posterior median minimises posterior expected absolute deviation. "
    "Find it (report the level index 1–5).\n\n"
    "Report: posterior_median" + _FOOTER_SINGLE,
    DM01_TARGETS_BASE,
    "Climate anomaly levels framing; same probabilities, median=3.")


# ══════════════════════════════════════════════════════════════════════════════
# 5. UNIFORM_MLE_01  (data=[1.2,3.4,2.1,4.7,0.9] → mle=4.7)
# ══════════════════════════════════════════════════════════════════════════════
UM01_TARGETS_BASE = [tgt("mle_theta", 4.7, 1e-4)]

add("UNIFORM_MLE_01", "rephrase",
    "[Task UNIFORM_MLE_01_rephrase  |  Tier 2  |  Basic]\n\n"
    "Five i.i.d. observations are drawn from Uniform(0, θ):\n"
    "  data = [1.2, 3.4, 2.1, 4.7, 0.9]\n\n"
    "Explain why the MLE of θ equals the sample maximum, and compute it.\n\n"
    "Report: mle_theta" + _FOOTER_SINGLE,
    UM01_TARGETS_BASE,
    "Ask for justification explicitly; same data.")

add("UNIFORM_MLE_01", "numerical",
    "[Task UNIFORM_MLE_01_numerical  |  Tier 2  |  Basic]\n\n"
    "You observe n = 5 i.i.d. draws from Uniform(0, θ):\n"
    "  data = [2.3, 5.1, 1.8, 6.2, 3.4]\n\n"
    "Derive the Maximum Likelihood Estimator (MLE) for θ.\n"
    "State why the MLE is the sample maximum.\n\n"
    "Report: mle_theta" + _FOOTER_SINGLE,
    [tgt("mle_theta", 6.2, 1e-4)],
    "New data; max=6.2.")

add("UNIFORM_MLE_01", "semantic",
    "[Task UNIFORM_MLE_01_semantic  |  Tier 2  |  Basic]\n\n"
    "A geologist records n = 5 sediment layer thicknesses (mm), each assumed "
    "i.i.d. from Uniform(0, θ) where θ is the maximum possible thickness:\n"
    "  measurements = [1.2, 3.4, 2.1, 4.7, 0.9]\n\n"
    "Find the MLE of the maximum thickness θ.\n\n"
    "Report: mle_theta" + _FOOTER_SINGLE,
    UM01_TARGETS_BASE,
    "Geological measurement framing; identical data and answer.")


# ══════════════════════════════════════════════════════════════════════════════
# 6. BOX_MULLER_01  (U=0.531,V=0.253,μ=50,σ=5)
# ══════════════════════════════════════════════════════════════════════════════
BM01_TARGETS_BASE = [
    tgt("z1", -0.021207522909263758, 1e-4),
    tgt("z2", 1.1249607799618835, 1e-4),
    tgt("x1", 49.89396238545368, 1e-3),
    tgt("x2", 55.624803899809415, 1e-3),
]

add("BOX_MULLER_01", "rephrase",
    "[Task BOX_MULLER_01_rephrase  |  Tier 2  |  Basic]\n\n"
    "Apply the Box-Muller transform to U = 0.531 and V = 0.253 to produce "
    "two independent standard normal variates z₁, z₂, then scale to "
    "Normal(μ = 50, σ = 5).\n\n"
    "Formulas:\n"
    "  z₁ = √(−2 ln U) · cos(2πV)\n"
    "  z₂ = √(−2 ln U) · sin(2πV)\n"
    "  xᵢ = μ + σ · zᵢ\n\n"
    "Report: z1, z2, x1, x2" + _FOOTER_MULTI,
    BM01_TARGETS_BASE,
    "Formula given explicitly; same inputs.")

add("BOX_MULLER_01", "numerical",
    "[Task BOX_MULLER_01_numerical  |  Tier 2  |  Basic]\n\n"
    "Using the Box-Muller transform, generate two independent standard normal "
    "values from U = 0.2 and V = 0.4  (both drawn from Uniform(0, 1)).\n\n"
    "Formulas:\n"
    "  z₁ = √(−2 ln U) · cos(2πV)\n"
    "  z₂ = √(−2 ln U) · sin(2πV)\n\n"
    "Then scale to Normal(μ = 100, σ = 10):\n"
    "  x₁ = μ + σ z₁,  x₂ = μ + σ z₂\n\n"
    "Report: z1, z2, x1, x2" + _FOOTER_MULTI,
    [tgt("z1", -1.451476, 1e-4), tgt("z2", 1.054559, 1e-4),
     tgt("x1", 85.485243, 1e-3), tgt("x2", 110.545588, 1e-3)],
    "U=0.2,V=0.4,μ=100,σ=10; z1≈-1.4515, z2≈1.0546.")

add("BOX_MULLER_01", "semantic",
    "[Task BOX_MULLER_01_semantic  |  Tier 2  |  Basic]\n\n"
    "A Monte Carlo simulation requires Normal(μ = 50, σ = 5) samples. "
    "Using pseudo-random uniforms U = 0.531 and V = 0.253, apply the "
    "Box-Muller transform to generate two Normal(50, 25) realisations.\n\n"
    "Formulas:\n"
    "  z₁ = √(−2 ln U) · cos(2πV),  z₂ = √(−2 ln U) · sin(2πV)\n"
    "  x₁ = 50 + 5 z₁,  x₂ = 50 + 5 z₂\n\n"
    "Report: z1, z2, x1, x2" + _FOOTER_MULTI,
    BM01_TARGETS_BASE,
    "Monte-Carlo simulation framing; same numbers.")


# ══════════════════════════════════════════════════════════════════════════════
# 7. HPD_01  (Beta(5,5) → 95% HPD: 0.2176, 0.7929)
# ══════════════════════════════════════════════════════════════════════════════
HPD01_TARGETS_BASE = [
    tgt("hpd_lower", 0.21757733531973342, 1e-3),
    tgt("hpd_upper", 0.7929603178709547, 1e-3),
]

add("HPD_01", "rephrase",
    "[Task HPD_01_rephrase  |  Tier 2  |  Intermediate]\n\n"
    "The posterior is Beta(α = 5, β = 5), which is symmetric about 0.5.\n\n"
    "Compute the 95% Highest Posterior Density (HPD) interval. "
    "For a symmetric unimodal distribution the HPD equals the equal-tailed "
    "credible interval.\n\n"
    "Report: hpd_lower, hpd_upper" + _FOOTER_MULTI,
    HPD01_TARGETS_BASE,
    "Hint about symmetry given; same posterior.")

add("HPD_01", "numerical",
    "[Task HPD_01_numerical  |  Tier 2  |  Intermediate]\n\n"
    "The posterior distribution is Beta(α = 4, β = 8).\n\n"
    "Find the 95% Highest Posterior Density (HPD) credible interval.\n\n"
    "Note: for skewed distributions the HPD is not equal-tailed — find the "
    "shortest interval [l, u] such that the density is equal at both endpoints "
    "and P(l ≤ θ ≤ u) = 0.95.\n\n"
    "Report: hpd_lower, hpd_upper" + _FOOTER_MULTI,
    [tgt("hpd_lower", 0.093372, 1e-3), tgt("hpd_upper", 0.587952, 1e-3)],
    "Beta(4,8) skewed left; HPD ≈ (0.0934, 0.5880).")

add("HPD_01", "semantic",
    "[Task HPD_01_semantic  |  Tier 2  |  Intermediate]\n\n"
    "After combining prior and likelihood a researcher obtains a Beta(5, 5) "
    "posterior for the proportion of voters supporting a policy.\n\n"
    "Report the 95% HPD credible interval for the support proportion.\n\n"
    "Report: hpd_lower, hpd_upper" + _FOOTER_MULTI,
    HPD01_TARGETS_BASE,
    "Voter-support proportion framing; identical posterior and answers.")


# ══════════════════════════════════════════════════════════════════════════════
# 8. MLE_MAP_01  (x=6,n=10,Beta(2,2))
# ══════════════════════════════════════════════════════════════════════════════
MM01_TARGETS_BASE = [
    tgt("mle", 0.6, 1e-4), tgt("map", 0.5833333333333334, 1e-4),
    tgt("posterior_mean", 0.5714285714285714, 1e-4),
    tgt("shrinkage", 0.1666666666666661, 1e-4),
]

add("MLE_MAP_01", "rephrase",
    "[Task MLE_MAP_01_rephrase  |  Tier 2  |  Intermediate]\n\n"
    "For x = 6 successes in n = 10 Binomial trials with prior Beta(2, 2):\n\n"
    "(1) MLE = x / n\n"
    "(2) MAP = (x + α − 1) / (n + α + β − 2)\n"
    "(3) Posterior mean = (x + α) / (n + α + β)\n"
    "(4) Shrinkage = |MLE − posterior mean|\n\n"
    "Compute all four quantities.\n\n"
    "Report: mle, map, posterior_mean, shrinkage" + _FOOTER_MULTI,
    MM01_TARGETS_BASE,
    "Formulas given explicitly; same inputs.")

add("MLE_MAP_01", "numerical",
    "[Task MLE_MAP_01_numerical  |  Tier 2  |  Intermediate]\n\n"
    "Binomial model: x = 8 successes in n = 12 trials.\n"
    "Prior: Beta(α = 2, β = 2)  (prior mean = 0.5).\n\n"
    "Compute:\n"
    "  (1) MLE = x / n\n"
    "  (2) MAP = (x + α − 1) / (n + α + β − 2)\n"
    "  (3) Posterior mean = (x + α) / (n + α + β)\n"
    "  (4) Shrinkage = |MLE − posterior mean|\n\n"
    "Report: mle, map, posterior_mean, shrinkage" + _FOOTER_MULTI,
    [tgt("mle", 8/12, 1e-4), tgt("map", 9/14, 1e-4),
     tgt("posterior_mean", 10/16, 1e-4), tgt("shrinkage", abs(8/12-10/16), 1e-4)],
    "x=8,n=12; mle=0.6667,map=0.6429,pm=0.625,shrink=0.0417.")

add("MLE_MAP_01", "semantic",
    "[Task MLE_MAP_01_semantic  |  Tier 2  |  Intermediate]\n\n"
    "An A/B test shows x = 6 conversions in n = 10 sessions. "
    "Prior belief about conversion rate θ is Beta(2, 2) (symmetrically centred).\n\n"
    "Compare MLE (pure data), MAP (penalised likelihood), and posterior mean "
    "(full Bayes). Quantify shrinkage toward the prior.\n\n"
    "  MLE = x/n,  MAP = (x+α−1)/(n+α+β−2),  PM = (x+α)/(n+α+β)\n"
    "  Shrinkage = |MLE − PM|\n\n"
    "Report: mle, map, posterior_mean, shrinkage" + _FOOTER_MULTI,
    MM01_TARGETS_BASE,
    "A/B conversion-rate framing; identical numbers.")


# ══════════════════════════════════════════════════════════════════════════════
# 9. CI_CREDIBLE_01
# ══════════════════════════════════════════════════════════════════════════════
CI01_TARGETS_BASE = [
    tgt("freq_lower", 4.599225986076149, 1e-3),
    tgt("freq_upper", 5.4757485266527315, 1e-3),
    tgt("bayes_lower", 4.5968180254381, 1e-3),
    tgt("bayes_upper", 5.473121517519301, 1e-3),
]

add("CI_CREDIBLE_01", "rephrase",
    "[Task CI_CREDIBLE_01_rephrase  |  Tier 2  |  Intermediate]\n\n"
    "You have n = 20 observations from Normal(μ, σ² = 1.0) with sample mean "
    "x̄ = 5.0375.\n"
    "Prior: μ ~ Normal(μ₀ = 0.0, τ₀² = 100.0).\n\n"
    "(1) Compute the 95% frequentist confidence interval for μ "
    "(use z = 1.96).\n"
    "(2) Compute the 95% Bayesian credible interval using the posterior "
    "Normal(μₙ, τₙ²) where\n"
    "    τₙ² = 1 / (1/τ₀² + n/σ²),  μₙ = τₙ²(μ₀/τ₀² + n·x̄/σ²).\n\n"
    "Report: freq_lower, freq_upper, bayes_lower, bayes_upper" + _FOOTER_MULTI,
    CI01_TARGETS_BASE,
    "Posterior formulas given explicitly; same data.")

add("CI_CREDIBLE_01", "numerical",
    "[Task CI_CREDIBLE_01_numerical  |  Tier 2  |  Intermediate]\n\n"
    "You have n = 30 observations from Normal(μ, σ² = 1.0) with sample mean "
    "x̄ = 3.5.\n"
    "Prior on μ: Normal(μ₀ = 0.0, τ₀² = 100.0).\n\n"
    "(1) Compute the 95% frequentist confidence interval for μ.\n"
    "(2) Compute the 95% Bayesian credible interval.\n\n"
    "Report: freq_lower, freq_upper, bayes_lower, bayes_upper" + _FOOTER_MULTI,
    [tgt("freq_lower", 3.142155, 1e-3), tgt("freq_upper", 3.857845, 1e-3),
     tgt("bayes_lower", 3.141055, 1e-3), tgt("bayes_upper", 3.856613, 1e-3)],
    "n=30, x̄=3.5; both intervals tighter due to larger n.")

add("CI_CREDIBLE_01", "semantic",
    "[Task CI_CREDIBLE_01_semantic  |  Tier 2  |  Intermediate]\n\n"
    "A lab measures reaction times (seconds) for n = 20 subjects. "
    "Assume Normal(μ, σ² = 1.0). The sample mean is x̄ = 5.0375 seconds.\n"
    "Prior: Normal(0, 100) (diffuse).\n\n"
    "Compare the classical 95% confidence interval for μ with the Bayesian "
    "95% credible interval.\n\n"
    "Report: freq_lower, freq_upper, bayes_lower, bayes_upper" + _FOOTER_MULTI,
    CI01_TARGETS_BASE,
    "Reaction-time experiment framing; same numbers.")


# ══════════════════════════════════════════════════════════════════════════════
# 10. JEFFREYS_01  (x=3,n=10,Jeffreys → α=3.5,β=7.5,mean≈0.3182)
# ══════════════════════════════════════════════════════════════════════════════
J01_TARGETS_BASE = [
    tgt("alpha_post", 3.5, 1e-6), tgt("beta_post", 7.5, 1e-6),
    tgt("posterior_mean", 0.3181818181818182, 1e-4),
]

add("JEFFREYS_01", "rephrase",
    "[Task JEFFREYS_01_rephrase  |  Tier 2  |  Intermediate]\n\n"
    "The Jeffreys prior for the Binomial model is Beta(0.5, 0.5). "
    "With x = 3 successes in n = 10 trials, the posterior is "
    "Beta(0.5 + x, 0.5 + n − x).\n\n"
    "(a) Compute α_post and β_post.\n"
    "(b) Compute the posterior mean.\n\n"
    "Report: alpha_post, beta_post, posterior_mean" + _FOOTER_MULTI,
    J01_TARGETS_BASE,
    "Formula spelled out; same inputs.")

add("JEFFREYS_01", "numerical",
    "[Task JEFFREYS_01_numerical  |  Tier 2  |  Intermediate]\n\n"
    "Using the Jeffreys prior for the Binomial model — Beta(0.5, 0.5) —\n"
    "with x = 5 successes in n = 12 trials:\n\n"
    "(a) State the posterior distribution Beta(α_post, β_post).\n"
    "(b) Compute the posterior mean.\n\n"
    "Report: alpha_post, beta_post, posterior_mean" + _FOOTER_MULTI,
    [tgt("alpha_post", 5.5, 1e-6), tgt("beta_post", 7.5, 1e-6),
     tgt("posterior_mean", 5.5/13, 1e-4)],
    "x=5,n=12; Beta(5.5,7.5), mean=5.5/13≈0.4231.")

add("JEFFREYS_01", "semantic",
    "[Task JEFFREYS_01_semantic  |  Tier 2  |  Intermediate]\n\n"
    "A forensic analyst uses the Jeffreys prior Beta(0.5, 0.5) as an "
    "objective, invariant prior for the probability θ that a DNA sample "
    "matches a reference. After x = 3 matches in n = 10 comparisons:\n\n"
    "(a) State the posterior distribution.\n"
    "(b) Compute the posterior mean.\n\n"
    "Report: alpha_post, beta_post, posterior_mean" + _FOOTER_MULTI,
    J01_TARGETS_BASE,
    "DNA forensics framing; identical numbers.")


# ══════════════════════════════════════════════════════════════════════════════
# 11. BAYES_RISK_01  (risks=[0.5,0.3],priors=[0.4,0.6] → 0.38)
# ══════════════════════════════════════════════════════════════════════════════
BR01_TARGETS_BASE = [tgt("bayes_risk", 0.38, 1e-4)]

add("BAYES_RISK_01", "rephrase",
    "[Task BAYES_RISK_01_rephrase  |  Tier 2  |  Basic]\n\n"
    "An estimator δ incurs frequentist risks R(δ, θ₁) = 0.5 and "
    "R(δ, θ₂) = 0.3. A prior assigns P(θ₁) = 0.4 and P(θ₂) = 0.6.\n\n"
    "The Bayes risk is r(π, δ) = Σᵢ π(θᵢ) R(δ, θᵢ).\n\n"
    "Compute the Bayes risk.\n\n"
    "Report: bayes_risk" + _FOOTER_SINGLE,
    BR01_TARGETS_BASE,
    "Formula given explicitly; same inputs.")

add("BAYES_RISK_01", "numerical",
    "[Task BAYES_RISK_01_numerical  |  Tier 2  |  Basic]\n\n"
    "An estimator δ has risk values R(δ, θᵢ) at 2 parameter values, "
    "with a discrete prior π(θᵢ):\n\n"
    "  Risk values R(δ, θᵢ): [0.6, 0.2]\n"
    "  Prior probabilities π(θᵢ): [0.3, 0.7]\n\n"
    "Compute the Bayes risk r(π, δ) = Σᵢ π(θᵢ) R(δ, θᵢ).\n\n"
    "Report: bayes_risk" + _FOOTER_SINGLE,
    [tgt("bayes_risk", 0.32, 1e-4)],
    "Risks [0.6,0.2], priors [0.3,0.7]; 0.6×0.3+0.2×0.7=0.32.")

add("BAYES_RISK_01", "semantic",
    "[Task BAYES_RISK_01_semantic  |  Tier 2  |  Basic]\n\n"
    "A weather forecaster uses estimator δ. When it rains (θ₁, prior prob 0.4) "
    "the forecast error risk is 0.5; when dry (θ₂, prior prob 0.6) "
    "the risk is 0.3.\n\n"
    "Compute the average (Bayes) risk under this prior.\n\n"
    "Report: bayes_risk" + _FOOTER_SINGLE,
    BR01_TARGETS_BASE,
    "Weather-forecast risk framing; identical numbers.")


# ══════════════════════════════════════════════════════════════════════════════
# 12. FISHER_INFO_01  (θ=0.3,n=10 → I_n=47.619)
# ══════════════════════════════════════════════════════════════════════════════
FI01_TARGETS_BASE = [tgt("fisher_info", 47.61904761904762, 1e-3)]

add("FISHER_INFO_01", "rephrase",
    "[Task FISHER_INFO_01_rephrase  |  Tier 3  |  Intermediate]\n\n"
    "For a Binomial(θ) model, Fisher information for a single observation is "
    "I₁(θ) = 1 / [θ(1−θ)]. With n = 10 i.i.d. observations:\n"
    "  I_n(θ) = n · I₁(θ)\n\n"
    "Evaluate I_n(0.3).\n\n"
    "Report: fisher_info" + _FOOTER_SINGLE,
    FI01_TARGETS_BASE,
    "Formula expanded; same θ and n.")

add("FISHER_INFO_01", "numerical",
    "[Task FISHER_INFO_01_numerical  |  Tier 3  |  Intermediate]\n\n"
    "Compute the Fisher information I_n(θ) for n = 15 i.i.d. observations\n"
    "from a Binomial distribution with parameter θ = 0.4.\n\n"
    "Recall: I_n(θ) = n / [θ(1 − θ)]\n\n"
    "Report: fisher_info" + _FOOTER_SINGLE,
    [tgt("fisher_info", 62.5, 1e-3)],
    "θ=0.4, n=15; I_n=15/0.24=62.5.")

add("FISHER_INFO_01", "semantic",
    "[Task FISHER_INFO_01_semantic  |  Tier 3  |  Intermediate]\n\n"
    "In a clinical trial with n = 10 patients, the outcome follows Binomial(θ) "
    "where θ = 0.3 is the true response rate.\n\n"
    "Compute the Fisher information in the full sample — the total information "
    "available about θ.\n\n"
    "Recall: I_n(θ) = n / [θ(1−θ)]\n\n"
    "Report: fisher_info" + _FOOTER_SINGLE,
    FI01_TARGETS_BASE,
    "Clinical-trial information framing; identical numbers.")


# ══════════════════════════════════════════════════════════════════════════════
# 13. RC_BOUND_01  (θ=0.3,n=10 → fi=47.619, rc=0.021)
# ══════════════════════════════════════════════════════════════════════════════
RC01_TARGETS_BASE = [
    tgt("fisher_info", 47.61904761904762, 1e-3),
    tgt("rc_bound", 0.020999999999999998, 1e-4),
]

add("RC_BOUND_01", "rephrase",
    "[Task RC_BOUND_01_rephrase  |  Tier 3  |  Basic]\n\n"
    "For n = 10 i.i.d. Binomial(θ = 0.3) observations:\n\n"
    "(a) Compute I_n(θ) = n / [θ(1−θ)].\n"
    "(b) The Rao-Cramér lower bound for an unbiased estimator is "
    "    RC = 1 / I_n(θ). Compute it.\n\n"
    "Report: fisher_info, rc_bound" + _FOOTER_MULTI,
    RC01_TARGETS_BASE,
    "Rao-Cramér formula stated explicitly; same inputs.")

add("RC_BOUND_01", "numerical",
    "[Task RC_BOUND_01_numerical  |  Tier 3  |  Basic]\n\n"
    "For n = 8 i.i.d. observations from a Binomial distribution\n"
    "with parameter θ = 0.5:\n\n"
    "(a) Compute the Fisher information I_n(θ).\n"
    "(b) Compute the Rao-Cramér lower bound RC = 1 / I_n(θ).\n\n"
    "Report: fisher_info, rc_bound" + _FOOTER_MULTI,
    [tgt("fisher_info", 32.0, 1e-3), tgt("rc_bound", 0.03125, 1e-4)],
    "θ=0.5, n=8; I_n=32, RC=0.03125.")

add("RC_BOUND_01", "semantic",
    "[Task RC_BOUND_01_semantic  |  Tier 3  |  Basic]\n\n"
    "A statistician designs an experiment with n = 10 Binomial trials at "
    "θ = 0.3 to estimate the success rate.\n\n"
    "(a) What is the Fisher information available in the sample?\n"
    "(b) What is the minimum variance any unbiased estimator can achieve "
    "    (Rao-Cramér bound)?\n\n"
    "Report: fisher_info, rc_bound" + _FOOTER_MULTI,
    RC01_TARGETS_BASE,
    "Experimental-design framing; identical inputs.")


# ══════════════════════════════════════════════════════════════════════════════
# 14. MARKOV_01
# ══════════════════════════════════════════════════════════════════════════════
MK01_TARGETS_BASE = [
    tgt("pi_0", 0.5591397849462366, 1e-4),
    tgt("pi_1", 0.22580645161290316, 1e-4),
    tgt("pi_2", 0.2150537634408602, 1e-4),
]

add("MARKOV_01", "rephrase",
    "[Task MARKOV_01_rephrase  |  Tier 3  |  Intermediate]\n\n"
    "A 3-state Markov chain has transition matrix:\n"
    "P = [\n"
    "  [0.5000, 0.2500, 0.2500]\n"
    "  [0.6667, 0.0000, 0.3333]\n"
    "  [0.6000, 0.4000, 0.0000]\n"
    "]\n\n"
    "Solve πᵀ = πᵀ P, Σ πᵢ = 1 for the stationary distribution.\n\n"
    "Report: pi_0, pi_1, pi_2" + _FOOTER_MULTI,
    MK01_TARGETS_BASE,
    "System of equations framing; same matrix.")

add("MARKOV_01", "numerical",
    "[Task MARKOV_01_numerical  |  Tier 3  |  Intermediate]\n\n"
    "A Markov chain on 3 states has transition matrix:\n"
    "P = [\n"
    "  [0.4000, 0.3000, 0.3000]\n"
    "  [0.6000, 0.1000, 0.3000]\n"
    "  [0.5000, 0.3000, 0.2000]\n"
    "]\n\n"
    "Find the stationary distribution π = (π₀, π₁, π₂).\n\n"
    "Report: pi_0, pi_1, pi_2" + _FOOTER_MULTI,
    [tgt("pi_0", 0.47727273, 1e-4), tgt("pi_1", 0.25, 1e-4),
     tgt("pi_2", 0.27272727, 1e-4)],
    "New matrix; π≈(0.4773,0.25,0.2727).")

add("MARKOV_01", "semantic",
    "[Task MARKOV_01_semantic  |  Tier 3  |  Intermediate]\n\n"
    "A consumer moves between three brands (0, 1, 2) each month according to "
    "the transition matrix:\n"
    "P = [\n"
    "  [0.5000, 0.2500, 0.2500]\n"
    "  [0.6667, 0.0000, 0.3333]\n"
    "  [0.6000, 0.4000, 0.0000]\n"
    "]\n\n"
    "Find the long-run market shares (stationary distribution).\n\n"
    "Report: pi_0, pi_1, pi_2" + _FOOTER_MULTI,
    MK01_TARGETS_BASE,
    "Brand-switching framing; same transition matrix.")


# ══════════════════════════════════════════════════════════════════════════════
# 15. ORDER_STAT_01  (k=3,n=5,y=0.4 → pdf=1.728)
# ══════════════════════════════════════════════════════════════════════════════
OS01_TARGETS_BASE = [tgt("order_stat_pdf", 1.728000000000001, 1e-4)]

add("ORDER_STAT_01", "rephrase",
    "[Task ORDER_STAT_01_rephrase  |  Tier 3  |  Intermediate]\n\n"
    "Let X₁, …, X₅ be i.i.d. Uniform[0, 1]. The PDF of the k-th order "
    "statistic X_(k) is Beta(k, n−k+1).\n\n"
    "Evaluate the PDF of X_(3) at y = 0.4.\n\n"
    "Report: order_stat_pdf" + _FOOTER_SINGLE,
    OS01_TARGETS_BASE,
    "Beta distribution connection made explicit; same values.")

add("ORDER_STAT_01", "numerical",
    "[Task ORDER_STAT_01_numerical  |  Tier 3  |  Intermediate]\n\n"
    "Let X₁, …, X_5 be i.i.d. Uniform[0, 1] random variables.\n"
    "Let X_(2) denote the 2nd order statistic (the 2nd smallest value).\n\n"
    "The PDF of X_(k) is:\n"
    "  g_(k)(y) = n! / [(k−1)! (n−k)!] · y^(k−1) · (1−y)^(n−k)  for y ∈ [0,1]\n\n"
    "Evaluate the PDF of X_(2) at y = 0.3.\n\n"
    "Report: order_stat_pdf" + _FOOTER_SINGLE,
    [tgt("order_stat_pdf", 2.058, 1e-4)],
    "k=2,n=5,y=0.3; g=20×0.3×0.343=2.058.")

add("ORDER_STAT_01", "semantic",
    "[Task ORDER_STAT_01_semantic  |  Tier 3  |  Intermediate]\n\n"
    "Five random exam scores are each uniformly distributed on [0, 1]. "
    "The median score is the 3rd order statistic X_(3).\n\n"
    "The PDF of X_(3) is Beta(3, 3). Evaluate this at y = 0.4.\n\n"
    "Report: order_stat_pdf" + _FOOTER_SINGLE,
    OS01_TARGETS_BASE,
    "Exam score framing; k=3 is median of 5 scores.")


# ══════════════════════════════════════════════════════════════════════════════
# 16. REGRESSION_01
# ══════════════════════════════════════════════════════════════════════════════
RG01_TARGETS_BASE = [
    tgt("A_hat", 0.0500000000000016, 1e-3),
    tgt("B_hat", 1.9899999999999998, 1e-3),
    tgt("s2", 0.03566666666666691, 1e-4),
    tgt("B_lower", 1.7999392904005407, 1e-3),
    tgt("B_upper", 2.180060709599459, 1e-3),
]

add("REGRESSION_01", "rephrase",
    "[Task REGRESSION_01_rephrase  |  Tier 3  |  Intermediate]\n\n"
    "Fit Y = A + B·x via OLS to the 5 data points:\n"
    "  x = [1, 2, 3, 4, 5],  y = [2.1, 3.9, 6.2, 7.8, 10.1]\n\n"
    "Formulas:\n"
    "  B̂ = Σ(xᵢ−x̄)(yᵢ−ȳ) / Σ(xᵢ−x̄)²\n"
    "  Â = ȳ − B̂·x̄\n"
    "  s² = Σ(yᵢ − Â − B̂xᵢ)² / (n−2)\n"
    "  95% CI for B: B̂ ± t_{n−2, 0.975} · s / √Sₓₓ\n\n"
    "Report: A_hat, B_hat, s2, B_lower, B_upper" + _FOOTER_MULTI,
    RG01_TARGETS_BASE,
    "Formulas written out; same data.")

add("REGRESSION_01", "numerical",
    "[Task REGRESSION_01_numerical  |  Tier 3  |  Intermediate]\n\n"
    "You have n = 5 data points for a simple linear regression Y = A + B·x + ε:\n"
    "  x = [2, 4, 6, 8, 10]\n"
    "  y = [5.1, 8.9, 13.0, 17.2, 21.0]\n\n"
    "Compute:\n"
    "  (1) OLS estimates Â and B̂\n"
    "  (2) Residual variance s²\n"
    "  (3) 95% confidence interval for B (use t_{3, 0.975})\n\n"
    "Report: A_hat, B_hat, s2, B_lower, B_upper" + _FOOTER_MULTI,
    [tgt("A_hat", 1.01, 1e-3), tgt("B_hat", 2.005, 1e-3),
     tgt("s2", 0.017, 1e-4),
     tgt("B_lower", 1.939392, 1e-3), tgt("B_upper", 2.070608, 1e-3)],
    "x=[2,4,6,8,10], y=[5.1,8.9,13,17.2,21]; Â=1.01, B̂=2.005.")

add("REGRESSION_01", "semantic",
    "[Task REGRESSION_01_semantic  |  Tier 3  |  Intermediate]\n\n"
    "A physicist measures spring extension (cm) under various weights (kg):\n"
    "  Weight x: [1, 2, 3, 4, 5]\n"
    "  Extension y: [2.1, 3.9, 6.2, 7.8, 10.1]\n\n"
    "Fit Hooke's Law: y = A + B·x. Estimate intercept Â, slope B̂ (spring "
    "constant), residual variance s², and 95% CI for B̂.\n\n"
    "Report: A_hat, B_hat, s2, B_lower, B_upper" + _FOOTER_MULTI,
    RG01_TARGETS_BASE,
    "Spring extension / Hooke's Law framing; identical data.")


# ══════════════════════════════════════════════════════════════════════════════
# 17. GAMBLER_01  (p=0.6,i=3,M=8)
# ══════════════════════════════════════════════════════════════════════════════
GB01_TARGETS_BASE = [
    tgt("ruin_prob", 0.2677240285487709, 1e-4),
    tgt("win_prob", 0.732275971451229, 1e-4),
]

add("GAMBLER_01", "rephrase",
    "[Task GAMBLER_01_rephrase  |  Tier 3  |  Intermediate]\n\n"
    "Gambler's ruin: fortune i = 3, absorbing barriers at 0 (ruin) and M = 8 "
    "(win), win probability per bet p = 0.6, q = 0.4.\n\n"
    "Using P(ruin | i) = [(q/p)^i − (q/p)^M] / [1 − (q/p)^M], compute "
    "ruin probability and win probability.\n\n"
    "Report: ruin_prob, win_prob" + _FOOTER_MULTI,
    GB01_TARGETS_BASE,
    "Formula given explicitly; same parameters.")

add("GAMBLER_01", "numerical",
    "[Task GAMBLER_01_numerical  |  Tier 3  |  Intermediate]\n\n"
    "A gambler starts with fortune i = 4 and plays until reaching 0 (ruin)\n"
    "or M = 10 (win). Each bet is won with probability p = 0.55 (lost with q = 0.45).\n\n"
    "Using the gambler's ruin formula:\n"
    "  P(ruin | i) = [(q/p)^i − (q/p)^M] / [1 − (q/p)^M]\n\n"
    "Compute the probability of ruin and the probability of winning.\n\n"
    "Report: ruin_prob, win_prob" + _FOOTER_MULTI,
    [tgt("ruin_prob", 0.362414, 1e-4), tgt("win_prob", 0.637586, 1e-4)],
    "i=4, M=10, p=0.55; ruin≈0.3624.")

add("GAMBLER_01", "semantic",
    "[Task GAMBLER_01_semantic  |  Tier 3  |  Intermediate]\n\n"
    "A poker player has i = 3 chips. The game ends when they go broke (0 chips) "
    "or accumulate M = 8 chips. Each hand is won with probability p = 0.6.\n\n"
    "What is the probability of going broke? Of winning?\n\n"
    "  P(ruin | i) = [(q/p)^i − (q/p)^M] / [1 − (q/p)^M]\n\n"
    "Report: ruin_prob, win_prob" + _FOOTER_MULTI,
    GB01_TARGETS_BASE,
    "Poker chip framing; same parameters.")


# ══════════════════════════════════════════════════════════════════════════════
# 18. STATIONARY_01
# ══════════════════════════════════════════════════════════════════════════════
ST01_TARGETS_BASE = [
    tgt("pi_0", 0.30967741935483845, 1e-4),
    tgt("pi_1", 0.406451612903226, 1e-4),
    tgt("pi_2", 0.28387096774193565, 1e-4),
]

add("STATIONARY_01", "rephrase",
    "[Task STATIONARY_01_rephrase  |  Tier 3  |  Intermediate]\n\n"
    "A Markov chain on 3 states has transition matrix:\n"
    "P = [\n"
    "  [0.2000, 0.5000, 0.3000]\n"
    "  [0.4000, 0.2000, 0.4000]\n"
    "  [0.3000, 0.6000, 0.1000]\n"
    "]\n\n"
    "The stationary distribution satisfies π P = π and Σᵢ πᵢ = 1. "
    "Set up the linear system and solve.\n\n"
    "Report: pi_0, pi_1, pi_2" + _FOOTER_MULTI,
    ST01_TARGETS_BASE,
    "Linear-system framing; same matrix.")

add("STATIONARY_01", "numerical",
    "[Task STATIONARY_01_numerical  |  Tier 3  |  Intermediate]\n\n"
    "A Markov chain on 3 states has transition matrix:\n"
    "P = [\n"
    "  [0.2000, 0.5000, 0.3000]\n"
    "  [0.4000, 0.3000, 0.3000]\n"
    "  [0.1000, 0.6000, 0.3000]\n"
    "]\n\n"
    "Find the stationary distribution π = (π₀, π₁, π₂).\n\n"
    "Report: pi_0, pi_1, pi_2" + _FOOTER_MULTI,
    [tgt("pi_0", 0.258333, 1e-4), tgt("pi_1", 0.441667, 1e-4),
     tgt("pi_2", 0.3, 1e-4)],
    "New matrix; π≈(0.2583,0.4417,0.3).")

add("STATIONARY_01", "semantic",
    "[Task STATIONARY_01_semantic  |  Tier 3  |  Intermediate]\n\n"
    "A population moves between three employment states — employed (0), "
    "unemployed (1), out-of-labour-force (2) — each month:\n"
    "P = [\n"
    "  [0.2000, 0.5000, 0.3000]\n"
    "  [0.4000, 0.2000, 0.4000]\n"
    "  [0.3000, 0.6000, 0.1000]\n"
    "]\n\n"
    "Find the long-run proportions in each state.\n\n"
    "Report: pi_0, pi_1, pi_2" + _FOOTER_MULTI,
    ST01_TARGETS_BASE,
    "Labour-market states framing; same transition matrix.")


# ══════════════════════════════════════════════════════════════════════════════
# 19. MINIMAX_01
# ══════════════════════════════════════════════════════════════════════════════
MIN01_TARGETS_BASE = [
    tgt("max_risk_hat1", 0.5, 1e-6),
    tgt("max_risk_hat2", 1.0, 1e-6),
    tgt("minimax_value", 0.5, 1e-6),
]

add("MINIMAX_01", "rephrase",
    "[Task MINIMAX_01_rephrase  |  Tier 3  |  Intermediate]\n\n"
    "Risk table for θ ∈ {0, 1, 2}:\n"
    "  R(δ₁, ·) = [0.0, 0.5, 0.0]\n"
    "  R(δ₂, ·) = [1.0, 0.0, 1.0]\n\n"
    "The minimax rule picks the estimator with the smallest worst-case risk. "
    "Compute max-risk for each, then identify the minimax value.\n\n"
    "Report: max_risk_hat1, max_risk_hat2, minimax_value" + _FOOTER_MULTI,
    MIN01_TARGETS_BASE,
    "Decision procedure stated; same risk table.")

add("MINIMAX_01", "numerical",
    "[Task MINIMAX_01_numerical  |  Tier 3  |  Intermediate]\n\n"
    "Two estimators δ₁ and δ₂ have the following risk values R(δ, θ) at "
    "θ ∈ [0, 1, 2]:\n\n"
    "  R(δ₁, θ): [0.2, 0.8, 0.2]\n"
    "  R(δ₂, θ): [0.9, 0.1, 0.7]\n\n"
    "Identify the minimax estimator and state its minimax value.\n\n"
    "Report: max_risk_hat1, max_risk_hat2, minimax_value" + _FOOTER_MULTI,
    [tgt("max_risk_hat1", 0.8, 1e-6), tgt("max_risk_hat2", 0.9, 1e-6),
     tgt("minimax_value", 0.8, 1e-6)],
    "R1=[0.2,0.8,0.2],R2=[0.9,0.1,0.7]; max_r1=0.8,max_r2=0.9,minimax=0.8.")

add("MINIMAX_01", "semantic",
    "[Task MINIMAX_01_semantic  |  Tier 3  |  Intermediate]\n\n"
    "An engineer chooses between two control policies δ₁ and δ₂. "
    "Under three operating conditions θ ∈ {0, 1, 2}, the risks are:\n"
    "  R(δ₁, ·) = [0.0, 0.5, 0.0]\n"
    "  R(δ₂, ·) = [1.0, 0.0, 1.0]\n\n"
    "A risk-averse engineer uses the minimax criterion. Which policy minimises "
    "worst-case risk?\n\n"
    "Report: max_risk_hat1, max_risk_hat2, minimax_value" + _FOOTER_MULTI,
    MIN01_TARGETS_BASE,
    "Engineering control-policy framing; same risk table.")


# ══════════════════════════════════════════════════════════════════════════════
# 20. BIAS_VAR_01  (n=5,θ=1.0)
# ══════════════════════════════════════════════════════════════════════════════
BV01_TARGETS_BASE = [
    tgt("bias", -0.16666666666666666, 1e-4),
    tgt("var_d2", 0.01984126984126984, 1e-5),
    tgt("mse_d2", 0.047619047619047616, 1e-5),
]

add("BIAS_VAR_01", "rephrase",
    "[Task BIAS_VAR_01_rephrase  |  Tier 3  |  Intermediate]\n\n"
    "For n = 5 i.i.d. draws from Uniform(0, θ = 1.0), let d₂ = max(Xᵢ).\n\n"
    "Using:\n"
    "  E[d₂] = n θ / (n+1),  Var(d₂) = n θ² / [(n+1)²(n+2)]\n"
    "  Bias = E[d₂] − θ,  MSE = Bias² + Var(d₂)\n\n"
    "Compute bias, variance, and MSE of d₂.\n\n"
    "Report: bias, var_d2, mse_d2" + _FOOTER_MULTI,
    BV01_TARGETS_BASE,
    "Formulas given; same n and θ.")

add("BIAS_VAR_01", "numerical",
    "[Task BIAS_VAR_01_numerical  |  Tier 3  |  Intermediate]\n\n"
    "Consider n = 8 i.i.d. draws X₁, …, X_n from Uniform(0, θ = 2.0).\n"
    "Let d₂ = max(X₁, …, X_n) be the MLE estimator for θ.\n\n"
    "Using the analytical formulas:\n"
    "  E[d₂] = n θ / (n+1)\n"
    "  Var(d₂) = n θ² / [(n+1)² (n+2)]\n"
    "  MSE(d₂) = Bias² + Var(d₂)\n\n"
    "Compute: bias, var_d2, mse_d2\n\n"
    "Report: bias, var_d2, mse_d2" + _FOOTER_MULTI,
    [tgt("bias", -2/9, 1e-4), tgt("var_d2", 8*4/(81*10), 1e-5),
     tgt("mse_d2", (2/9)**2 + 8*4/(81*10), 1e-5)],
    "n=8, θ=2; bias=-2/9≈-0.2222, mse≈0.0889.")

add("BIAS_VAR_01", "semantic",
    "[Task BIAS_VAR_01_semantic  |  Tier 3  |  Intermediate]\n\n"
    "A surveyor measures the height of n = 5 trees, each uniformly distributed "
    "on [0, θ] where θ is the tallest possible tree. The MLE is d₂ = max(Xᵢ).\n\n"
    "For true θ = 1.0, compute the bias, variance, and MSE of the MLE.\n\n"
    "Report: bias, var_d2, mse_d2" + _FOOTER_MULTI,
    BV01_TARGETS_BASE,
    "Tree-height framing; same n=5, θ=1.")


# ══════════════════════════════════════════════════════════════════════════════
# 21. LOG_ML_01  (Beta(1,1),x=6,n=10)
# ══════════════════════════════════════════════════════════════════════════════
LM01_TARGETS_BASE = [tgt("log_ml", -7.745002803515839, 1e-4)]

add("LOG_ML_01", "rephrase",
    "[Task LOG_ML_01_rephrase  |  Tier 3  |  Advanced]\n\n"
    "For a Beta(1.0, 1.0) prior with x = 6 successes in n = 10 Binomial trials, "
    "compute the log marginal likelihood:\n\n"
    "  log p(x | α, β) = log B(α+x, β+n−x) − log B(α, β)\n\n"
    "where B(a,b) = Γ(a)Γ(b)/Γ(a+b) is the Beta function.\n\n"
    "Report: log_ml" + _FOOTER_SINGLE,
    LM01_TARGETS_BASE,
    "Beta-function formula provided; same inputs.")

add("LOG_ML_01", "numerical",
    "[Task LOG_ML_01_numerical  |  Tier 3  |  Advanced]\n\n"
    "For a Beta(α = 2.0, β = 2.0) prior with x = 5 successes in n = 8 "
    "Binomial trials, compute the log marginal likelihood:\n\n"
    "  log p(x | α, β) = log B(α+x, β+n−x) − log B(α, β)\n\n"
    "Report: log_ml" + _FOOTER_SINGLE,
    [tgt("log_ml", -5.953243, 1e-4)],
    "Beta(2,2) prior, x=5, n=8; log_ml≈-5.9532.")

add("LOG_ML_01", "semantic",
    "[Task LOG_ML_01_semantic  |  Tier 3  |  Advanced]\n\n"
    "A data scientist computes the evidence (marginal likelihood) for a "
    "Beta-Binomial model. Prior: Beta(1, 1). Data: x = 6 clicks in n = 10 "
    "ad impressions.\n\n"
    "Compute the log evidence:\n"
    "  log p(x) = log B(1+x, 1+n−x) − log B(1, 1)\n\n"
    "Report: log_ml" + _FOOTER_SINGLE,
    LM01_TARGETS_BASE,
    "Evidence / model-comparison framing; identical inputs.")


# ══════════════════════════════════════════════════════════════════════════════
# 22. BAYES_FACTOR_01  (x=3,n=10)
# ══════════════════════════════════════════════════════════════════════════════
BF01B_TARGETS_BASE = [
    tgt("log_BF", 0.32841760423869104, 1e-4),
    tgt("BF", 1.388768806950624, 1e-3),
]

add("BAYES_FACTOR_01", "rephrase",
    "[Task BAYES_FACTOR_01_rephrase  |  Tier 3  |  Intermediate]\n\n"
    "Compare M₁: Beta(1, 1) prior vs M₂: Beta(0.5, 0.5) prior for "
    "Binomial data x = 3, n = 10.\n\n"
    "log BF₁₂ = log p(x | M₁) − log p(x | M₂)\n"
    "where log p(x | M) = log B(α+x, β+n−x) − log B(α, β).\n\n"
    "Report: log_BF, BF" + _FOOTER_MULTI,
    BF01B_TARGETS_BASE,
    "Formula given explicitly; same inputs.")

add("BAYES_FACTOR_01", "numerical",
    "[Task BAYES_FACTOR_01_numerical  |  Tier 3  |  Intermediate]\n\n"
    "Compare two models for Binomial data with x = 5 successes in n = 10 trials:\n\n"
    "  M₁: Beta(1.0, 1.0) prior\n"
    "  M₂: Beta(0.5, 0.5) prior\n\n"
    "Compute the Bayes factor BF₁₂ = p(x | M₁) / p(x | M₂) and its log.\n\n"
    "Report: log_BF, BF" + _FOOTER_MULTI,
    [tgt("log_BF", 0.406190, 1e-4), tgt("BF", 1.501088, 1e-3)],
    "x=5, n=10; log_BF≈0.4062, BF≈1.5011.")

add("BAYES_FACTOR_01", "semantic",
    "[Task BAYES_FACTOR_01_semantic  |  Tier 3  |  Intermediate]\n\n"
    "A meta-analyst compares two elicited priors for a drug response rate θ:\n"
    "  M₁: flat prior Beta(1, 1)\n"
    "  M₂: Jeffreys prior Beta(0.5, 0.5)\n\n"
    "Data: x = 3 responders in n = 10 patients.\n\n"
    "Compute the Bayes factor favouring M₁ and its log.\n\n"
    "Report: log_BF, BF" + _FOOTER_MULTI,
    BF01B_TARGETS_BASE,
    "Drug response / prior comparison framing; same x,n.")


# ══════════════════════════════════════════════════════════════════════════════
# 23. OPT_SCALED_01  (n=5,θ=1.0)
# ══════════════════════════════════════════════════════════════════════════════
OPT01_TARGETS_BASE = [
    tgt("c_opt", 1.1666666666666667, 1e-4),
    tgt("mse_opt", 0.027777777777777776, 1e-5),
]

add("OPT_SCALED_01", "rephrase",
    "[Task OPT_SCALED_01_rephrase  |  Tier 4  |  Advanced]\n\n"
    "For n = 5 i.i.d. draws from Uniform(0, θ = 1.0), "
    "the scaled estimator d_c = c · max(Xᵢ) has MSE:\n"
    "  MSE(d_c) = θ² [n c² / (n+2) − 2nc / (n+1) + 1]\n\n"
    "Minimise over c to find c* = (n+2)/(n+1), then compute MSE(d_c*).\n\n"
    "Report: c_opt, mse_opt" + _FOOTER_MULTI,
    OPT01_TARGETS_BASE,
    "Derivation path given; same n and θ.")

add("OPT_SCALED_01", "numerical",
    "[Task OPT_SCALED_01_numerical  |  Tier 4  |  Advanced]\n\n"
    "For n = 4 i.i.d. draws from Uniform(0, θ = 2.0),\n"
    "consider the scaled estimator d_c = c · max(X₁, …, X_n).\n\n"
    "(a) Find the optimal constant c* that minimises MSE(d_c).\n"
    "    Formula: c* = (n+2)/(n+1)\n"
    "(b) Compute MSE(d_c*) = θ² / (n+1)²\n\n"
    "Report: c_opt, mse_opt" + _FOOTER_MULTI,
    [tgt("c_opt", 1.2, 1e-4), tgt("mse_opt", 0.16, 1e-4)],
    "n=4, θ=2; c*=6/5=1.2, mse*=4/25=0.16.")

add("OPT_SCALED_01", "semantic",
    "[Task OPT_SCALED_01_semantic  |  Tier 4  |  Advanced]\n\n"
    "An engineer estimates the maximum lifetime θ of a component from n = 5 "
    "i.i.d. Uniform(0, θ = 1.0) lifetimes. The estimator is d_c = c · max(Xᵢ).\n\n"
    "Find c* that minimises MSE and compute the resulting MSE.\n\n"
    "Report: c_opt, mse_opt" + _FOOTER_MULTI,
    OPT01_TARGETS_BASE,
    "Component lifetime framing; same n=5, θ=1.")


# ══════════════════════════════════════════════════════════════════════════════
# 24. MSE_COMPARE_01  (n=5,θ=1.0)
# ══════════════════════════════════════════════════════════════════════════════
MC01_TARGETS_BASE = [
    tgt("mse_d1", 0.06666666666666667, 1e-5),
    tgt("mse_d2", 0.047619047619047616, 1e-5),
    tgt("mse_dc", 0.027777777777777776, 1e-5),
]

add("MSE_COMPARE_01", "rephrase",
    "[Task MSE_COMPARE_01_rephrase  |  Tier 4  |  Advanced]\n\n"
    "For n = 5 i.i.d. draws from Uniform(0, θ = 1.0), compare:\n"
    "  d₁ = 2X̄  (unbiased)\n"
    "  d₂ = max(Xᵢ)  (MLE)\n"
    "  d_c* = c* · max(Xᵢ)  (optimal scaled, c* = (n+2)/(n+1))\n\n"
    "MSE formulas:\n"
    "  MSE(d₁) = θ²/(3n)\n"
    "  MSE(d₂) = 2θ²/[(n+1)(n+2)]\n"
    "  MSE(d_c*) = θ²/(n+1)²\n\n"
    "Report: mse_d1, mse_d2, mse_dc" + _FOOTER_MULTI,
    MC01_TARGETS_BASE,
    "MSE formulas given; same n=5, θ=1.")

add("MSE_COMPARE_01", "numerical",
    "[Task MSE_COMPARE_01_numerical  |  Tier 4  |  Advanced]\n\n"
    "For n = 9 i.i.d. draws from Uniform(0, θ = 1.0), compare three estimators:\n\n"
    "  d₁ = 2 · X̄           MSE = θ²/(3n)\n"
    "  d₂ = max(Xᵢ)         MSE = 2θ²/[(n+1)(n+2)]\n"
    "  d_c* = c* · max(Xᵢ)  MSE = θ²/(n+1)²\n\n"
    "Report: mse_d1, mse_d2, mse_dc" + _FOOTER_MULTI,
    [tgt("mse_d1", 1/(3*9), 1e-5), tgt("mse_d2", 2/(10*11), 1e-5),
     tgt("mse_dc", 1/100, 1e-5)],
    "n=9, θ=1; mse_d1≈0.0370, mse_d2≈0.0182, mse_dc=0.01.")

add("MSE_COMPARE_01", "semantic",
    "[Task MSE_COMPARE_01_semantic  |  Tier 4  |  Advanced]\n\n"
    "A data scientist compares three estimators for the upper bound θ of a "
    "Uniform(0, θ) distribution using n = 5 observations (true θ = 1.0):\n\n"
    "  d₁ = 2X̄ (method-of-moments)\n"
    "  d₂ = max(Xᵢ) (MLE)\n"
    "  d_c* (optimal scaled MLE)\n\n"
    "Rank them by MSE and report all three values.\n\n"
    "Report: mse_d1, mse_d2, mse_dc" + _FOOTER_MULTI,
    MC01_TARGETS_BASE,
    "Estimator-comparison / model-selection framing; same n=5, θ=1.")


# ══════════════════════════════════════════════════════════════════════════════
# 25. MLE_EFFICIENCY_01  (θ=0.4,n=30)
# ══════════════════════════════════════════════════════════════════════════════
ME01_TARGETS_BASE = [
    tgt("rc_bound", 0.007999999999999998, 1e-5),
    tgt("efficiency_ratio", 1.0, 1e-6),
    tgt("is_efficient", 1.0, 1e-6),
]

add("MLE_EFFICIENCY_01", "rephrase",
    "[Task MLE_EFFICIENCY_01_rephrase  |  Tier 4  |  Advanced]\n\n"
    "For Binomial(θ = 0.4), the MLE θ̂ = X̄ achieves the Rao-Cramér bound.\n\n"
    "(1) Compute RC = 1 / I_n(θ) = θ(1−θ) / n  for n = 30.\n"
    "(2) Efficiency ratio = RC / Var(MLE) = 1.0 (since MLE is efficient).\n"
    "(3) is_efficient = 1 if efficiency_ratio = 1.0 else 0.\n\n"
    "Report: rc_bound, efficiency_ratio, is_efficient" + _FOOTER_MULTI,
    ME01_TARGETS_BASE,
    "Efficiency argument spelled out; same θ and n.")

add("MLE_EFFICIENCY_01", "numerical",
    "[Task MLE_EFFICIENCY_01_numerical  |  Tier 4  |  Advanced]\n\n"
    "For the Binomial distribution with parameter θ = 0.6\n"
    "and sample size n = 25, the MLE is known to be efficient.\n\n"
    "Compute:\n"
    "  (1) The Fisher information Rao-Cramér bound: RC = θ(1−θ)/n\n"
    "  (2) The efficiency ratio (1.0 for an efficient estimator)\n"
    "  (3) is_efficient (1 if efficient, 0 otherwise)\n\n"
    "Report: rc_bound, efficiency_ratio, is_efficient" + _FOOTER_MULTI,
    [tgt("rc_bound", 0.0096, 1e-5), tgt("efficiency_ratio", 1.0, 1e-6),
     tgt("is_efficient", 1.0, 1e-6)],
    "θ=0.6, n=25; RC=0.24/25=0.0096.")

add("MLE_EFFICIENCY_01", "semantic",
    "[Task MLE_EFFICIENCY_01_semantic  |  Tier 4  |  Advanced]\n\n"
    "A pollster estimates support θ = 0.4 for a candidate from n = 30 "
    "independent yes/no responses. The estimator is the sample proportion.\n\n"
    "Show that the sample proportion is the efficient MLE by computing the "
    "Rao-Cramér bound and confirming that efficiency_ratio = 1.\n\n"
    "Report: rc_bound, efficiency_ratio, is_efficient" + _FOOTER_MULTI,
    ME01_TARGETS_BASE,
    "Opinion-poll framing; same θ=0.4, n=30.")


# ─────────────────────────────────────────────────────────────────────────────
# Validate and write
# ─────────────────────────────────────────────────────────────────────────────

assert len(records) == 75, f"Expected 75 records, got {len(records)}"

# Sanity: 3 per base task
from collections import Counter
by_base = Counter(r["base_task_id"] for r in records)
assert all(v == 3 for v in by_base.values()), f"Not 3 per base: {by_base}"

by_type = Counter(r["perturbation_type"] for r in records)
assert by_type == {"rephrase": 25, "numerical": 25, "semantic": 25}, str(by_type)

out_path = os.path.join(os.path.dirname(__file__), "perturbations.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(records, f, indent=2, ensure_ascii=False)

print(f"Wrote {len(records)} perturbations to {out_path}")
print(f"Types: {dict(by_type)}")
print(f"Base tasks: {len(by_base)} unique")
