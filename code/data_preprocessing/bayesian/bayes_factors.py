# baseline/bayesian/bayes_factors.py
"""
Bayes factors and log marginal likelihoods for conjugate models.

Reference:
  Kass & Raftery (1995) "Bayes Factors", JASA 90(430):773-795.
  Ghosh et al (2006) "Introduction to Bayesian Analysis", §6.3.
  Lee (2012) "Bayesian Statistics: An Introduction", §4.5.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List

import numpy as np
from scipy.special import betaln, gammaln


# ── A2 / B1 — Log Marginal Likelihoods ───────────────────────────────────────

def log_marginal_likelihood_beta_binomial(
    alpha: float,
    beta: float,
    x: int,
    n: int,
) -> float:
    """
    Log marginal likelihood for Binomial(n, p) with Beta(alpha, beta) prior.

    The marginal likelihood (integrating out p) equals:
        p(x | alpha, beta) = C(n,x) · B(alpha+x, beta+n-x) / B(alpha, beta)

    This function returns the log kernel without the combinatorial constant,
    which cancels in Bayes factor calculations:
        log p*(x | alpha, beta) = log B(alpha+x, beta+n-x) − log B(alpha, beta)

    Reference: Ghosh et al (2006) §6.3; Lee (2012) §4.5.

    Args:
        alpha: Beta prior first shape parameter (> 0).
        beta:  Beta prior second shape parameter (> 0).
        x:     Number of successes (0 <= x <= n).
        n:     Number of trials (>= 0).

    Returns:
        Log marginal likelihood (log-scale, excluding combinatorial constant).
    """
    if alpha <= 0 or beta <= 0:
        raise ValueError(f"alpha and beta must be > 0, got alpha={alpha}, beta={beta}")
    if x < 0 or n < 0 or x > n:
        raise ValueError(f"Need 0 <= x <= n, got x={x}, n={n}")
    return float(betaln(alpha + x, beta + n - x) - betaln(alpha, beta))


def log_marginal_likelihood_gamma_poisson(
    alpha: float,
    beta: float,
    data: List[int],
) -> float:
    """
    Log marginal likelihood for Poisson(lambda) data with Gamma(alpha, beta) prior.

    Integrating out lambda:
        log p(data | alpha, beta) =
            log Γ(alpha + Σxᵢ) − log Γ(alpha)
          + alpha · log(beta) − (alpha + Σxᵢ) · log(beta + n)
          − Σ log(xᵢ!)

    where alpha is the shape and beta is the rate parameter of the prior.

    Reference: Hoff (2009) §3.2; Carlin & Louis (2008) §2.2.

    Args:
        alpha: Gamma prior shape (> 0).
        beta:  Gamma prior rate (> 0).
        data:  List of non-negative integer counts (non-empty).

    Returns:
        Log marginal likelihood (float).
    """
    if alpha <= 0 or beta <= 0:
        raise ValueError(f"alpha and beta must be > 0, got alpha={alpha}, beta={beta}")
    if not data:
        raise ValueError("data must be non-empty")
    n = len(data)
    s = sum(data)
    log_ml = (
        gammaln(alpha + s) - gammaln(alpha)
        + alpha * math.log(beta) - (alpha + s) * math.log(beta + n)
        - sum(gammaln(xi + 1) for xi in data)
    )
    return float(log_ml)


def log_marginal_likelihood_dirichlet_multinomial(
    alpha: List[float],
    counts: List[int],
) -> float:
    """
    Log marginal likelihood for Multinomial counts with Dirichlet(alpha) prior.

    Integrating out the probability vector p:
        log p(counts | alpha) =
            log Γ(Σαₖ) − log Γ(Σαₖ + Σcₖ)
          + Σₖ [log Γ(αₖ + cₖ) − log Γ(αₖ)]

    Reference: Hoff (2009) §3.3; Ghosh et al (2006) §5.1.

    Args:
        alpha:  Dirichlet prior concentration parameters (all > 0).
        counts: Observed counts per category (all >= 0, non-empty).

    Returns:
        Log marginal likelihood (float).
    """
    alpha = np.asarray(alpha, dtype=float)
    counts = np.asarray(counts, dtype=float)
    if alpha.shape != counts.shape:
        raise ValueError("alpha and counts must have the same length")
    if np.any(alpha <= 0):
        raise ValueError("All alpha values must be > 0")
    if np.any(counts < 0):
        raise ValueError("All counts must be >= 0")
    sum_alpha = float(np.sum(alpha))
    sum_counts = float(np.sum(counts))
    log_ml = (
        gammaln(sum_alpha) - gammaln(sum_alpha + sum_counts)
        + float(np.sum(gammaln(alpha + counts) - gammaln(alpha)))
    )
    return float(log_ml)


# ── A2 — Bayes Factor ─────────────────────────────────────────────────────────

def bayes_factor_beta_binomial(
    alpha1: float, beta1: float,
    alpha2: float, beta2: float,
    x: int, n: int,
) -> Dict[str, Any]:
    """
    Bayes factor BF₁₂ comparing two Beta-Binomial models on the same data.

    BF₁₂ = p(x | M₁) / p(x | M₂)
          = exp(log p*(x|M₁) − log p*(x|M₂))

    Evidence strength follows the Kass & Raftery (1995) scale on |log BF|
    (natural log):
        |log BF| < 1   → "not worth mentioning"
        1 ≤ |log BF| < 3 → "positive"
        3 ≤ |log BF| < 5 → "strong"
        |log BF| ≥ 5   → "very strong"

    Reference: Kass & Raftery (1995) JASA 90:773; Lee (2012) §4.5.

    Args:
        alpha1, beta1: Beta prior parameters for model M₁.
        alpha2, beta2: Beta prior parameters for model M₂.
        x: Observed successes.
        n: Total trials.

    Returns:
        dict with keys: log_BF, BF, log_ml_M1, log_ml_M2,
                        favored_model ("M1"|"M2"|"tie"),
                        evidence_strength (str).
    """
    log_ml1 = log_marginal_likelihood_beta_binomial(alpha1, beta1, x, n)
    log_ml2 = log_marginal_likelihood_beta_binomial(alpha2, beta2, x, n)
    log_bf = log_ml1 - log_ml2
    bf = math.exp(log_bf)

    if log_bf > 0:
        favored = "M1"
    elif log_bf < 0:
        favored = "M2"
    else:
        favored = "tie"

    abs_log = abs(log_bf)
    if abs_log < 1.0:
        strength = "not worth mentioning"
    elif abs_log < 3.0:
        strength = "positive"
    elif abs_log < 5.0:
        strength = "strong"
    else:
        strength = "very strong"

    return {
        "log_BF":           float(log_bf),
        "BF":               float(bf),
        "log_ml_M1":        float(log_ml1),
        "log_ml_M2":        float(log_ml2),
        "favored_model":    favored,
        "evidence_strength": strength,
    }
