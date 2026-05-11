# baseline/bayesian/bayes_estimators.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Optional, Tuple, List
import numpy as np
from scipy import stats

Loss = Literal["quadratic", "absolute", "0-1"]

@dataclass(frozen=True)
class BayesEstimator:
    loss: Loss
    estimator: str
    value: float
    notes: str = ""

# ---- Generic helpers (using distribution objects) ----

def bayes_estimator_from_beta(alpha: float, beta: float, loss: Loss) -> BayesEstimator:
    if loss == "quadratic":
        return BayesEstimator(loss, "posterior_mean", float(alpha / (alpha + beta)))
    if loss == "absolute":
        # exact numeric median (no closed-form generally)
        return BayesEstimator(loss, "posterior_median", float(stats.beta.ppf(0.5, alpha, beta)), "computed via quantile")
    if loss == "0-1":
        # mode exists if alpha,beta > 1
        if alpha <= 1 or beta <= 1:
            return BayesEstimator(loss, "posterior_mode_undefined", float("nan"), "mode undefined unless alpha>1 and beta>1")
        return BayesEstimator(loss, "posterior_mode", float((alpha - 1) / (alpha + beta - 2)))
    raise ValueError("loss must be one of: quadratic, absolute, 0-1")

def bayes_estimator_from_gamma_shape_rate(alpha: float, rate: float, loss: Loss) -> BayesEstimator:
    if loss == "quadratic":
        return BayesEstimator(loss, "posterior_mean", float(alpha / rate))
    if loss == "absolute":
        return BayesEstimator(loss, "posterior_median", float(stats.gamma.ppf(0.5, a=alpha, scale=1.0/rate)), "computed via quantile")
    if loss == "0-1":
        if alpha <= 1:
            return BayesEstimator(loss, "posterior_mode_undefined", float("nan"), "mode undefined unless alpha>1")
        return BayesEstimator(loss, "posterior_mode", float((alpha - 1) / rate))
    raise ValueError("loss must be one of: quadratic, absolute, 0-1")

def bayes_estimator_from_normal(mu: float, var: float, loss: Loss) -> BayesEstimator:
    # For Normal, mean=median=mode=mu
    if loss in ("quadratic", "absolute", "0-1"):
        return BayesEstimator(loss, "mu", float(mu))
    raise ValueError("loss must be one of: quadratic, absolute, 0-1")

def bayes_estimator_from_student_t(loc: float, scale: float, df: float, loss: Loss) -> BayesEstimator:
    # For symmetric unimodal distributions: median=mode=loc; mean exists if df>1
    if loss == "absolute":
        return BayesEstimator(loss, "posterior_median", float(loc))
    if loss == "0-1":
        return BayesEstimator(loss, "posterior_mode", float(loc))
    if loss == "quadratic":
        if df <= 1:
            return BayesEstimator(loss, "posterior_mean_undefined", float("nan"), "mean undefined for df<=1")
        return BayesEstimator(loss, "posterior_mean", float(loc))
    raise ValueError("loss must be one of: quadratic, absolute, 0-1")


def beta_median_approx(alpha: float, beta: float) -> BayesEstimator:
    """
    Lecture approximation for the median of a Beta(alpha, beta) distribution:

        median ≈ (alpha - 1/3) / (alpha + beta - 2/3)

    This is a closed-form approximation introduced in the course lectures as an
    alternative to the exact numeric median (stats.beta.ppf(0.5, alpha, beta)).
    It is accurate when both alpha and beta are greater than 1, and improves as
    alpha and beta grow. It is NOT the exact median — use stats.beta.ppf for
    ground-truth computations.

    Returns NaN with a note if alpha <= 1 or beta <= 1, where the approximation
    is not reliable (the Beta distribution becomes J-shaped or boundary-heavy).
    """
    if alpha <= 1 or beta <= 1:
        return BayesEstimator(
            loss="absolute",
            estimator="beta_median_approx_undefined",
            value=float("nan"),
            notes="approximation requires alpha > 1 and beta > 1",
        )
    value = (alpha - 1 / 3) / (alpha + beta - 2 / 3)
    return BayesEstimator(
        loss="absolute",
        estimator="beta_median_approx",
        value=float(value),
        notes="lecture approximation: (alpha-1/3)/(alpha+beta-2/3); not exact",
    )


def discrete_posterior_median(values: List[float], probs: List[float]) -> float:
    """
    Compute the median of a discrete posterior distribution.

    Finds the smallest value k in `values` such that the cumulative probability
    P(X <= k) >= 0.5. This is the exact discrete median, as opposed to continuous
    quantile approximations used for Beta/Gamma posteriors.

    Lecture 21 example: used when the posterior is a discrete PMF (e.g., a
    finite grid of theta values with associated posterior weights), where
    stats.X.ppf(0.5) does not apply.

    Args:
        values: Ordered support points of the discrete distribution.
        probs:  Probability mass at each support point. Must sum to 1 (within
                tolerance) and each entry must be >= 0.

    Returns:
        The discrete posterior median.
    """
    if len(values) == 0 or len(probs) == 0:
        raise ValueError("values and probs must be non-empty")
    if len(values) != len(probs):
        raise ValueError("values and probs must have the same length")
    if any(p < 0 for p in probs):
        raise ValueError("all probs must be >= 0")
    total = sum(probs)
    if abs(total - 1.0) > 1e-6:
        raise ValueError(f"probs must sum to 1, got {total:.6f}")

    cumulative = 0.0
    for v, p in zip(values, probs):
        cumulative += p
        if cumulative >= 0.5:
            return float(v)

    return float(values[-1])  # guard for floating-point edge at the tail


def asymmetric_linear_bayes_estimator(
    posterior_samples: np.ndarray,
    c1: float,
    c2: float,
) -> BayesEstimator:
    """
    Bayes estimator under asymmetric linear (linex-style) loss:

        L(theta, delta) = c1 * (theta - delta)  if theta > delta  (underestimate)
                        = c2 * (delta - theta)  if delta > theta  (overestimate)

    The Bayes estimator minimizing expected loss is the c1/(c1+c2) quantile
    of the posterior distribution.

    Args:
        posterior_samples: 1-D array of posterior draws for the parameter.
        c1: Cost per unit of underestimating (theta > delta). Must be > 0.
        c2: Cost per unit of overestimating (delta > theta). Must be > 0.

    Returns:
        BayesEstimator with the optimal quantile value and the quantile level
        recorded in the notes field.
    """
    samples = np.asarray(posterior_samples).astype(float)
    if samples.size == 0:
        raise ValueError("posterior_samples cannot be empty")
    if c1 <= 0:
        raise ValueError(f"c1 must be > 0, got {c1}")
    if c2 <= 0:
        raise ValueError(f"c2 must be > 0, got {c2}")

    q = c1 / (c1 + c2)
    value = float(np.quantile(samples, q))
    return BayesEstimator(
        loss="asymmetric_linear",
        estimator=f"quantile_{q:.4f}",
        value=value,
        notes=f"c1={c1}, c2={c2}, quantile level={q:.4f}",
    )