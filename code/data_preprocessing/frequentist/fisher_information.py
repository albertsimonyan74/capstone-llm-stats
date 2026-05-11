# baseline/frequentist/fisher_information.py
"""
Fisher information, Rao-Cramér bounds, and exponential family verification.

Implements the theoretical results from Lectures 23–24:
  - Fisher information for standard families
  - Rao-Cramér lower bound for unbiased and biased estimators
  - Exponential family structure identification
  - Numerical log-likelihood differentiation
  - Efficiency verification via simulation
"""
from __future__ import annotations

import math
from typing import Any, Callable, Dict, List

import numpy as np
from scipy import stats


# ── Supported distributions ──────────────────────────────────────────────────

# Regular exponential family distributions — Fisher information is well-defined
_REGULAR_DISTS = {"binomial", "poisson", "normal", "exponential", "normal_var", "gamma_rate"}
_ALL_DISTS = _REGULAR_DISTS | {"uniform", "gamma", "beta"}


def _require_positive(x: float, name: str) -> None:
    if x <= 0:
        raise ValueError(f"{name} must be > 0, got {x}")


def _require_prob(theta: float, name: str = "theta") -> None:
    if not (0 < theta < 1):
        raise ValueError(f"{name} must be in (0, 1) for Binomial, got {theta}")


def _check_dist(dist: str, supported: set) -> None:
    if dist not in supported:
        raise ValueError(f"dist='{dist}' not supported. Choose from: {sorted(supported)}")


# ── Private log-likelihood helper ─────────────────────────────────────────────

def _log_likelihood(dist: str, theta: float, data: List[float]) -> float:
    """Compute log P(data | theta) for a given distribution."""
    if dist == "binomial":
        # Bernoulli(theta) observations — each datum is 0 or 1
        return float(sum(stats.bernoulli.logpmf(int(round(x)), theta) for x in data))
    if dist == "poisson":
        return float(sum(stats.poisson.logpmf(int(round(x)), mu=theta) for x in data))
    if dist == "normal":
        # Normal(mu=theta, sigma^2=1) — known variance, as in Lecture 23 Example 38
        return float(sum(stats.norm.logpdf(x, loc=theta, scale=1.0) for x in data))
    raise ValueError(f"dist='{dist}' not supported in _log_likelihood")


# ── 1. fisher_information ─────────────────────────────────────────────────────

def fisher_information(dist: str, theta: float, n: int = 1) -> float:
    """
    Total Fisher information I_n(theta) for n i.i.d. observations.

    By the additive property of Fisher information, I_n(theta) = n * I_1(theta),
    where I_1(theta) = E[(d/dtheta log f(X|theta))^2].

    Lecture 23, Definition/Theorem: Fisher information quantifies how much
    information a sample carries about the unknown parameter theta. It appears
    as the denominator in the Rao-Cramér lower bound, bounding the variance
    of any unbiased estimator from below.

    Supported distributions and their I_1(theta):
      "binomial"    → 1 / (theta * (1 - theta))    [Bernoulli(theta) obs]
      "poisson"     → 1 / theta                    [Poisson(lambda=theta) obs]
      "normal"      → 1  (sigma^2 = 1 known)       [Normal(mu=theta, sigma^2=1)]
      "exponential" → 1 / theta^2                  [Exp(rate=theta), parameterised by rate]
      "normal_var"  → 1 / (2 * theta^2)            [Normal(mu=0 known, variance=theta)]
      "gamma_rate"  → alpha / theta^2              [Gamma(shape=alpha, rate=theta); alpha via n]
      "uniform"     → raises NotImplementedError   [not a regular exponential family]

    Args:
        dist:  Distribution name (see above).
        theta: True parameter value.
        n:     Number of i.i.d. observations (default 1).

    Returns:
        I_n(theta) = n * I_1(theta).
    """
    if dist == "uniform":
        raise NotImplementedError(
            "Fisher information is not defined for Uniform(0, theta). "
            "The Uniform family is not a regular exponential family: its support "
            "depends on theta, so the regularity conditions required by the "
            "Rao-Cramér theorem (interchange of differentiation and integration) "
            "are violated. The MLE max(X_i) achieves O(1/n^2) MSE, which is "
            "faster than the O(1/n) rate the RC bound would predict — illustrating "
            "that RC does not apply here."
        )
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")

    _check_dist(dist, _REGULAR_DISTS)

    if dist == "binomial":
        _require_prob(theta)
        i1 = 1.0 / (theta * (1.0 - theta))
    elif dist == "poisson":
        _require_positive(theta, "theta")
        i1 = 1.0 / theta
    elif dist == "normal":
        # Normal(mu=theta, sigma^2=1 known): I_1 = 1/sigma^2 = 1
        i1 = 1.0
    elif dist == "exponential":
        # Exp(rate=theta): f(x|theta) = theta * exp(-theta*x)
        # Score: d/dtheta log f = 1/theta - x  →  I_1 = E[(1/theta - X)^2] = 1/theta^2
        _require_positive(theta, "theta")
        i1 = 1.0 / (theta ** 2)
    elif dist == "normal_var":
        # Normal(mu=0 known, sigma^2=theta): I_1(theta) = 1/(2*theta^2)
        _require_positive(theta, "theta")
        i1 = 1.0 / (2.0 * theta ** 2)
    else:  # gamma_rate
        # Gamma(shape=alpha, rate=theta): I_1(theta) = alpha / theta^2
        # alpha is encoded as n here (shape parameter; caller must pass n=alpha)
        _require_positive(theta, "theta")
        if n < 1:
            raise ValueError(f"n (=shape alpha) must be >= 1 for gamma_rate, got {n}")
        return float(n / (theta ** 2))  # already accounts for n copies

    return float(n * i1)


# ── 2. rao_cramer_bound ───────────────────────────────────────────────────────

def rao_cramer_bound(fisher_info: float, bias_deriv: float = 0.0) -> float:
    """
    Rao-Cramér lower bound on the variance of an estimator.

    For any estimator T(X) of theta with bias b(theta) = E[T] - theta:
      Var(T) >= (1 + b'(theta))^2 / I_n(theta)

    For an unbiased estimator (b'(theta) = 0):
      Var(T) >= 1 / I_n(theta)

    Lecture 23, Theorem (Rao-Cramér): no unbiased estimator can achieve
    variance below 1/I_n(theta). An estimator achieving this bound exactly
    is called efficient. From Lecture 24: the MLE for exponential family
    distributions is asymptotically efficient.

    Args:
        fisher_info:  I_n(theta), the total Fisher information. Must be > 0.
        bias_deriv:   b'(theta) = d/dtheta E[T(X)]. Default 0 (unbiased case).

    Returns:
        RC lower bound = (1 + bias_deriv)^2 / fisher_info.
    """
    _require_positive(fisher_info, "fisher_info")
    return float((1.0 + bias_deriv) ** 2 / fisher_info)


# ── 3. estimator_bias ─────────────────────────────────────────────────────────

def estimator_bias(
    estimator_fn: Callable[[List[float]], float],
    theta: float,
    n: int,
    n_sim: int = 10_000,
) -> float:
    """
    Monte Carlo estimate of bias for an estimator applied to Uniform(0, theta) samples.

    Simulates n_sim datasets of size n from Uniform(0, theta), applies
    estimator_fn to each, and returns mean(estimates) - theta.

    Lecture 25 example: used to verify that d1 = 2*mean(X) is unbiased
    (bias ≈ 0) while d2 = max(X_i) has bias ≈ -theta/(n+1), and to confirm
    that the optimal scaled estimator dc = ((n+2)/(n+1)) * max(X_i) has
    a small but non-zero bias that buys lower MSE overall.

    Args:
        estimator_fn: Function mapping a list of floats to a scalar estimate.
        theta:        True parameter value for Uniform(0, theta). Must be > 0.
        n:            Sample size per simulation. Must be >= 1.
        n_sim:        Number of Monte Carlo repetitions. Must be >= 1.

    Returns:
        Estimated bias = E[estimator_fn(X)] - theta.
    """
    _require_positive(theta, "theta")
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    if n_sim < 1:
        raise ValueError(f"n_sim must be >= 1, got {n_sim}")

    rng = np.random.default_rng()
    samples = rng.uniform(0.0, theta, size=(n_sim, n))
    estimates = np.array([estimator_fn(row.tolist()) for row in samples])
    return float(np.mean(estimates) - theta)


# ── 4. is_efficient ───────────────────────────────────────────────────────────

def is_efficient(
    estimator_variance: float,
    fisher_info: float,
    bias_deriv: float = 0.0,
    tol: float = 1e-6,
) -> bool:
    """
    Check whether an estimator achieves the Rao-Cramér bound (up to tolerance).

    An estimator is efficient if its variance equals the RC lower bound:
      Var(T) = (1 + b'(theta))^2 / I_n(theta)

    Lecture 23/24: for regular exponential family distributions, the MLE is
    efficient (achieves the RC bound exactly in finite samples, not just
    asymptotically). This function verifies efficiency numerically by checking
    Var(T) <= RC_bound + tol.

    Args:
        estimator_variance: Var(T), the variance of the estimator.
        fisher_info:        I_n(theta), total Fisher information.
        bias_deriv:         b'(theta). Default 0 (unbiased estimator).
        tol:                Numerical tolerance for the comparison.

    Returns:
        True if estimator_variance <= rao_cramer_bound(...) + tol.
    """
    bound = rao_cramer_bound(fisher_info, bias_deriv)
    return bool(estimator_variance <= bound + tol)


# ── 5. is_exponential_family ──────────────────────────────────────────────────

def is_exponential_family(dist: str) -> Dict[str, Any]:
    """
    Return the exponential family decomposition for a distribution, if applicable.

    A distribution belongs to the exponential family if its density/PMF can be
    written as:
      p(x | theta) = h(x) * exp{ A(theta) * T(x) + B(theta) }

    where T(x) is the sufficient statistic, A(theta) is the natural parameter,
    B(theta) is the log-normalising constant (log partition function, negated),
    and h(x) is the base measure.

    Lecture 23/24: membership in the exponential family is sufficient for:
      (a) T(x) = sum(x_i) to be a sufficient statistic,
      (b) the MLE to be efficient (achieves the RC bound exactly),
      (c) the score equation d/dtheta log L = 0 to have a unique solution.

    Args:
        dist: One of "binomial", "poisson", "normal", "gamma", "beta", "uniform".

    Returns:
        dict with "is_exp_family": True and T_x, A_theta, B_theta, h_x strings,
        or "is_exp_family": False with a "reason" string for non-members.
    """
    _check_dist(dist, _ALL_DISTS)

    if dist == "binomial":
        return {
            "is_exp_family": True,
            "T_x": "sum(x_i)  [total number of successes]",
            "A_theta": "log(theta / (1 - theta))  [log-odds / logit]",
            "B_theta": "n * log(1 - theta)  [log normalising constant]",
            "h_x": "prod C(n, x_i)  [binomial coefficients]",
            "notes": (
                "Single-parameter exponential family in theta (probability). "
                "Natural parameter eta = log(theta/(1-theta)) → theta = sigmoid(eta)."
            ),
        }

    if dist == "poisson":
        return {
            "is_exp_family": True,
            "T_x": "sum(x_i)  [total count]",
            "A_theta": "log(theta)  [log of rate lambda]",
            "B_theta": "-n * theta  [= -n * lambda]",
            "h_x": "prod (1 / x_i!)  [reciprocal factorials]",
            "notes": (
                "Single-parameter exponential family in lambda=theta. "
                "Natural parameter eta = log(theta) → theta = exp(eta)."
            ),
        }

    if dist == "normal":
        return {
            "is_exp_family": True,
            "T_x": "sum(x_i)  [sufficient for mu when sigma^2 known]",
            "A_theta": "theta / sigma^2  [= theta when sigma^2=1]",
            "B_theta": "-n * theta^2 / (2 * sigma^2)  [= -n*theta^2/2 when sigma^2=1]",
            "h_x": "(2*pi*sigma^2)^{-n/2} * exp(-sum(x_i^2) / (2*sigma^2))",
            "notes": (
                "Normal with known sigma^2 is a single-parameter exponential family in mu. "
                "MLE (sample mean) is efficient — achieves RC bound exactly."
            ),
        }

    if dist == "gamma":
        return {
            "is_exp_family": True,
            "T_x": "(sum(log(x_i)), sum(x_i))  [for both shape and rate]",
            "A_theta": "(alpha - 1, -beta)  [natural parameters for shape alpha, rate beta]",
            "B_theta": "log(Gamma(alpha)) - alpha*log(beta)  [log partition function]",
            "h_x": "1  [base measure is 1 on (0, inf)]",
            "notes": (
                "Two-parameter exponential family. If alpha is known, "
                "single-parameter family in rate beta with T(x) = sum(x_i)."
            ),
        }

    if dist == "beta":
        return {
            "is_exp_family": True,
            "T_x": "(sum(log(x_i)), sum(log(1 - x_i)))  [for both alpha and beta]",
            "A_theta": "(alpha - 1, beta - 1)  [natural parameters]",
            "B_theta": "log(B(alpha, beta))  [log Beta function = log Gamma(alpha)+log Gamma(beta)-log Gamma(alpha+beta)]",
            "h_x": "1  [base measure is 1 on (0, 1)]",
            "notes": (
                "Two-parameter exponential family. If one shape parameter is fixed, "
                "becomes single-parameter with the corresponding log-sum as T(x)."
            ),
        }

    # uniform
    return {
        "is_exp_family": False,
        "reason": (
            "Uniform(0, theta) is NOT an exponential family. Its support (0, theta) "
            "depends on the parameter theta, violating the regularity condition that "
            "the support be fixed (independent of theta). As a consequence: "
            "(1) the MLE max(X_i) is not consistent with the score equation; "
            "(2) the Rao-Cramér bound does not apply; "
            "(3) the MLE achieves MSE ~ theta^2/n^2, much faster than the O(1/n) "
            "rate the RC bound would predict for regular families."
        ),
    }


# ── 6. log_likelihood_derivative ─────────────────────────────────────────────

def log_likelihood_derivative(
    dist: str,
    theta: float,
    data: List[float],
) -> float:
    """
    Numerical derivative of the log-likelihood at theta: d/dtheta log P(data | theta).

    Uses scipy.misc.derivative (central difference, dx=1e-5) to evaluate the
    score function at the given theta. At the MLE, this derivative equals zero
    (the score equation).

    Lecture 23, Score function: the score s(theta) = d/dtheta log L(theta | x)
    has E[s(theta)] = 0 and Var(s(theta)) = I(theta) under regularity conditions.
    This function is used to numerically verify that the MLE is a stationary
    point of the log-likelihood and to validate the Fisher information formula
    I(theta) = -E[d^2/dtheta^2 log f].

    Lecture 24 example: for Binomial data with MLE theta_hat = mean(x),
    calling this at theta = mean(x) should return ≈ 0 (up to numerical error).

    Args:
        dist:  One of "binomial", "poisson", "normal".
        theta: Parameter value at which to evaluate the derivative.
        data:  Observed sample as a list of floats.

    Returns:
        d/dtheta log P(data | theta), evaluated numerically at theta.
    """
    _check_dist(dist, _REGULAR_DISTS)
    if not data:
        raise ValueError("data must be non-empty")

    if dist == "binomial":
        _require_prob(theta)
    elif dist == "poisson":
        _require_positive(theta, "theta")

    def log_lik(t: float) -> float:
        return _log_likelihood(dist, t, data)

    dx = 1e-5
    return float((log_lik(theta + dx) - log_lik(theta - dx)) / (2 * dx))


# ── 7. verify_rao_cramer ──────────────────────────────────────────────────────

def verify_rao_cramer(
    dist: str,
    theta: float,
    n: int,
    n_sim: int = 5_000,
) -> Dict[str, Any]:
    """
    Empirically verify that the MLE achieves the Rao-Cramér bound via simulation.

    For each of n_sim datasets of size n, computes the MLE and records its value.
    The sample variance of the MLEs is compared to the analytical RC bound
    1 / I_n(theta). For exponential family distributions the ratio should be ≈ 1.0
    (the MLE is efficient), converging as n_sim → ∞.

    Lecture 24: demonstrates the efficiency of the MLE for Binomial, Poisson, and
    Normal distributions by showing that Var(MLE) ≈ 1/I_n(theta) in simulation,
    matching the RC bound exactly. Efficiency ratio = Var(MLE) / RC_bound ≈ 1.

    MLE used per distribution:
      "binomial" → mean(x_i)  where x_i ~ Bernoulli(theta)
      "poisson"  → mean(x_i)  where x_i ~ Poisson(theta)
      "normal"   → mean(x_i)  where x_i ~ Normal(theta, sigma^2=1)

    Args:
        dist:   One of "binomial", "poisson", "normal".
        theta:  True parameter value.
        n:      Sample size per simulation. Must be >= 1.
        n_sim:  Number of Monte Carlo repetitions. Must be >= 1.

    Returns:
        dict with keys:
          dist             – distribution name
          theta            – true parameter value
          n                – sample size
          mle_variance     – sample variance of MLE across n_sim repetitions
          rc_bound         – 1 / I_n(theta), the Rao-Cramér lower bound
          is_efficient     – True if mle_variance <= rc_bound + 1e-3
          efficiency_ratio – mle_variance / rc_bound  (should be ≈ 1.0)
    """
    _check_dist(dist, _REGULAR_DISTS)
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    if n_sim < 1:
        raise ValueError(f"n_sim must be >= 1, got {n_sim}")

    rng = np.random.default_rng()

    if dist == "binomial":
        _require_prob(theta)
        # x_i ~ Bernoulli(theta); MLE = mean(x)
        data = rng.binomial(1, theta, size=(n_sim, n))
        mles = data.mean(axis=1)
    elif dist == "poisson":
        _require_positive(theta, "theta")
        # x_i ~ Poisson(theta); MLE = mean(x)
        data = rng.poisson(theta, size=(n_sim, n))
        mles = data.mean(axis=1).astype(float)
    else:  # normal, sigma^2=1
        # x_i ~ Normal(theta, 1); MLE = mean(x)
        data = rng.normal(loc=theta, scale=1.0, size=(n_sim, n))
        mles = data.mean(axis=1)

    mle_variance = float(np.var(mles))
    rc_bound = rao_cramer_bound(fisher_information(dist, theta, n))
    efficiency_ratio = mle_variance / rc_bound if rc_bound > 0 else float("inf")

    return {
        "dist": dist,
        "theta": theta,
        "n": n,
        "mle_variance": mle_variance,
        "rc_bound": rc_bound,
        "is_efficient": is_efficient(mle_variance, fisher_information(dist, theta, n), tol=1e-3),
        "efficiency_ratio": efficiency_ratio,
    }


# ── 8. verify_mle_efficiency ──────────────────────────────────────────────────

def verify_mle_efficiency(
    dist: str,
    theta: float,
    n: int,
    n_sim: int = 5_000,
) -> Dict[str, Any]:
    """
    Verify that the MLE is efficient by comparing its variance to the RC bound.

    Extends verify_rao_cramer with two additions: a wider efficiency tolerance
    (ratio within 5% of 1.0 rather than 1e-3 absolute), and an explicit
    exponential_family flag drawn from is_exponential_family(), linking the
    efficiency result back to the theoretical reason (membership in an
    exponential family guarantees MLE efficiency in regular cases).

    Lecture 23/24 connection: the Rao-Cramér theorem guarantees that no
    unbiased estimator can have variance below 1/I_n(theta). For exponential
    family distributions the MLE achieves this bound exactly, making it
    the uniformly minimum variance unbiased estimator (UMVUE). This function
    empirically confirms that relationship.

    Lecture 24, Example 39 (Binomial, theta=0.4, n=30): the MLE theta_hat =
    mean(X_i) has Var = theta*(1-theta)/n = 0.4*0.6/30 ≈ 0.008, and the
    RC bound is 1/I_30(0.4) = theta*(1-theta)/30 ≈ 0.008. Efficiency ratio ≈ 1.

    Args:
        dist:   One of "binomial", "poisson", "normal".
        theta:  True parameter value.
        n:      Sample size per simulation run. Must be >= 1.
        n_sim:  Number of Monte Carlo repetitions. Must be >= 1.

    Returns:
        dict with keys:
          dist               – distribution name
          mle_variance       – sample variance of MLE over n_sim repetitions
          rc_bound           – 1 / I_n(theta)
          efficiency_ratio   – mle_variance / rc_bound  (≈ 1.0 for efficient MLE)
          is_efficient       – True if |efficiency_ratio - 1| <= 0.05
          exponential_family – True if dist is a regular exponential family
    """
    _check_dist(dist, _REGULAR_DISTS)
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    if n_sim < 1:
        raise ValueError(f"n_sim must be >= 1, got {n_sim}")

    rng = np.random.default_rng()

    if dist == "binomial":
        _require_prob(theta)
        mles = rng.binomial(1, theta, size=(n_sim, n)).mean(axis=1)
    elif dist == "poisson":
        _require_positive(theta, "theta")
        mles = rng.poisson(theta, size=(n_sim, n)).mean(axis=1).astype(float)
    else:  # normal, sigma^2=1
        mles = rng.normal(loc=theta, scale=1.0, size=(n_sim, n)).mean(axis=1)

    mle_variance = float(np.var(mles))
    rc_bound = rao_cramer_bound(fisher_information(dist, theta, n))
    efficiency_ratio = mle_variance / rc_bound if rc_bound > 0 else float("inf")
    exp_family_info = is_exponential_family(dist)

    return {
        "dist": dist,
        "mle_variance": mle_variance,
        "rc_bound": rc_bound,
        "efficiency_ratio": efficiency_ratio,
        "is_efficient": bool(abs(efficiency_ratio - 1.0) <= 0.05),
        "exponential_family": bool(exp_family_info.get("is_exp_family", False)),
    }


# ── 9. sufficient_statistic ───────────────────────────────────────────────────

_SUFFICIENT_STATS: Dict[str, Dict[str, Any]] = {
    "poisson": {
        "statistic": "sum(x_i)  [total count]",
        "formula": "T(x) = sum_{i=1}^{n} x_i",
        "is_sufficient": True,
        "explanation": (
            "By the Fisher-Neyman factorisation theorem, T(x) = sum(x_i) is "
            "sufficient for the Poisson rate lambda: the likelihood factors as "
            "f(x|lambda) = g(T(x), lambda) * h(x) with h(x) = prod(1/x_i!). "
            "T(x)/n = xbar is the MLE and UMVUE."
        ),
    },
    "normal_mu": {
        "statistic": "sample mean  xbar = mean(x_i)",
        "formula": "T(x) = (1/n) sum x_i  [or equivalently sum(x_i)]",
        "is_sufficient": True,
        "explanation": (
            "For Normal(mu, sigma^2) with sigma^2 known, T(x) = sum(x_i) is "
            "sufficient for mu. The likelihood factors via the exponential family "
            "structure with natural parameter mu/sigma^2 and sufficient statistic "
            "sum(x_i). xbar = T(x)/n is the MLE and is efficient."
        ),
    },
    "normal_sigma": {
        "statistic": "sum of squared deviations  S^2 = sum((x_i - xbar)^2)",
        "formula": "T(x) = sum_{i=1}^{n} (x_i - xbar)^2",
        "is_sufficient": True,
        "explanation": (
            "For Normal(mu, sigma^2) with mu known, T(x) = sum((x_i - mu)^2) "
            "is sufficient for sigma^2. When mu is unknown, the pair "
            "(sum(x_i), sum(x_i^2)) is jointly sufficient for (mu, sigma^2)."
        ),
    },
    "binomial": {
        "statistic": "sum(x_i)  [total successes]",
        "formula": "T(x) = sum_{i=1}^{n} x_i",
        "is_sufficient": True,
        "explanation": (
            "For Bernoulli(theta) observations, T(x) = sum(x_i) counts total "
            "successes and is sufficient for theta. The MLE theta_hat = T(x)/n "
            "depends on data only through T(x)."
        ),
    },
    "gamma": {
        "statistic": "(sum(x_i), sum(log(x_i)))  [for shape and rate]",
        "formula": "T(x) = (sum x_i, sum log(x_i))",
        "is_sufficient": True,
        "explanation": (
            "Gamma(alpha, beta) is a two-parameter exponential family. "
            "The pair (sum(x_i), sum(log(x_i))) is jointly sufficient for "
            "(alpha, beta). If alpha is known, sum(x_i) alone is sufficient "
            "for the rate beta."
        ),
    },
}


def sufficient_statistic(dist: str) -> Dict[str, Any]:
    """
    Return the sufficient statistic for a distribution.

    By the Fisher-Neyman factorisation theorem, T(x) is sufficient for theta
    iff the likelihood factors as f(x|theta) = g(T(x), theta) * h(x).
    For exponential families, the natural sufficient statistic is always
    sufficient.

    Supported: "normal_mu", "normal_sigma", "poisson", "binomial", "gamma".

    Args:
        dist: Distribution name.

    Returns:
        dict with statistic, formula, is_sufficient (True), explanation.
    """
    if dist not in _SUFFICIENT_STATS:
        raise ValueError(
            f"dist='{dist}' not supported. Choose from: {sorted(_SUFFICIENT_STATS)}"
        )
    return dict(_SUFFICIENT_STATS[dist])


# ── 10. neyman_factorization ──────────────────────────────────────────────────

_NEYMAN_FACTS: Dict[str, Dict[str, Any]] = {
    "poisson": {
        "is_sufficient": True,
        "T_x": "sum(x_i)",
        "h_x": "prod(1 / x_i!)",
        "g_t_theta": "exp(-n*theta) * theta^T  where T = sum(x_i)",
        "explanation": (
            "Poisson(theta): f(x|theta) = prod[theta^x_i * exp(-theta) / x_i!] "
            "= [prod(1/x_i!)] * [theta^sum(x_i) * exp(-n*theta)]. "
            "h(x) = prod(1/x_i!) depends only on x; g depends on x only via T=sum(x_i)."
        ),
    },
    "normal": {
        "is_sufficient": True,
        "T_x": "sum(x_i)  [or equivalently xbar]",
        "h_x": "(2*pi*sigma^2)^{-n/2} * exp(-sum(x_i^2) / (2*sigma^2))",
        "g_t_theta": "exp(theta * sum(x_i) / sigma^2 - n*theta^2 / (2*sigma^2))",
        "explanation": (
            "Normal(theta, sigma^2) with sigma^2 known: T(x)=sum(x_i) is sufficient "
            "for theta by the exponential family factorisation. h(x) absorbs the "
            "sum(x_i^2) term; g depends on x only through sum(x_i)."
        ),
    },
    "binomial": {
        "is_sufficient": True,
        "T_x": "sum(x_i)  [total successes]",
        "h_x": "prod C(1, x_i) = 1  [for Bernoulli observations]",
        "g_t_theta": "theta^sum(x_i) * (1-theta)^(n - sum(x_i))",
        "explanation": (
            "Bernoulli(theta) observations: f(x|theta) = theta^sum(x_i) * (1-theta)^(n-sum(x_i)). "
            "h(x)=1; g depends on x only through T=sum(x_i)."
        ),
    },
    "gamma": {
        "is_sufficient": True,
        "T_x": "(sum(x_i), sum(log(x_i)))",
        "h_x": "1  [base measure on (0, inf)^n]",
        "g_t_theta": "beta^(n*alpha) / Gamma(alpha)^n * exp(-beta*sum(x_i) + (alpha-1)*sum(log(x_i)))",
        "explanation": (
            "Gamma(alpha, beta) two-parameter exponential family. "
            "The pair T(x) = (sum(x_i), sum(log(x_i))) is jointly sufficient. "
            "h(x)=1; g absorbs all theta-dependence through T(x)."
        ),
    },
}


def neyman_factorization(dist: str, statistic: str) -> Dict[str, Any]:
    """
    Apply the Fisher-Neyman factorisation theorem to verify a sufficient statistic.

    The theorem states: T(x) is sufficient for theta iff the likelihood factors as
      f(x | theta) = g(T(x), theta) * h(x)
    where h does not depend on theta.

    For exponential family distributions (Poisson, Normal, Binomial, Gamma),
    the natural sufficient statistic always satisfies the factorisation.

    Args:
        dist:      One of "poisson", "normal", "binomial", "gamma".
        statistic: The claimed sufficient statistic (e.g. "sum", "mean").
                   Currently any non-empty string is accepted for supported
                   distributions — the factorisation is returned analytically.

    Returns:
        dict with is_sufficient, h_x, g_t_theta, T_x, explanation.
    """
    if dist not in _NEYMAN_FACTS:
        raise ValueError(
            f"dist='{dist}' not supported. Choose from: {sorted(_NEYMAN_FACTS)}"
        )
    if not statistic:
        raise ValueError("statistic must be a non-empty string")
    return dict(_NEYMAN_FACTS[dist])
