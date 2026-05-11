# baseline/bayesian/normal_gamma.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List
import math

from scipy import stats

from data_preprocessing.bayesian.utils import require_positive, CredibleInterval


@dataclass(frozen=True)
class NormalGammaPosterior:
    """
    Normal-Gamma conjugate posterior for Normal likelihood with unknown mean and precision.

    Likelihood:
      x_i | (mu, tau) ~ Normal(mu, 1/tau)

    Prior:
      tau ~ Gamma(alpha0, beta0)              # shape-rate
      mu | tau ~ Normal(mu0, 1/(kappa0 * tau))

    Posterior:
      tau | data ~ Gamma(alpha_n, beta_n)     # shape-rate
      mu | tau, data ~ Normal(mu_n, 1/(kappa_n * tau))

    Marginal:
      mu | data ~ Student-t(df = 2*alpha_n, loc = mu_n, scale = sqrt(beta_n/(kappa_n*alpha_n)))
    """
    mu_n: float
    kappa_n: float
    alpha_n: float
    beta_n: float  # rate

    def posterior_mean_mu(self) -> float:
        return self.mu_n

    def posterior_mean_tau(self) -> float:
        # E[tau] exists for alpha_n > 0
        return self.alpha_n / self.beta_n

    def posterior_mean_sigma2(self) -> float:
        # sigma^2 = 1/tau ; E[sigma^2] exists for alpha_n > 1
        if self.alpha_n <= 1:
            return float("nan")
        return self.beta_n / (self.alpha_n - 1)

    def credible_interval_mu_marginal(self, level: float = 0.95) -> CredibleInterval:
        df = 2 * self.alpha_n
        scale = math.sqrt(self.beta_n / (self.kappa_n * self.alpha_n))
        lo = stats.t.ppf((1 - level) / 2, df=df, loc=self.mu_n, scale=scale)
        hi = stats.t.ppf(1 - (1 - level) / 2, df=df, loc=self.mu_n, scale=scale)
        return CredibleInterval(level=level, lower=float(lo), upper=float(hi))

    def credible_interval_tau(self, level: float = 0.95) -> CredibleInterval:
        # tau ~ Gamma(shape=alpha_n, rate=beta_n)
        # SciPy: gamma(a, scale=1/rate)
        scale = 1.0 / self.beta_n
        lo = stats.gamma.ppf((1 - level) / 2, a=self.alpha_n, scale=scale)
        hi = stats.gamma.ppf(1 - (1 - level) / 2, a=self.alpha_n, scale=scale)
        return CredibleInterval(level=level, lower=float(lo), upper=float(hi))
    
    def credible_interval_sigma2(self, level: float = 0.95) -> CredibleInterval:
        """
        Since tau ~ Gamma(alpha_n, rate=beta_n),
        sigma^2 = 1/tau ~ Inv-Gamma(alpha_n, scale=beta_n) in a consistent rate-based setup.

        In SciPy, invgamma uses parameters:
          invgamma(a=shape, scale=scale)
        Here scale = beta_n (rate-based conjugacy result for 1/tau).
        """
        lo = stats.invgamma.ppf((1 - level) / 2, a=self.alpha_n, scale=self.beta_n)
        hi = stats.invgamma.ppf(1 - (1 - level) / 2, a=self.alpha_n, scale=self.beta_n)
        return CredibleInterval(level=level, lower=float(lo), upper=float(hi))


def normal_gamma_update(
    mu0: float,
    kappa0: float,
    alpha0: float,
    beta0: float,   # rate
    data: List[float],
) -> NormalGammaPosterior:
    # Parameterization note (cf. Lecture 16):
    #   kappa0 here is the prior pseudo-count for the mean (also written λ0
    #   or n0 in some textbooks). It controls how strongly the prior mean μ0
    #   is weighted relative to the data mean.
    #   beta0 is the RATE parameter of the Gamma prior on precision τ
    #   (i.e. beta0 = 1/scale). Some textbooks use the scale parameterization
    #   instead — do not confuse them when comparing update formulas.
    require_positive(kappa0, "kappa0")
    require_positive(alpha0, "alpha0")
    require_positive(beta0, "beta0")
    if not data:
        raise ValueError("data must be non-empty")

    n = len(data)
    xbar = sum(data) / n
    ss = sum((x - xbar) ** 2 for x in data)  # sum of squares around xbar

    kappa_n = kappa0 + n
    mu_n = (kappa0 * mu0 + n * xbar) / kappa_n
    alpha_n = alpha0 + n / 2.0

    # shape-rate update
    beta_n = beta0 + 0.5 * ss + (kappa0 * n * (xbar - mu0) ** 2) / (2.0 * kappa_n)

    return NormalGammaPosterior(
        mu_n=float(mu_n),
        kappa_n=float(kappa_n),
        alpha_n=float(alpha_n),
        beta_n=float(beta_n),
    )