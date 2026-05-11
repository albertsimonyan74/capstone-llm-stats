# baseline/bayesian/posterior_predictive.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
import numpy as np
from scipy import stats

from data_preprocessing.bayesian.dirichlet_multinomial import dirichlet_multinomial_pmf
from data_preprocessing.bayesian.utils import require_int_nonnegative, require_positive


# ---- Beta–Binomial predictive ----

def beta_binomial_predictive_pmf(k: int, m: int, alpha_post: float, beta_post: float) -> float:
    require_int_nonnegative(k, "k")
    require_int_nonnegative(m, "m")
    if k > m:
        return 0.0
    require_positive(alpha_post, "alpha_post")
    require_positive(beta_post, "beta_post")
    return float(stats.betabinom.pmf(k, m, alpha_post, beta_post))


# ---- Gamma–Poisson predictive (Negative Binomial) ----
# If lambda ~ Gamma(alpha, rate=beta), then y ~ NegBin(r=alpha, p=beta/(beta+1))
# with pmf: C(y+r-1,y) * p^r * (1-p)^y

def gamma_poisson_predictive_pmf(y: int, alpha_post: float, beta_post: float) -> float:
    require_int_nonnegative(y, "y")
    require_positive(alpha_post, "alpha_post")
    require_positive(beta_post, "beta_post")
    r = alpha_post
    p = beta_post / (beta_post + 1.0)
    return float(stats.nbinom.pmf(y, n=r, p=p))


# ---- Dirichlet–Multinomial predictive ----

def dirichlet_multinomial_predictive_pmf(counts: List[int], alpha_post: List[float]) -> float:
    # multi-trial predictive for a vector of counts
    return float(dirichlet_multinomial_pmf(counts, alpha_post))

def dirichlet_predictive_next(alpha_post: List[float]) -> List[float]:
    a = np.asarray(alpha_post, dtype=float)
    probs = a / float(np.sum(a))
    return [float(x) for x in probs]


# ---- Normal (known variance) predictive ----

def normal_known_var_predictive_pdf(y_new: float, mu_n: float, tau_n2: float, sigma2: float) -> float:
    """
    Posterior predictive PDF for a new observation under Normal-Normal conjugacy
    with known likelihood variance.

    If  μ | data ~ N(μ_n, τ_n²)  and  Y_new | μ ~ N(μ, σ²),  then:
        Y_new | data ~ N(μ_n, τ_n² + σ²)

    Args:
        y_new:  New observation at which to evaluate the predictive density.
        mu_n:   Posterior mean of μ.
        tau_n2: Posterior variance of μ.
        sigma2: Known likelihood variance σ².

    Returns:
        Predictive PDF value p(y_new | data).
    """
    require_positive(tau_n2, "tau_n2")
    require_positive(sigma2, "sigma2")
    pred_var = tau_n2 + sigma2
    return float(stats.norm.pdf(y_new, loc=mu_n, scale=pred_var ** 0.5))


# ---- Normal-Gamma predictive ----

def normal_gamma_predictive_pdf(
    y_new: float,
    mu_n: float,
    kappa_n: float,
    alpha_n: float,
    beta_n: float,
) -> float:
    """
    Posterior predictive PDF for a new observation under the Normal-Gamma conjugate model.

    If  (μ, τ) | data ~ NormalGamma(μ_n, κ_n, α_n, β_n),  then the marginal
    predictive for Y_new is a Student-t:

        Y_new | data ~ t(df=2α_n, loc=μ_n, scale=√(β_n(κ_n+1)/(κ_n·α_n)))

    Args:
        y_new:   New observation at which to evaluate the predictive density.
        mu_n:    Posterior mean hyperparameter.
        kappa_n: Posterior pseudo-count hyperparameter (κ_n > 0).
        alpha_n: Posterior shape hyperparameter (α_n > 0).
        beta_n:  Posterior rate hyperparameter (β_n > 0).

    Returns:
        Predictive PDF value p(y_new | data).
    """
    require_positive(kappa_n, "kappa_n")
    require_positive(alpha_n, "alpha_n")
    require_positive(beta_n, "beta_n")
    df = 2.0 * alpha_n
    scale = (beta_n * (kappa_n + 1) / (kappa_n * alpha_n)) ** 0.5
    return float(stats.t.pdf(y_new, df=df, loc=mu_n, scale=scale))


# ── A4 — Posterior Predictive Checks ─────────────────────────────────────────

def posterior_predictive_check(
    observed_stat: float,
    posterior_samples: np.ndarray,
    predictive_sampler,
    test_statistic,
    n_rep: int = 1000,
    seed: int = 42,
) -> dict:
    """
    Generic posterior predictive check (PPC).

    For each posterior sample theta_i:
      1. Draw y_rep ~ p(y | theta_i) via predictive_sampler(theta_i, rng).
      2. Compute T(y_rep) via test_statistic(y_rep).

    The Bayesian p-value is P(T(y_rep) ≤ T_obs): small values indicate the
    observation falls in the lower tail of the predictive distribution
    (surprisingly small relative to what the model expects).

    A model is declared to "pass" if 0.05 < p_value < 0.95, i.e. the
    observed statistic is not in an extreme tail of the predictive
    distribution.

    Reference: Hoff (2009) §4.4; Carlin & Louis (2008) §2.5.

    Args:
        observed_stat:       Observed test statistic T(y_obs).
        posterior_samples:   Array of posterior draws (shape: n_post,).
        predictive_sampler:  Callable(theta, rng) → replicated dataset y_rep.
        test_statistic:      Callable(y_rep) → scalar T.
        n_rep:               Not used (samples drive replication count); kept
                             for API compatibility.
        seed:                Random seed for predictive_sampler calls.

    Returns:
        dict with: p_value, T_obs, T_rep_mean, T_rep_std,
                   T_rep_quantiles (dict), passed.
    """
    rng = np.random.default_rng(seed)
    T_rep = np.array([
        test_statistic(predictive_sampler(theta, rng))
        for theta in np.asarray(posterior_samples).ravel()
    ])
    p_value = float(np.mean(T_rep <= observed_stat))
    return {
        "p_value":    p_value,
        "T_obs":      float(observed_stat),
        "T_rep_mean": float(np.mean(T_rep)),
        "T_rep_std":  float(np.std(T_rep)),
        "T_rep_quantiles": {
            "0.025": float(np.quantile(T_rep, 0.025)),
            "0.5":   float(np.quantile(T_rep, 0.500)),
            "0.975": float(np.quantile(T_rep, 0.975)),
        },
        "passed": bool(0.05 < p_value < 0.95),
    }


def posterior_predictive_check_beta_binomial(
    alpha_post: float,
    beta_post: float,
    n_obs: int,
    x_obs: int,
    n_rep: int = 2000,
    seed: int = 42,
) -> dict:
    """
    Posterior predictive check for the Beta-Binomial conjugate model.

    For each of n_rep replicates:
      1. Draw theta_i ~ Beta(alpha_post, beta_post).
      2. Draw x_rep ~ Binomial(n_obs, theta_i).

    The Bayesian p-value P(x_rep ≤ x_obs) measures where the observed count
    falls in the predictive distribution.  Values near 0 or 1 indicate
    model-data conflict.

    Reference: Hoff (2009) §4.4; Ghosh et al (2006) §6.5.

    Args:
        alpha_post: Posterior Beta first shape parameter (> 0).
        beta_post:  Posterior Beta second shape parameter (> 0).
        n_obs:      Number of trials for replication.
        x_obs:      Observed number of successes (test statistic T(y_obs)).
        n_rep:      Number of posterior predictive replicates.
        seed:       Random seed.

    Returns:
        dict with: p_value, T_obs, T_rep_mean, T_rep_std,
                   T_rep_quantiles, passed.
    """
    require_positive(alpha_post, "alpha_post")
    require_positive(beta_post, "beta_post")
    require_int_nonnegative(n_obs, "n_obs")
    require_int_nonnegative(x_obs, "x_obs")
    rng = np.random.default_rng(seed)
    thetas = rng.beta(alpha_post, beta_post, size=n_rep)
    x_reps = rng.binomial(n_obs, thetas)
    p_value = float(np.mean(x_reps <= x_obs))
    return {
        "p_value":    p_value,
        "T_obs":      float(x_obs),
        "T_rep_mean": float(np.mean(x_reps)),
        "T_rep_std":  float(np.std(x_reps)),
        "T_rep_quantiles": {
            "0.025": float(np.quantile(x_reps, 0.025)),
            "0.5":   float(np.quantile(x_reps, 0.500)),
            "0.975": float(np.quantile(x_reps, 0.975)),
        },
        "passed": bool(0.05 < p_value < 0.95),
    }