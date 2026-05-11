# baseline/bayesian/ground_truth.py
from __future__ import annotations
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from data_preprocessing.bayesian.conjugate_models import beta_binomial_update, gamma_poisson_update, normal_known_var_update
from data_preprocessing.bayesian.normal_gamma import normal_gamma_update
from data_preprocessing.bayesian.dirichlet_multinomial import dirichlet_multinomial_update
from data_preprocessing.bayesian.posterior_predictive import (
    beta_binomial_predictive_pmf,
    gamma_poisson_predictive_pmf,
    dirichlet_multinomial_predictive_pmf,
    dirichlet_predictive_next,
)
from data_preprocessing.bayesian.bayes_estimators import (
    bayes_estimator_from_beta,
    bayes_estimator_from_gamma_shape_rate,
    bayes_estimator_from_normal,
    bayes_estimator_from_student_t,
)


def gt_beta_binomial(
    alpha: float,
    beta: float,
    x: int,
    n: int,
    ci_level: float = 0.95,
    predictive_k: Optional[int] = None,
    predictive_m: Optional[int] = None,
) -> Dict[str, Any]:
    post = beta_binomial_update(alpha=alpha, beta=beta, x=x, n=n)
    ci = post.credible_interval(level=ci_level)

    out = {
        "posterior_family": "Beta",
        "alpha_post": post.alpha_post,
        "beta_post": post.beta_post,
        "posterior_mean": post.mean(),
        "posterior_var": post.var(),
        "ci_level": ci_level,
        "ci_lower": ci.lower,
        "ci_upper": ci.upper,
        "posterior_predictive_p_success_next": post.posterior_predictive_prob_success_next(),
    }

    if predictive_k is not None and predictive_m is not None:
        out["predictive_pmf_k_m"] = beta_binomial_predictive_pmf(
            k=predictive_k, m=predictive_m, alpha_post=post.alpha_post, beta_post=post.beta_post
        )
        out["predictive_k"] = predictive_k
        out["predictive_m"] = predictive_m

    return out


def gt_gamma_poisson(
    alpha: float,
    rate: float,
    counts: List[int],
    ci_level: float = 0.95,
    predictive_y: Optional[int] = None,
) -> Dict[str, Any]:
    post = gamma_poisson_update(alpha=alpha, rate=rate, counts=counts)
    ci = post.credible_interval(level=ci_level)

    out = {
        "posterior_family": "Gamma",
        "alpha_post": post.alpha_post,
        "rate_post": post.rate_post,
        "posterior_mean": post.mean(),
        "posterior_var": post.var(),
        "ci_level": ci_level,
        "ci_lower": ci.lower,
        "ci_upper": ci.upper,
        "posterior_predictive_mean_next": post.posterior_predictive_mean_next(),
    }

    if predictive_y is not None:
        out["predictive_pmf_y"] = gamma_poisson_predictive_pmf(
            y=predictive_y, alpha_post=post.alpha_post, beta_post=post.rate_post
        )
        out["predictive_y"] = predictive_y

    return out


def gt_normal_known_var(
    mu0: float,
    tau0_2: float,
    sigma2: float,
    data: List[float],
    ci_level: float = 0.95,
) -> Dict[str, Any]:
    post = normal_known_var_update(mu0=mu0, tau0_2=tau0_2, sigma2=sigma2, data=data)
    ci = post.credible_interval(level=ci_level)

    return {
        "posterior_family": "Normal",
        "mu_n": post.mu_n,
        "tau_n2": post.tau_n2,
        "posterior_mean": post.mean(),
        "posterior_var": post.var(),
        "ci_level": ci_level,
        "ci_lower": ci.lower,
        "ci_upper": ci.upper,
    }


def gt_normal_gamma_precision(
    mu0: float,
    kappa0: float,
    alpha0: float,
    beta0: float,
    data: List[float],
    ci_level: float = 0.95,
) -> Dict[str, Any]:
    post = normal_gamma_update(mu0=mu0, kappa0=kappa0, alpha0=alpha0, beta0=beta0, data=data)
    ci_mu = post.credible_interval_mu_marginal(level=ci_level)
    ci_tau = post.credible_interval_tau(level=ci_level)
    ci_sigma2 = post.credible_interval_sigma2(level=ci_level)

    return {
        "posterior_family": "Normal-Gamma",
        "mu_n": post.mu_n,
        "kappa_n": post.kappa_n,
        "alpha_n": post.alpha_n,
        "beta_n": post.beta_n,
        "posterior_mean_mu": post.posterior_mean_mu(),
        "posterior_mean_tau": post.posterior_mean_tau(),
        "posterior_mean_sigma2": post.posterior_mean_sigma2(),
        "ci_level": ci_level,
        "ci_mu_lower": ci_mu.lower,
        "ci_mu_upper": ci_mu.upper,
        "ci_tau_lower": ci_tau.lower,
        "ci_tau_upper": ci_tau.upper,
        "ci_sigma2_lower": ci_sigma2.lower,
        "ci_sigma2_upper": ci_sigma2.upper,
    }


def gt_dirichlet_multinomial(
    alpha: List[float],
    counts: List[int],
    predictive_counts: Optional[List[int]] = None,
) -> Dict[str, Any]:
    post = dirichlet_multinomial_update(alpha=alpha, counts=counts)
    alpha_post = post["posterior_alpha"]
    mean_vec = post["posterior_mean"]
    concentration = sum(alpha_post)

    out = {
        "posterior_family": "Dirichlet",
        "alpha_post": [float(x) for x in alpha_post],
        "posterior_mean_vector": [float(x) for x in mean_vec],
        "concentration": float(concentration),
        "predictive_next_probs": [float(x) for x in dirichlet_predictive_next(alpha_post)],
    }

    if predictive_counts is not None:
        out["predictive_counts"] = predictive_counts
        out["predictive_pmf_counts"] = dirichlet_multinomial_predictive_pmf(predictive_counts, alpha_post)

    return out


# -------------------------
# Decision theory: closed-form estimator targets
# -------------------------

def gt_bayes_estimator_beta(alpha_post: float, beta_post: float, loss: str) -> Dict[str, Any]:
    est = bayes_estimator_from_beta(alpha_post, beta_post, loss)  # type: ignore[arg-type]
    return {"loss": est.loss, "estimator": est.estimator, "value": est.value, "notes": est.notes}

def gt_bayes_estimator_gamma(alpha_post: float, rate_post: float, loss: str) -> Dict[str, Any]:
    est = bayes_estimator_from_gamma_shape_rate(alpha_post, rate_post, loss)  # type: ignore[arg-type]
    return {"loss": est.loss, "estimator": est.estimator, "value": est.value, "notes": est.notes}

def gt_bayes_estimator_normal(mu: float, var: float, loss: str) -> Dict[str, Any]:
    est = bayes_estimator_from_normal(mu, var, loss)  # type: ignore[arg-type]
    return {"loss": est.loss, "estimator": est.estimator, "value": est.value, "notes": est.notes}

def gt_bayes_estimator_student_t(loc: float, scale: float, df: float, loss: str) -> Dict[str, Any]:
    est = bayes_estimator_from_student_t(loc, scale, df, loss)  # type: ignore[arg-type]
    return {"loss": est.loss, "estimator": est.estimator, "value": est.value, "notes": est.notes}