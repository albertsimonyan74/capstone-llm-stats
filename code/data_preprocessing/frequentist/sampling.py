# baseline/frequentist/sampling.py
"""
Sampling algorithms from Lecture 36.

Implements the Box-Muller transform for generating Normal random variates
from Uniform(0,1) inputs, together with a statistical verification routine.

Theory (Lecture 36):
  If U, V ~ Uniform(0,1) are independent then:
    eta1 = sqrt(-2 * log(U)) * cos(2*pi*V)
    eta2 = sqrt(-2 * log(U)) * sin(2*pi*V)
  are i.i.d. Normal(0,1).

  Remark: eta1^2 + eta2^2 = -2*log(U) ~ Exponential(1/2) = chi2(2),
  connecting to the chi-squared additive property in conjugate_models.py.
"""
from __future__ import annotations

import math
from typing import Optional, Tuple

import numpy as np
from scipy.stats import ks_2samp, norm


# ── 1. box_muller_standard ────────────────────────────────────────────────────

def box_muller_standard(u: float, v: float) -> Tuple[float, float]:
    """
    Apply the Box-Muller transform to produce two independent N(0,1) draws.

    Given U, V ~ Uniform(0,1) independent:
      eta1 = sqrt(-2 * log(U)) * cos(2*pi*V)
      eta2 = sqrt(-2 * log(U)) * sin(2*pi*V)

    Both eta1 and eta2 are marginally N(0,1) and mutually independent.

    Lecture 36 Example 42: U=0.531, V=0.253 →
      eta1 ≈ -0.021,  eta2 ≈ 1.125
    Scale to N(50, 25): x1 = 50 + 5*eta1 ≈ 49.895,  x2 = 50 + 5*eta2 ≈ 55.625

    Args:
        u: Uniform(0,1) draw. Must be in (0, 1) (strict, to avoid log(0)).
        v: Uniform(0,1) draw. Must be in (0, 1).

    Returns:
        (eta1, eta2): pair of independent N(0,1) values.

    Raises:
        ValueError: if u or v is not strictly in (0, 1).
    """
    if not (0.0 < u < 1.0):
        raise ValueError(f"u must be in (0, 1), got {u}")
    if not (0.0 < v < 1.0):
        raise ValueError(f"v must be in (0, 1), got {v}")
    r = math.sqrt(-2.0 * math.log(u))
    angle = 2.0 * math.pi * v
    eta1 = r * math.cos(angle)
    eta2 = r * math.sin(angle)
    return float(eta1), float(eta2)


# ── 2. box_muller_sample ──────────────────────────────────────────────────────

def box_muller_sample(
    mu: float = 0.0,
    sigma: float = 1.0,
    n: int = 1,
    seed: Optional[int] = None,
) -> np.ndarray:
    """
    Generate n samples from Normal(mu, sigma^2) via the Box-Muller transform.

    Draws pairs of Uniform(0,1) values and applies box_muller_standard to
    produce N(0,1) variates, then scales: X = mu + sigma * eta.

    If n is odd, one extra variate is generated and discarded so that
    the output always has exactly n elements.

    Args:
        mu:    Mean of the target Normal distribution.
        sigma: Standard deviation (> 0).
        n:     Number of samples to return.
        seed:  Optional random seed for reproducibility.

    Returns:
        1-D array of shape (n,) with draws from N(mu, sigma^2).
    """
    if sigma <= 0:
        raise ValueError(f"sigma must be > 0, got {sigma}")
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")

    rng = np.random.default_rng(seed)
    # Generate enough pairs to cover n outputs
    n_pairs = math.ceil(n / 2)
    us = rng.uniform(1e-10, 1.0 - 1e-10, size=n_pairs)
    vs = rng.uniform(1e-10, 1.0 - 1e-10, size=n_pairs)

    samples = []
    for u, v in zip(us, vs):
        e1, e2 = box_muller_standard(float(u), float(v))
        samples.append(e1)
        samples.append(e2)

    # Trim to exactly n and scale
    result = np.array(samples[:n], dtype=float)
    return mu + sigma * result


# ── 3. verify_box_muller ──────────────────────────────────────────────────────

def verify_box_muller(
    n_sim: int = 10_000,
    seed: int = 42,
) -> dict:
    """
    Statistically verify that Box-Muller produces N(0,1) samples.

    Generates n_sim samples via box_muller_sample, then:
      - Reports sample mean and std.
      - Runs a KS test against the N(0,1) CDF.
      - Sets verified=True if KS p-value > 0.05.

    Args:
        n_sim: Number of samples to generate.
        seed:  Random seed.

    Returns:
        dict with mean, std, ks_statistic, ks_p_value, verified.
    """
    samples = box_muller_sample(mu=0.0, sigma=1.0, n=n_sim, seed=seed)
    mean = float(np.mean(samples))
    std = float(np.std(samples))
    ks_stat, ks_p = ks_2samp(samples, norm.rvs(size=n_sim, random_state=seed + 1))
    return {
        "mean": mean,
        "std": std,
        "ks_statistic": float(ks_stat),
        "ks_p_value": float(ks_p),
        "verified": bool(ks_p > 0.05),
    }
