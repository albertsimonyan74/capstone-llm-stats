# baseline/frequentist/order_statistics.py
"""
Order statistics for the Uniform[0,1] distribution.

Implements density, CDF, and distributional results for order statistics
from Lectures 26–29 of the course.

Cross-references:
  - max_order_statistic_cdf for Uniform(0,theta) gives the CDF of the
    MLE estimator d2 = max(X_i) from uniform_estimators.py.
  - range = max(X_i) - min(X_i) = d2 - X_(1) (see uniform_range_distribution).
"""
from __future__ import annotations

import math
from typing import Any, Dict, Optional

import numpy as np
from scipy import integrate as _integrate
from scipy.stats import beta as _beta_dist, expon as _expon_dist, norm as _norm_dist, ks_2samp

# Supported non-uniform distributions for order statistics
_SUPPORTED_DISTS = {"uniform", "exponential", "normal"}


# ── Helpers: CDF and PDF by distribution ─────────────────────────────────────

def _uniform_cdf(x: float) -> float:
    """CDF of Uniform[0,1]: F(x) = clamp(x, 0, 1)."""
    return float(min(max(x, 0.0), 1.0))


def _uniform_pdf(x: float) -> float:
    """PDF of Uniform[0,1]: f(x) = 1 if 0 <= x <= 1 else 0."""
    return 1.0 if 0.0 <= x <= 1.0 else 0.0


def _get_cdf_pdf(dist: str, params: Optional[Dict] = None):
    """Return (cdf, pdf) callables for the given distribution.

    Supported distributions:
      "uniform"     — Uniform[0,1]; params ignored
      "exponential" — Exp(rate); params = {"rate": float, default 1.0}
      "normal"      — Normal(mu, sigma); params = {"mu": float, "sigma": float, defaults 0,1}
    """
    params = params or {}
    if dist == "uniform":
        return _uniform_cdf, _uniform_pdf
    if dist == "exponential":
        rate = float(params.get("rate", 1.0))
        if rate <= 0:
            raise ValueError(f"rate must be > 0 for exponential, got {rate}")
        # Exp(rate): CDF = 1 - exp(-rate*x), PDF = rate*exp(-rate*x), support x >= 0
        def cdf(x: float) -> float:
            return float(_expon_dist.cdf(x, scale=1.0 / rate))
        def pdf(x: float) -> float:
            return float(_expon_dist.pdf(x, scale=1.0 / rate))
        return cdf, pdf
    if dist == "normal":
        mu = float(params.get("mu", 0.0))
        sigma = float(params.get("sigma", 1.0))
        if sigma <= 0:
            raise ValueError(f"sigma must be > 0 for normal, got {sigma}")
        def cdf(x: float) -> float:  # type: ignore[misc]
            return float(_norm_dist.cdf(x, loc=mu, scale=sigma))
        def pdf(x: float) -> float:  # type: ignore[misc]
            return float(_norm_dist.pdf(x, loc=mu, scale=sigma))
        return cdf, pdf
    raise NotImplementedError(
        f"order_statistics: dist='{dist}' is not supported. "
        f"Choose from: {sorted(_SUPPORTED_DISTS)}"
    )


# ── Concept 16 — k-th order statistic density ────────────────────────────────

def order_statistic_pdf(
    y: float,
    k: int,
    n: int,
    dist: str = "uniform",
    params: Optional[Dict] = None,
) -> float:
    """
    PDF of the k-th order statistic X_(k) from a sample of size n.

    General formula for i.i.d. draws from F with density f:
      g_(k)(y) = n! / [(k-1)! (n-k)!] * F(y)^(k-1) * (1-F(y))^(n-k) * f(y)

    For Uniform[0,1] this simplifies to Beta(k, n-k+1).pdf(y).

    Args:
        y:      Evaluation point.
        k:      Order (1 = minimum, n = maximum). Must satisfy 1 <= k <= n.
        n:      Sample size. Must be >= 1.
        dist:   Distribution family: "uniform", "exponential", or "normal".
        params: Optional distribution parameters (e.g. {"rate": 2.0} for exponential).

    Returns:
        g_(k)(y) — the PDF of the k-th order statistic at y.
    """
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    if not (1 <= k <= n):
        raise ValueError(f"k must be in [1, n], got k={k}, n={n}")

    if dist == "uniform":
        if not (0.0 <= y <= 1.0):
            return 0.0
        return float(_beta_dist.pdf(y, a=k, b=n - k + 1))

    cdf, pdf = _get_cdf_pdf(dist, params)
    Fy = cdf(y)
    fy = pdf(y)
    # n! / [(k-1)! (n-k)!] = n * C(n-1, k-1)
    coeff = math.factorial(n) / (math.factorial(k - 1) * math.factorial(n - k))
    return float(coeff * (Fy ** (k - 1)) * ((1.0 - Fy) ** (n - k)) * fy)


# ── Concept 17 — Min order statistic CDF ─────────────────────────────────────

def min_order_statistic_cdf(
    x: float,
    n: int,
    dist: str = "uniform",
    params: Optional[Dict] = None,
) -> float:
    """
    CDF of the minimum X_(1) from a sample of size n.

    F_(1)(x) = 1 - [1 - F(x)]^n

    This follows from P(X_(1) > x) = P(all X_i > x) = [1 - F(x)]^n.

    For Uniform[0,1]: F_(1)(x) = 1 - (1-x)^n.
    Note: min of n i.i.d. Exp(rate) is Exp(n*rate) — this formula yields that.

    Args:
        x:      Evaluation point.
        n:      Sample size. Must be >= 1.
        dist:   Distribution family: "uniform", "exponential", or "normal".
        params: Optional distribution parameters.

    Returns:
        F_(1)(x) = 1 - (1 - F(x))^n.
    """
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    cdf, _ = _get_cdf_pdf(dist, params)
    fx = cdf(x)
    return float(1.0 - (1.0 - fx) ** n)


# ── Concept 18 — Max order statistic CDF ─────────────────────────────────────

def max_order_statistic_cdf(
    x: float,
    n: int,
    dist: str = "uniform",
    params: Optional[Dict] = None,
) -> float:
    """
    CDF of the maximum X_(n) from a sample of size n.

    F_(n)(x) = [F(x)]^n

    This follows from P(X_(n) <= x) = P(all X_i <= x) = [F(x)]^n.

    For Uniform[0,1]: F_(n)(x) = x^n.

    Cross-reference: for Uniform(0, theta), the CDF of the MLE d2 = max(X_i)
    is F_(n)(x) = (x/theta)^n, as implemented in uniform_estimators.py.

    Args:
        x:      Evaluation point.
        n:      Sample size. Must be >= 1.
        dist:   Distribution family: "uniform", "exponential", or "normal".
        params: Optional distribution parameters.

    Returns:
        F_(n)(x) = F(x)^n.
    """
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    cdf, _ = _get_cdf_pdf(dist, params)
    fx = cdf(x)
    return float(fx ** n)


# ── Concept 19 — Joint density of min and max ────────────────────────────────

def joint_min_max_density(
    x: float,
    y: float,
    n: int,
    dist: str = "uniform",
    params: Optional[Dict] = None,
) -> float:
    """
    Joint density of (X_(1), X_(n)) — the minimum and maximum.

    g_(1,n)(x, y) = n(n-1) [F(y) - F(x)]^(n-2) f(x) f(y),  x < y

    For Uniform[0,1]: g_(1,n)(x, y) = n(n-1)(y - x)^(n-2)  for 0 <= x < y <= 1.

    Args:
        x:      Value of the minimum. Must be < y.
        y:      Value of the maximum. Must be > x.
        n:      Sample size. Must be >= 2.
        dist:   Distribution family: "uniform", "exponential", or "normal".
        params: Optional distribution parameters.

    Returns:
        Joint density at (x, y).

    Raises:
        ValueError: if x >= y.
    """
    if n < 2:
        raise ValueError(f"n must be >= 2 for joint min-max density, got {n}")
    if x >= y:
        raise ValueError(f"x must be strictly less than y, got x={x}, y={y}")
    cdf, pdf = _get_cdf_pdf(dist, params)
    fx = cdf(x)
    fy = cdf(y)
    f_x = pdf(x)
    f_y = pdf(y)
    return float(n * (n - 1) * (fy - fx) ** (n - 2) * f_x * f_y)


# ── Concept 20 — Range distribution CDF ──────────────────────────────────────

def range_cdf(
    x: float,
    n: int,
    dist: str = "uniform",
    params: Optional[Dict] = None,
) -> float:
    """
    CDF of the range R = X_(n) - X_(1) for i.i.d. draws.

    F_R(r) = n * integral_{-inf}^{+inf} [F(y+r) - F(y)]^(n-1) f(y) dy

    For Uniform[0,1] with 0 <= r <= 1, the analytical result is:
      F_R(r) = r^(n-1) * [n - (n-1)*r]

    For other distributions, numerical integration via scipy.integrate.quad
    is used.

    Cross-reference: R = max(X_i) - min(X_i) = d2 - X_(1), connecting to
    both uniform_estimators.py (MLE = d2 = max) and min_order_statistic_cdf.

    Args:
        x:      Evaluation point for the range (must be >= 0).
        n:      Sample size. Must be >= 2.
        dist:   Distribution family: "uniform", "exponential", or "normal".
        params: Optional distribution parameters.

    Returns:
        F_R(x) — CDF of the range at x.
    """
    if n < 2:
        raise ValueError(f"n must be >= 2 for range CDF, got {n}")
    if x <= 0.0:
        return 0.0

    if dist == "uniform":
        if x >= 1.0:
            return 1.0
        # Analytical formula for Uniform[0,1] range CDF (Lecture 29 Example 45)
        return float(n * (1.0 - x) * x ** (n - 1) + x ** n)

    cdf, pdf = _get_cdf_pdf(dist, params)

    def integrand(y: float) -> float:
        diff = cdf(y + x) - cdf(y)
        if diff <= 0.0:
            return 0.0
        return n * (diff ** (n - 1)) * pdf(y)

    # Integration bounds: for exponential use [0, inf); for normal use (-inf, inf)
    if dist == "exponential":
        result, _ = _integrate.quad(integrand, 0.0, np.inf, limit=200)
    else:
        result, _ = _integrate.quad(integrand, -np.inf, np.inf, limit=200)

    return float(min(max(result, 0.0), 1.0))


# ── Concept 21 — Range of Uniform[0,1] follows Beta(n-1, 2) ──────────────────

def uniform_range_distribution(
    n: int,
    n_sim: int = 10_000,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Verify that the range R = X_(n) - X_(1) of Uniform[0,1] follows Beta(n-1, 2).

    The range of n i.i.d. Uniform[0,1] draws has the distribution:
      R ~ Beta(n-1, 2)
    with mean (n-1)/(n+1) and variance 2(n-1)/[(n+1)^2 (n+2)].

    Verified by simulating n_sim samples of size n, computing the range of
    each, and running a KS test against Beta(n-1, 2).

    Cross-reference:
      range = max(X_i) - min(X_i) = d2 - X_(1)
      where d2 is the MLE from uniform_estimators.py.

    Args:
        n:      Sample size. Must be >= 2.
        n_sim:  Number of Monte Carlo repetitions.
        seed:   Random seed.

    Returns:
        dict with dist, alpha (=n-1), beta (=2), ks_p_value, verified (True if p>0.05).
    """
    if n < 2:
        raise ValueError(f"n must be >= 2 for range distribution, got {n}")
    rng = np.random.default_rng(seed)
    samples = rng.uniform(0.0, 1.0, size=(n_sim, n))
    ranges = samples.max(axis=1) - samples.min(axis=1)
    # Beta(n-1, 2) reference draws
    rng2 = np.random.default_rng(seed + 1)
    beta_draws = rng2.beta(n - 1, 2, size=n_sim)
    ks_stat, p_val = ks_2samp(ranges, beta_draws)
    return {
        "dist": f"Beta({n-1}, 2)",
        "alpha": n - 1,
        "beta": 2,
        "ks_p_value": float(p_val),
        "verified": bool(p_val > 0.05),
    }
