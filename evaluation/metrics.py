# evaluation/metrics.py
# Scoring weights must match llm_runner/response_parser.py — see CLAUDE.md §7
"""
Scoring + aggregation utilities for DS 299 capstone benchmark.

Per-task components in [0,1]:
  N = Numerical Accuracy       — extracted numbers match ground truth
  M = Method/Structure         — required reasoning steps present
  A = Assumption Compliance    — required statistical assumptions mentioned
  C = Confidence Calibration   — model is confident when correct, uncertain when wrong
  R = Reasoning Quality        — step-by-step derivation quality and interpretation

NMACR weights — literature-derived (sole canonical scheme since Approach A,
2026-05-03). Sum to 1.0.
  A 0.30, R 0.25, M 0.20, C 0.15, N 0.10

See llm-stats-vault/90-archive/audit/aggregation_locus.md for the single-path rationale and
llm-stats-vault/90-archive/audit/methodology_continuity.md §"NMACR weighting" for the literature defense
(Du 2025, Boye & Moell 2025, Yamauchi 2025, ReasonBench 2025, Wei 2022,
Chen 2022, Bishop 2006, Nagarkar 2026, FermiEval 2025, Liu 2025).

Stress-test multiplier:
  Tier 5 tasks have multiplier 1.50; others 1.00

Model score (normalized):
  Score(model) = sum_t(k_t * S_base_t) / sum_t(k_t)
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Sequence, Tuple
import statistics


# Scoring weights must match llm_runner/response_parser.py — see CLAUDE.md §7
NMACR_WEIGHTS: Dict[str, float] = {
    "A": 0.30,
    "R": 0.25,
    "M": 0.20,
    "C": 0.15,
    "N": 0.10,
}
assert abs(sum(NMACR_WEIGHTS.values()) - 1.0) < 1e-9, "NMACR weights must sum to 1.0"

WEIGHTING_SCHEME = "literature_v1"

# Backwards-compatible alias (no remaining importers, kept defensively)
WEIGHTS = NMACR_WEIGHTS

STRESS_TEST_TIER = 5
STRESS_MULTIPLIER = 1.50

ROBUSTNESS_SIGMA0 = 0.15


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def stress_multiplier_for_tier(tier: int) -> float:
    return STRESS_MULTIPLIER if tier == STRESS_TEST_TIER else 1.0


@dataclass(frozen=True)
class NumericTarget:
    key: str
    true_value: float
    full_credit_tol: float = 1e-3
    zero_credit_scale: float = 1e-1


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    tier: int
    difficulty: str  # "basic" | "intermediate" | "advanced"
    required_structure_checks: List[str] = field(default_factory=list)
    required_assumption_checks: List[str] = field(default_factory=list)
    numeric_targets: List[NumericTarget] = field(default_factory=list)
    notes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskRun:
    model_name: str
    task_id: str
    run_id: str = "base"
    perturbation_group: Optional[str] = None

    output_text: str = ""
    extracted_numbers: Dict[str, float] = field(default_factory=dict)

    structure_flags: Dict[str, bool] = field(default_factory=dict)
    assumption_flags: Dict[str, bool] = field(default_factory=dict)

    # Rubric scores
    conceptual_rubric_score_0to2: Optional[int] = None
    confidence: Optional[float] = None  # raw extracted confidence value

    # Component C and R (computed by response_parser.full_score or recompute script)
    confidence_calib_score: float = 0.5   # C: confidence calibration score
    reasoning_qual_score:   float = 0.5   # R: reasoning quality score


@dataclass
class ComponentScores:
    N: float
    M: float
    C: float
    A: float
    R: float


@dataclass
class TaskScore:
    task_id: str
    model_name: str
    tier: int
    difficulty: str

    component_scores: ComponentScores
    base_score: float
    multiplier: float
    final_weighted_score: float

    per_run_base_scores: List[Tuple[str, float]] = field(default_factory=list)


@dataclass
class ModelAggregate:
    model_name: str
    normalized_score: float
    weighted_sum: float
    weight_total: float
    by_tier: Dict[int, float] = field(default_factory=dict)
    by_difficulty: Dict[str, float] = field(default_factory=dict)


def numerical_score(task: TaskSpec, run: TaskRun) -> float:
    if not task.numeric_targets:
        return 1.0

    scores: List[float] = []
    for tgt in task.numeric_targets:
        pred = run.extracted_numbers.get(tgt.key, None)
        if pred is None:
            scores.append(0.0)
            continue

        abs_err = abs(pred - tgt.true_value)
        z = max(tgt.zero_credit_scale, tgt.full_credit_tol)

        if abs_err <= tgt.full_credit_tol:
            s = 1.0
        else:
            s = 1.0 - (abs_err / z)

        scores.append(clamp01(s))

    return sum(scores) / len(scores) if scores else 0.0


def checklist_score(required_items: Sequence[str], flags: Dict[str, bool]) -> float:
    if not required_items:
        return 1.0
    got = sum(1 for item in required_items if flags.get(item, False))
    return got / len(required_items)


def method_structure_score(task: TaskSpec, run: TaskRun) -> float:
    return checklist_score(task.required_structure_checks, run.structure_flags)


def assumption_compliance_score(task: TaskSpec, run: TaskRun) -> float:
    return checklist_score(task.required_assumption_checks, run.assumption_flags)


def conceptual_score(task: TaskSpec, run: TaskRun) -> float:
    if run.conceptual_rubric_score_0to2 is None:
        return 0.0
    if run.conceptual_rubric_score_0to2 not in (0, 1, 2):
        raise ValueError("conceptual_rubric_score_0to2 must be 0, 1, or 2.")
    return run.conceptual_rubric_score_0to2 / 2.0


def base_score_from_components(cs: ComponentScores) -> float:
    s = (
        NMACR_WEIGHTS["N"] * cs.N
        + NMACR_WEIGHTS["M"] * cs.M
        + NMACR_WEIGHTS["C"] * cs.C
        + NMACR_WEIGHTS["A"] * cs.A
        + NMACR_WEIGHTS["R"] * cs.R
    )
    return clamp01(s)


def robustness_score_from_base_scores(per_run_base_scores: List[float], sigma0: float = ROBUSTNESS_SIGMA0) -> float:
    if len(per_run_base_scores) <= 1:
        return 1.0
    sd = statistics.pstdev(per_run_base_scores)
    r = 1.0 - min(1.0, sd / max(1e-12, sigma0))
    return clamp01(r)


def score_task_with_perturbations(task: TaskSpec, runs_for_task: List[TaskRun]) -> TaskScore:
    if not runs_for_task:
        raise ValueError("runs_for_task is empty.")
    model_name = runs_for_task[0].model_name
    task_id = task.task_id
    for r in runs_for_task:
        if r.model_name != model_name or r.task_id != task_id:
            raise ValueError("runs_for_task must contain same model_name and task_id.")

    per_run_scores: List[Tuple[str, float, float, float, float, float]] = []

    for r in runs_for_task:
        N = numerical_score(task, r)
        M = method_structure_score(task, r)
        A = assumption_compliance_score(task, r)
        C = r.confidence_calib_score   # confidence calibration
        R = r.reasoning_qual_score     # reasoning quality

        tmp = ComponentScores(N=N, M=M, C=C, A=A, R=R)
        base = base_score_from_components(tmp)
        per_run_scores.append((r.run_id, base, N, M, A, C, R))

    N_avg = sum(x[2] for x in per_run_scores) / len(per_run_scores)
    M_avg = sum(x[3] for x in per_run_scores) / len(per_run_scores)
    A_avg = sum(x[4] for x in per_run_scores) / len(per_run_scores)
    C_avg = sum(x[5] for x in per_run_scores) / len(per_run_scores)
    R_avg = sum(x[6] for x in per_run_scores) / len(per_run_scores)

    per_run_base_noR = [(run_id, base) for run_id, base, *_ in per_run_scores]
    R = R_avg

    cs = ComponentScores(N=clamp01(N_avg), M=clamp01(M_avg), C=clamp01(C_avg), A=clamp01(A_avg), R=clamp01(R))
    base = base_score_from_components(cs)

    mult = stress_multiplier_for_tier(task.tier)
    final_weighted = mult * base

    return TaskScore(
        task_id=task.task_id,
        model_name=model_name,
        tier=task.tier,
        difficulty=task.difficulty,
        component_scores=cs,
        base_score=base,
        multiplier=mult,
        final_weighted_score=final_weighted,
        per_run_base_scores=per_run_base_noR,
    )


def aggregate_model_scores(task_scores: List[TaskScore]) -> ModelAggregate:
    if not task_scores:
        raise ValueError("task_scores is empty.")
    model_name = task_scores[0].model_name
    if any(ts.model_name != model_name for ts in task_scores):
        raise ValueError("All TaskScore objects must have same model_name.")

    weighted_sum = sum(ts.final_weighted_score for ts in task_scores)
    weight_total = sum(ts.multiplier for ts in task_scores)
    normalized = weighted_sum / weight_total if weight_total > 0 else 0.0

    by_tier: Dict[int, float] = {}
    for tier in sorted(set(ts.tier for ts in task_scores)):
        group = [ts for ts in task_scores if ts.tier == tier]
        ws = sum(ts.final_weighted_score for ts in group)
        wt = sum(ts.multiplier for ts in group)
        by_tier[tier] = ws / wt if wt > 0 else 0.0

    by_difficulty: Dict[str, float] = {}
    for diff in sorted(set(ts.difficulty for ts in task_scores)):
        group = [ts for ts in task_scores if ts.difficulty == diff]
        ws = sum(ts.final_weighted_score for ts in group)
        wt = sum(ts.multiplier for ts in group)
        by_difficulty[diff] = ws / wt if wt > 0 else 0.0

    return ModelAggregate(
        model_name=model_name,
        normalized_score=clamp01(normalized),
        weighted_sum=weighted_sum,
        weight_total=weight_total,
        by_tier=by_tier,
        by_difficulty=by_difficulty,
    )


def score_all_models(tasks: Dict[str, TaskSpec], runs: List[TaskRun]) -> Tuple[List[TaskScore], List[ModelAggregate]]:
    grouped: Dict[Tuple[str, str, str], List[TaskRun]] = {}

    for r in runs:
        if r.task_id not in tasks:
            raise KeyError(f"TaskRun.task_id='{r.task_id}' not found in tasks dict.")
        group_id = r.perturbation_group or r.task_id
        key = (r.model_name, r.task_id, group_id)
        grouped.setdefault(key, []).append(r)

    task_scores: List[TaskScore] = []
    for (model_name, task_id, group_id), group_runs in grouped.items():
        spec = tasks[task_id]
        task_scores.append(score_task_with_perturbations(spec, group_runs))

    aggregates: List[ModelAggregate] = []
    for mn in sorted(set(ts.model_name for ts in task_scores)):
        aggregates.append(aggregate_model_scores([ts for ts in task_scores if ts.model_name == mn]))

    aggregates.sort(key=lambda x: x.normalized_score, reverse=True)
    return task_scores, aggregates