# baseline/bayesian/conjugate_models.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import math

import numpy as np
from scipy import stats
from scipy.stats import ks_2samp

from data_preprocessing.bayesian.utils import require_positive, require_nonnegative, require_int_nonnegative
from data_preprocessing.bayesian.intervals import beta_credible_interval, gamma_credible_interval, normal_credible_interval
from data_preprocessing.bayesian.utils import CredibleInterval


# -------------------------
# Beta-Binomial
# -------------------------

@dataclass(frozen=True)
class BetaBinomialPosterior:
    alpha_post: float
    beta_post: float

    def mean(self) -> float:
        return self.alpha_post / (self.alpha_post + self.beta_post)

    def var(self) -> float:
        a, b = self.alpha_post, self.beta_post
        denom = (a + b) ** 2 * (a + b + 1)
        return (a * b) / denom

    def credible_interval(self, level: float = 0.95) -> CredibleInterval:
        return beta_credible_interval(self.alpha_post, self.beta_post, level=level)

    def posterior_predictive_prob_success_next(self) -> float:
        # P(X_next=1 | data) = E[p | data]
        return self.mean()


def beta_binomial_update(alpha: float, beta: float, x: int, n: int) -> BetaBinomialPosterior:
    require_positive(alpha, "alpha")
    require_positive(beta, "beta")
    require_int_nonnegative(x, "x")
    require_int_nonnegative(n, "n")
    if x > n:
        raise ValueError("x cannot exceed n")

    a_post = alpha + x
    b_post = beta + (n - x)
    return BetaBinomialPosterior(alpha_post=float(a_post), beta_post=float(b_post))


# -------------------------
# Gamma-Poisson
# -------------------------

@dataclass(frozen=True)
class GammaPoissonPosterior:
    alpha_post: float
    rate_post: float  # rate parameter (beta in some texts)

    def mean(self) -> float:
        return self.alpha_post / self.rate_post

    def var(self) -> float:
        return self.alpha_post / (self.rate_post ** 2)

    def credible_interval(self, level: float = 0.95) -> CredibleInterval:
        return gamma_credible_interval(self.alpha_post, self.rate_post, level=level)

    def posterior_predictive_mean_next(self) -> float:
        # For Poisson-gamma mixture, predictive mean = posterior mean of lambda
        return self.mean()


def gamma_poisson_update(alpha: float, rate: float, counts: List[int]) -> GammaPoissonPosterior:
    require_positive(alpha, "alpha")
    require_positive(rate, "rate")
    if not counts:
        raise ValueError("counts must be non-empty")
    for i, c in enumerate(counts):
        require_int_nonnegative(c, f"counts[{i}]")

    sum_x = sum(counts)
    n = len(counts)
    a_post = alpha + sum_x
    rate_post = rate + n
    return GammaPoissonPosterior(alpha_post=float(a_post), rate_post=float(rate_post))


# -------------------------
# Normal-Normal (known variance)
# Prior: mu ~ N(mu0, tau0^2), Likelihood: x_i ~ N(mu, sigma^2) with sigma^2 known
# Posterior: mu | data ~ N(mu_n, tau_n^2)
# -------------------------

@dataclass(frozen=True)
class NormalKnownVarPosterior:
    mu_n: float
    tau_n2: float

    def mean(self) -> float:
        return self.mu_n

    def var(self) -> float:
        return self.tau_n2

    def credible_interval(self, level: float = 0.95) -> CredibleInterval:
        return normal_credible_interval(self.mu_n, self.tau_n2, level=level)


def binomial_uniform_prior_update(x: int, n: int) -> BetaBinomialPosterior:
    """
    Posterior for Binomial(n, theta) likelihood with a Uniform(0, 1) prior on theta.

    Uniform(0, 1) = Beta(1, 1), so this is a shortcut for beta_binomial_update
    with alpha=1, beta=1. The posterior is Beta(1 + x, 1 + n - x).

    Lecture 21 example: the simplest conjugate case — a "flat" prior that
    assigns equal probability to all theta in (0, 1). The posterior mean
    is (x+1)/(n+2), which shrinks the MLE x/n toward 0.5 and avoids
    the boundary estimates of 0 or 1 when x=0 or x=n.

    Args:
        x: Number of successes observed. Must be an integer in [0, n].
        n: Number of trials. Must be a non-negative integer.

    Returns:
        BetaBinomialPosterior with alpha_post = 1 + x, beta_post = 1 + n - x.
    """
    return beta_binomial_update(alpha=1.0, beta=1.0, x=x, n=n)


def normal_known_var_update(mu0: float, tau0_2: float, sigma2: float, data: List[float]) -> NormalKnownVarPosterior:
    require_positive(tau0_2, "tau0_2")
    require_positive(sigma2, "sigma2")
    if not data:
        raise ValueError("data must be non-empty")

    n = len(data)
    xbar = sum(data) / n

    # precision form
    prec0 = 1.0 / tau0_2
    preclik = n / sigma2
    tau_n2 = 1.0 / (prec0 + preclik)
    mu_n = tau_n2 * (prec0 * mu0 + preclik * xbar)

    return NormalKnownVarPosterior(mu_n=float(mu_n), tau_n2=float(tau_n2))


# ── Concept 6 — Gamma additive property ──────────────────────────────────────

def verify_gamma_additive(
    alpha1: float,
    alpha2: float,
    n_sim: int = 10_000,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Verify that Gamma(alpha1,1) + Gamma(alpha2,1) ~ Gamma(alpha1+alpha2, 1).

    If X ~ Gamma(alpha1, beta) and Y ~ Gamma(alpha2, beta) independently,
    then X + Y ~ Gamma(alpha1 + alpha2, beta). This is verified via KS test.

    Args:
        alpha1, alpha2: Shape parameters (both > 0).
        n_sim:          Number of simulation draws.
        seed:           Random seed.

    Returns:
        dict with ks_statistic, p_value, is_additive (True if p_value > 0.05).
    """
    rng = np.random.default_rng(seed)
    x = rng.gamma(alpha1, 1.0, size=n_sim)
    y = rng.gamma(alpha2, 1.0, size=n_sim)
    sums = x + y
    # Draw from Gamma(alpha1+alpha2, 1) with a different seed offset
    rng2 = np.random.default_rng(seed + 1)
    direct = rng2.gamma(alpha1 + alpha2, 1.0, size=n_sim)
    ks_stat, p_val = ks_2samp(sums, direct)
    return {
        "ks_statistic": float(ks_stat),
        "p_value": float(p_val),
        "is_additive": bool(p_val > 0.05),
    }


# ── Concept 7 — Beta-Gamma connection ────────────────────────────────────────

def verify_beta_gamma_connection(
    alpha1: float,
    alpha2: float,
    n_sim: int = 10_000,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Verify that X/(X+Y) ~ Beta(alpha1, alpha2) when X~Gamma(alpha1,1), Y~Gamma(alpha2,1).

    This is the Gamma-Beta connection: if X and Y are independent Gamma random
    variables, the ratio X/(X+Y) follows a Beta distribution. Used to prove
    that the Dirichlet distribution is the multivariate generalisation.

    Args:
        alpha1, alpha2: Shape parameters.
        n_sim:          Number of simulation draws.
        seed:           Random seed.

    Returns:
        dict with ks_statistic, p_value, verified (True if p_value > 0.05).
    """
    rng = np.random.default_rng(seed)
    x = rng.gamma(alpha1, 1.0, size=n_sim)
    y = rng.gamma(alpha2, 1.0, size=n_sim)
    ratio = x / (x + y)
    rng2 = np.random.default_rng(seed + 1)
    beta_direct = rng2.beta(alpha1, alpha2, size=n_sim)
    ks_stat, p_val = ks_2samp(ratio, beta_direct)
    return {
        "ks_statistic": float(ks_stat),
        "p_value": float(p_val),
        "verified": bool(p_val > 0.05),
    }


# ── Concept 9 — Chi-squared additive property ────────────────────────────────

def verify_chi2_additive(
    df1: int,
    df2: int,
    n_sim: int = 10_000,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Verify that chi2(df1) + chi2(df2) ~ chi2(df1+df2).

    Chi-squared is a special case of Gamma: chi2(k) = Gamma(k/2, 1/2).
    The additive property follows directly from the Gamma additive property.

    Args:
        df1, df2: Degrees of freedom (both >= 1).
        n_sim:    Number of simulation draws.
        seed:     Random seed.

    Returns:
        dict with ks_statistic, p_value, is_additive (True if p_value > 0.05).
    """
    rng = np.random.default_rng(seed)
    x = rng.chisquare(df1, size=n_sim)
    y = rng.chisquare(df2, size=n_sim)
    sums = x + y
    rng2 = np.random.default_rng(seed + 1)
    direct = rng2.chisquare(df1 + df2, size=n_sim)
    ks_stat, p_val = ks_2samp(sums, direct)
    return {
        "ks_statistic": float(ks_stat),
        "p_value": float(p_val),
        "is_additive": bool(p_val > 0.05),
    }


# ── Concept 10 — Diffuse (flat) prior ────────────────────────────────────────

def flat_prior(theta: float, a: float, b: float) -> float:
    """
    Uniform (flat) prior density on [a, b].

    Returns 1/(b-a) if a <= theta <= b, else 0.

    Args:
        theta: Parameter value.
        a, b:  Support bounds (a < b).

    Returns:
        Prior density at theta.
    """
    if a >= b:
        raise ValueError(f"a must be < b, got a={a}, b={b}")
    if a <= theta <= b:
        return float(1.0 / (b - a))
    return 0.0


# ── Concept 11 — Improper priors ─────────────────────────────────────────────

def improper_prior_location(mu: float) -> float:
    """
    Improper flat prior for a location parameter: p(mu) ∝ 1.

    This prior assigns equal (unnormalisable) weight to all real values of mu.
    Combined with a Normal likelihood it yields a proper Normal posterior.

    Args:
        mu: Any real value.

    Returns:
        1.0 (unnormalised density, constant everywhere).
    """
    return 1.0


def improper_prior_scale(sigma: float) -> float:
    """
    Improper Jeffreys prior for a scale parameter: p(sigma) ∝ 1/sigma.

    Jeffreys prior for a scale parameter is p(sigma) = 1/sigma (sigma > 0).
    This is the invariant prior under multiplicative reparametrisation.

    Args:
        sigma: Scale parameter. Must be > 0.

    Returns:
        1/sigma.

    Raises:
        ValueError: if sigma <= 0.
    """
    if sigma <= 0:
        raise ValueError(f"sigma must be > 0 for improper scale prior, got {sigma}")
    return float(1.0 / sigma)


# ── Concept 12 — Improper prior yields proper posterior ──────────────────────

def posterior_with_flat_prior(
    mu: float,
    data: List[float],
    sigma: float = 1.0,
) -> float:
    """
    Posterior density for Normal mean with flat (improper) prior, normalised.

    With p(mu) ∝ 1 and data ~ N(mu, sigma^2), the posterior is:
      p(mu | data) ∝ L(mu | data) = prod_i N(x_i | mu, sigma^2)
                  ∝ N(mu | x_bar, sigma^2/n)

    This function returns the normalised posterior density, which is
    N(mu | x_bar, sigma^2/n). The posterior mean equals the sample mean
    (also the MLE), showing that the flat prior yields the likelihood-
    dominated posterior.

    Args:
        mu:    Evaluation point for the posterior density.
        data:  Observed data. Must be non-empty.
        sigma: Known standard deviation of each observation (default 1.0).

    Returns:
        p(mu | data) = N(mu; x_bar, sigma^2 / n).
    """
    if not data:
        raise ValueError("data must be non-empty")
    require_positive(sigma, "sigma")
    n = len(data)
    xbar = sum(data) / n
    post_var = (sigma ** 2) / n
    return float(stats.norm.pdf(mu, loc=xbar, scale=post_var ** 0.5))


# ── Concept 15 — Improper Beta(0,0) prior ────────────────────────────────────

def improper_beta_prior_update(s: int, n: int) -> Dict[str, Any]:
    """
    Posterior for Binomial(n, theta) with improper Beta(0,0) prior.

    The Beta(0,0) prior is improper (both shape parameters equal 0, which is
    outside the valid domain for a Beta distribution). After observing s
    successes in n trials, the posterior is Beta(s, n-s) — a Haldane prior
    result. The posterior mean is s/n = the MLE.

    Note: if s=0 or s=n the posterior Beta(0, n) or Beta(n, 0) is also
    improper (a warning is included in the returned dict).

    Lecture 21 reference: improper priors as limiting cases of proper priors.

    Args:
        s: Number of successes. Must satisfy 0 <= s <= n.
        n: Number of trials. Must be >= 0.

    Returns:
        dict with keys: prior, alpha, beta, posterior_mean, note.
    """
    if n < 0:
        raise ValueError(f"n must be >= 0, got {n}")
    if s < 0 or s > n:
        raise ValueError(f"s must be in [0, n], got s={s}, n={n}")
    alpha_post = s
    beta_post = n - s
    note = "proper posterior" if (0 < s < n) else "improper posterior (boundary: posterior is also improper)"
    posterior_mean = float(s / n) if n > 0 else float("nan")
    return {
        "prior": "Beta(0,0) improper",
        "alpha": alpha_post,
        "beta": beta_post,
        "posterior_mean": posterior_mean,
        "note": note,
    }


# ── A3 — Jeffreys Priors ──────────────────────────────────────────────────────

def jeffreys_prior_binomial(theta: float) -> float:
    """
    Jeffreys prior for the Binomial success probability theta.

    The Fisher information for Binomial(n, theta) is I(theta) = n/(theta(1-theta)).
    Jeffreys prior is proportional to sqrt(I(theta)):
        p(theta) ∝ theta^{-1/2} (1-theta)^{-1/2}  =  Beta(1/2, 1/2) density.

    This prior is invariant under reparametrisation of theta.

    Reference: Lee (2012) §3.3; Ghosh et al (2006) §5.1.2.

    Args:
        theta: Probability parameter in (0, 1).

    Returns:
        Beta(0.5, 0.5) density at theta (normalised).

    Raises:
        ValueError: if theta not in (0, 1).
    """
    if not (0 < theta < 1):
        raise ValueError(f"theta must be in (0,1), got {theta}")
    return float(stats.beta.pdf(theta, 0.5, 0.5))


def jeffreys_prior_poisson(lam: float) -> float:
    """
    Jeffreys prior for the Poisson rate lambda.

    The Fisher information for Poisson(lambda) is I(lambda) = 1/lambda.
    Jeffreys prior is proportional to sqrt(I(lambda)):
        p(lambda) ∝ lambda^{-1/2}   (improper Gamma(1/2, 0) prior).

    Returns the unnormalised density value 1/sqrt(lambda).

    Reference: Lee (2012) §3.3; Ghosh et al (2006) §5.1.3.

    Args:
        lam: Poisson rate (> 0).

    Returns:
        1/sqrt(lam).

    Raises:
        ValueError: if lam <= 0.
    """
    if lam <= 0:
        raise ValueError(f"lam must be > 0, got {lam}")
    return float(1.0 / math.sqrt(lam))


def jeffreys_prior_normal_mean(mu: float) -> float:
    """
    Jeffreys prior for a Normal mean with known variance.

    The Fisher information for N(mu, sigma^2) w.r.t. mu is I(mu) = 1/sigma^2,
    a constant.  The Jeffreys prior is therefore p(mu) ∝ constant (flat/improper).

    Returns 1.0 for any mu (unnormalised).

    Reference: Lee (2012) §3.3; Ghosh et al (2006) §5.1.4.

    Args:
        mu: Any real value.

    Returns:
        1.0 (unnormalised constant density).
    """
    return 1.0


def jeffreys_update_binomial(x: int, n: int) -> Dict[str, Any]:
    """
    Posterior for Binomial(n, theta) with Jeffreys prior Beta(0.5, 0.5).

    Posterior: theta | x, n ~ Beta(x + 0.5, n - x + 0.5).

    The Jeffreys prior Beta(0.5, 0.5) is preferred over the uniform Beta(1,1)
    because it is invariant under monotone reparametrisations of theta.
    It is also known as the arc-sine distribution on (0,1).

    Reference: Lee (2012) §3.3; Bolstad (2007) §9.

    Args:
        x: Number of successes (0 <= x <= n).
        n: Number of trials (>= 0).

    Returns:
        dict with keys: prior, alpha, beta, posterior_mean.
    """
    require_int_nonnegative(x, "x")
    require_int_nonnegative(n, "n")
    if x > n:
        raise ValueError(f"x must be <= n, got x={x}, n={n}")
    alpha_post = float(x) + 0.5
    beta_post = float(n - x) + 0.5
    return {
        "prior":          "Beta(0.5, 0.5) Jeffreys",
        "alpha":          alpha_post,
        "beta":           beta_post,
        "posterior_mean": alpha_post / (alpha_post + beta_post),
    }


# ── B2 — MLE vs MAP Comparison ───────────────────────────────────────────────

def mle_vs_map(
    dist: str,
    prior_params: dict,
    data,
) -> Dict[str, Any]:
    """
    Compare MLE, MAP, and posterior mean for conjugate Bayesian models.

    Supported distributions:
        "binomial" — data = {"x": int, "n": int}
                     prior_params = {"alpha": float, "beta": float}
        "poisson"  — data = list of non-negative integers
                     prior_params = {"alpha": float, "beta": float} (Gamma rate prior)
        "normal"   — data = list of floats, prior_params = {"mu0": float, "tau0_sq": float,
                     "sigma_sq": float}

    MAP is the mode of the posterior; posterior mean is E[theta | data].
    Shrinkage = (MLE - MAP) / (MLE - prior_mean), measuring how much the MAP
    moves from the MLE toward the prior mean.

    Reference: Bolstad (2007) §9; Bishop (2006) §3.3; Lee (2012) §3.

    Args:
        dist:         One of "binomial", "poisson", "normal".
        prior_params: Dict of prior hyperparameters (see above).
        data:         Observed data — dict for "binomial", list otherwise.

    Returns:
        dict with keys: mle, map, posterior_mean, prior_mean, n, shrinkage, note.
    """
    dist = dist.lower()
    if dist == "binomial":
        alpha = float(prior_params["alpha"])
        beta_p = float(prior_params["beta"])
        x = int(data["x"])
        n = int(data["n"])
        if n == 0:
            raise ValueError("n must be > 0 for binomial MLE")
        mle = x / n
        # MAP = mode of Beta(alpha+x, beta+n-x)
        # mode = (alpha+x-1) / (alpha+beta+n-2)  [valid when both params > 1]
        a_post = alpha + x
        b_post = beta_p + (n - x)
        if a_post > 1 and b_post > 1:
            map_est = (a_post - 1) / (a_post + b_post - 2)
        elif a_post <= 1:
            map_est = 0.0  # mode at boundary
        else:
            map_est = 1.0
        post_mean = a_post / (a_post + b_post)
        prior_mean = alpha / (alpha + beta_p)
        denom = mle - prior_mean
        shrinkage = float((mle - map_est) / denom) if abs(denom) > 1e-12 else 0.0
        note = "MAP shrinks toward prior mean; posterior mean shrinks further"

    elif dist == "poisson":
        alpha = float(prior_params["alpha"])
        beta_p = float(prior_params["beta"])
        arr = list(data)
        n = len(arr)
        s = sum(arr)
        mle = s / n
        a_post = alpha + s
        rate_post = beta_p + n
        # MAP = mode of Gamma(a_post, rate_post) = (a_post-1)/rate_post [a_post>=1]
        map_est = (a_post - 1) / rate_post if a_post >= 1 else 0.0
        post_mean = a_post / rate_post
        prior_mean = alpha / beta_p
        denom = mle - prior_mean
        shrinkage = float((mle - map_est) / denom) if abs(denom) > 1e-12 else 0.0
        note = "MAP shrinks toward prior mean; posterior mean shrinks further"

    elif dist == "normal":
        mu0 = float(prior_params["mu0"])
        tau0_sq = float(prior_params["tau0_sq"])
        sigma_sq = float(prior_params["sigma_sq"])
        arr = list(data)
        n = len(arr)
        mle = sum(arr) / n  # = xbar
        prec0 = 1.0 / tau0_sq
        prec_lik = n / sigma_sq
        tau_n2 = 1.0 / (prec0 + prec_lik)
        mu_n = tau_n2 * (prec0 * mu0 + prec_lik * mle)
        # For Normal, MAP = posterior mean (symmetric posterior)
        map_est = mu_n
        post_mean = mu_n
        prior_mean = mu0
        denom = mle - prior_mean
        shrinkage = float((mle - map_est) / denom) if abs(denom) > 1e-12 else 0.0
        note = "For Normal with conjugate Normal prior, MAP equals posterior mean"

    else:
        raise ValueError(f"Unsupported dist '{dist}'. Choose: binomial, poisson, normal")

    return {
        "mle":            float(mle),
        "map":            float(map_est),
        "posterior_mean": float(post_mean),
        "prior_mean":     float(prior_mean),
        "n":              int(n),
        "shrinkage":      shrinkage,
        "note":           note,
    }