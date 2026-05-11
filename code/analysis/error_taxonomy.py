# evaluation/error_taxonomy.py
"""
Standard error taxonomy tags (for your report + analysis).

You can attach one or more tags per TaskRun after manual review
(or later via heuristics).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


# Top-level categories
CONCEPTUAL = "conceptual"
METHOD_SELECTION = "method_selection"
MATHEMATICAL = "mathematical"
COMPUTATIONAL = "computational"
ASSUMPTION = "assumption"
INTERPRETATION = "interpretation"
BAYES_PRIOR = "bayes_prior"
BAYES_POSTERIOR = "bayes_posterior"
DECISION_THEORY = "decision_theory"
SIMULATION = "simulation"
ROBUSTNESS = "robustness"
HALLUCINATION = "hallucination"

ALL_TAGS = [
    CONCEPTUAL, METHOD_SELECTION, MATHEMATICAL, COMPUTATIONAL, ASSUMPTION, INTERPRETATION,
    BAYES_PRIOR, BAYES_POSTERIOR, DECISION_THEORY, SIMULATION, ROBUSTNESS, HALLUCINATION
]


@dataclass
class ErrorAnnotation:
    task_id: str
    model_name: str
    run_id: str = "base"
    tags: List[str] = field(default_factory=list)
    notes: Optional[str] = None

    def validate(self) -> None:
        invalid = [t for t in self.tags if t not in ALL_TAGS]
        if invalid:
            raise ValueError(f"Invalid taxonomy tags: {invalid}. Allowed: {ALL_TAGS}")