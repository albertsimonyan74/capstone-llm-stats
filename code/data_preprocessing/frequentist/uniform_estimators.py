# baseline/frequentist/uniform_estimators.py
"""
Analytical ground-truth implementations for estimator comparison under the
Uniform(0, theta) model, following the Lecture 25 MSE analysis framework.

All variance and MSE formulas are closed-form (analytical), derived from the
order-statistic distribution of U(0, theta). Sample-based quantities are only
used in compare_mse, which accepts simulation arrays.
"""
from __future__ import annotations

from typing import Any, Dict

import numpy as np


def _require_positive(x: float, name: str) -> None:
    if x <= 0:
        raise ValueError(f"{name} must be > 0, got {x}")


def _require_nonempty(data: list, name: str = "data") -> None:
    if not data:
        raise ValueError(f"{name} must be non-empty")


# ─────────────────────────────────────────────────────────────────────────────

def unbiased_estimator_uniform(data: list[float]) -> Dict[str, Any]:
    """
    Unbiased estimator d1 = 2 * mean(X) for Uniform(0, theta).

    Lecture 25 example: d1 is derived by noting that E[X_i] = theta/2,
    so E[2 * mean(X)] = theta — making d1 unbiased for all n and theta.
    Its variance is Var(d1) = 4 * Var(mean(X)) = 4 * (theta^2/12) / n
    = theta^2 / (3n), which grows relative to the competing MLE d2 as n
    increases, motivating the search for a lower-MSE alternative.

    Note: the "variance" returned here is the analytical formula theta^2/(3n),
    which requires knowing theta_true. It is NOT the sample variance of d1.

    Args:
        data: Observed sample from Uniform(0, theta). Must be non-empty
              and all values must be > 0.

    Returns:
        dict with keys:
          estimator  – "d1"
          value      – 2 * mean(data)  (the point estimate)
          variance   – theta^2 / (3n)  expressed symbolically as a callable
                       and numerically as a function of the estimate itself:
                       uses d1/2 as a plug-in estimate of theta when theta
                       is unknown, but see mle_uniform_analytics for the
                       version that takes theta_true explicitly.

    Note on "variance" key:
        Because the true theta is unknown in practice, we return the formula
        string and the plug-in numerical value using d1 as the theta estimate.
        For evaluation against a known theta_true, pass theta_true explicitly
        to optimal_scaled_estimator_uniform which contains mse_d1.
    """
    _require_nonempty(data)
    if any(x <= 0 for x in data):
        raise ValueError("all data values must be > 0 for Uniform(0, theta)")

    n = len(data)
    d1 = 2.0 * float(sum(data)) / n
    theta_plugin = d1  # plug-in estimate of theta for the variance formula

    return {
        "estimator": "d1",
        "value": d1,
        "variance_formula": "theta^2 / (3 * n)",
        "variance_plugin": theta_plugin ** 2 / (3 * n),  # plug-in: theta ≈ d1
        "n": n,
    }


def mle_uniform_analytics(data: list[float], theta_true: float) -> Dict[str, Any]:
    """
    Analytical properties of d2 = max(X_1,...,X_n), the MLE for Uniform(0, theta).

    Lecture 25 example: d2 is the MLE but is biased downward. Its distribution
    is that of the n-th order statistic of U(0, theta):
      f_{X_(n)}(x) = n * x^{n-1} / theta^n   for x in (0, theta)

    From this density:
      E[d2]   = n / (n+1) * theta      →  bias = -theta/(n+1)
      Var(d2) = n * theta^2 / ((n+1)^2 * (n+2))
      MSE(d2) = Var(d2) + Bias^2
              = n*theta^2/((n+1)^2*(n+2)) + theta^2/(n+1)^2
              = 2 * theta^2 / ((n+1) * (n+2))

    The MSE of d2 is smaller than that of d1 for n >= 2, which motivates
    the further improvement via the optimal scaled estimator dc in Lecture 25.

    Args:
        data:       Observed sample from Uniform(0, theta). Non-empty, all > 0.
        theta_true: True value of theta (known, for evaluation purposes).

    Returns:
        dict with keys:
          estimator  – "d2"
          value      – max(data), the MLE point estimate
          n          – sample size
          e_d2       – n/(n+1) * theta_true  (analytical expectation)
          bias       – e_d2 - theta_true = -theta_true/(n+1)
          var_d2     – n * theta_true^2 / ((n+1)^2 * (n+2))
          mse_d2     – 2 * theta_true^2 / ((n+1) * (n+2))
          theta_true – echoed back for traceability
    """
    _require_nonempty(data)
    if any(x <= 0 for x in data):
        raise ValueError("all data values must be > 0 for Uniform(0, theta)")
    _require_positive(theta_true, "theta_true")

    n = len(data)
    d2 = float(max(data))
    theta = theta_true

    e_d2 = n / (n + 1) * theta
    bias = e_d2 - theta                                      # = -theta/(n+1)
    var_d2 = n * theta ** 2 / ((n + 1) ** 2 * (n + 2))
    mse_d2 = 2 * theta ** 2 / ((n + 1) * (n + 2))

    return {
        "estimator": "d2",
        "value": d2,
        "n": n,
        "e_d2": e_d2,
        "bias": bias,
        "var_d2": var_d2,
        "mse_d2": mse_d2,
        "theta_true": theta,
    }


def optimal_scaled_estimator_uniform(n: int, theta_true: float) -> Dict[str, Any]:
    """
    Optimal scaled estimator dc = c * max(X_i) for Uniform(0, theta).

    Lecture 25 example: the key result of the lecture. We consider the family
    of estimators d_c = c * max(X_i) and minimise MSE(d_c) over c:

      MSE(d_c) = E[(c * X_(n) - theta)^2]
               = c^2 * E[X_(n)^2] - 2c * theta * E[X_(n)] + theta^2

    Using E[X_(n)] = n*theta/(n+1) and E[X_(n)^2] = n*theta^2/((n+1)(n+2)/... ),
    differentiating and setting to zero gives:

      c_opt = (n+2) / (n+1)

    Substituting back:
      MSE(d_c_opt) = theta^2 / (n+1)^2

    Comparison:
      MSE(d1) = theta^2 / (3n)
      MSE(d2) = 2*theta^2 / ((n+1)*(n+2))
      MSE(dc) = theta^2 / (n+1)^2

    dc dominates both d1 and d2 for all n >= 1.

    Args:
        n:          Sample size. Must be >= 1.
        theta_true: True value of theta (known, for evaluation purposes).

    Returns:
        dict with keys:
          c_opt          – (n+2)/(n+1), the MSE-minimising scale factor
          mse_opt        – theta^2 / (n+1)^2, MSE of dc at c_opt
          mse_d1         – theta^2 / (3*n), MSE of the unbiased estimator d1
          mse_d2         – 2*theta^2 / ((n+1)*(n+2)), MSE of the MLE d2
          best_estimator – "dc" (always lowest MSE among d1, d2, dc)
          n              – echoed back
          theta_true     – echoed back
    """
    if not isinstance(n, (int, np.integer)) or n < 1:
        raise ValueError(f"n must be an integer >= 1, got {n}")
    _require_positive(theta_true, "theta_true")

    theta = theta_true
    c_opt = (n + 2) / (n + 1)
    mse_opt = theta ** 2 / (n + 1) ** 2
    mse_d1 = theta ** 2 / (3 * n)
    mse_d2 = 2 * theta ** 2 / ((n + 1) * (n + 2))

    return {
        "c_opt": c_opt,
        "mse_opt": mse_opt,
        "mse_d1": mse_d1,
        "mse_d2": mse_d2,
        "best_estimator": "dc",
        "n": n,
        "theta_true": theta,
    }


def bias_variance_decomp_uniform_max(n: int, theta: float) -> Dict[str, float]:
    """
    Closed-form bias-variance decomposition for d2 = max(X_i) under Uniform(0, theta).

    Extracted from build_tasks_bayesian.py:293-295 so the perturbation generator
    can recompute ground truth without duplicating the formulas.

    Returns dict with keys: bias, var_d2, mse_d2.
    """
    if not isinstance(n, (int, np.integer)) or n < 1:
        raise ValueError(f"n must be an integer >= 1, got {n}")
    _require_positive(theta, "theta")
    bias = -theta / (n + 1)
    var_d2 = n * theta ** 2 / ((n + 1) ** 2 * (n + 2))
    mse_d2 = 2 * theta ** 2 / ((n + 1) * (n + 2))
    return {"bias": float(bias), "var_d2": float(var_d2), "mse_d2": float(mse_d2)}


def compare_mse(
    theta_true: float,
    estimators: Dict[str, np.ndarray],
) -> Dict[str, Any]:
    """
    Sample-based MSE comparison across multiple estimators at a fixed theta.

    For each estimator (represented as an array of repeated draws), computes
    bias, variance, and MSE using the bias-variance decomposition:
      MSE = Bias^2 + Variance

    Results are sorted by MSE ascending and a "ranking" list is added.

    Lecture 25 example: used to empirically verify the ordering
    MSE(dc) < MSE(d2) < MSE(d1) for Uniform(0, theta), as derived
    analytically via the optimal scaled estimator.

    Args:
        theta_true:  True value of the parameter theta.
        estimators:  Dict mapping estimator name (str) to a 1-D np.ndarray
                     of repeated estimates. Each array must be non-empty.

    Returns:
        Dict with one entry per estimator name, each containing:
          bias      – E[T] - theta  (signed)
          variance  – Var(T) = E[(T - E[T])^2]
          mse       – E[(T - theta)^2]
        Plus a top-level "ranking" key: list of estimator names sorted by
        MSE ascending.
    """
    _require_positive(theta_true, "theta_true")
    if not estimators:
        raise ValueError("estimators dict must be non-empty")

    results: Dict[str, Any] = {}

    for name, arr in estimators.items():
        ev = np.asarray(arr).astype(float).ravel()
        if ev.size == 0:
            raise ValueError(f"estimator '{name}' has an empty array")
        mean_t = float(np.mean(ev))
        bias = mean_t - theta_true
        variance = float(np.var(ev))
        mse = float(np.mean((ev - theta_true) ** 2))
        results[name] = {"bias": bias, "variance": variance, "mse": mse}

    ranking = sorted(results.keys(), key=lambda k: results[k]["mse"])
    results["ranking"] = ranking

    return results
