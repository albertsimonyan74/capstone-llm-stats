# baseline/bayesian/dirichlet_multinomial.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np
from scipy.special import gammaln, betaln
from scipy.stats import ks_2samp

from data_preprocessing.bayesian.utils import require_positive, require_int_nonnegative


@dataclass(frozen=True)
class DirichletPosterior:
    alpha_post: List[float]

    def mean(self) -> List[float]:
        a = np.asarray(self.alpha_post, dtype=float)
        s = float(np.sum(a))
        return [float(x) for x in (a / s)]
        
    def concentration(self) -> float:
        return float(np.sum(np.asarray(self.alpha_post, dtype=float)))

    def predictive_prob_next(self) -> List[float]:
        # Next single draw predictive = posterior mean
        return self.mean()


def dirichlet_multinomial_update(alpha: List[float], counts: List[int]) -> Dict:
    """
    Conjugate update for Dirichlet-Multinomial model.

    Prior: theta ~ Dirichlet(alpha)
    Likelihood: counts ~ Multinomial(n, theta)
    Posterior: theta | counts ~ Dirichlet(alpha + counts)

    Args:
        alpha:  Prior concentration parameters (all > 0).
        counts: Observed counts for each category (all >= 0).

    Returns:
        dict with keys:
          posterior_alpha  – list of updated alpha parameters
          posterior_mean   – list of posterior means (alpha_post / sum(alpha_post))
    """
    if not alpha or not counts:
        raise ValueError("alpha and counts must be non-empty")
    if len(alpha) != len(counts):
        raise ValueError("alpha and counts must have the same length")

    for i, a in enumerate(alpha):
        require_positive(float(a), f"alpha[{i}]")
    for i, c in enumerate(counts):
        require_int_nonnegative(int(c), f"counts[{i}]")

    alpha_post = [float(a) + int(c) for a, c in zip(alpha, counts)]
    total = sum(alpha_post)
    posterior_mean = [a / total for a in alpha_post]
    return {"posterior_alpha": alpha_post, "posterior_mean": posterior_mean}


def _dirichlet_multinomial_update_posterior(alpha: List[float], counts: List[int]) -> DirichletPosterior:
    """Internal: returns DirichletPosterior dataclass (used by ground_truth.py)."""
    result = dirichlet_multinomial_update(alpha, counts)
    return DirichletPosterior(alpha_post=result["posterior_alpha"])


def dirichlet_multinomial_logpmf(counts: List[int], alpha: List[float]) -> float:
    """
    Dirichlet-Multinomial log PMF for counts x (sum x = m) with parameters alpha.

    P(x | alpha) = m! / Π x_i! * Γ(α0) / Γ(α0+m) * Π Γ(α_i + x_i) / Γ(α_i)
      where α0 = Σ α_i
    """
    if len(counts) != len(alpha):
        raise ValueError("counts and alpha must have same length")

    for i, c in enumerate(counts):
        require_int_nonnegative(int(c), f"counts[{i}]")
    for i, a in enumerate(alpha):
        require_positive(float(a), f"alpha[{i}]")

    x = np.asarray(counts, dtype=int)
    a = np.asarray(alpha, dtype=float)

    m = int(np.sum(x))
    a0 = float(np.sum(a))

    # log(m!) - sum log(x_i!)
    log_coeff = gammaln(m + 1) - float(np.sum(gammaln(x + 1)))

    log_part = gammaln(a0) - gammaln(a0 + m) + float(np.sum(gammaln(a + x) - gammaln(a)))

    return float(log_coeff + log_part)


def dirichlet_multinomial_pmf(counts: List[int], alpha: List[float]) -> float:
    return float(np.exp(dirichlet_multinomial_logpmf(counts, alpha)))


# ── Concept 1 — Multinomial PMF ───────────────────────────────────────────────

def multinomial_pmf(n: int, k: List[int], p: List[float]) -> float:
    """
    Multinomial probability mass function.

    P(K=k | n, p) = n! / (k_1! * ... * k_m!) * p_1^k_1 * ... * p_m^k_m

    Args:
        n: Total number of trials. Must equal sum(k).
        k: List of category counts. All non-negative integers.
        p: List of category probabilities. Must sum to 1.

    Returns:
        Multinomial PMF value.
    """
    if len(k) != len(p):
        raise ValueError("k and p must have the same length")
    if abs(sum(p) - 1.0) > 1e-9:
        raise ValueError(f"p must sum to 1, got {sum(p)}")
    if sum(k) != n:
        raise ValueError(f"sum(k)={sum(k)} must equal n={n}")
    k_arr = np.asarray(k, dtype=int)
    p_arr = np.asarray(p, dtype=float)
    log_coeff = gammaln(n + 1) - float(np.sum(gammaln(k_arr + 1)))
    log_prob = float(np.sum(k_arr * np.log(p_arr)))
    return float(np.exp(log_coeff + log_prob))


# ── Concept 2 — Multinomial log-PMF and sampling ─────────────────────────────

def multinomial_logpmf(n: int, k: List[int], p: List[float]) -> float:
    """
    Log of the Multinomial PMF.

    Args:
        n: Total number of trials.
        k: Category counts.
        p: Category probabilities (must sum to 1).

    Returns:
        log P(K=k | n, p).
    """
    if len(k) != len(p):
        raise ValueError("k and p must have the same length")
    if abs(sum(p) - 1.0) > 1e-9:
        raise ValueError(f"p must sum to 1, got {sum(p)}")
    if sum(k) != n:
        raise ValueError(f"sum(k)={sum(k)} must equal n={n}")
    k_arr = np.asarray(k, dtype=int)
    p_arr = np.asarray(p, dtype=float)
    log_coeff = gammaln(n + 1) - float(np.sum(gammaln(k_arr + 1)))
    log_prob = float(np.sum(k_arr * np.log(p_arr)))
    return float(log_coeff + log_prob)


def multinomial_sample(
    n: int,
    p: List[float],
    size: int = 1,
    seed: Optional[int] = None,
) -> np.ndarray:
    """
    Draw samples from a Multinomial(n, p) distribution.

    Args:
        n:    Number of trials per draw.
        p:    Category probabilities (must sum to 1).
        size: Number of independent samples.
        seed: Optional random seed for reproducibility.

    Returns:
        Array of shape (size, len(p)) where each row sums to n.
    """
    rng = np.random.default_rng(seed)
    return rng.multinomial(n, p, size=size)


# ── Concept 3 — Dirichlet density ────────────────────────────────────────────

def dirichlet_pdf(p: List[float], alpha: List[float]) -> float:
    """
    Dirichlet probability density function.

    f(p | alpha) = Gamma(sum alpha) / prod(Gamma(alpha_i)) * prod(p_i^(alpha_i - 1))

    Args:
        p:     Point on the simplex (all positive, sum = 1).
        alpha: Concentration parameters (all > 0).

    Returns:
        Dirichlet PDF value at p.
    """
    if len(p) != len(alpha):
        raise ValueError("p and alpha must have the same length")
    p_arr = np.asarray(p, dtype=float)
    a_arr = np.asarray(alpha, dtype=float)
    if np.any(a_arr <= 0):
        raise ValueError("all alpha must be > 0")
    if abs(np.sum(p_arr) - 1.0) > 1e-9:
        raise ValueError(f"p must sum to 1, got {np.sum(p_arr)}")
    if np.any(p_arr <= 0):
        raise ValueError("all p must be > 0")
    log_norm = gammaln(np.sum(a_arr)) - float(np.sum(gammaln(a_arr)))
    log_kernel = float(np.sum((a_arr - 1.0) * np.log(p_arr)))
    return float(np.exp(log_norm + log_kernel))


# ── Concept 5 — Dirichlet uniform on simplex ─────────────────────────────────

def is_uniform_dirichlet(alpha: List[float], tol: float = 1e-10) -> bool:
    """
    Check whether a Dirichlet is uniform on the simplex (all alpha_i equal to 1).

    Dirichlet(1, 1, ..., 1) is the uniform distribution on the K-simplex:
    the density is constant (= (K-1)!) everywhere on the simplex.

    Args:
        alpha: Concentration parameters.
        tol:   Tolerance for comparing each alpha_i to 1.0.

    Returns:
        True if all alpha_i == 1 (within tol), False otherwise.
    """
    return all(abs(a - 1.0) <= tol for a in alpha)


# ── Concept 8 — Dirichlet construction from Gamma variables ──────────────────

def dirichlet_from_gamma(
    alpha: List[float],
    n_samples: int,
    seed: Optional[int] = None,
) -> np.ndarray:
    """
    Generate Dirichlet samples via the Gamma construction.

    If Y_i ~ Gamma(alpha_i, 1) independently, then
    X = (Y_1, ..., Y_K) / sum(Y_i) ~ Dirichlet(alpha).

    Args:
        alpha:     Concentration parameters (all > 0).
        n_samples: Number of samples to draw.
        seed:      Optional random seed.

    Returns:
        Array of shape (n_samples, len(alpha)) with rows summing to 1.
    """
    a_arr = np.asarray(alpha, dtype=float)
    if np.any(a_arr <= 0):
        raise ValueError("all alpha must be > 0")
    rng = np.random.default_rng(seed)
    # Draw independent Gamma(alpha_i, 1) for each category
    gammas = np.column_stack([rng.gamma(a, 1.0, size=n_samples) for a in a_arr])
    row_sums = gammas.sum(axis=1, keepdims=True)
    return gammas / row_sums