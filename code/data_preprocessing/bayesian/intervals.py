# baseline/bayesian/intervals.py
from __future__ import annotations
from typing import Tuple
from dataclasses import dataclass

import numpy as np
from scipy import stats

from data_preprocessing.bayesian.utils import CredibleInterval


def _validate_level(level: float) -> None:
    if not (0 < level < 1):
        raise ValueError(f"level must be in (0, 1), got {level}")


def beta_credible_interval(alpha: float, beta: float, level: float = 0.95) -> CredibleInterval:
    _validate_level(level)
    lo = stats.beta.ppf((1 - level) / 2, alpha, beta)
    hi = stats.beta.ppf(1 - (1 - level) / 2, alpha, beta)
    return CredibleInterval(level=level, lower=float(lo), upper=float(hi))

def gamma_credible_interval(alpha: float, rate: float, level: float = 0.95) -> CredibleInterval:
    _validate_level(level)
    # SciPy gamma uses "scale" = 1/rate
    scale = 1.0 / rate
    lo = stats.gamma.ppf((1 - level) / 2, a=alpha, scale=scale)
    hi = stats.gamma.ppf(1 - (1 - level) / 2, a=alpha, scale=scale)
    return CredibleInterval(level=level, lower=float(lo), upper=float(hi))

def normal_credible_interval(mu: float, var: float, level: float = 0.95) -> CredibleInterval:
    _validate_level(level)
    sd = var ** 0.5
    lo, hi = stats.norm.interval(level, loc=mu, scale=sd)
    return CredibleInterval(level=level, lower=float(lo), upper=float(hi))


# ── A1 — HPD Credible Intervals ───────────────────────────────────────────────

def hpd_credible_interval(
    samples: np.ndarray,
    level: float = 0.95,
) -> tuple:
    """
    Highest Posterior Density (HPD) interval via the sorted-window method.

    The HPD interval is the shortest interval [lo, hi] that contains at least
    ``level`` fraction of the posterior mass.  For a unimodal, symmetric
    posterior (e.g. Normal) it coincides with the equal-tail interval; for
    skewed posteriors it is strictly shorter.

    Algorithm: sort the samples, then slide a window of size
    ceil(level * n) across the sorted array and return the window with the
    smallest width (hi − lo).

    Reference: Hoff (2009) §2.3; Lee (2012) §2.6.

    Args:
        samples: 1-D array of posterior draws.
        level:   Nominal coverage (default 0.95).

    Returns:
        (lower, upper) as floats.
    """
    _validate_level(level)
    samples = np.asarray(samples, dtype=float).ravel()
    if samples.size < 2:
        raise ValueError("Need at least 2 samples for HPD estimation.")
    sorted_s = np.sort(samples)
    n = len(sorted_s)
    n_included = int(np.ceil(level * n))
    # widths of all windows of exactly n_included consecutive sorted samples
    widths = sorted_s[n_included - 1:] - sorted_s[:n - n_included + 1]
    idx = int(np.argmin(widths))
    return float(sorted_s[idx]), float(sorted_s[idx + n_included - 1])


def beta_hpd_interval(
    alpha: float,
    beta: float,
    level: float = 0.95,
) -> tuple:
    """
    HPD credible interval for a Beta(alpha, beta) posterior.

    Generates 100 000 Beta samples and applies ``hpd_credible_interval``.
    For symmetric Beta distributions (alpha == beta) the result matches the
    equal-tail interval to within sampling error; for skewed distributions
    the HPD interval is strictly shorter.

    Reference: Lee (2012) §2.6; Bolstad (2007) §8.

    Args:
        alpha: First shape parameter (> 0).
        beta:  Second shape parameter (> 0).
        level: Nominal coverage (default 0.95).

    Returns:
        (lower, upper) as floats.
    """
    _validate_level(level)
    samples = stats.beta.rvs(alpha, beta, size=100_000, random_state=42)
    return hpd_credible_interval(samples, level)


def normal_hpd_interval(
    mu: float,
    sigma: float,
    level: float = 0.95,
) -> tuple:
    """
    HPD credible interval for a Normal(mu, sigma) posterior.

    Because the Normal distribution is symmetric and unimodal, the HPD
    interval coincides exactly with the equal-tail credible interval:
    [mu − z * sigma, mu + z * sigma]  where z = Φ⁻¹((1+level)/2).

    Reference: Lee (2012) §2.6.

    Args:
        mu:    Posterior mean.
        sigma: Posterior standard deviation (not variance).
        level: Nominal coverage (default 0.95).

    Returns:
        (lower, upper) as floats.
    """
    _validate_level(level)
    lo, hi = stats.norm.interval(level, loc=mu, scale=sigma)
    return float(lo), float(hi)


# ── B3 — Confidence Interval vs Credible Interval Comparison ─────────────────

def compare_ci_vs_credible_normal(
    mu0: float,
    tau0_sq: float,
    sigma_sq: float,
    data: list,
    level: float = 0.95,
) -> dict:
    """
    Compute both a frequentist confidence interval and a Bayesian credible
    interval for the mean of a Normal population with known variance.

    Frequentist 95% CI (z-interval, sigma known):
        x̄ ± z_{α/2} · σ/√n

    Bayesian 95% credible interval (Normal-Normal conjugate):
        μ_n ± z_{α/2} · √τ_n²
    where μ_n and τ_n² are the posterior mean and variance from
    ``normal_known_var_update``.

    With a very diffuse prior (large τ₀²) the two intervals converge to the
    same result.  With an informative prior the Bayesian interval is narrower
    and centred at a compromise between the prior mean and the data mean.

    Reference: Bolstad (2007) ch 9 & 12; Lee (2012) §2.6.2.

    Args:
        mu0:      Prior mean.
        tau0_sq:  Prior variance (τ₀²).  Use a large value for a diffuse prior.
        sigma_sq: Known likelihood variance (σ²).
        data:     Observed data (list of floats, non-empty).
        level:    Nominal coverage (default 0.95).

    Returns:
        dict with keys:
            freq_ci, bayes_credible, posterior_mean, freq_center,
            width_freq, width_bayes, intervals_overlap, interpretation_note.
    """
    _validate_level(level)
    if not data:
        raise ValueError("data must be non-empty")
    if tau0_sq <= 0:
        raise ValueError("tau0_sq must be > 0")
    if sigma_sq <= 0:
        raise ValueError("sigma_sq must be > 0")

    arr = np.asarray(data, dtype=float)
    n = len(arr)
    xbar = float(np.mean(arr))
    z = float(stats.norm.ppf(1.0 - (1.0 - level) / 2))

    # Frequentist z-interval (known sigma)
    margin_freq = z * (sigma_sq ** 0.5) / (n ** 0.5)
    freq_lo = xbar - margin_freq
    freq_hi = xbar + margin_freq

    # Bayesian Normal-Normal posterior
    prec0 = 1.0 / tau0_sq
    prec_lik = n / sigma_sq
    tau_n2 = 1.0 / (prec0 + prec_lik)
    mu_n = tau_n2 * (prec0 * mu0 + prec_lik * xbar)
    margin_bayes = z * (tau_n2 ** 0.5)
    bayes_lo = mu_n - margin_bayes
    bayes_hi = mu_n + margin_bayes

    overlap = bool(freq_lo <= bayes_hi and bayes_lo <= freq_hi)

    return {
        "freq_ci":            (float(freq_lo), float(freq_hi)),
        "bayes_credible":     (float(bayes_lo), float(bayes_hi)),
        "posterior_mean":     float(mu_n),
        "freq_center":        float(xbar),
        "width_freq":         float(freq_hi - freq_lo),
        "width_bayes":        float(bayes_hi - bayes_lo),
        "intervals_overlap":  overlap,
        "interpretation_note": (
            "Frequentist 95% CI: in repeated sampling, 95% of such intervals "
            "would contain the true mu (a statement about the procedure, not "
            "about this specific interval). "
            "Bayesian 95% credible interval: given the prior and data, "
            "P(mu in [lo, hi] | data) = 0.95 (a direct probability statement "
            "about the parameter)."
        ),
    }