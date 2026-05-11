# evaluation/rubrics.py
"""
Rubric templates.

You will use these as the reference when assigning:
- conceptual_rubric_score_0to2
- structure_flags
- assumption_flags

This file is intentionally plain: it documents how to score.
"""

from __future__ import annotations

# Conceptual interpretation rubric for C (0..2)
CONCEPTUAL_RUBRIC = {
    0: "Incorrect/misleading interpretation OR confuses key concepts (e.g., CI vs probability, p-value misuse).",
    1: "Partially correct but incomplete/unclear; minor conceptual issues.",
    2: "Correct and clear; interpretation aligns with computed results and uncertainty statements.",
}

# Typical Bayes structure checklist keys (for structure_flags)
# You can add/rename keys as you build tasks.
DEFAULT_STRUCTURE_KEYS = [
    "states_prior",
    "states_likelihood",
    "states_posterior_kernel_or_family",
    "updates_hyperparameters_correctly",
    "uses_sufficient_statistics",
    "states_posterior_summary_mean",
    "states_credible_interval",
]

# Typical assumption checklist keys (for assumption_flags)
DEFAULT_ASSUMPTION_KEYS = [
    "states_iid",
    "states_distributional_assumption",
    "checks_or_warns_assumptions",
    "does_not_proceed_if_violated",
]

# Decision theory checklist keys (for Tier 2)
DECISION_THEORY_KEYS = [
    "identifies_loss_function",
    "chooses_bayes_estimator_for_loss",
    "computes_risk_or_mse_correctly",
    "compares_estimators_correctly",
]