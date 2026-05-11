# baseline/build_tasks_bayesian.py
from __future__ import annotations
import json
import os
from typing import Any, Dict, List

import numpy as np

# ── Bayesian baseline functions ───────────────────────────────────────────────
from data_preprocessing.bayesian.ground_truth import (
    gt_beta_binomial,
    gt_gamma_poisson,
    gt_normal_gamma_precision,
    gt_dirichlet_multinomial,
)
from data_preprocessing.bayesian.bayes_estimators import discrete_posterior_median
from data_preprocessing.bayesian.uniform_model import uniform_mle
from data_preprocessing.bayesian.conjugate_models import binomial_uniform_prior_update
from data_preprocessing.bayesian.decision_theory import minimax_risk, discrete_bayes_risk
from data_preprocessing.bayesian.markov_chains import (
    stationary_distribution,
    gambling_ruin_probability,
    n_step_transition,
)

# ── Frequentist baseline functions ───────────────────────────────────────────
from data_preprocessing.frequentist.fisher_information import fisher_information, rao_cramer_bound
from data_preprocessing.frequentist.uniform_estimators import optimal_scaled_estimator_uniform
from data_preprocessing.frequentist.order_statistics import (
    order_statistic_pdf,
    min_order_statistic_cdf,
    uniform_range_distribution,
)
from data_preprocessing.frequentist.sampling import box_muller_standard
from data_preprocessing.frequentist.regression import ols_estimators, residual_variance, credibility_intervals
from data_preprocessing.frequentist.order_statistics import max_order_statistic_cdf, uniform_range_distribution

# ── New baseline functions (Priority A/B implementations) ────────────────────
from data_preprocessing.bayesian.intervals import beta_hpd_interval, compare_ci_vs_credible_normal
from data_preprocessing.bayesian.bayes_factors import (
    bayes_factor_beta_binomial,
    log_marginal_likelihood_beta_binomial,
    log_marginal_likelihood_gamma_poisson,
)
from data_preprocessing.bayesian.conjugate_models import jeffreys_update_binomial, mle_vs_map
from data_preprocessing.bayesian.posterior_predictive import posterior_predictive_check_beta_binomial
from data_preprocessing.bayesian.bayesian_regression import normal_inverse_gamma_regression_update


# ─────────────────────────────────────────────────────────────────────────────
# Shared task builder
# ─────────────────────────────────────────────────────────────────────────────

def make_task(
    task_id: str,
    tier: int,
    difficulty: str,
    structure: List[str],
    assumptions: List[str],
    numeric_targets: Dict[str, float],
    notes: Dict[str, Any],
    tol: float = 1e-3,
    zero: float = 1e-1,
) -> Dict[str, Any]:
    return {
        "task_id": task_id,
        "tier": tier,
        "difficulty": difficulty,
        "required_structure_checks": structure,
        "required_assumption_checks": assumptions,
        "numeric_targets": [
            {"key": k, "true_value": float(v), "full_credit_tol": tol, "zero_credit_scale": zero}
            for k, v in numeric_targets.items()
        ],
        "notes": notes,
    }


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 0 — Original conjugate-model tasks (unchanged)
# ─────────────────────────────────────────────────────────────────────────────

def gen_original_tasks() -> List[Dict[str, Any]]:
    tasks: List[Dict[str, Any]] = []

    gt1 = gt_beta_binomial(alpha=2, beta=2, x=6, n=10, ci_level=0.95, predictive_k=3, predictive_m=5)
    tasks.append(make_task(
        task_id="BETA_BINOM_01", tier=1, difficulty="basic",
        structure=["states_prior", "states_likelihood", "states_posterior_kernel_or_family", "updates_hyperparameters_correctly"],
        assumptions=["states_iid", "states_distributional_assumption"],
        numeric_targets={"posterior_mean": gt1["posterior_mean"], "ci_lower": gt1["ci_lower"],
                         "ci_upper": gt1["ci_upper"], "predictive_pmf_k_m": gt1["predictive_pmf_k_m"]},
        notes={"topic": "beta-binomial", "inputs": {"alpha":2,"beta":2,"x":6,"n":10,"k":3,"m":5}},
    ))

    gt2 = gt_gamma_poisson(alpha=1.0, rate=1.0, counts=[2,0,3,1], ci_level=0.95, predictive_y=2)
    tasks.append(make_task(
        task_id="GAMMA_POISSON_01", tier=1, difficulty="intermediate",
        structure=["states_prior", "states_likelihood", "states_posterior_kernel_or_family", "updates_hyperparameters_correctly"],
        assumptions=["states_iid", "states_distributional_assumption"],
        numeric_targets={"posterior_mean": gt2["posterior_mean"], "ci_lower": gt2["ci_lower"],
                         "ci_upper": gt2["ci_upper"], "predictive_pmf_y": gt2["predictive_pmf_y"]},
        notes={"topic": "gamma-poisson", "inputs": {"alpha":1.0,"rate":1.0,"counts":[2,0,3,1],"y":2}},
    ))

    gt3 = gt_normal_gamma_precision(mu0=0.0, kappa0=1.0, alpha0=2.0, beta0=2.0, data=[1.0,2.0,1.5,0.5])
    tasks.append(make_task(
        task_id="NORMAL_GAMMA_01", tier=1, difficulty="advanced",
        structure=["states_prior", "states_likelihood", "states_posterior_kernel_or_family", "updates_hyperparameters_correctly"],
        assumptions=["states_iid", "states_distributional_assumption"],
        numeric_targets={"posterior_mean_mu": gt3["posterior_mean_mu"], "ci_mu_lower": gt3["ci_mu_lower"],
                         "ci_mu_upper": gt3["ci_mu_upper"], "posterior_mean_tau": gt3["posterior_mean_tau"]},
        notes={"topic": "normal-gamma", "inputs": {"mu0":0.0,"kappa0":1.0,"alpha0":2.0,"beta0":2.0,"data":[1.0,2.0,1.5,0.5]}},
    ))

    gt4 = gt_dirichlet_multinomial(alpha=[1,1,1], counts=[10,5,0], predictive_counts=[2,1,0])
    tasks.append(make_task(
        task_id="DIRICHLET_01", tier=1, difficulty="intermediate",
        structure=["states_prior", "states_likelihood", "states_posterior_kernel_or_family", "updates_hyperparameters_correctly"],
        assumptions=["states_iid", "states_distributional_assumption"],
        numeric_targets={"p1_mean": gt4["posterior_mean_vector"][0], "p2_mean": gt4["posterior_mean_vector"][1],
                         "p3_mean": gt4["posterior_mean_vector"][2], "predictive_pmf_counts": gt4["predictive_pmf_counts"]},
        notes={"topic": "dirichlet-multinomial", "inputs": {"alpha":[1,1,1],"counts":[10,5,0],"pred_counts":[2,1,0]}},
    ))

    return tasks


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 1 — Bayes estimators (Lectures 21–22)
# ─────────────────────────────────────────────────────────────────────────────

def gen_discrete_posterior_median_tasks() -> List[Dict[str, Any]]:
    """Five instances of discrete posterior median (Lecture 21)."""
    instances = [
        {"values": [1, 2, 3, 4, 5],        "probs": [0.10, 0.20, 0.30, 0.25, 0.15]},
        {"values": [0.5, 1.0, 1.5, 2.0],   "probs": [0.30, 0.40, 0.20, 0.10]},
        {"values": [10, 20, 30],             "probs": [0.10, 0.50, 0.40]},
        {"values": [2, 4, 6, 8],             "probs": [0.25, 0.25, 0.25, 0.25]},
        {"values": [1, 3, 5, 7, 9],          "probs": [0.05, 0.20, 0.50, 0.20, 0.05]},
    ]
    tasks = []
    for i, inst in enumerate(instances, 1):
        median = discrete_posterior_median(inst["values"], inst["probs"])
        tasks.append(make_task(
            task_id=f"DISC_MEDIAN_{i:02d}",
            tier=2, difficulty="intermediate",
            structure=["states_cumulative_probability_rule", "identifies_first_cumsum_geq_half"],
            assumptions=["values_are_ordered"],
            numeric_targets={"posterior_median": median},
            notes={"topic": "discrete_posterior_median", "inputs": inst},
            tol=1e-6, zero=0.05,
        ))
    return tasks


def gen_uniform_mle_tasks() -> List[Dict[str, Any]]:
    """Five instances of Uniform(0,theta) MLE = max(data) (Lecture 24)."""
    instances = [
        {"data": [1.2, 3.4, 2.1, 4.7, 0.9]},
        {"data": [0.5, 1.8, 3.2, 2.9, 1.1, 3.8]},
        {"data": [7.1, 2.3, 5.8, 9.2, 4.6]},
        {"data": [0.3, 0.7, 0.5, 0.9, 0.4, 0.8, 0.6]},
        {"data": [12.5, 8.3, 15.7, 11.2, 9.8, 14.1]},
    ]
    tasks = []
    for i, inst in enumerate(instances, 1):
        mle = uniform_mle(inst["data"])
        tasks.append(make_task(
            task_id=f"UNIFORM_MLE_{i:02d}",
            tier=2, difficulty="basic",
            structure=["identifies_mle_as_max_order_statistic", "states_likelihood_function"],
            assumptions=["states_iid", "states_distributional_assumption"],
            numeric_targets={"mle_theta": mle},
            notes={"topic": "uniform_mle", "inputs": inst},
            tol=1e-6, zero=0.01,
        ))
    return tasks


def gen_binomial_flat_prior_tasks() -> List[Dict[str, Any]]:
    """Five instances of Binomial likelihood + Uniform(0,1) prior (Lecture 21)."""
    instances = [
        {"x": 3,  "n": 10},
        {"x": 7,  "n": 10},
        {"x": 0,  "n": 5},
        {"x": 15, "n": 20},
        {"x": 4,  "n": 8},
    ]
    tasks = []
    for i, inst in enumerate(instances, 1):
        post = binomial_uniform_prior_update(inst["x"], inst["n"])
        tasks.append(make_task(
            task_id=f"BINOM_FLAT_{i:02d}",
            tier=1, difficulty="basic",
            structure=["states_flat_prior_as_beta_1_1", "states_posterior_family",
                       "updates_hyperparameters_correctly"],
            assumptions=["states_iid", "states_distributional_assumption"],
            numeric_targets={
                "alpha_post": post.alpha_post,
                "beta_post":  post.beta_post,
                "posterior_mean": post.mean(),
            },
            notes={"topic": "binomial_flat_prior",
                   "inputs": {"x": inst["x"], "n": inst["n"],
                              "prior": "Beta(1,1) = Uniform(0,1)"}},
            tol=1e-6, zero=0.05,
        ))
    return tasks


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 2 — Decision theory (Lecture 22)
# ─────────────────────────────────────────────────────────────────────────────

def gen_minimax_comparison_tasks() -> List[Dict[str, Any]]:
    """Five instances of minimax estimator selection (Lecture 22, Example 37)."""
    instances = [
        {"theta_grid": [0, 1, 2], "hat1_risks": [0.0, 0.5, 0.0], "hat2_risks": [1.0, 0.0, 1.0]},
        {"theta_grid": [0, 1, 2], "hat1_risks": [0.3, 0.3, 0.3], "hat2_risks": [0.1, 0.8, 0.1]},
        {"theta_grid": [0, 1, 2], "hat1_risks": [0.5, 0.5, 0.5], "hat2_risks": [0.0, 0.4, 0.0]},
        {"theta_grid": [0, 1, 2], "hat1_risks": [0.2, 0.6, 0.2], "hat2_risks": [0.4, 0.4, 0.4]},
        {"theta_grid": [0, 1, 2], "hat1_risks": [0.1, 0.4, 0.1], "hat2_risks": [0.3, 0.3, 0.3]},
    ]
    tasks = []
    for i, inst in enumerate(instances, 1):
        result = minimax_risk(
            estimators={
                "hat1": np.array(inst["hat1_risks"]),
                "hat2": np.array(inst["hat2_risks"]),
            },
            theta_grid=np.array(inst["theta_grid"]),
        )
        tasks.append(make_task(
            task_id=f"MINIMAX_{i:02d}",
            tier=3, difficulty="intermediate",
            structure=["computes_max_risk_per_estimator", "selects_estimator_with_min_max_risk"],
            assumptions=[],
            numeric_targets={
                "max_risk_hat1":  result["risks"]["hat1"]["max_risk"],
                "max_risk_hat2":  result["risks"]["hat2"]["max_risk"],
                "minimax_value":  result["minimax_value"],
            },
            notes={
                "topic": "minimax_comparison",
                "minimax_estimator": result["minimax_estimator"],
                "inputs": inst,
            },
            tol=1e-6, zero=0.05,
        ))
    return tasks


def gen_discrete_bayes_risk_tasks() -> List[Dict[str, Any]]:
    """Five instances of discrete-prior Bayes risk (Lecture 22)."""
    instances = [
        {"risk_values": [0.5, 0.3],           "prior_probs": [0.4, 0.6]},
        {"risk_values": [1.0, 0.5, 0.2],      "prior_probs": [0.3, 0.3, 0.4]},
        {"risk_values": [0.8, 0.2],            "prior_probs": [0.5, 0.5]},
        {"risk_values": [0.0, 0.5, 0.5, 0.0], "prior_probs": [0.25, 0.25, 0.25, 0.25]},
        {"risk_values": [0.9, 0.1, 0.4],       "prior_probs": [0.2, 0.5, 0.3]},
    ]
    tasks = []
    for i, inst in enumerate(instances, 1):
        br = discrete_bayes_risk(inst["risk_values"], inst["prior_probs"])
        tasks.append(make_task(
            task_id=f"BAYES_RISK_{i:02d}",
            tier=2, difficulty="basic",
            structure=["applies_prior_weighting", "sums_weighted_risks"],
            assumptions=[],
            numeric_targets={"bayes_risk": br},
            notes={"topic": "discrete_bayes_risk", "inputs": inst},
            tol=1e-6, zero=0.05,
        ))
    return tasks


def gen_bias_variance_decomp_tasks() -> List[Dict[str, Any]]:
    """
    Five instances of bias-variance decomposition for d2=max(Xi), Uniform(0,theta).
    Uses closed-form analytical formulas from Lecture 25.
    """
    instances = [
        {"n": 5,  "theta": 1.0},
        {"n": 10, "theta": 2.0},
        {"n": 20, "theta": 3.0},
        {"n": 8,  "theta": 4.0},
        {"n": 15, "theta": 5.0},
    ]
    tasks = []
    for i, inst in enumerate(instances, 1):
        n, theta = inst["n"], inst["theta"]
        bias   = -theta / (n + 1)
        var_d2 = n * theta ** 2 / ((n + 1) ** 2 * (n + 2))
        mse_d2 = 2 * theta ** 2 / ((n + 1) * (n + 2))
        tasks.append(make_task(
            task_id=f"BIAS_VAR_{i:02d}",
            tier=3, difficulty="intermediate",
            structure=["computes_bias_from_expectation",
                       "computes_variance_of_estimator",
                       "states_mse_equals_bias_sq_plus_variance"],
            assumptions=["states_iid", "states_distributional_assumption"],
            numeric_targets={
                "bias":   bias,
                "var_d2": var_d2,
                "mse_d2": mse_d2,
            },
            notes={
                "topic": "bias_variance_decomp",
                "estimator": "d2 = max(X_i)",
                "model": "Uniform(0, theta)",
                "inputs": inst,
            },
            tol=1e-6, zero=0.01,
        ))
    return tasks


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 3 — Frequentist / Fisher (Lectures 23–25)
# ─────────────────────────────────────────────────────────────────────────────

def gen_fisher_information_tasks() -> List[Dict[str, Any]]:
    """Five instances of Fisher information I_n(theta) (Lecture 23)."""
    instances = [
        {"dist": "binomial", "theta": 0.3, "n": 10},
        {"dist": "binomial", "theta": 0.5, "n": 20},
        {"dist": "poisson",  "theta": 4.0, "n": 5},
        {"dist": "normal",   "theta": 2.0, "n": 15},
        {"dist": "poisson",  "theta": 2.0, "n": 8},
    ]
    tasks = []
    for i, inst in enumerate(instances, 1):
        fi = fisher_information(inst["dist"], inst["theta"], inst["n"])
        difficulty = "basic" if inst["dist"] == "normal" else "intermediate"
        tasks.append(make_task(
            task_id=f"FISHER_INFO_{i:02d}",
            tier=3, difficulty=difficulty,
            structure=["states_fisher_information_formula",
                       "applies_correct_formula_for_distribution"],
            assumptions=["states_regularity_conditions"],
            numeric_targets={"fisher_info": fi},
            notes={"topic": "fisher_information", "inputs": inst},
            tol=1e-3, zero=1.0,
        ))
    return tasks


def gen_rao_cramer_bound_tasks() -> List[Dict[str, Any]]:
    """Five instances of the Rao-Cramér lower bound 1/I(theta) (Lecture 23)."""
    instances = [
        {"dist": "binomial", "theta": 0.3, "n": 10},
        {"dist": "binomial", "theta": 0.5, "n": 20},
        {"dist": "poisson",  "theta": 4.0, "n": 20},
        {"dist": "normal",   "theta": 1.0, "n": 10},
        {"dist": "poisson",  "theta": 2.0, "n": 8},
    ]
    tasks = []
    for i, inst in enumerate(instances, 1):
        fi  = fisher_information(inst["dist"], inst["theta"], inst["n"])
        rc  = rao_cramer_bound(fi)
        tasks.append(make_task(
            task_id=f"RC_BOUND_{i:02d}",
            tier=3, difficulty="basic",
            structure=["states_rc_bound_as_reciprocal_of_fisher_info",
                       "identifies_unbiased_case_bias_deriv_zero"],
            assumptions=["states_unbiasedness_assumption"],
            numeric_targets={"fisher_info": fi, "rc_bound": rc},
            notes={"topic": "rao_cramer_bound", "inputs": inst},
            tol=1e-4, zero=0.05,
        ))
    return tasks


def gen_optimal_scaled_estimator_tasks() -> List[Dict[str, Any]]:
    """Five instances of optimal scaled estimator dc = c*max(Xi) (Lecture 25)."""
    instances = [
        {"n": 5,  "theta": 1.0},
        {"n": 10, "theta": 2.0},
        {"n": 20, "theta": 3.0},
        {"n": 8,  "theta": 4.0},
        {"n": 15, "theta": 5.0},
    ]
    tasks = []
    for i, inst in enumerate(instances, 1):
        res = optimal_scaled_estimator_uniform(inst["n"], inst["theta"])
        tasks.append(make_task(
            task_id=f"OPT_SCALED_{i:02d}",
            tier=4, difficulty="advanced",
            structure=["derives_optimal_c_by_minimising_mse",
                       "states_c_opt_formula_n_plus_2_over_n_plus_1",
                       "computes_resulting_mse"],
            assumptions=["states_iid", "states_distributional_assumption"],
            numeric_targets={
                "c_opt":   res["c_opt"],
                "mse_opt": res["mse_opt"],
            },
            notes={
                "topic": "optimal_scaled_estimator",
                "model": "Uniform(0, theta)",
                "estimator": "dc = c * max(X_i)",
                "inputs": inst,
            },
            tol=1e-6, zero=0.01,
        ))
    return tasks


def gen_mse_comparison_tasks() -> List[Dict[str, Any]]:
    """Five instances comparing MSE(d1), MSE(d2), MSE(dc) for Uniform(0,theta) (Lecture 25)."""
    instances = [
        {"n": 5,  "theta": 1.0},
        {"n": 10, "theta": 2.0},
        {"n": 20, "theta": 3.0},
        {"n": 8,  "theta": 4.0},
        {"n": 15, "theta": 5.0},
    ]
    tasks = []
    for i, inst in enumerate(instances, 1):
        res = optimal_scaled_estimator_uniform(inst["n"], inst["theta"])
        tasks.append(make_task(
            task_id=f"MSE_COMPARE_{i:02d}",
            tier=4, difficulty="advanced",
            structure=["computes_mse_d1_analytical",
                       "computes_mse_d2_analytical",
                       "computes_mse_dc_at_optimal_c",
                       "identifies_dc_as_minimum_mse_estimator"],
            assumptions=["states_iid", "states_distributional_assumption"],
            numeric_targets={
                "mse_d1": res["mse_d1"],
                "mse_d2": res["mse_d2"],
                "mse_dc": res["mse_opt"],
            },
            notes={
                "topic": "mse_comparison",
                "model": "Uniform(0, theta)",
                "best_estimator": "dc",
                "inputs": inst,
            },
            tol=1e-6, zero=0.01,
        ))
    return tasks


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 4 — Markov chains (Lectures 30–33)
# ─────────────────────────────────────────────────────────────────────────────

def gen_markov_tasks() -> List[Dict[str, Any]]:
    """
    Five Markov chain tasks covering stationary distributions, gambler's ruin,
    and n-step transition probabilities (Lectures 31–33).
    """
    # Fixed transition matrices and parameters for reproducibility
    instances = [
        # inst 1: 3-state ergodic chain — stationary distribution
        {
            "subtype": "stationary",
            "P": [[0.5, 0.25, 0.25],
                  [2/3, 0.0,  1/3 ],
                  [0.6, 0.4,  0.0 ]],
            "note": "Lecture 33 Example 23.6",
        },
        # inst 2: gambler's ruin, fair game
        {
            "subtype": "gamblers_ruin",
            "p": 0.5, "i": 3, "M": 10,
            "note": "fair game p=0.5",
        },
        # inst 3: gambler's ruin, unfair
        {
            "subtype": "gamblers_ruin",
            "p": 0.4, "i": 5, "M": 10,
            "note": "unfair p=0.4",
        },
        # inst 4: 3-state chain — 2-step transition probability P^2[0,2]
        {
            "subtype": "n_step",
            "P": [[0.5, 0.25, 0.25],
                  [2/3, 0.0,  1/3 ],
                  [0.6, 0.4,  0.0 ]],
            "n": 2, "i": 1, "j": 2,
            "note": "P^2[2,3] = 1/6 (Lecture 31 Example 21.1)",
        },
        # inst 5: 2-state chain — stationary distribution
        {
            "subtype": "stationary_2state",
            "P": [[0.7, 0.3],
                  [0.4, 0.6]],
            "note": "two-state chain: pi = [4/7, 3/7]",
        },
    ]

    tasks = []
    for i, inst in enumerate(instances, 1):
        subtype = inst["subtype"]

        if subtype == "stationary":
            P = np.array(inst["P"])
            pi = stationary_distribution(P)
            targets = {"pi_0": float(pi[0]), "pi_1": float(pi[1]), "pi_2": float(pi[2])}
            structure = ["solves_pi_P_eq_pi", "normalises_to_one",
                         "uses_eigenvalue_or_linear_system"]
            assumptions = ["chain_is_irreducible", "chain_is_aperiodic"]
            notes = {"topic": "markov_stationary", "inputs": {"P": inst["P"]},
                     "note": inst["note"]}

        elif subtype == "gamblers_ruin":
            res = gambling_ruin_probability(inst["p"], inst["i"], inst["M"])
            targets = {"ruin_prob": res["ruin_prob"], "win_prob": res["win_prob"]}
            structure = ["applies_gamblers_ruin_formula", "handles_fair_vs_unfair_case"]
            assumptions = ["absorbing_boundaries_at_0_and_M"]
            notes = {"topic": "gamblers_ruin",
                     "inputs": {"p": inst["p"], "i": inst["i"], "M": inst["M"]},
                     "note": inst["note"]}

        elif subtype == "n_step":
            P = np.array(inst["P"])
            Pn = n_step_transition(P, inst["n"])
            targets = {f"P{inst['n']}_{inst['i']}_{inst['j']}": float(Pn[inst["i"], inst["j"]])}
            structure = ["computes_matrix_power", "applies_chapman_kolmogorov"]
            assumptions = []
            notes = {"topic": "markov_n_step",
                     "inputs": {"P": inst["P"], "n": inst["n"],
                                "i": inst["i"], "j": inst["j"]},
                     "note": inst["note"]}

        else:  # stationary_2state
            P = np.array(inst["P"])
            pi = stationary_distribution(P)
            targets = {"pi_0": float(pi[0]), "pi_1": float(pi[1])}
            structure = ["solves_pi_P_eq_pi", "normalises_to_one"]
            assumptions = ["chain_is_irreducible"]
            notes = {"topic": "markov_stationary_2state",
                     "inputs": {"P": inst["P"]},
                     "note": inst["note"]}

        tasks.append(make_task(
            task_id=f"MARKOV_{i:02d}",
            tier=3, difficulty="intermediate",
            structure=structure,
            assumptions=assumptions,
            numeric_targets=targets,
            notes=notes,
            tol=1e-4, zero=0.05,
        ))
    return tasks


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 5 — Order statistics (Lectures 26–29)
# ─────────────────────────────────────────────────────────────────────────────

def gen_order_stat_tasks() -> List[Dict[str, Any]]:
    """
    Five order statistics tasks: k-th order stat PDF, min CDF, and range
    distribution (Lectures 26–29).
    """
    instances = [
        # inst 1: PDF of X_(3) from n=5 Uniform[0,1] at y=0.4
        {"subtype": "pdf",  "y": 0.4, "k": 3, "n": 5},
        # inst 2: PDF of X_(1) (minimum) from n=4 at y=0.2
        {"subtype": "pdf",  "y": 0.2, "k": 1, "n": 4},
        # inst 3: CDF of minimum from n=5 at x=0.3
        {"subtype": "min_cdf", "x": 0.3, "n": 5},
        # inst 4: CDF of minimum from n=8 at x=0.5
        {"subtype": "min_cdf", "x": 0.5, "n": 8},
        # inst 5: Range ~ Beta(n-1, 2) for n=5
        {"subtype": "range", "n": 5},
    ]

    tasks = []
    for i, inst in enumerate(instances, 1):
        subtype = inst["subtype"]

        if subtype == "pdf":
            val = order_statistic_pdf(inst["y"], inst["k"], inst["n"])
            targets = {"order_stat_pdf": float(val)}
            structure = ["states_order_stat_pdf_formula",
                         "identifies_beta_distribution_connection"]
            assumptions = ["states_iid", "uniform_support_0_1"]
            notes = {"topic": "order_statistic_pdf",
                     "inputs": {"y": inst["y"], "k": inst["k"], "n": inst["n"]},
                     "formula": f"Beta({inst['k']}, {inst['n']-inst['k']+1}).pdf({inst['y']})"}

        elif subtype == "min_cdf":
            val = min_order_statistic_cdf(inst["x"], inst["n"])
            targets = {"min_cdf": float(val)}
            structure = ["states_min_cdf_as_1_minus_survival",
                         "applies_F_1_x_formula"]
            assumptions = ["states_iid", "uniform_support_0_1"]
            notes = {"topic": "min_order_statistic_cdf",
                     "inputs": {"x": inst["x"], "n": inst["n"]},
                     "formula": f"1 - (1 - {inst['x']})^{inst['n']}"}

        else:  # range
            res = uniform_range_distribution(inst["n"])
            targets = {
                "range_beta_alpha": float(res["alpha"]),
                "range_beta_beta":  float(res["beta"]),
            }
            structure = ["identifies_range_as_beta_distribution",
                         "states_correct_parameters_n_minus_1_and_2"]
            assumptions = ["states_iid", "uniform_support_0_1"]
            notes = {"topic": "uniform_range_distribution",
                     "inputs": {"n": inst["n"]},
                     "result": res["dist"]}

        tasks.append(make_task(
            task_id=f"ORDER_STAT_{i:02d}",
            tier=3, difficulty="intermediate",
            structure=structure,
            assumptions=assumptions,
            numeric_targets=targets,
            notes=notes,
            tol=1e-4, zero=0.05,
        ))
    return tasks


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 6 — Simple linear regression (Lecture 37–38)
# ─────────────────────────────────────────────────────────────────────────────

def gen_regression_tasks() -> List[Dict[str, Any]]:
    """
    Five OLS linear regression tasks: slope/intercept estimation, residual
    variance, and 95 % confidence intervals.
    """
    instances = [
        {"x": [1.0, 2.0, 3.0, 4.0, 5.0],
         "y": [2.1, 3.9, 6.2, 7.8, 10.1]},
        {"x": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
         "y": [1.0, 2.8, 5.1, 6.9, 9.2, 11.0]},
        {"x": [2.0, 4.0, 6.0, 8.0, 10.0],
         "y": [3.5, 7.2, 9.8, 13.5, 17.1]},
        {"x": [1.0, 3.0, 5.0, 7.0, 9.0],
         "y": [5.0, 8.5, 12.0, 16.2, 19.5]},
        {"x": [10.0, 20.0, 30.0, 40.0, 50.0],
         "y": [25.0, 45.5, 65.0, 84.5, 105.0]},
    ]

    tasks = []
    for i, inst in enumerate(instances, 1):
        ests = ols_estimators(inst["x"], inst["y"])
        s2   = residual_variance(inst["x"], inst["y"])
        ci   = credibility_intervals(inst["x"], inst["y"], level=0.95)
        tasks.append(make_task(
            task_id=f"REGRESSION_{i:02d}",
            tier=3, difficulty="intermediate",
            structure=["computes_B_hat_via_Sxy_over_Sxx",
                       "computes_A_hat_via_ybar_minus_B_hat_xbar",
                       "computes_residual_variance_SSR_over_n_minus_2",
                       "constructs_t_based_confidence_intervals"],
            assumptions=["states_iid", "normal_errors", "constant_variance"],
            numeric_targets={
                "A_hat":   ests["A_hat"],
                "B_hat":   ests["B_hat"],
                "s2":      s2,
                "B_lower": ci["B_lower"],
                "B_upper": ci["B_upper"],
            },
            notes={
                "topic":  "ols_regression",
                "model":  "Y = A + B*x + epsilon, epsilon ~ N(0, sigma^2)",
                "inputs": {"x": inst["x"], "y": inst["y"]},
                "level":  0.95,
            },
            tol=1e-3, zero=0.1,
        ))
    return tasks


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 7 — Box-Muller transform (Lecture 36)
# ─────────────────────────────────────────────────────────────────────────────

def gen_sampling_tasks() -> List[Dict[str, Any]]:
    """
    Five Box-Muller transform tasks: given (U, V), compute (z1, z2) and
    optionally scale to N(mu, sigma^2) (Lecture 36, Example 42).
    """
    instances = [
        # Lecture 36 Example 42
        {"U": 0.531, "V": 0.253, "mu": 50.0, "sigma": 5.0},
        # Additional instances with varied parameters
        {"U": 0.200, "V": 0.500, "mu":  0.0, "sigma": 1.0},
        {"U": 0.750, "V": 0.100, "mu": 10.0, "sigma": 2.0},
        {"U": 0.050, "V": 0.750, "mu":  0.0, "sigma": 1.0},
        {"U": 0.900, "V": 0.300, "mu": 100.0, "sigma": 15.0},
    ]

    tasks = []
    for i, inst in enumerate(instances, 1):
        z1, z2 = box_muller_standard(inst["U"], inst["V"])
        x1 = inst["mu"] + inst["sigma"] * z1
        x2 = inst["mu"] + inst["sigma"] * z2
        tasks.append(make_task(
            task_id=f"BOX_MULLER_{i:02d}",
            tier=2, difficulty="basic",
            structure=["applies_box_muller_formula",
                       "computes_r_as_sqrt_neg2_log_U",
                       "applies_cos_sin_with_2pi_V"],
            assumptions=["U_V_independent_uniform_0_1"],
            numeric_targets={
                "z1": float(z1),
                "z2": float(z2),
                "x1": float(x1),
                "x2": float(x2),
            },
            notes={
                "topic":   "box_muller_transform",
                "inputs":  {"U": inst["U"], "V": inst["V"],
                            "mu": inst["mu"], "sigma": inst["sigma"]},
                "formula": "z1 = sqrt(-2*log(U))*cos(2*pi*V), "
                           "z2 = sqrt(-2*log(U))*sin(2*pi*V), "
                           "x = mu + sigma*z",
            },
            tol=1e-3, zero=0.1,
        ))
    return tasks


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 8 — HPD credible intervals (A1)
# ─────────────────────────────────────────────────────────────────────────────

def gen_hpd_interval_tasks() -> List[Dict[str, Any]]:
    """
    Five HPD interval tasks for Beta posteriors.

    Covers symmetric and skewed Beta distributions, illustrating that the HPD
    interval is strictly shorter than the equal-tail interval for skewed posteriors.
    Reference: Lee (2012) §2.6; Hoff (2009) §2.3.
    """
    instances = [
        # symmetric — HPD == equal-tail
        {"alpha": 5,  "beta": 5,  "level": 0.95,
         "note": "symmetric Beta(5,5): HPD equals equal-tail interval"},
        # moderately skewed
        {"alpha": 2,  "beta": 8,  "level": 0.95,
         "note": "right-skewed Beta(2,8): HPD is shorter than equal-tail"},
        # strongly skewed — HPD starts at 0
        {"alpha": 1,  "beta": 10, "level": 0.95,
         "note": "monotone Beta(1,10): HPD = [0, F^{-1}(0.95)]"},
        # left-skewed
        {"alpha": 10, "beta": 2,  "level": 0.95,
         "note": "left-skewed Beta(10,2): HPD ends near 1"},
        # moderate asymmetry
        {"alpha": 3,  "beta": 7,  "level": 0.90,
         "note": "Beta(3,7) at 90% level"},
    ]
    tasks = []
    for i, inst in enumerate(instances, 1):
        lo, hi = beta_hpd_interval(inst["alpha"], inst["beta"], inst["level"])
        tasks.append(make_task(
            task_id=f"HPD_{i:02d}",
            tier=2, difficulty="intermediate",
            structure=["computes_hpd_via_shortest_interval",
                       "notes_hpd_shorter_than_equal_tail"],
            assumptions=["states_distributional_assumption"],
            numeric_targets={"hpd_lower": lo, "hpd_upper": hi},
            notes={
                "topic":  "hpd_credible_interval",
                "inputs": {"alpha": inst["alpha"], "beta": inst["beta"],
                           "level": inst["level"]},
                "note":   inst["note"],
            },
            tol=1e-2, zero=0.05,
        ))
    return tasks


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 9 — Bayes factors (A2)
# ─────────────────────────────────────────────────────────────────────────────

def gen_bayes_factor_tasks() -> List[Dict[str, Any]]:
    """
    Five Bayes factor tasks comparing M1=Beta(1,1) vs M2=Beta(0.5,0.5) priors
    for Binomial data.

    BF_{12} = p(x|M1) / p(x|M2) = exp(log B(1+x,1+n-x) - log B(1,1)
                                      - log B(0.5+x,0.5+n-x) + log B(0.5,0.5))
    Reference: Kass & Raftery (1995); Lee (2012) §4.5; Ghosh et al (2006) §6.3.
    """
    instances = [
        {"x":  3, "n": 10, "note": "minority successes favour uniform prior"},
        {"x":  8, "n": 15, "note": "moderate successes"},
        {"x":  5, "n": 20, "note": "sparse data, n=20"},
        {"x":  2, "n": 10, "note": "few successes"},
        {"x": 12, "n": 25, "note": "larger dataset"},
    ]
    tasks = []
    for i, inst in enumerate(instances, 1):
        res = bayes_factor_beta_binomial(
            alpha1=1.0, beta1=1.0,
            alpha2=0.5, beta2=0.5,
            x=inst["x"], n=inst["n"],
        )
        tasks.append(make_task(
            task_id=f"BAYES_FACTOR_{i:02d}",
            tier=3, difficulty="intermediate",
            structure=["applies_bayes_factor_formula",
                       "states_evidence_scale"],
            assumptions=["states_distributional_assumption"],
            numeric_targets={"log_BF": res["log_BF"], "BF": res["BF"]},
            notes={
                "topic":    "bayes_factor_beta_binomial",
                "inputs":   {"x": inst["x"], "n": inst["n"],
                             "M1": "Beta(1,1)", "M2": "Beta(0.5,0.5)"},
                "favored":  res["favored_model"],
                "strength": res["evidence_strength"],
                "note":     inst["note"],
            },
            tol=1e-4, zero=0.1,
        ))
    return tasks


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 10 — Jeffreys prior (A3)
# ─────────────────────────────────────────────────────────────────────────────

def gen_jeffreys_prior_tasks() -> List[Dict[str, Any]]:
    """
    Five Jeffreys prior update tasks for the Binomial model.

    Jeffreys prior: Beta(0.5, 0.5).
    Posterior: Beta(x + 0.5, n - x + 0.5).

    The Jeffreys prior is invariant under reparametrisation of theta, unlike
    the uniform Beta(1,1) prior.
    Reference: Lee (2012) §3.3; Ghosh et al (2006) §5.1.2.
    """
    instances = [
        {"x":  3, "n": 10},
        {"x":  7, "n": 12},
        {"x":  2, "n":  8},
        {"x": 10, "n": 15},
        {"x":  4, "n":  6},
    ]
    tasks = []
    for i, inst in enumerate(instances, 1):
        res = jeffreys_update_binomial(inst["x"], inst["n"])
        tasks.append(make_task(
            task_id=f"JEFFREYS_{i:02d}",
            tier=2, difficulty="intermediate",
            structure=["states_jeffreys_prior_formula",
                       "notes_jeffreys_invariance",
                       "updates_hyperparameters_correctly"],
            assumptions=["states_iid", "states_distributional_assumption"],
            numeric_targets={
                "alpha_post":     res["alpha"],
                "beta_post":      res["beta"],
                "posterior_mean": res["posterior_mean"],
            },
            notes={
                "topic":  "jeffreys_prior_binomial",
                "inputs": {"x": inst["x"], "n": inst["n"],
                           "prior": "Beta(0.5, 0.5) Jeffreys"},
                "note":   ("Posterior Beta(x+0.5, n-x+0.5). "
                           "Compare with flat prior: Beta(x+1, n-x+1)."),
            },
            tol=1e-6, zero=0.05,
        ))
    return tasks


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 11 — Posterior predictive checks (A4)
# ─────────────────────────────────────────────────────────────────────────────

def gen_ppc_tasks() -> List[Dict[str, Any]]:
    """
    Five posterior predictive check tasks for the Beta-Binomial model.

    Tasks 1, 2, 5: well-specified — x_obs near the predictive median (should PASS).
    Tasks 3, 4:    extreme observations — x_obs in the tail (should FAIL).

    The Bayesian p-value P(x_rep <= x_obs) is near 0.5 for well-calibrated
    predictions and near 0 or 1 for model-data conflict.
    Reference: Hoff (2009) §4.4; Carlin & Louis (2008) §2.5.
    """
    instances = [
        # PASS: posterior fitted on x=6/10, checking x_obs=6 (well-calibrated)
        {"alpha_post": 7.0, "beta_post": 5.0,  "n_obs": 10, "x_obs":  6,
         "seed": 42, "note": "well-specified: x_obs near predictive median"},
        # PASS: Beta(4,8) posterior, n=15, moderate x_obs=5
        {"alpha_post": 4.0, "beta_post": 8.0,  "n_obs": 15, "x_obs":  5,
         "seed": 42, "note": "well-specified: x_obs consistent with model"},
        # FAIL: x_obs=0 (extreme low — far below predictive mean)
        {"alpha_post": 7.0, "beta_post": 5.0,  "n_obs": 10, "x_obs":  0,
         "seed": 42, "note": "model-data conflict: x_obs too low"},
        # FAIL: x_obs=15 (extreme high — far above predictive mean for theta~0.33)
        {"alpha_post": 4.0, "beta_post": 8.0,  "n_obs": 15, "x_obs": 15,
         "seed": 42, "note": "model-data conflict: x_obs too high"},
        # PASS: Beta(6,6) symmetric posterior, n=20, x_obs=10 (centre)
        {"alpha_post": 6.0, "beta_post": 6.0,  "n_obs": 20, "x_obs": 10,
         "seed": 42, "note": "well-specified: symmetric posterior, x_obs at centre"},
    ]
    tasks = []
    for i, inst in enumerate(instances, 1):
        res = posterior_predictive_check_beta_binomial(
            alpha_post=inst["alpha_post"],
            beta_post=inst["beta_post"],
            n_obs=inst["n_obs"],
            x_obs=inst["x_obs"],
            n_rep=5000,
            seed=inst["seed"],
        )
        tasks.append(make_task(
            task_id=f"PPC_{i:02d}",
            tier=3, difficulty="intermediate",
            structure=["generates_predictive_replicates",
                       "checks_tail_probability"],
            assumptions=["states_distributional_assumption"],
            numeric_targets={
                "p_value": res["p_value"],
                "passed":  float(res["passed"]),
            },
            notes={
                "topic":       "posterior_predictive_check",
                "inputs":      {"alpha_post": inst["alpha_post"],
                                "beta_post":  inst["beta_post"],
                                "n_obs":      inst["n_obs"],
                                "x_obs":      inst["x_obs"],
                                "n_rep":      5000},
                "passed":      res["passed"],
                "T_rep_mean":  res["T_rep_mean"],
                "note":        inst["note"],
            },
            tol=5e-2, zero=0.25,
        ))
    return tasks


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 12 — Bayesian linear regression (A5)
# ─────────────────────────────────────────────────────────────────────────────

def gen_bayesian_regression_tasks() -> List[Dict[str, Any]]:
    """
    Five Bayesian linear regression tasks using the Normal-Inverse-Gamma conjugate model.

    Prior: beta | sigma^2 ~ N(mu0, sigma^2 * Lambda0^{-1}), sigma^2 ~ IG(a0, b0).
    All tasks use a very diffuse prior so the posterior mean is close to OLS.

    Datasets are generated synthetically with known true parameters.
    Reference: Bolstad (2007) ch 14; Hoff (2009) §9.2; Lee (2012) §6.3.
    """
    # Each instance: true intercept (a), true slope (b), x values, sigma
    raw = [
        {"a": 1.0, "b": 2.0,  "x": [1,2,3,4,5,6,7,8,9,10],   "sigma": 0.5, "seed": 10},
        {"a": 3.0, "b": 0.5,  "x": [0,2,4,6,8,10,12,14,16,18,20], "sigma": 1.0, "seed": 20},
        {"a": 0.0, "b": 4.0,  "x": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15], "sigma": 2.0, "seed": 30},
        {"a": 2.0, "b": -1.0, "x": [0,1,2,3,4,5,6,7,8,9],     "sigma": 0.8, "seed": 40},
        {"a": 5.0, "b": 2.0,  "x": [1,3,5,7,9,11,13],         "sigma": 1.5, "seed": 50},
    ]
    instances = []
    for r in raw:
        rng = np.random.default_rng(r["seed"])
        x_arr = np.array(r["x"], dtype=float)
        y_arr = r["a"] + r["b"] * x_arr + rng.normal(0, r["sigma"], len(x_arr))
        instances.append({
            "x": x_arr.tolist(),
            "y": y_arr.tolist(),
            "true_a": r["a"],
            "true_b": r["b"],
        })

    tasks = []
    for i, inst in enumerate(instances, 1):
        x_arr = np.array(inst["x"])
        y_arr = np.array(inst["y"])
        n = len(x_arr)
        X = np.column_stack([np.ones(n), x_arr])
        mu0 = np.zeros(2)
        Lambda0 = 0.001 * np.eye(2)   # very diffuse prior
        res = normal_inverse_gamma_regression_update(X, y_arr, mu0, Lambda0, 1.0, 1.0)
        intercept_post = float(res["posterior_mean_beta"][0])
        slope_post     = float(res["posterior_mean_beta"][1])
        tasks.append(make_task(
            task_id=f"BAYES_REG_{i:02d}",
            tier=3, difficulty="advanced",
            structure=["applies_normal_inverse_gamma_update",
                       "states_bayesian_regression_prior",
                       "computes_B_hat_via_Sxy_over_Sxx"],
            assumptions=["states_iid", "normal_errors", "constant_variance"],
            numeric_targets={
                "intercept_post": intercept_post,
                "slope_post":     slope_post,
            },
            notes={
                "topic":       "bayesian_linear_regression",
                "model":       "y = a + b*x + eps, eps~N(0,sigma^2)",
                "prior":       "beta|sigma^2~N(0, sigma^2*1000*I), sigma^2~IG(1,1)",
                "inputs":      {"x": inst["x"], "y": [round(v, 6) for v in inst["y"]]},
                "true_params": {"a": inst["true_a"], "b": inst["true_b"]},
            },
            tol=0.1, zero=0.5,
        ))
    return tasks


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 13 — MLE vs MAP comparison (B2)
# ─────────────────────────────────────────────────────────────────────────────

def gen_mle_vs_map_tasks() -> List[Dict[str, Any]]:
    """
    Five MLE vs MAP comparison tasks for the Beta-Binomial model.

    Illustrates how the MAP estimate shrinks the MLE toward the prior mean,
    with posterior mean shrinking even further.
    Reference: Bolstad (2007) §9; Bishop (2006) §3.3.
    """
    instances = [
        {"x":  6, "n": 10, "alpha": 2, "beta": 2,
         "note": "symmetric Beta(2,2) prior"},
        {"x":  3, "n": 15, "alpha": 1, "beta": 1,
         "note": "flat prior Beta(1,1): MAP=MLE"},
        {"x": 12, "n": 20, "alpha": 3, "beta": 3,
         "note": "informative symmetric prior pulls toward 0.5"},
        {"x":  2, "n": 10, "alpha": 2, "beta": 5,
         "note": "prior biased toward low theta"},
        {"x":  8, "n": 12, "alpha": 4, "beta": 2,
         "note": "prior biased toward high theta"},
    ]
    tasks = []
    for i, inst in enumerate(instances, 1):
        res = mle_vs_map(
            "binomial",
            {"alpha": inst["alpha"], "beta": inst["beta"]},
            {"x": inst["x"], "n": inst["n"]},
        )
        tasks.append(make_task(
            task_id=f"MLE_MAP_{i:02d}",
            tier=2, difficulty="intermediate",
            structure=["computes_map_from_posterior_mode",
                       "contrasts_mle_and_map",
                       "updates_hyperparameters_correctly"],
            assumptions=["states_iid", "states_distributional_assumption"],
            numeric_targets={
                "mle":            res["mle"],
                "map":            res["map"],
                "posterior_mean": res["posterior_mean"],
                "shrinkage":      res["shrinkage"],
            },
            notes={
                "topic":  "mle_vs_map_binomial",
                "inputs": {"x": inst["x"], "n": inst["n"],
                           "alpha": inst["alpha"], "beta": inst["beta"]},
                "prior_mean": res["prior_mean"],
                "note":  inst["note"],
            },
            tol=1e-4, zero=0.05,
        ))
    return tasks


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 14 — Confidence interval vs credible interval (B3)
# ─────────────────────────────────────────────────────────────────────────────

def gen_ci_vs_credible_tasks() -> List[Dict[str, Any]]:
    """
    Five tasks comparing frequentist CIs and Bayesian credible intervals for the
    Normal mean with known variance.

    With a diffuse prior the two intervals almost coincide; with an informative
    prior the Bayesian interval is pulled toward the prior mean and narrowed.
    Reference: Bolstad (2007) ch 9, 12; Lee (2012) §2.6.2.
    """
    # (mu0, tau0_sq, sigma_sq, true_mean, n, seed, note)
    configs = [
        (0.0, 100.0, 1.0,  5.0, 20, 1, "very diffuse prior: CI ≈ credible"),
        (0.0,   0.5, 1.0,  5.0, 20, 2, "informative prior: credible pulled to 0"),
        (5.0,   0.1, 2.0,  5.0, 10, 3, "strong prior at true mean"),
        (3.0,   5.0, 1.0,  4.5, 15, 4, "moderate prior away from data"),
        (0.0, 100.0, 1.0,  0.0,  5, 5, "diffuse prior, small n"),
    ]
    tasks = []
    for i, (mu0, tau0_sq, sigma_sq, true_mean, n, seed, note) in enumerate(configs, 1):
        rng = np.random.default_rng(seed)
        data = (true_mean + rng.normal(0, sigma_sq**0.5, n)).tolist()
        res = compare_ci_vs_credible_normal(mu0, tau0_sq, sigma_sq, data, level=0.95)
        fl, fh = res["freq_ci"]
        bl, bh = res["bayes_credible"]
        tasks.append(make_task(
            task_id=f"CI_CREDIBLE_{i:02d}",
            tier=2, difficulty="intermediate",
            structure=["computes_frequentist_ci",
                       "computes_bayesian_credible"],
            assumptions=["states_distributional_assumption",
                         "constant_variance"],
            numeric_targets={
                "freq_lower":  fl,
                "freq_upper":  fh,
                "bayes_lower": bl,
                "bayes_upper": bh,
            },
            notes={
                "topic":    "ci_vs_credible_normal",
                "inputs":   {"mu0": mu0, "tau0_sq": tau0_sq,
                             "sigma_sq": sigma_sq, "n": n,
                             "data": [round(v, 6) for v in data]},
                "posterior_mean": res["posterior_mean"],
                "freq_center":    res["freq_center"],
                "note":     note,
            },
            tol=1e-3, zero=0.05,
        ))
    return tasks


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 15 — Log marginal likelihood (B1 / A2 extension)
# ─────────────────────────────────────────────────────────────────────────────

def gen_log_marginal_likelihood_tasks() -> List[Dict[str, Any]]:
    """
    Five log marginal likelihood tasks for Beta-Binomial (3) and
    Gamma-Poisson (2) conjugate models.

    The log marginal likelihood (log normalising constant) is the key quantity
    for Bayes factor computation and model comparison.
    Reference: Kass & Raftery (1995); Ghosh et al (2006) §6.3.
    """
    instances = [
        {"model": "beta_binomial",
         "alpha": 1.0, "beta": 1.0, "x": 6, "n": 10,
         "note": "uniform prior"},
        {"model": "beta_binomial",
         "alpha": 2.0, "beta": 3.0, "x": 4, "n": 12,
         "note": "informative prior"},
        {"model": "beta_binomial",
         "alpha": 0.5, "beta": 0.5, "x": 8, "n": 15,
         "note": "Jeffreys prior"},
        {"model": "gamma_poisson",
         "alpha": 2.0, "beta": 1.0, "data": [1, 2, 3, 2, 1],
         "note": "Gamma(2,1) prior, count data"},
        {"model": "gamma_poisson",
         "alpha": 3.0, "beta": 2.0, "data": [2, 4, 1, 3],
         "note": "Gamma(3,2) prior, sparse data"},
    ]
    tasks = []
    for i, inst in enumerate(instances, 1):
        if inst["model"] == "beta_binomial":
            log_ml = log_marginal_likelihood_beta_binomial(
                inst["alpha"], inst["beta"], inst["x"], inst["n"]
            )
            inp = {"model": "Beta-Binomial",
                   "alpha": inst["alpha"], "beta": inst["beta"],
                   "x": inst["x"], "n": inst["n"]}
        else:
            log_ml = log_marginal_likelihood_gamma_poisson(
                inst["alpha"], inst["beta"], inst["data"]
            )
            inp = {"model": "Gamma-Poisson",
                   "alpha": inst["alpha"], "beta": inst["beta"],
                   "data": inst["data"]}
        tasks.append(make_task(
            task_id=f"LOG_ML_{i:02d}",
            tier=3, difficulty="advanced",
            structure=["applies_beta_function_for_ml",
                       "computes_normalizing_constant"],
            assumptions=["states_iid", "states_distributional_assumption"],
            numeric_targets={"log_ml": log_ml},
            notes={
                "topic":  "log_marginal_likelihood",
                "inputs": inp,
                "note":   inst["note"],
            },
            tol=1e-4, zero=0.5,
        ))
    return tasks


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 16 — Gambler's ruin (dedicated, 3 tasks) — STEP 2
# ─────────────────────────────────────────────────────────────────────────────

def gen_gambler_tasks() -> List[Dict[str, Any]]:
    """
    Three dedicated gambler's ruin tasks (different params from MARKOV group).

    Uses gambling_ruin_probability(p, i, M) directly.
    Reference: Hoff (2009) §; Lecture 30-33.
    """
    instances = [
        {"p": 0.6, "i": 3, "M": 8,
         "note": "favourable game p=0.6"},
        {"p": 0.5, "i": 7, "M": 15,
         "note": "fair game, asymmetric starting position"},
        {"p": 0.3, "i": 2, "M": 10,
         "note": "strongly unfavourable p=0.3"},
    ]
    tasks = []
    for i, inst in enumerate(instances, 1):
        res = gambling_ruin_probability(inst["p"], inst["i"], inst["M"])
        tasks.append(make_task(
            task_id=f"GAMBLER_{i:02d}",
            tier=3, difficulty="intermediate",
            structure=["applies_gamblers_ruin_formula",
                       "handles_fair_vs_unfair_case"],
            assumptions=["absorbing_boundaries_at_0_and_M"],
            numeric_targets={
                "ruin_prob": res["ruin_prob"],
                "win_prob":  res["win_prob"],
            },
            notes={
                "topic":  "gamblers_ruin",
                "inputs": {"p": inst["p"], "i": inst["i"], "M": inst["M"]},
                "formula": ("fair: ruin_prob=(M-i)/M; "
                            "unfair: ruin_prob=((q/p)^i - (q/p)^M)/(1-(q/p)^M)"),
                "note":   inst["note"],
            },
            tol=1e-4, zero=0.05,
        ))
    return tasks


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 17 — Stationary distribution (dedicated, 3 tasks) — STEP 2
# ─────────────────────────────────────────────────────────────────────────────

def gen_stationary_tasks() -> List[Dict[str, Any]]:
    """
    Three dedicated stationary distribution tasks using fresh transition matrices.

    Uses stationary_distribution(P) directly; distinct from MARKOV group tasks.
    Reference: Lecture 31-33.
    """
    instances = [
        # 3-state symmetric-ish chain
        {
            "P": [[0.2, 0.5, 0.3],
                  [0.4, 0.2, 0.4],
                  [0.3, 0.6, 0.1]],
            "note": "3-state, non-uniform stationary distribution",
        },
        # 2-state with strong self-loops
        {
            "P": [[0.9, 0.1],
                  [0.2, 0.8]],
            "note": "2-state: pi = [2/3, 1/3]",
        },
        # 4-state, irregular
        {
            "P": [[0.5, 0.25, 0.25, 0.0],
                  [0.2, 0.4,  0.3,  0.1],
                  [0.1, 0.1,  0.6,  0.2],
                  [0.3, 0.2,  0.1,  0.4]],
            "note": "4-state ergodic chain",
        },
    ]
    tasks = []
    for idx, inst in enumerate(instances, 1):
        P = np.array(inst["P"])
        pi = stationary_distribution(P)
        k = P.shape[0]
        targets = {f"pi_{j}": float(pi[j]) for j in range(k)}
        tasks.append(make_task(
            task_id=f"STATIONARY_{idx:02d}",
            tier=3, difficulty="intermediate",
            structure=["solves_pi_P_eq_pi", "normalises_to_one",
                       "uses_eigenvalue_or_linear_system"],
            assumptions=["chain_is_irreducible", "chain_is_aperiodic"],
            numeric_targets=targets,
            notes={
                "topic":  "stationary_distribution",
                "inputs": {"P": inst["P"]},
                "note":   inst["note"],
            },
            tol=1e-4, zero=0.05,
        ))
    return tasks


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 18 — Range distribution (dedicated, 3 tasks) — STEP 2
# ─────────────────────────────────────────────────────────────────────────────

def gen_range_dist_tasks() -> List[Dict[str, Any]]:
    """
    Three dedicated Uniform[0,1] range distribution tasks.

    The range R = X_(n) - X_(1) ~ Beta(n-1, 2).
    Uses uniform_range_distribution(n) to confirm KS test.
    Reference: Lecture 26-29 order statistics.
    """
    instances = [
        {"n": 4,  "note": "R ~ Beta(3, 2) for n=4 Uniform[0,1] samples"},
        {"n": 8,  "note": "R ~ Beta(7, 2) for n=8"},
        {"n": 12, "note": "R ~ Beta(11, 2) for n=12"},
    ]
    tasks = []
    for i, inst in enumerate(instances, 1):
        res = uniform_range_distribution(inst["n"])
        tasks.append(make_task(
            task_id=f"RANGE_DIST_{i:02d}",
            tier=3, difficulty="intermediate",
            structure=["identifies_range_as_beta_distribution",
                       "states_correct_parameters_n_minus_1_and_2"],
            assumptions=["states_iid", "uniform_support_0_1"],
            numeric_targets={
                "alpha":    float(res["alpha"]),
                "beta":     float(res["beta"]),
                "verified": 1.0,
            },
            notes={
                "topic":   "uniform_range_distribution",
                "inputs":  {"n": inst["n"]},
                "formula": f"R ~ Beta({inst['n']-1}, 2)",
                "note":    inst["note"],
            },
            tol=1e-6, zero=0.5,
        ))
    return tasks


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 19 — MLE efficiency (dedicated, 3 tasks) — STEP 2
# ─────────────────────────────────────────────────────────────────────────────

def gen_mle_efficiency_tasks() -> List[Dict[str, Any]]:
    """
    Three MLE efficiency tasks using the Rao-Cramér bound.

    For regular exponential families (Binomial, Poisson, Normal) the MLE is
    efficient: its variance equals the RC lower bound 1/I_n(theta).
    Targets use analytical values (efficiency_ratio = 1.0 theoretically).
    Reference: Lecture 23-24; Ghosh et al (2006) §5.1.
    """
    instances = [
        {"dist": "binomial", "theta": 0.4, "n": 30,
         "note": "Lecture 24 Example 39: MLE=xbar, Var=theta(1-theta)/n=RC bound"},
        {"dist": "poisson",  "theta": 3.0, "n": 20,
         "note": "Poisson MLE=xbar, Var=lambda/n=RC bound"},
        {"dist": "normal",   "theta": 2.0, "n": 15,
         "note": "Normal MLE=xbar (sigma^2=1 known), Var=1/n=RC bound"},
    ]
    tasks = []
    for i, inst in enumerate(instances, 1):
        fi  = fisher_information(inst["dist"], inst["theta"], inst["n"])
        rc  = rao_cramer_bound(fi)
        tasks.append(make_task(
            task_id=f"MLE_EFFICIENCY_{i:02d}",
            tier=4, difficulty="advanced",
            structure=["states_fisher_information_formula",
                       "states_rc_bound_as_reciprocal_of_fisher_info",
                       "states_unbiasedness_assumption"],
            assumptions=["states_regularity_conditions",
                         "states_unbiasedness_assumption"],
            numeric_targets={
                "rc_bound":        rc,
                "efficiency_ratio": 1.0,
                "is_efficient":    1.0,
            },
            notes={
                "topic":    "mle_efficiency",
                "inputs":   {"dist": inst["dist"],
                             "theta": inst["theta"], "n": inst["n"]},
                "fisher_info": fi,
                "note":     inst["note"],
                "warning":  ("efficiency_ratio=1.0 is the theoretical value for "
                             "regular exponential families; simulation estimate "
                             "may differ slightly"),
            },
            tol=1e-4, zero=0.1,
        ))
    return tasks


# ─────────────────────────────────────────────────────────────────────────────
# Conceptual task builder
# ─────────────────────────────────────────────────────────────────────────────

def make_conceptual_task(
    task_id: str,
    tier: int,
    difficulty: str,
    question: str,
    rubric_keys: List[str],
    reference_answer: str,
    topic: str,
) -> Dict[str, Any]:
    """Build a conceptual (qualitative) task — no numeric targets."""
    return {
        "task_id":                    task_id,
        "tier":                       tier,
        "difficulty":                 difficulty,
        "task_type":                  "conceptual",
        "required_structure_checks":  [],
        "required_assumption_checks": [],
        "numeric_targets":            [],
        "rubric_keys":                rubric_keys,
        "question":                   question,
        "reference_answer":           reference_answer,
        "notes":                      {"topic": topic},
    }


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 20 — Conceptual tasks (STEP 3)
# ─────────────────────────────────────────────────────────────────────────────

def gen_conceptual_tasks() -> List[Dict[str, Any]]:
    """Ten conceptual reasoning tasks for qualitative LLM evaluation."""
    return [
        make_conceptual_task(
            task_id="CONCEPTUAL_01",
            tier=2, difficulty="intermediate",
            question=(
                "A researcher reports p=0.03. Does this mean the probability "
                "that the null hypothesis is true given the data is 3%? Explain."
            ),
            rubric_keys=[
                "p-value is not posterior probability",
                "requires prior on H0",
                "Bayes theorem needed",
                "posterior P(H0|data) depends on prior",
            ],
            reference_answer=(
                "No. p=P(data|H0), not P(H0|data). Converting requires a prior "
                "via Bayes theorem. P(H0|data) depends on the prior probability "
                "of H0."
            ),
            topic="p_value_vs_posterior",
        ),
        make_conceptual_task(
            task_id="CONCEPTUAL_02",
            tier=2, difficulty="intermediate",
            question=(
                "When does the Highest Posterior Density (HPD) interval differ "
                "from the equal-tail credible interval? Give an example."
            ),
            rubric_keys=[
                "HPD shortest interval containing given probability",
                "equal-tail cuts equal probability from each tail",
                "differ when posterior is asymmetric/skewed",
                "example with skewed distribution like Beta(1,5)",
            ],
            reference_answer=(
                "HPD is the shortest interval with the required probability mass. "
                "Equal-tail intervals cut equal mass from each tail. They coincide "
                "for symmetric unimodal posteriors but differ for skewed ones. "
                "Example: Beta(1,10) — HPD starts at 0, equal-tail does not."
            ),
            topic="hpd_vs_equal_tail",
        ),
        make_conceptual_task(
            task_id="CONCEPTUAL_03",
            tier=3, difficulty="intermediate",
            question=(
                "A study reports a Bayes factor BF10=15 in favor of H1. "
                "How do you interpret this? How does it differ from a p-value?"
            ),
            rubric_keys=[
                "BF is ratio of marginal likelihoods",
                "BF=15 is strong evidence for H1 (Kass-Raftery scale)",
                "p-value is one-sided tail probability under H0",
                "BF incorporates prior predictive comparison",
            ],
            reference_answer=(
                "BF10=15 means the data are 15 times more likely under H1 than H0. "
                "On the Kass-Raftery scale this is strong evidence for H1. "
                "Unlike a p-value, the Bayes factor compares predictive performance "
                "of two models and does not depend on stopping rules."
            ),
            topic="bayes_factor_interpretation",
        ),
        make_conceptual_task(
            task_id="CONCEPTUAL_04",
            tier=3, difficulty="advanced",
            question=(
                "What property makes Jeffreys prior special compared to a "
                "uniform prior? Demonstrate with the Binomial model."
            ),
            rubric_keys=[
                "invariant under reparametrization",
                "uniform on theta != uniform on log-odds",
                "Jeffreys = Beta(0.5,0.5) for Binomial",
                "sqrt of Fisher information",
            ],
            reference_answer=(
                "Jeffreys prior p(theta) ∝ sqrt(I(theta)) is invariant under "
                "reparametrisation: applying it to any monotone transform of theta "
                "gives the same prior. For Binomial: I(theta)=1/(theta(1-theta)), "
                "so p(theta) ∝ theta^{-1/2}(1-theta)^{-1/2} = Beta(0.5, 0.5). "
                "A uniform prior on theta is not uniform on log-odds."
            ),
            topic="jeffreys_prior_invariance",
        ),
        make_conceptual_task(
            task_id="CONCEPTUAL_05",
            tier=2, difficulty="intermediate",
            question=(
                "A 95% Bayesian credible interval is [0.3, 0.7] for a proportion "
                "theta. What is the correct interpretation? How does it differ "
                "from a 95% frequentist confidence interval?"
            ),
            rubric_keys=[
                "credible: P(theta in [0.3,0.7]|data)=0.95",
                "confidence: 95% of such intervals contain true theta",
                "credible interval makes direct probability statement about parameter",
                "confidence interval is statement about procedure",
            ],
            reference_answer=(
                "Credible interval: given the prior and data, P(theta in [0.3,0.7]) "
                "= 0.95. This is a direct probability statement about the parameter. "
                "Frequentist CI: if we repeated the experiment, 95% of CIs computed "
                "this way would contain the true theta — a statement about the "
                "procedure, not about this specific interval."
            ),
            topic="credible_vs_confidence_interval",
        ),
        make_conceptual_task(
            task_id="CONCEPTUAL_06",
            tier=3, difficulty="intermediate",
            question=(
                "With n=5 observations, a Beta(10,10) prior and Beta(1,1) prior "
                "give very different posteriors. With n=500, they are nearly "
                "identical. Explain why."
            ),
            rubric_keys=[
                "likelihood dominates prior with large n",
                "posterior proportional to prior times likelihood",
                "data overwhelms prior asymptotically",
                "Bernstein-von Mises: posterior concentrates around MLE",
            ],
            reference_answer=(
                "The posterior is proportional to prior × likelihood. For small n "
                "the prior contributes substantially; for large n the likelihood "
                "dominates. The Bernstein-von Mises theorem guarantees that as "
                "n→∞ the posterior concentrates around the MLE regardless of the "
                "prior (under regularity conditions)."
            ),
            topic="prior_influence_large_n",
        ),
        make_conceptual_task(
            task_id="CONCEPTUAL_07",
            tier=2, difficulty="basic",
            question=(
                "For a Binomial model with x=1, n=2 and Beta(2,2) prior, "
                "compute and compare MLE, MAP, and posterior mean. "
                "Which should you use and when?"
            ),
            rubric_keys=[
                "MLE=0.5 (x/n)",
                "MAP=(x+alpha-1)/(n+alpha+beta-2)=2/4=0.5",
                "posterior mean=(x+alpha)/(n+alpha+beta)=3/6=0.5",
                "MAP minimizes 0-1 loss, posterior mean minimizes MSE",
            ],
            reference_answer=(
                "MLE = x/n = 0.5. MAP = (1+2-1)/(2+2+2-2) = 2/4 = 0.5. "
                "Posterior mean = (1+2)/(2+2+2) = 3/6 = 0.5. For this symmetric "
                "case all three coincide. Posterior mean minimises MSE (quadratic "
                "loss); MAP minimises 0-1 loss; MLE ignores the prior."
            ),
            topic="mle_map_posterior_mean",
        ),
        make_conceptual_task(
            task_id="CONCEPTUAL_08",
            tier=3, difficulty="advanced",
            question=(
                "What does it mean for observations to be exchangeable? "
                "Why is this important in Bayesian statistics?"
            ),
            rubric_keys=[
                "exchangeable: joint dist invariant to permutation",
                "weaker than iid",
                "de Finetti: exchangeable sequence = mixture of iid",
                "justifies use of prior distribution",
            ],
            reference_answer=(
                "A sequence X1,...,Xn is exchangeable if its joint distribution "
                "is invariant under permutation of indices. This is weaker than "
                "i.i.d. De Finetti's theorem: any exchangeable sequence can be "
                "represented as a mixture of i.i.d. distributions. This provides "
                "the theoretical justification for the Bayesian model where "
                "observations are conditionally i.i.d. given theta, with theta "
                "having a prior distribution."
            ),
            topic="exchangeability_de_finetti",
        ),
        make_conceptual_task(
            task_id="CONCEPTUAL_09",
            tier=2, difficulty="intermediate",
            question=(
                "What are the advantages of using conjugate priors? "
                "What situations make them inappropriate?"
            ),
            rubric_keys=[
                "closed-form posterior — no numerical integration",
                "posterior in same family as prior",
                "limitation: may not reflect true prior beliefs",
                "inappropriate when prior is multimodal or has sharp constraints",
            ],
            reference_answer=(
                "Advantages: the posterior is in the same parametric family as "
                "the prior, giving a closed-form update with no numerical "
                "integration. Easy to interpret; hyperparameters have "
                "pseudo-count interpretations. Limitations: the conjugate family "
                "may not represent genuine prior beliefs (e.g. cannot express "
                "bimodal prior), and forces a specific distributional shape. "
                "Better alternatives: MCMC or variational methods for complex "
                "priors."
            ),
            topic="conjugate_prior_advantages",
        ),
        make_conceptual_task(
            task_id="CONCEPTUAL_10",
            tier=3, difficulty="intermediate",
            question=(
                "A posterior predictive check yields a Bayesian p-value of 0.02. "
                "What does this indicate about the model? What should the analyst do?"
            ),
            rubric_keys=[
                "p-value near 0 or 1 indicates model misfit",
                "0.02 means observed statistic is extreme under model",
                "model may be misspecified",
                "consider alternative models or relaxed assumptions",
            ],
            reference_answer=(
                "A Bayesian p-value of 0.02 means the observed test statistic "
                "falls in the lower 2% of the posterior predictive distribution — "
                "the data are surprisingly extreme under the fitted model, "
                "indicating potential model misspecification. The analyst should "
                "examine which aspect of the data the model fails to capture, "
                "consider a more flexible likelihood, or relax distributional "
                "assumptions."
            ),
            topic="ppc_interpretation",
        ),
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    out_path = "data/raw_data/benchmark_v1/tasks.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    generators = [
        ("original conjugate tasks",         gen_original_tasks),
        ("discrete_posterior_median",         gen_discrete_posterior_median_tasks),
        ("uniform_mle",                       gen_uniform_mle_tasks),
        ("binomial_flat_prior",               gen_binomial_flat_prior_tasks),
        ("minimax_comparison",                gen_minimax_comparison_tasks),
        ("discrete_bayes_risk",               gen_discrete_bayes_risk_tasks),
        ("bias_variance_decomp",              gen_bias_variance_decomp_tasks),
        ("fisher_information",                gen_fisher_information_tasks),
        ("rao_cramer_bound",                  gen_rao_cramer_bound_tasks),
        ("optimal_scaled_estimator",          gen_optimal_scaled_estimator_tasks),
        ("mse_comparison",                    gen_mse_comparison_tasks),
        ("markov_chains",                     gen_markov_tasks),
        ("order_statistics",                  gen_order_stat_tasks),
        ("ols_regression",                    gen_regression_tasks),
        ("box_muller_sampling",               gen_sampling_tasks),
        # Priority A/B new generators
        ("hpd_credible_interval",             gen_hpd_interval_tasks),
        ("bayes_factor",                      gen_bayes_factor_tasks),
        ("jeffreys_prior",                    gen_jeffreys_prior_tasks),
        ("posterior_predictive_check",        gen_ppc_tasks),
        ("bayesian_regression",               gen_bayesian_regression_tasks),
        ("mle_vs_map",                        gen_mle_vs_map_tasks),
        ("ci_vs_credible",                    gen_ci_vs_credible_tasks),
        ("log_marginal_likelihood",           gen_log_marginal_likelihood_tasks),
        # Step 2 — dedicated gap-filling generators (3 tasks each)
        ("gamblers_ruin_dedicated",           gen_gambler_tasks),
        ("stationary_distribution_dedicated", gen_stationary_tasks),
        ("range_distribution_dedicated",      gen_range_dist_tasks),
        ("mle_efficiency",                    gen_mle_efficiency_tasks),
        # Step 3 — conceptual tasks
        ("conceptual",                        gen_conceptual_tasks),
    ]

    all_tasks: List[Dict[str, Any]] = []
    summary_rows = []

    for label, gen_fn in generators:
        batch = gen_fn()
        all_tasks.extend(batch)
        ids = [t["task_id"] for t in batch]
        summary_rows.append((label, len(batch), ids))

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_tasks, f, ensure_ascii=False, indent=2)

    # ── Summary ──────────────────────────────────────────────────────────────
    print(f"\n{'Task type':<32} {'Count':>5}   IDs")
    print("─" * 80)
    for label, count, ids in summary_rows:
        id_str = ", ".join(ids)
        print(f"{label:<32} {count:>5}   {id_str}")
    print("─" * 80)
    print(f"{'TOTAL':<32} {len(all_tasks):>5}")
    print(f"\nWrote {len(all_tasks)} tasks → {out_path}")


if __name__ == "__main__":
    main()
