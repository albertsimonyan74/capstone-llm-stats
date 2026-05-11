# baseline/bayesian/bayesian_regression.py
"""
Bayesian linear regression with Normal-Inverse-Gamma conjugate prior.

Model:
    y = X β + ε,  ε ~ N(0, σ² I)
Prior:
    β | σ² ~ N(μ₀, σ² Λ₀⁻¹)   (Λ₀ is the prior precision matrix)
    σ²     ~ IG(a₀, b₀)         (Inverse-Gamma, b₀ is scale)

Posterior (closed form):
    Λ_n = Λ₀ + X'X
    μ_n = Λ_n⁻¹ (Λ₀ μ₀ + X'y)
    a_n = a₀ + n/2
    b_n = b₀ + ½(y'y + μ₀'Λ₀μ₀ − μ_n'Λ_nμ_n)

Predictive (new point x_new):
    y_new | x_new, data ~ t(2 a_n, x_new' μ_n, sqrt(b_n/a_n · (1 + x_new' Λ_n⁻¹ x_new)))

References:
  Bolstad (2007) "Introduction to Bayesian Statistics", ch 14.
  Lee (2012) "Bayesian Statistics: An Introduction", §6.3.
  Hoff (2009) "A First Course in Bayesian Statistical Methods", §9.2.
  Bishop (2006) "Pattern Recognition and Machine Learning", §3.3.
"""
from __future__ import annotations

from typing import Any, Dict, Tuple

import numpy as np
from scipy import stats


def normal_inverse_gamma_regression_update(
    X: np.ndarray,
    y: np.ndarray,
    mu0: np.ndarray,
    Lambda0: np.ndarray,
    a0: float,
    b0: float,
) -> Dict[str, Any]:
    """
    Conjugate Normal-Inverse-Gamma posterior update for Bayesian linear regression.

    Prior:
        β | σ² ~ N(μ₀, σ² Λ₀⁻¹)
        σ²     ~ IG(a₀, b₀)

    Posterior hyperparameters:
        Λ_n = Λ₀ + X'X
        μ_n = Λ_n⁻¹ (Λ₀ μ₀ + X'y)
        a_n = a₀ + n/2
        b_n = b₀ + ½(y'y + μ₀'Λ₀μ₀ − μ_n'Λ_nμ_n)

    Posterior means:
        E[β | data]  = μ_n
        E[σ² | data] = b_n / (a_n − 1)  [requires a_n > 1]

    With a very diffuse prior (Λ₀ → 0), μ_n converges to the OLS estimate.

    Reference: Bolstad (2007) ch 14; Hoff (2009) §9.2; Bishop (2006) §3.3.

    Args:
        X:       Design matrix of shape (n, p).  Include a column of 1s for intercept.
        y:       Response vector of shape (n,).
        mu0:     Prior mean vector of shape (p,).
        Lambda0: Prior precision matrix of shape (p, p).  Use a small multiple
                 of the identity for a diffuse prior.
        a0:      Prior IG shape (> 0).
        b0:      Prior IG scale (> 0).

    Returns:
        dict with keys:
            mu_n               — posterior mean of β (shape p,)
            Lambda_n           — posterior precision matrix (shape p×p)
            a_n                — posterior IG shape
            b_n                — posterior IG scale
            beta_hat_ols       — OLS estimate (X'X)⁻¹X'y
            posterior_mean_beta — same as mu_n (convenience alias)
            posterior_var_sigma2 — E[σ² | data] = b_n/(a_n-1) if a_n > 1, else NaN

    Raises:
        ValueError: if dimensions are inconsistent or a0/b0 <= 0.
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float).ravel()
    mu0 = np.asarray(mu0, dtype=float).ravel()
    Lambda0 = np.asarray(Lambda0, dtype=float)

    n, p = X.shape
    if y.shape[0] != n:
        raise ValueError(f"X has {n} rows but y has {y.shape[0]} elements")
    if mu0.shape[0] != p:
        raise ValueError(f"mu0 length {mu0.shape[0]} != p={p}")
    if Lambda0.shape != (p, p):
        raise ValueError(f"Lambda0 must be ({p},{p}), got {Lambda0.shape}")
    if a0 <= 0 or b0 <= 0:
        raise ValueError(f"a0 and b0 must be > 0, got a0={a0}, b0={b0}")

    XtX = X.T @ X
    Xty = X.T @ y

    Lambda_n = Lambda0 + XtX
    Lambda_n_inv = np.linalg.solve(Lambda_n, np.eye(p))
    mu_n = Lambda_n_inv @ (Lambda0 @ mu0 + Xty)

    a_n = a0 + n / 2.0
    b_n = (b0
           + 0.5 * (y @ y + mu0 @ Lambda0 @ mu0 - mu_n @ Lambda_n @ mu_n))

    # OLS estimate
    XtX_inv = np.linalg.solve(XtX, np.eye(p)) if n >= p else np.linalg.pinv(XtX)
    beta_ols = XtX_inv @ Xty

    post_var_sigma2 = float(b_n / (a_n - 1)) if a_n > 1 else float("nan")

    return {
        "mu_n":                mu_n,
        "Lambda_n":            Lambda_n,
        "a_n":                 float(a_n),
        "b_n":                 float(b_n),
        "beta_hat_ols":        beta_ols,
        "posterior_mean_beta": mu_n,
        "posterior_var_sigma2": post_var_sigma2,
    }


def bayesian_regression_predict(
    x_new: np.ndarray,
    mu_n: np.ndarray,
    Lambda_n: np.ndarray,
    a_n: float,
    b_n: float,
    n: int,
) -> Dict[str, Any]:
    """
    Predictive distribution for a new observation under the Normal-Inverse-Gamma model.

    The marginal predictive distribution integrating out β and σ² is a Student-t:
        y_new | x_new, data ~ t(df=2 a_n, loc=x_new' μ_n,
                                 scale=sqrt(b_n/a_n · (1 + x_new' Λ_n⁻¹ x_new)))

    The 95% predictive interval uses the t quantiles.

    Reference: Bishop (2006) §3.3.2; Bolstad (2007) ch 14.

    Args:
        x_new:    Feature vector for the new point (shape p,).  Include 1 for intercept.
        mu_n:     Posterior mean of β (shape p,).
        Lambda_n: Posterior precision matrix (shape p×p).
        a_n:      Posterior IG shape.
        b_n:      Posterior IG scale.
        n:        Number of training observations (used for degrees of freedom).

    Returns:
        dict with keys: pred_mean, pred_var, pred_interval_95 (tuple).
    """
    x_new = np.asarray(x_new, dtype=float).ravel()
    mu_n = np.asarray(mu_n, dtype=float).ravel()
    Lambda_n = np.asarray(Lambda_n, dtype=float)

    pred_mean = float(x_new @ mu_n)

    # Variance: b_n/a_n * (1 + x_new' Λ_n⁻¹ x_new)
    Lambda_n_inv_x = np.linalg.solve(Lambda_n, x_new)
    x_Lam_x = float(x_new @ Lambda_n_inv_x)
    pred_var = float((b_n / a_n) * (1.0 + x_Lam_x))
    pred_scale = float(pred_var ** 0.5)

    df = 2.0 * a_n
    lo, hi = stats.t.interval(0.95, df=df, loc=pred_mean, scale=pred_scale)

    return {
        "pred_mean":        pred_mean,
        "pred_var":         pred_var,
        "pred_interval_95": (float(lo), float(hi)),
    }
