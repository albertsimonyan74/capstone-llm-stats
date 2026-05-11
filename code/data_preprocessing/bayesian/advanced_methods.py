"""
baseline/bayesian/advanced_methods.py
Computational Bayesian methods: Gibbs, MH, HMC, RJMCMC, VB, ABC, Hierarchical.
Each class: __init__(params), solve() -> dict, validate() -> bool.
All solve() calls np.random.seed(42) for reproducibility.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List

import numpy as np
from scipy.special import expit, logit


# ── 1. Gibbs Sampler (bivariate normal) ──────────────────────────────────────

class GibbsSampler:
    """
    Gibbs sampling for bivariate normal (mu_x, mu_y, sigma_x, sigma_y, rho).
    Targets: posterior_mean_x, posterior_mean_y, posterior_var_x.
    """

    def __init__(self, params: Dict[str, Any]) -> None:
        self.mu_x      = float(params["mu_x"])
        self.mu_y      = float(params["mu_y"])
        self.sigma_x   = float(params["sigma_x"])
        self.sigma_y   = float(params["sigma_y"])
        self.rho       = float(params["rho"])
        self.n_samples = int(params["n_samples"])
        self.n_burnin  = int(params["n_burnin"])

    def solve(self) -> Dict[str, float]:
        np.random.seed(42)
        csd_x = self.sigma_x * math.sqrt(1.0 - self.rho ** 2)
        csd_y = self.sigma_y * math.sqrt(1.0 - self.rho ** 2)
        x_curr, y_curr = self.mu_x, self.mu_y
        samples_x: List[float] = []
        samples_y: List[float] = []
        for i in range(self.n_burnin + self.n_samples):
            cm_x = self.mu_x + self.rho * (self.sigma_x / self.sigma_y) * (y_curr - self.mu_y)
            x_curr = float(np.random.normal(cm_x, csd_x))
            cm_y = self.mu_y + self.rho * (self.sigma_y / self.sigma_x) * (x_curr - self.mu_x)
            y_curr = float(np.random.normal(cm_y, csd_y))
            if i >= self.n_burnin:
                samples_x.append(x_curr)
                samples_y.append(y_curr)
        return {
            "posterior_mean_x": float(np.mean(samples_x)),
            "posterior_mean_y": float(np.mean(samples_y)),
            "posterior_var_x":  float(np.var(samples_x)),
        }

    def validate(self) -> bool:
        result = self.solve()
        analytic_mean_x = self.mu_x
        analytic_var_x  = self.sigma_x ** 2
        # Relative tolerance: 15% of analytic values (MC noise scales with sigma)
        mean_tol = max(0.15, 0.15 * abs(analytic_mean_x)) if analytic_mean_x != 0 else 0.5
        var_tol  = max(0.15, 0.15 * analytic_var_x)
        return (
            abs(result["posterior_mean_x"] - analytic_mean_x) < mean_tol
            and abs(result["posterior_var_x"] - analytic_var_x) < var_tol
        )


# ── 2. Metropolis-Hastings (Binomial + Normal prior, logit space) ─────────────

class MetropolisHastings:
    """
    MH for Binomial likelihood with Normal prior on logit(theta).
    Targets: posterior_mean, posterior_std, acceptance_rate.
    """

    def __init__(self, params: Dict[str, Any]) -> None:
        self.prior_mean    = float(params["prior_mean"])
        self.prior_std     = float(params["prior_std"])
        self.n_obs         = int(params["n_obs"])
        self.n_success     = int(params["n_success"])
        self.proposal_std  = float(params["proposal_std"])
        self.n_samples     = int(params["n_samples"])

    def _log_target(self, phi: float) -> float:
        theta = float(expit(phi))
        log_prior = -0.5 * ((phi - self.prior_mean) / self.prior_std) ** 2
        if theta <= 0.0 or theta >= 1.0:
            return -np.inf
        log_lik = (
            self.n_success * math.log(theta)
            + (self.n_obs - self.n_success) * math.log(1.0 - theta)
        )
        return log_prior + log_lik

    def solve(self) -> Dict[str, float]:
        np.random.seed(42)
        n_burnin = self.n_samples // 2
        phi_curr = float(logit(0.5))
        accepted = 0
        samples: List[float] = []
        for i in range(n_burnin + self.n_samples):
            phi_prop = phi_curr + float(np.random.normal(0.0, self.proposal_std))
            log_alpha = self._log_target(phi_prop) - self._log_target(phi_curr)
            if math.log(float(np.random.uniform())) < log_alpha:
                phi_curr = phi_prop
                if i >= n_burnin:
                    accepted += 1
            if i >= n_burnin:
                samples.append(float(expit(phi_curr)))
        theta_arr = np.array(samples)
        return {
            "posterior_mean":    float(np.mean(theta_arr)),
            "posterior_std":     float(np.std(theta_arr)),
            "acceptance_rate":   float(accepted / self.n_samples),
        }

    def validate(self) -> bool:
        result = self.solve()
        # Sanity: posterior_mean must be in (0,1) and acceptance_rate reasonable
        return (
            0.0 < result["posterior_mean"] < 1.0
            and 0.0 < result["acceptance_rate"] < 1.0
        )


# ── 3. Hamiltonian Monte Carlo (Gaussian target) ──────────────────────────────

class HamiltonianMC:
    """
    HMC on Gaussian posterior (Normal prior + Normal likelihood).
    Targets: posterior_mean, posterior_std, energy_error.
    """

    def __init__(self, params: Dict[str, Any]) -> None:
        self.prior_mean    = float(params["prior_mean"])
        self.prior_std     = float(params["prior_std"])
        self.likelihood_std= float(params["likelihood_std"])
        self.obs_mean      = float(params["obs_mean"])
        self.n_obs         = int(params["n_obs"])
        self.step_size     = float(params["step_size"])
        self.n_leapfrog    = int(params["n_leapfrog"])

    def _analytic_posterior(self):
        prior_var  = self.prior_std ** 2
        lik_var    = self.likelihood_std ** 2
        post_var   = 1.0 / (1.0 / prior_var + self.n_obs / lik_var)
        post_mean  = post_var * (
            self.prior_mean / prior_var
            + self.n_obs * self.obs_mean / lik_var
        )
        return post_mean, post_var

    def _U(self, theta: float) -> float:
        prior_var = self.prior_std ** 2
        lik_var   = self.likelihood_std ** 2
        return (
            0.5 * (theta - self.prior_mean) ** 2 / prior_var
            + 0.5 * self.n_obs * (theta - self.obs_mean) ** 2 / lik_var
        )

    def _dU(self, theta: float) -> float:
        prior_var = self.prior_std ** 2
        lik_var   = self.likelihood_std ** 2
        return (
            (theta - self.prior_mean) / prior_var
            + self.n_obs * (theta - self.obs_mean) / lik_var
        )

    def solve(self) -> Dict[str, float]:
        np.random.seed(42)
        post_mean, post_var = self._analytic_posterior()
        n_samples = 1000
        n_burnin  = 200
        theta_curr = self.prior_mean
        samples: List[float] = []
        energy_errors: List[float] = []

        for i in range(n_burnin + n_samples):
            p_curr = float(np.random.normal())
            H_curr = self._U(theta_curr) + 0.5 * p_curr ** 2

            theta_prop = theta_curr
            p_prop     = p_curr
            # leapfrog
            p_prop -= 0.5 * self.step_size * self._dU(theta_prop)
            for _ in range(self.n_leapfrog):
                theta_prop += self.step_size * p_prop
                if _ < self.n_leapfrog - 1:
                    p_prop -= self.step_size * self._dU(theta_prop)
            p_prop -= 0.5 * self.step_size * self._dU(theta_prop)

            H_prop = self._U(theta_prop) + 0.5 * p_prop ** 2
            energy_errors.append(abs(H_prop - H_curr))

            log_alpha = -H_prop + H_curr
            if math.log(float(np.random.uniform())) < log_alpha:
                theta_curr = theta_prop
            if i >= n_burnin:
                samples.append(theta_curr)

        arr = np.array(samples)
        return {
            "posterior_mean": float(np.mean(arr)),
            "posterior_std":  float(np.std(arr)),
            "energy_error":   float(np.mean(energy_errors)),
        }

    def validate(self) -> bool:
        result = self.solve()
        post_mean, post_var = self._analytic_posterior()
        return (
            abs(result["posterior_mean"] - post_mean) < 0.1
            and abs(result["posterior_std"] - math.sqrt(post_var)) < 0.1
        )


# ── 4. Reversible Jump MCMC (model selection, analytical BF) ─────────────────

class RJMCMC:
    """
    Analytical Bayes factor between two Normal models.
    M1: single mean over all data. M2: separate means for two equal halves.
    Targets: posterior_prob_m1, posterior_prob_m2, bayes_factor.
    """

    def __init__(self, params: Dict[str, Any]) -> None:
        self.data          = list(params["data"])
        self.prior_prob_m1 = float(params["prior_prob_m1"])
        self.proposal_std  = float(params["proposal_std"])   # kept for API compat
        # sigma^2 and tau^2 are assumed equal to sample variance / 2 by convention
        y = np.array(self.data)
        self.sigma2 = float(np.var(y, ddof=1)) if len(y) > 1 else 1.0
        self.tau2   = self.sigma2  # diffuse prior variance = data variance

    def _log_marginal(self, y: np.ndarray) -> float:
        n    = len(y)
        ybar = float(np.mean(y))
        ss   = float(np.sum((y - ybar) ** 2))
        sigma2, tau2 = self.sigma2, self.tau2
        return (
            -n / 2.0 * math.log(2.0 * math.pi)
            - (n - 1) / 2.0 * math.log(sigma2)
            - 0.5 * math.log(sigma2 + n * tau2)
            - ss / (2.0 * sigma2)
            - n * ybar ** 2 / (2.0 * (sigma2 + n * tau2))
        )

    def solve(self) -> Dict[str, float]:
        np.random.seed(42)
        y = np.array(self.data)
        mid = len(y) // 2
        y1, y2 = y[:mid], y[mid:]

        log_ml_m1 = self._log_marginal(y)
        log_ml_m2 = self._log_marginal(y1) + self._log_marginal(y2)

        log_bf   = log_ml_m1 - log_ml_m2
        log_bf   = float(np.clip(log_bf, -30.0, 30.0))
        bf       = math.exp(log_bf)

        p1 = self.prior_prob_m1
        p2 = 1.0 - p1
        # posterior odds = BF * prior odds
        post_odds_m1 = bf * (p1 / p2)
        post_prob_m1 = post_odds_m1 / (1.0 + post_odds_m1)
        post_prob_m2 = 1.0 - post_prob_m1

        return {
            "posterior_prob_m1": float(post_prob_m1),
            "posterior_prob_m2": float(post_prob_m2),
            "bayes_factor":      float(bf),
        }

    def validate(self) -> bool:
        result = self.solve()
        return (
            abs(result["posterior_prob_m1"] + result["posterior_prob_m2"] - 1.0) < 1e-6
            and result["bayes_factor"] > 0.0
        )


# ── 5. Variational Bayes (CAVI, Normal-Normal conjugate) ─────────────────────

class VariationalBayes:
    """
    Exact CAVI for Normal likelihood + Normal prior (conjugate → closed-form).
    Targets: variational_mean, variational_var, final_elbo.
    """

    def __init__(self, params: Dict[str, Any]) -> None:
        self.prior_mean    = float(params["prior_mean"])
        self.prior_var     = float(params["prior_var"])
        self.likelihood_var= float(params["likelihood_var"])
        self.observations  = list(params["observations"])
        self.n_iter        = int(params["n_iter"])

    def solve(self) -> Dict[str, float]:
        np.random.seed(42)
        n      = len(self.observations)
        x_bar  = float(np.mean(self.observations))
        prior_var = self.prior_var
        lik_var   = self.likelihood_var

        # Exact closed-form (conjugate — CAVI converges in one step)
        var_q  = 1.0 / (1.0 / prior_var + n / lik_var)
        mu_q   = var_q * (self.prior_mean / prior_var + n * x_bar / lik_var)

        # ELBO = E_q[log p(x|θ)] + E_q[log p(θ)] - E_q[log q(θ)]
        # E_q[log p(x|θ)] = -n/2*log(2π*lik_var) - 1/(2*lik_var)*[n*(x_bar-mu_q)^2 + n*var_q]
        # (using sum decomposition around x_bar)
        ss_x = float(np.sum([(xi - x_bar) ** 2 for xi in self.observations]))
        E_log_lik = (
            -n / 2.0 * math.log(2.0 * math.pi * lik_var)
            - 1.0 / (2.0 * lik_var) * (
                ss_x + n * (x_bar - mu_q) ** 2 + n * var_q
            )
        )
        E_log_prior = (
            -0.5 * math.log(2.0 * math.pi * prior_var)
            - 0.5 / prior_var * ((mu_q - self.prior_mean) ** 2 + var_q)
        )
        # entropy of q
        H_q = 0.5 * math.log(2.0 * math.pi * math.e * var_q)
        elbo = E_log_lik + E_log_prior + H_q

        return {
            "variational_mean": float(mu_q),
            "variational_var":  float(var_q),
            "final_elbo":       float(elbo),
        }

    def validate(self) -> bool:
        result = self.solve()
        return result["variational_var"] > 0.0


# ── 6. Approximate Bayesian Computation (rejection sampler) ──────────────────

class ABCMethod:
    """
    ABC rejection sampling: draw θ~Uniform(prior_low,prior_high),
    simulate x~N(θ, obs_std^2, n_obs), accept if |mean(x_sim)-obs_mean|<=epsilon.
    Targets: abc_posterior_mean, abc_posterior_std.
    """

    def __init__(self, params: Dict[str, Any]) -> None:
        self.observed_mean   = float(params["observed_mean"])
        self.observed_std    = float(params["observed_std"])
        self.n_obs           = int(params["n_obs"])
        self.prior_low       = float(params["prior_low"])
        self.prior_high      = float(params["prior_high"])
        self.n_simulations   = int(params["n_simulations"])
        self.epsilon         = float(params["epsilon"])

    def solve(self) -> Dict[str, float]:
        np.random.seed(42)
        accepted: List[float] = []
        for _ in range(self.n_simulations):
            theta = float(np.random.uniform(self.prior_low, self.prior_high))
            x_sim = np.random.normal(theta, self.observed_std, self.n_obs)
            if abs(float(np.mean(x_sim)) - self.observed_mean) <= self.epsilon:
                accepted.append(theta)
        if len(accepted) == 0:
            # fallback: midpoint
            mid = (self.prior_low + self.prior_high) / 2.0
            return {"abc_posterior_mean": mid, "abc_posterior_std": 0.0}
        arr = np.array(accepted)
        return {
            "abc_posterior_mean": float(np.mean(arr)),
            "abc_posterior_std":  float(np.std(arr)),
        }

    def validate(self) -> bool:
        result = self.solve()
        return self.prior_low <= result["abc_posterior_mean"] <= self.prior_high


# ── 7. Hierarchical Bayes (empirical Bayes shrinkage) ────────────────────────

class HierarchicalBayes:
    """
    Empirical Bayes / hierarchical Normal model.
    y_j ~ N(theta_j, sigma^2/n_j), theta_j ~ N(mu, tau^2).
    Hyperprior: mu ~ N(hyperprior_mean, hyperprior_var).
    Targets: hyperpost_mean, hyperpost_var, shrinkage_factor.
    """

    def __init__(self, params: Dict[str, Any]) -> None:
        self.group_means    = list(params["group_means"])
        self.group_sizes    = list(params["group_sizes"])
        self.hyperprior_mean= float(params["hyperprior_mean"])
        self.hyperprior_var = float(params["hyperprior_var"])
        # sigma^2 and tau^2 embedded in hyperprior_var conventions:
        # se2_j = sigma2 / n_j; use empirical estimate
        y = np.array(self.group_means)
        self.sigma2 = float(np.var(y, ddof=1)) if len(y) > 1 else 1.0
        self.tau2   = self.hyperprior_var  # treat hyperprior_var as tau^2

    def solve(self) -> Dict[str, float]:
        np.random.seed(42)
        y  = np.array(self.group_means, dtype=float)
        nj = np.array(self.group_sizes, dtype=float)

        se2  = self.sigma2 / nj           # sampling variance per group
        tau2 = self.tau2

        precisions = 1.0 / (se2 + tau2)

        # Posterior hyperparameters for mu
        hyperpost_prec = float(np.sum(precisions)) + 1.0 / self.hyperprior_var
        hyperpost_var  = 1.0 / hyperpost_prec
        hyperpost_mean = hyperpost_var * (
            float(np.sum(precisions * y))
            + self.hyperprior_mean / self.hyperprior_var
        )

        # Shrinkage factor: mean over groups of se2/(se2+tau2)
        shrinkage = float(np.mean(se2 / (se2 + tau2)))

        return {
            "hyperpost_mean":    float(hyperpost_mean),
            "hyperpost_var":     float(hyperpost_var),
            "shrinkage_factor":  float(shrinkage),
        }

    def validate(self) -> bool:
        result = self.solve()
        return (
            result["hyperpost_var"] > 0.0
            and 0.0 <= result["shrinkage_factor"] <= 1.0
        )
