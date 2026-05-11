# llm_runner/response_parser.py
# Scoring weights must match evaluation/metrics.py — see CLAUDE.md §7
"""
Parse LLM responses and score them against ground truth.

Five scoring dimensions (NMACR — literature-derived weights, sole canonical
scheme since Approach A, 2026-05-03):
  N = Numerical Accuracy   — extracted numbers match ground truth (within tolerance)
  M = Method Structure     — response demonstrates required reasoning steps
  A = Assumption Compliance — response mentions required statistical assumptions
  C = Confidence Calibration — model is confident when correct, uncertain when wrong
  R = Reasoning Quality    — step-by-step derivation quality and interpretation

Combined final score (numeric tasks):
  0.10*N + 0.20*M + 0.30*A + 0.15*C + 0.25*R
Conceptual tasks: 1.0 * rubric_score
Pass threshold: final_score >= 0.5

See llm-stats-vault/90-archive/audit/aggregation_locus.md (single-path rationale) and
llm-stats-vault/90-archive/audit/methodology_continuity.md §"NMACR weighting" (literature defense).
"""
from __future__ import annotations

import re
from typing import Any, Dict, List

# ── NMACR weights — literature-derived (must match NMACR_WEIGHTS in evaluation/metrics.py) ──
# Scoring weights must match evaluation/metrics.py — see CLAUDE.md §7
W_N = 0.10  # Numerical Accuracy        — Liu 2025, Boye & Moell 2025
W_M = 0.20  # Method Structure          — Wei 2022, Chen 2022, Bishop 2006
W_A = 0.30  # Assumption Compliance     — Du 2025, Boye & Moell 2025, Yamauchi 2025
W_C = 0.15  # Confidence Calibration    — Nagarkar 2026, FermiEval 2025, Multi-Answer 2026
W_R = 0.25  # Reasoning Quality         — Yamauchi 2025, Boye & Moell 2025, ReasonBench 2025
assert abs((W_N + W_M + W_A + W_C + W_R) - 1.0) < 1e-9, "NMACR weights must sum to 1.0"

from models.prompt_builder import parse_answer, format_numeric_targets

# Common words excluded when matching rubric key concepts
_RUBRIC_STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "in", "on", "at", "by", "to", "of", "or", "and", "with", "from",
    "that", "this", "it", "its", "not", "as", "for", "needed", "required",
}


# ── Keyword mappings for structure / assumption checks ─────────────────────

# Maps check_name → list of keywords; a check passes if ANY keyword appears
# in the (lowercased) response text.
_STRUCTURE_KEYWORDS: Dict[str, List[str]] = {
    # Bayesian conjugate checks
    "states_prior":                         ["prior", "beta(", "gamma(", "dirichlet", "uniform prior"],
    "states_likelihood":                    ["likelihood", "binomial", "poisson", "normal", "multinomial"],
    "states_posterior_kernel_or_family":    ["posterior", "beta(", "gamma(", "normal(", "dirichlet("],
    "updates_hyperparameters_correctly":    ["alpha", "beta", "posterior", "update", "+"],
    # Discrete median
    "states_cumulative_probability_rule":   ["cumulative", "cumsum", "sum of prob", "≥ 0.5", ">= 0.5"],
    "identifies_first_cumsum_geq_half":     ["cumulative", "0.5", "median"],
    "values_are_ordered":                   ["order", "sorted", "ascending"],
    # Uniform MLE
    "identifies_mle_as_max_order_statistic": ["max", "maximum", "order statistic", "x_(n)", "mle"],
    "states_likelihood_function":           ["likelihood", "l(theta", "l(θ"],
    # Flat prior
    "states_flat_prior_as_beta_1_1":        ["beta(1", "uniform(0,1)", "flat prior", "beta(1,1)"],
    "states_posterior_family":              ["posterior", "beta("],
    # Minimax
    "computes_max_risk_per_estimator":      ["max risk", "maximum risk", "max_risk", "worst"],
    "selects_estimator_with_min_max_risk":  ["minimax", "min", "minimum", "lower max"],
    # Bayes risk
    "applies_prior_weighting":              ["prior", "weight", "π(", "pi("],
    "sums_weighted_risks":                  ["sum", "weighted", "bayes risk", "∑"],
    # Bias-variance
    "computes_bias_from_expectation":       ["bias", "e[", "expected", "expectation", "e("],
    "computes_variance_of_estimator":       ["var", "variance"],
    "states_mse_equals_bias_sq_plus_variance": ["mse", "bias", "variance", "bias²", "bias^2"],
    # Fisher / RC
    "states_fisher_information_formula":    ["fisher", "i(theta", "i(θ", "i_n"],
    "applies_correct_formula_for_distribution": ["1/(theta", "1/theta", "n/theta", "1/σ"],
    "states_regularity_conditions":         ["regular", "differentiable", "support", "condition"],
    "states_rc_bound_as_reciprocal_of_fisher_info": ["1/i", "reciprocal", "lower bound", "rc"],
    "identifies_unbiased_case_bias_deriv_zero": ["unbiased", "b'=0", "b'(θ)=0", "bias deriv"],
    "states_unbiasedness_assumption":       ["unbiased", "e[t]=θ", "b(θ)=0"],
    # Optimal scaled estimator
    "derives_optimal_c_by_minimising_mse":  ["minimis", "minimiz", "d/dc", "derivative", "optimal c"],
    "states_c_opt_formula_n_plus_2_over_n_plus_1": ["(n+2)/(n+1)", "n+2", "(n+2)", "c*"],
    "computes_resulting_mse":               ["mse", "mean squared error"],
    # MSE comparison
    "computes_mse_d1_analytical":           ["mse(d1)", "mse d1", "θ²/(3n)", "theta^2/3"],
    "computes_mse_d2_analytical":           ["mse(d2)", "mse d2", "max"],
    "computes_mse_dc_at_optimal_c":         ["mse(dc)", "mse dc", "optimal", "c*"],
    "identifies_dc_as_minimum_mse_estimator": ["dc", "d_c", "smallest", "minimum mse", "best"],
    # Markov
    "solves_pi_P_eq_pi":                    ["π·p", "pi·p", "π p", "stationary", "πp = π"],
    "normalises_to_one":                    ["sum", "=1", "= 1", "normalise", "normalize"],
    "uses_eigenvalue_or_linear_system":     ["eigenvalue", "eigenvector", "linear system", "solve"],
    "applies_gamblers_ruin_formula":        ["ruin", "gambler", "(q/p)", "q/p"],
    "handles_fair_vs_unfair_case":          ["fair", "p=0.5", "p = 0.5", "unfair"],
    "computes_matrix_power":               ["p^n", "p^2", "matrix power", "matrix multiplication"],
    "applies_chapman_kolmogorov":           ["chapman", "kolmogorov", "p^n"],
    # Order statistics
    "states_order_stat_pdf_formula":        ["g_(k)", "g_k", "order stat", "beta(k", "pdf"],
    "identifies_beta_distribution_connection": ["beta", "beta(k", "beta distribution"],
    "states_min_cdf_as_1_minus_survival":   ["1 - (1-x)", "survival", "1-(1-x)^n"],
    "applies_F_1_x_formula":               ["f_(1)", "f(1)", "min cdf", "cdf"],
    "identifies_range_as_beta_distribution": ["beta", "range", "beta(n-1"],
    "states_correct_parameters_n_minus_1_and_2": ["n-1", "n−1", "alpha=n-1", "β=2"],
    # Regression
    "computes_B_hat_via_Sxy_over_Sxx":      ["sxy/sxx", "sxy", "sxx", "b_hat", "b̂", "slope"],
    "computes_A_hat_via_ybar_minus_B_hat_xbar": ["intercept", "a_hat", "â", "ȳ - b̂", "ybar"],
    "computes_residual_variance_SSR_over_n_minus_2": ["ssr", "s²", "s^2", "n-2", "residual var"],
    "constructs_t_based_confidence_intervals": ["t-distribution", "t distribution", "t_{n-2}", "confidence interval", "ci"],
    # Box-Muller
    "applies_box_muller_formula":           ["box-muller", "box muller", "z1", "z2", "sqrt(-2"],
    "computes_r_as_sqrt_neg2_log_U":        ["sqrt(-2", "√(-2", "-2*log", "-2 log"],
    "applies_cos_sin_with_2pi_V":           ["cos(2π", "cos(2*pi", "sin(2π", "sin(2*pi"],
    # HPD intervals
    "computes_hpd_via_shortest_interval":   ["hpd", "highest density", "shortest interval", "hdr"],
    "notes_hpd_shorter_than_equal_tail":    ["shorter", "hpd", "equal tail", "equal-tail", "highest density"],
    # Bayes factors
    "applies_bayes_factor_formula":         ["bayes factor", "bf", "marginal likelihood", "log bf"],
    "states_evidence_scale":                ["evidence", "positive", "strong", "very strong", "kass", "raftery"],
    # Jeffreys prior
    "states_jeffreys_prior_formula":        ["jeffreys", "jeffrey", "beta(0.5", "invariant", "sqrt(i"],
    "notes_jeffreys_invariance":            ["invariant", "reparametri", "transformation", "jeffreys"],
    # Posterior predictive checks
    "generates_predictive_replicates":      ["replicate", "predictive", "ppc", "posterior predictive"],
    "checks_tail_probability":              ["p-value", "tail", "proportion", "fraction", "replicate"],
    # Bayesian regression
    "applies_normal_inverse_gamma_update":  ["normal-inverse-gamma", "nig", "posterior", "precision", "lambda"],
    "states_bayesian_regression_prior":     ["prior", "normal", "inverse-gamma", "sigma^2", "conjugate"],
    # MLE vs MAP
    "computes_map_from_posterior_mode":     ["map", "maximum a posteriori", "mode", "posterior mode"],
    "contrasts_mle_and_map":               ["mle", "map", "maximum likelihood", "shrink", "prior"],
    # CI vs Credible interval
    "computes_frequentist_ci":             ["confidence interval", "z-interval", "frequentist", "repeated"],
    "computes_bayesian_credible":          ["credible", "posterior", "bayesian", "credible interval"],
    # Log marginal likelihood
    "applies_beta_function_for_ml":        ["beta function", "betaln", "marginal", "b(alpha", "b(a+x"],
    "computes_normalizing_constant":       ["normalizing constant", "marginal likelihood", "log b(", "betaln"],
}

_ASSUMPTION_KEYWORDS: Dict[str, List[str]] = {
    "states_iid":                       ["iid", "i.i.d", "independent", "identically distributed"],
    "states_distributional_assumption": ["distribution", "normal", "poisson", "binomial",
                                         "uniform", "assumed", "assumption"],
    "values_are_ordered":               ["order", "sorted", "ascending"],
    "states_regularity_conditions":     ["regular", "regularity", "differentiable", "support"],
    "states_unbiasedness_assumption":   ["unbiased", "e[t]", "b(θ)=0"],
    "chain_is_irreducible":             ["irreducible", "communicate", "every state"],
    "chain_is_aperiodic":               ["aperiodic", "period", "convergence"],
    "absorbing_boundaries_at_0_and_M":  ["absorbing", "boundary", "barrier", "0 and", "ruin"],
    "uniform_support_0_1":              ["uniform[0,1]", "uniform(0,1)", "uniform 0 1", "[0,1]"],
    "U_V_independent_uniform_0_1":      ["uniform(0,1)", "u,v", "u and v", "independent"],
    "normal_errors":                    ["normal error", "ε ~ n", "epsilon ~ n",
                                         "normally distributed", "gaussian"],
    "constant_variance":                ["homoscedastic", "constant var", "σ² constant",
                                         "equal varianc"],
}


def _keyword_check(text: str, check_name: str, keywords: Dict[str, List[str]]) -> bool:
    """Return True if any keyword for check_name appears in text (case-insensitive)."""
    kws = keywords.get(check_name, [])
    if not kws:
        # Unknown check — give benefit of the doubt
        return True
    lower = text.lower()
    return any(kw.lower() in lower for kw in kws)


# ── parse_and_score ───────────────────────────────────────────────────────────

def parse_and_score(
    raw_response: str,
    task: dict,
    tol: float = 0.01,
) -> Dict[str, Any]:
    """
    Extract numeric values from the response and compare to ground truth.

    A value is "correct" if |parsed - true| <= tol * max(1, |true|).
    (Relative tolerance against the scale of the true value.)

    Args:
        raw_response: Full text response from an LLM.
        task:         Task dict from tasks.json.
        tol:          Relative tolerance for numeric correctness.

    Returns:
        dict with parsed_values, ground_truth, n_correct, n_total,
        numeric_score, answer_found, length_match, tol.
    """
    ground_truth = format_numeric_targets(task)
    parsed = parse_answer(raw_response)
    answer_found = len(parsed) > 0
    length_match = len(parsed) == len(ground_truth)

    n_total = len(ground_truth)
    n_correct = 0
    if length_match and n_total > 0:
        for p, g in zip(parsed, ground_truth):
            scale = max(1.0, abs(g))
            if abs(p - g) <= tol * scale:
                n_correct += 1

    numeric_score = n_correct / n_total if n_total > 0 else 0.0

    return {
        "parsed_values": parsed,
        "ground_truth":  ground_truth,
        "n_correct":     n_correct,
        "n_total":       n_total,
        "numeric_score": float(numeric_score),
        "answer_found":  answer_found,
        "length_match":  length_match,
        "tol":           tol,
    }


# ── check_structure ───────────────────────────────────────────────────────────

def check_structure(raw_response: str, task: dict) -> Dict[str, Any]:
    """
    Check whether the response demonstrates required reasoning structure.

    Each required_structure_check is tested via keyword matching against the
    response text. The structure_score is the fraction of checks that pass.

    Args:
        raw_response: Full text response.
        task:         Task dict.

    Returns:
        dict with checks ({check_name: bool}) and structure_score.
    """
    required = task.get("required_structure_checks", [])
    if not required:
        return {"checks": {}, "structure_score": 1.0}

    checks = {
        c: _keyword_check(raw_response, c, _STRUCTURE_KEYWORDS)
        for c in required
    }
    score = sum(checks.values()) / len(checks)
    return {"checks": checks, "structure_score": float(score)}


# ── check_assumptions ─────────────────────────────────────────────────────────

def check_assumptions(raw_response: str, task: dict) -> Dict[str, Any]:
    """
    Check whether the response mentions required statistical assumptions.

    Args:
        raw_response: Full text response.
        task:         Task dict.

    Returns:
        dict with checks ({check_name: bool}) and assumption_score.
    """
    required = task.get("required_assumption_checks", [])
    if not required:
        return {"checks": {}, "assumption_score": 1.0}

    checks = {
        c: _keyword_check(raw_response, c, _ASSUMPTION_KEYWORDS)
        for c in required
    }
    score = sum(checks.values()) / len(checks)
    return {"checks": checks, "assumption_score": float(score)}


# ── rubric_score ──────────────────────────────────────────────────────────────

def rubric_score(raw_response: str, task: dict) -> Dict[str, Any]:
    """
    Score a conceptual task by checking for key concept phrases.

    Each rubric_key is tested via case-insensitive substring matching.
    rubric_score = len(keys_found) / len(rubric_keys).

    Args:
        raw_response: Full text response from an LLM.
        task:         Task dict with 'rubric_keys' and 'reference_answer'.

    Returns:
        dict with rubric_keys, keys_found, keys_missing, rubric_score,
        reference_answer.
    """
    rubric_keys      = task.get("rubric_keys", [])
    reference_answer = task.get("reference_answer", "")
    lower            = raw_response.lower()

    def _key_matches(key: str) -> bool:
        # Extract meaningful words from the rubric key (drop stop words & punctuation)
        words = re.sub(r"[^a-z0-9\s\-]", " ", key.lower()).split()
        meaningful = [w for w in words if w not in _RUBRIC_STOP_WORDS and len(w) > 1]
        if not meaningful:
            return key.lower() in lower
        hits = sum(1 for w in meaningful if w in lower)
        # Pass if at least 60% of meaningful key terms appear in the response
        return hits >= len(meaningful) * 0.6

    keys_found   = [k for k in rubric_keys if _key_matches(k)]
    keys_missing = [k for k in rubric_keys if not _key_matches(k)]
    score = len(keys_found) / len(rubric_keys) if rubric_keys else 1.0
    return {
        "rubric_keys":      rubric_keys,
        "keys_found":       keys_found,
        "keys_missing":     keys_missing,
        "rubric_score":     float(score),
        "reference_answer": reference_answer,
    }


# ── confidence calibration ────────────────────────────────────────────────────

def extract_confidence(response_text: str) -> float:
    """
    Extract confidence score from model response. Returns float in [0.1, 0.9].

    Priority:
    1. Explicit percentage: "confidence: 85%"
    2. X/10 scale: "certainty: 8/10"
    3. Linguistic: hedge words lower score, definitive words raise it
    4. Default: 0.5 (neutral)
    """
    text = response_text.lower()

    # Priority 1: explicit percentage
    pct_match = re.search(
        r'(?:confidence|certainty|certain)[:\s]+(\d+(?:\.\d+)?)\s*%', text
    )
    if pct_match:
        return min(0.9, max(0.1, float(pct_match.group(1)) / 100))

    # Priority 2: X/10 scale
    scale_match = re.search(
        r'(?:confidence|certainty)[:\s]+(\d+(?:\.\d+)?)\s*/\s*10', text
    )
    if scale_match:
        return min(0.9, max(0.1, float(scale_match.group(1)) / 10))

    # Priority 3: linguistic analysis
    hedge_words = [
        'i think', 'i believe', 'approximately', 'roughly',
        'about', 'around', 'maybe', 'perhaps', 'might',
        'not sure', 'uncertain', 'unclear', 'could be',
        'i am not', "i'm not", 'unsure',
    ]
    definitive_words = [
        'the answer is', 'exactly', 'precisely',
        'the posterior is', 'therefore', 'thus',
        'we can compute', 'plugging in', 'solving',
    ]

    score = 0.5
    for word in hedge_words:
        if word in text:
            score -= 0.05
    for word in definitive_words:
        if word in text:
            score += 0.04

    return min(0.9, max(0.1, score))


def confidence_calibration_score(confidence: float, numerical_score: float) -> float:
    """
    Calibration score: reward confidence ≈ numerical_score.
    Overconfidence on wrong answer penalized 1.5×; underconfidence 0.8×.
    Returns float in [0.0, 1.0].
    """
    error = confidence - numerical_score
    if error > 0:
        calibration_error = error * 1.5   # overconfident — steeper penalty
    else:
        calibration_error = abs(error) * 0.8  # underconfident — lighter penalty
    return max(0.0, 1.0 - calibration_error)


# ── reasoning quality ─────────────────────────────────────────────────────────

def reasoning_quality_score(response_text: str, task_type: str) -> float:
    """
    Score step-by-step reasoning quality. Returns float in [0.0, 1.0].

    Four criteria × 0.25 each:
    1. Shows work  — mathematical derivation present
    2. Identifies model — names correct statistical model/family
    3. States formula — writes update equation before plugging in
    4. Interprets result — explains what the answer means
    """
    text = response_text.lower()
    score = 0.0

    # Criterion 1: Shows work (0.25)
    math_signals = [
        r'[αβθμσλ]', r'step\s*\d', r'first.*then',
        r'=\s*\d', r'\\frac', r'posterior\s*=',
        r'alpha\s*\+', r'beta\s*\+', r'plug',
    ]
    if any(re.search(p, text) for p in math_signals):
        score += 0.25

    # Criterion 2: Identifies model (0.25)
    model_keywords: Dict[str, list] = {
        'BETA_BINOM':    ['beta', 'binomial', 'conjugate', 'bernoulli'],
        'GAMMA_POISSON': ['gamma', 'poisson', 'rate', 'count'],
        'NORMAL_GAMMA':  ['normal', 'precision', 'variance'],
        'DIRICHLET':     ['dirichlet', 'multinomial', 'categorical'],
        'DEFAULT':       ['prior', 'posterior', 'likelihood', 'bayes'],
    }
    keywords = model_keywords.get(task_type, model_keywords['DEFAULT'])
    if any(kw in text for kw in keywords):
        score += 0.25

    # Criterion 3: States formula (0.25)
    formula_signals = [
        r'posterior.*=', r'alpha.*\+.*n', r'beta.*\+',
        r'mean\s*=', r'var(?:iance)?\s*=', r'\d+\s*/\s*\d+',
        r'p\(.*\|.*\)', r'e\[.*\|',
    ]
    if any(re.search(p, text) for p in formula_signals):
        score += 0.25

    # Criterion 4: Interprets result (0.25)
    interpret_signals = [
        'this means', 'therefore', 'thus', 'we conclude',
        'represents', 'indicates', 'probability that',
        'there is a', '95%', 'credible',
    ]
    if any(s in text for s in interpret_signals):
        score += 0.25

    return score


# ── full_score ────────────────────────────────────────────────────────────────

def full_score(raw_response: str, task: dict) -> Dict[str, Any]:
    """
    Compute a combined score from all five components.

    Weights (numeric tasks, literature-derived):
        0.10*N + 0.20*M + 0.30*A + 0.15*C + 0.25*R
    Rubric-only tasks:        1.0 * rubric_score
    Mixed tasks:              0.6 * numeric + 0.4 * rubric
    Pass threshold: final_score >= 0.5

    Args:
        raw_response: Full text response from an LLM.
        task:         Task dict.

    Returns:
        dict with numeric, structure, assumptions, confidence_score,
        reasoning_score sub-dicts, final_score, pass (bool), and
        optionally rubric sub-dict.
    """
    has_rubric  = bool(task.get("rubric_keys"))
    has_numeric = bool(task.get("numeric_targets"))

    num  = parse_and_score(raw_response, task)
    stru = check_structure(raw_response, task)
    assu = check_assumptions(raw_response, task)

    task_type  = task.get("task_type") or ""
    confidence = extract_confidence(raw_response)
    c_score    = confidence_calibration_score(confidence, num["numeric_score"])
    r_score    = reasoning_quality_score(raw_response, task_type)

    rubric = None
    if has_rubric and not has_numeric:
        rubric = rubric_score(raw_response, task)
        final  = rubric["rubric_score"]
    elif has_rubric and has_numeric:
        rubric = rubric_score(raw_response, task)
        final  = 0.6 * num["numeric_score"] + 0.4 * rubric["rubric_score"]
    else:
        final = (
            W_N * num["numeric_score"]
            + W_M * stru["structure_score"]
            + W_A * assu["assumption_score"]
            + W_C * c_score
            + W_R * r_score
        )

    result: Dict[str, Any] = {
        "numeric":           num,
        "structure":         stru,
        "assumptions":       assu,
        "confidence_score":  float(c_score),
        "reasoning_score":   float(r_score),
        "final_score":       float(final),
        "pass":              bool(final >= 0.5),
    }
    if rubric is not None:
        result["rubric"] = rubric
    return result
