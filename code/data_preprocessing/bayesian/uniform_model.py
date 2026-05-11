# baseline/bayesian/uniform_model.py
"""
Ground-truth implementations for the Uniform(0, theta) model.

Covers the MLE (max statistic) and the posterior under a Uniform prior,
as introduced in Lectures 21 and 24.
"""
from __future__ import annotations
from typing import Any, Dict, List

from data_preprocessing.bayesian.utils import require_positive


def uniform_mle(data: List[float]) -> float:
    """
    MLE for Uniform(0, theta): theta_hat = max(X_1, ..., X_n).

    The likelihood L(theta | x_1,...,x_n) = 1/theta^n * I(theta >= max(x))
    is maximised at the smallest admissible theta, which is max(x).

    Lecture 24 example: illustrates that the MLE of theta for U(0,theta)
    is the order statistic X_(n), not the sample mean. Also used as the
    starting estimator for the MSE analysis in Lecture 25.

    Args:
        data: Non-empty list of observed values. All must be > 0.

    Returns:
        MLE estimate of theta (= max of data).
    """
    if not data:
        raise ValueError("data must be non-empty")
    if any(x <= 0 for x in data):
        raise ValueError("all data values must be > 0 for Uniform(0, theta)")
    return float(max(data))


def uniform_posterior_uniform_prior(
    data: List[float],
    theta_lo: float,
    theta_hi: float,
) -> Dict[str, Any]:
    """
    Posterior for theta given data from Uniform(0, theta) and a Uniform(theta_lo, theta_hi) prior.

    Likelihood:  L(theta | x) = theta^{-n}  for theta >= max(x), else 0.
    Prior:       pi(theta) proportional to 1  on (theta_lo, theta_hi).
    Posterior:   pi(theta | x) proportional to theta^{-n}
                 on (max(x_max, theta_lo), theta_hi), unnormalised.

    The posterior is a Pareto-like distribution truncated to
    (effective_lo, theta_hi), where effective_lo = max(max(data), theta_lo).

    Lecture 21 / 24 example: demonstrates that a Uniform prior on theta
    combined with a Uniform(0,theta) likelihood yields a proper posterior
    only when theta_hi > max(data), with posterior mass concentrated near
    the MLE max(data).

    Args:
        data:      Observed sample from Uniform(0, theta).
        theta_lo:  Lower bound of the Uniform prior on theta.
        theta_hi:  Upper bound of the Uniform prior on theta.

    Returns:
        dict with keys:
          n             – sample size
          x_max         – max(data), the MLE and effective lower bound
          effective_lo  – max(x_max, theta_lo); posterior support starts here
          theta_hi      – upper bound of posterior support
          posterior_form – description of the posterior family
          posterior_mean – E[theta | data] under this posterior
          posterior_mode – mode of the posterior (= effective_lo, since
                           theta^{-n} is decreasing)
    """
    if not data:
        raise ValueError("data must be non-empty")
    if any(x <= 0 for x in data):
        raise ValueError("all data values must be > 0 for Uniform(0, theta)")
    if theta_lo < 0:
        raise ValueError(f"theta_lo must be >= 0, got {theta_lo}")
    require_positive(theta_hi, "theta_hi")
    if theta_hi <= theta_lo:
        raise ValueError(f"theta_hi must be > theta_lo, got {theta_hi} <= {theta_lo}")

    n = len(data)
    x_max = float(max(data))
    effective_lo = max(x_max, theta_lo)

    if effective_lo >= theta_hi:
        raise ValueError(
            f"max(data)={x_max} >= theta_hi={theta_hi}: posterior has zero mass. "
            "Increase theta_hi or check data."
        )

    # Posterior: pi(theta|x) ∝ theta^{-n} on (effective_lo, theta_hi)
    # Normalising constant: ∫_{a}^{b} theta^{-n} dtheta
    #   = [theta^{1-n} / (1-n)]_{a}^{b}  for n != 1
    #   = ln(b/a)                          for n == 1
    a, b = effective_lo, theta_hi

    if n == 1:
        # ∫_a^b theta^{-1} dtheta = ln(b/a)
        import math
        norm = math.log(b / a)
        # E[theta] = ∫_a^b theta * theta^{-1} / norm dtheta = (b-a)/norm
        posterior_mean = (b - a) / norm
    else:
        # ∫_a^b theta^{-n} dtheta = (b^{1-n} - a^{1-n}) / (1-n)
        norm = (b ** (1 - n) - a ** (1 - n)) / (1 - n)
        # E[theta] = ∫_a^b theta^{1-n} dtheta / norm
        #          = (b^{2-n} - a^{2-n}) / ((2-n) * norm)  for n != 2
        if n == 2:
            import math
            e_num = math.log(b / a)
        else:
            e_num = (b ** (2 - n) - a ** (2 - n)) / (2 - n)
        posterior_mean = e_num / norm

    return {
        "n": n,
        "x_max": x_max,
        "effective_lo": effective_lo,
        "theta_hi": theta_hi,
        "posterior_form": f"proportional to theta^(-{n}) on ({effective_lo}, {theta_hi})",
        "posterior_mean": float(posterior_mean),
        "posterior_mode": float(effective_lo),  # theta^{-n} is decreasing, so mode is at left boundary
    }
