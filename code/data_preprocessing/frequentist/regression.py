# baseline/frequentist/regression.py
"""
Simple linear regression (OLS) for the capstone benchmark.

Model: Y_i = A + B * x_i + epsilon_i,  epsilon_i ~ N(0, sigma^2) i.i.d.

OLS estimators (closed form):
  B_hat = Sxy / Sxx          where Sxy = sum((x_i-xbar)(y_i-ybar)),
                                    Sxx = sum((x_i-xbar)^2)
  A_hat = ybar - B_hat * xbar

Residual variance (unbiased):
  s^2 = SSR / (n-2)          where SSR = sum((y_i - A_hat - B_hat*x_i)^2)

Confidence intervals (level alpha):
  A_hat +/- t_{n-2, alpha/2} * se(A_hat)
  B_hat +/- t_{n-2, alpha/2} * se(B_hat)

  se(B_hat) = sqrt(s^2 / Sxx)
  se(A_hat) = sqrt(s^2 * (1/n + xbar^2/Sxx))
"""
from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
from scipy.stats import t as t_dist


def _validate_xy(x: List[float], y: List[float]) -> Tuple[np.ndarray, np.ndarray]:
    xa = np.asarray(x, dtype=float)
    ya = np.asarray(y, dtype=float)
    if xa.ndim != 1 or ya.ndim != 1:
        raise ValueError("x and y must be 1-D")
    if len(xa) != len(ya):
        raise ValueError(f"x and y must have the same length, got {len(xa)} vs {len(ya)}")
    if len(xa) < 3:
        raise ValueError(f"Need at least 3 observations for regression, got {len(xa)}")
    if np.var(xa) == 0:
        raise ValueError("x has zero variance; OLS undefined")
    return xa, ya


def ols_estimators(x: List[float], y: List[float]) -> Dict[str, float]:
    """
    Compute OLS slope and intercept for simple linear regression Y = A + B*x.

    Args:
        x: Predictor values (length >= 3, non-constant).
        y: Response values (same length as x).

    Returns:
        dict with A_hat (intercept) and B_hat (slope).
    """
    xa, ya = _validate_xy(x, y)
    xbar = float(np.mean(xa))
    ybar = float(np.mean(ya))
    Sxx = float(np.sum((xa - xbar) ** 2))
    Sxy = float(np.sum((xa - xbar) * (ya - ybar)))
    B_hat = Sxy / Sxx
    A_hat = ybar - B_hat * xbar
    return {"A_hat": float(A_hat), "B_hat": float(B_hat)}


def residual_variance(x: List[float], y: List[float]) -> float:
    """
    Compute the unbiased residual variance s^2 = SSR / (n-2).

    Args:
        x: Predictor values.
        y: Response values.

    Returns:
        s^2 — unbiased estimate of the error variance sigma^2.
    """
    xa, ya = _validate_xy(x, y)
    ests = ols_estimators(x, y)
    A_hat, B_hat = ests["A_hat"], ests["B_hat"]
    residuals = ya - (A_hat + B_hat * xa)
    ssr = float(np.sum(residuals ** 2))
    n = len(xa)
    return ssr / (n - 2)


def credibility_intervals(
    x: List[float],
    y: List[float],
    level: float = 0.95,
) -> Dict[str, float]:
    """
    Compute confidence intervals for A_hat and B_hat at the given level.

    Uses the t-distribution with n-2 degrees of freedom.

    Args:
        x:     Predictor values.
        y:     Response values.
        level: Confidence level in (0, 1). Default 0.95.

    Returns:
        dict with A_lower, A_upper, B_lower, B_upper, s2, A_hat, B_hat.
    """
    if not (0 < level < 1):
        raise ValueError(f"level must be in (0, 1), got {level}")
    xa, ya = _validate_xy(x, y)
    ests = ols_estimators(x, y)
    A_hat, B_hat = ests["A_hat"], ests["B_hat"]
    s2 = residual_variance(x, y)
    n = len(xa)
    xbar = float(np.mean(xa))
    Sxx = float(np.sum((xa - xbar) ** 2))

    se_B = float(np.sqrt(s2 / Sxx))
    se_A = float(np.sqrt(s2 * (1.0 / n + xbar ** 2 / Sxx)))

    alpha = 1.0 - level
    t_crit = float(t_dist.ppf(1.0 - alpha / 2.0, df=n - 2))

    return {
        "A_hat":   float(A_hat),
        "B_hat":   float(B_hat),
        "s2":      float(s2),
        "A_lower": float(A_hat - t_crit * se_A),
        "A_upper": float(A_hat + t_crit * se_A),
        "B_lower": float(B_hat - t_crit * se_B),
        "B_upper": float(B_hat + t_crit * se_B),
        "t_crit":  t_crit,
        "se_A":    se_A,
        "se_B":    se_B,
    }
