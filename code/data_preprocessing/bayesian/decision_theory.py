# baseline/bayesian/decision_theory.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import numpy as np

@dataclass(frozen=True)
class BayesEstimatorResult:
    loss: str
    estimator: str
    value: float
    notes: str = ""

def bayes_estimator_from_samples(posterior_samples: np.ndarray, loss: str) -> BayesEstimatorResult:
    """
    Compute Bayes estimator for a scalar parameter given posterior samples.
    This is a practical baseline method that remains valid even when closed-form
    median is hard.

    loss:
      - "quadratic" -> posterior mean
      - "absolute"  -> posterior median
      - "0-1"       -> posterior mode approx via histogram density peak
    """
    samples = np.asarray(posterior_samples).astype(float)
    if samples.size == 0:
        raise ValueError("posterior_samples cannot be empty")

    loss = loss.lower().strip()

    if loss == "quadratic":
        return BayesEstimatorResult(loss=loss, estimator="posterior_mean", value=float(np.mean(samples)))
    if loss == "absolute":
        return BayesEstimatorResult(loss=loss, estimator="posterior_median", value=float(np.median(samples)))
    if loss in ("0-1", "0_1", "zero-one", "zero_one"):
        # crude mode estimate via histogram
        hist, edges = np.histogram(samples, bins=50, density=True)
        idx = int(np.argmax(hist))
        mode = 0.5 * (edges[idx] + edges[idx + 1])
        return BayesEstimatorResult(loss="0-1", estimator="posterior_mode_approx", value=float(mode), notes="histogram mode")
    raise ValueError("loss must be one of: quadratic, absolute, 0-1")

def mse_risk(theta_true: float, estimator_values: np.ndarray) -> float:
    """
    MSE risk estimate from repeated estimator samples:
      risk = E[(T - theta)^2]
    """
    ev = np.asarray(estimator_values).astype(float)
    if ev.size == 0:
        raise ValueError("estimator_values cannot be empty")
    return float(np.mean((ev - theta_true) ** 2))


def analytical_bayes_risk_quadratic(posterior_var: float) -> float:
    """
    Closed-form Bayes risk under quadratic loss for the posterior mean estimator.

    Under quadratic loss L(θ, δ) = (θ - δ)², the Bayes estimator is the
    posterior mean, and its Bayes risk equals the posterior variance:
      risk = E_posterior[(θ - E[θ|data])²] = Var(θ | data)

    Args:
        posterior_var: Posterior variance of θ given data.

    Returns:
        Bayes risk (= posterior_var).
    """
    if posterior_var < 0:
        raise ValueError(f"posterior_var must be >= 0, got {posterior_var}")
    return float(posterior_var)


def discrete_bayes_risk(risk_values: List[float], prior_probs: List[float]) -> float:
    """
    Compute Bayes risk for a discrete prior: B(delta) = sum_i R(delta, theta_i) * pi(theta_i).

    The Bayes risk is the prior-weighted average of the risk function across
    all values of theta in the discrete support. The estimator with the smallest
    Bayes risk is the Bayes estimator under that prior.

    Lecture 22 example: used to compare two estimators (e.g., delta_1 vs delta_2)
    under a discrete prior pi(theta_1), pi(theta_2) by computing B(delta_1)
    and B(delta_2) and selecting the smaller value.

    Args:
        risk_values:  R(delta, theta_i) for each theta_i in the support.
        prior_probs:  Prior probability pi(theta_i) for each theta_i.
                      Must be non-negative and sum to 1 (within tolerance).

    Returns:
        Bayes risk B(delta) = sum_i risk_values[i] * prior_probs[i].
    """
    if not risk_values or not prior_probs:
        raise ValueError("risk_values and prior_probs must be non-empty")
    if len(risk_values) != len(prior_probs):
        raise ValueError("risk_values and prior_probs must have the same length")
    if any(p < 0 for p in prior_probs):
        raise ValueError("all prior_probs must be >= 0")
    total = sum(prior_probs)
    if abs(total - 1.0) > 1e-6:
        raise ValueError(f"prior_probs must sum to 1, got {total:.6f}")

    return float(sum(r * p for r, p in zip(risk_values, prior_probs)))


def bias_variance_decomposition(theta_true: float, estimator_values: np.ndarray) -> dict:
    """
    Compute MSE = Bias^2 + Variance from repeated estimator evaluations.

    Given N draws of an estimator T(X) at a fixed true parameter theta:
      Bias     = E[T] - theta
      Variance = E[(T - E[T])^2]
      MSE      = E[(T - theta)^2] = Bias^2 + Variance

    The identity MSE = Bias^2 + Variance is verified numerically and a
    tolerance check is included.

    Lecture 25 example: used to compare d_1 = 2*mean(X) (unbiased, larger
    variance) against d_2 = max(X_i) (biased, smaller variance) for
    Uniform(0, theta), where the trade-off between bias and variance
    determines which estimator has lower MSE for a given n.

    Args:
        theta_true:       True value of the parameter.
        estimator_values: 1-D array of estimator draws T(X_1),...,T(X_N).
                          Must be non-empty.

    Returns:
        dict with keys:
          bias      – E[T] - theta  (signed)
          variance  – Var(T) = E[(T - E[T])^2]
          mse       – E[(T - theta)^2]
          bias_sq   – bias^2
          check_ok  – True if |mse - (bias^2 + variance)| < 1e-10
    """
    ev = np.asarray(estimator_values).astype(float)
    if ev.size == 0:
        raise ValueError("estimator_values cannot be empty")

    mean_t = float(np.mean(ev))
    bias = mean_t - theta_true
    variance = float(np.var(ev))          # population variance: E[(T - E[T])^2]
    mse = float(np.mean((ev - theta_true) ** 2))
    bias_sq = bias ** 2
    check_ok = abs(mse - (bias_sq + variance)) < 1e-10

    return {
        "bias": bias,
        "variance": variance,
        "mse": mse,
        "bias_sq": bias_sq,
        "check_ok": check_ok,
    }


# ── Loss presets ──────────────────────────────────────────────────────────────

_LOSS_PRESETS: Dict[str, Callable[[float, float], float]] = {
    "squared":  lambda e, t: (e - t) ** 2,
    "absolute": lambda e, t: abs(e - t),
    "0-1":      lambda e, t: 0.0 if abs(e - t) < 1e-6 else 1.0,
}


def _resolve_loss(loss_fn: Union[str, Callable]) -> Callable[[float, float], float]:
    """Return a callable loss, resolving string shortcuts."""
    if callable(loss_fn):
        return loss_fn
    if isinstance(loss_fn, str) and loss_fn in _LOSS_PRESETS:
        return _LOSS_PRESETS[loss_fn]
    raise ValueError(
        f"loss_fn must be a callable or one of {list(_LOSS_PRESETS)}, got {loss_fn!r}"
    )


# ── general_risk ──────────────────────────────────────────────────────────────

def general_risk(
    theta_true: float,
    estimator_values: np.ndarray,
    loss_fn: Union[str, Callable],
) -> float:
    """
    Compute the frequentist risk R(δ, θ) = E[L(δ(X), θ)] from repeated estimates.

    Risk is approximated as the sample mean of the loss over all provided
    estimator draws at the fixed true parameter value theta_true:
      R(δ, θ) ≈ (1/N) Σ L(δ(X_i), θ)

    Lecture 22, Definition: the risk function summarises the average penalty
    incurred by estimator δ at a single fixed θ. Combined with a prior over θ,
    it yields the Bayes risk (see discrete_bayes_risk). The estimator that
    minimises max_θ R(δ, θ) is the minimax estimator (see minimax_risk).

    Built-in string shortcuts for loss_fn:
      "squared"  → L(e, t) = (e − t)²         [squared error / MSE]
      "absolute" → L(e, t) = |e − t|           [absolute error / MAE]
      "0-1"      → L(e, t) = 0 if |e−t|<1e-6 else 1  [misclassification]

    Args:
        theta_true:       True parameter value θ.
        estimator_values: 1-D array of estimator draws δ(X_1), …, δ(X_N).
                          Must be non-empty.
        loss_fn:          Callable with signature loss_fn(estimate, theta) → float,
                          or one of the string shortcuts above.

    Returns:
        Estimated risk R(δ, θ) as a float.
    """
    ev = np.asarray(estimator_values).astype(float).ravel()
    if ev.size == 0:
        raise ValueError("estimator_values cannot be empty")
    loss = _resolve_loss(loss_fn)
    return float(np.mean([loss(e, theta_true) for e in ev]))


# ── minimax_risk ──────────────────────────────────────────────────────────────

def minimax_risk(
    estimators: Dict[str, np.ndarray],
    theta_grid: np.ndarray,
    loss_fn: Union[str, Callable] = "squared",
) -> Dict[str, Any]:
    """
    Find the minimax estimator: the one that minimises the maximum risk over θ.

    For each estimator, the risk at each θ in theta_grid is taken directly from
    the corresponding column of the provided arrays (pre-computed risk values),
    and the maximum risk across the grid is recorded. The minimax estimator is
    the one with the lowest maximum risk.

    Input format: estimators[name] is a 1-D array of pre-computed risk values
    R(δ, θ_j) at each θ_j in theta_grid (len must match len(theta_grid)).

    Lecture 22, Example 37: illustrates that the minimax criterion selects the
    estimator with the most controlled worst-case behaviour, even if it is not
    optimal under a specific prior. In the lecture example:
      hat1 risks = [0, 0.5, 0] over θ ∈ {0,1,2} → max risk = 0.5
      hat2 risks = [1, 0,   1] over θ ∈ {0,1,2} → max risk = 1.0
      → minimax selects hat1 (lower worst-case risk).

    Args:
        estimators:  Dict mapping estimator name → 1-D array of risk values,
                     one per theta in theta_grid. All arrays must have the same
                     length as theta_grid and be non-empty.
        theta_grid:  Array of θ values at which risks were evaluated.
        loss_fn:     String shortcut or callable — stored in the result for
                     traceability but not applied here (risks are pre-computed).

    Returns:
        dict with keys:
          risks             – {name: {"max_risk": float, "worst_theta": float}}
          minimax_estimator – name of the estimator with the lowest max risk
          minimax_value     – its max risk value
          loss_fn           – name or repr of the loss used
    """
    if not estimators:
        raise ValueError("estimators must be non-empty")
    theta_arr = np.asarray(theta_grid).astype(float).ravel()
    if theta_arr.size == 0:
        raise ValueError("theta_grid must be non-empty")
    _resolve_loss(loss_fn)  # validate early; not applied since risks are pre-computed

    risks: Dict[str, Dict[str, float]] = {}
    for name, risk_arr in estimators.items():
        rv = np.asarray(risk_arr).astype(float).ravel()
        if rv.size != theta_arr.size:
            raise ValueError(
                f"estimators['{name}'] has length {rv.size} but theta_grid has "
                f"length {theta_arr.size}; they must match."
            )
        idx = int(np.argmax(rv))
        risks[name] = {
            "max_risk": float(rv[idx]),
            "worst_theta": float(theta_arr[idx]),
        }

    minimax_name = min(risks, key=lambda k: risks[k]["max_risk"])
    loss_label = loss_fn if isinstance(loss_fn, str) else repr(loss_fn)

    return {
        "risks": risks,
        "minimax_estimator": minimax_name,
        "minimax_value": risks[minimax_name]["max_risk"],
        "loss_fn": loss_label,
    }