"""Utility for deriving task_type from task_id.

The benchmark's tasks_all.json doesn't carry a `task_type` field consistently
(Phase 1 omits it, Phase 2 sets it). To keep analyses robust, derive
task_type from task_id via the standard regex.

task_id format: TYPE_NN[_perturbation_suffix]
Examples:
  BETA_BINOM_01            -> BETA_BINOM
  BETA_BINOM_01_rephrase   -> BETA_BINOM
  STATIONARY_03_numerical  -> STATIONARY
  HMC_05                   -> HMC
"""
from __future__ import annotations
import re

# Matches the trailing _NN(_suffix?) at end of task_id
_TASK_TYPE_RE = re.compile(r"^(.+?)_\d+(?:_[a-z_]+)?$")


def task_type_from_id(task_id: str) -> str:
    """Return the task_type prefix from a task_id.

    Falls back to the full task_id if the pattern doesn't match.
    """
    m = _TASK_TYPE_RE.match(task_id)
    return m.group(1) if m else task_id


if __name__ == "__main__":
    cases = [
        ("BETA_BINOM_01", "BETA_BINOM"),
        ("BETA_BINOM_01_rephrase", "BETA_BINOM"),
        ("STATIONARY_03_numerical", "STATIONARY"),
        ("HMC_05", "HMC"),
        ("MARKOV_01", "MARKOV"),
        ("RJMCMC_02", "RJMCMC"),
        ("BAYES_FACTOR_01", "BAYES_FACTOR"),
        ("BIAS_VAR_05", "BIAS_VAR"),
        ("MSE_COMPARE_04", "MSE_COMPARE"),
    ]
    failures = []
    for inp, expected in cases:
        got = task_type_from_id(inp)
        if got != expected:
            failures.append(f"  {inp}: expected {expected!r}, got {got!r}")
    if failures:
        print("FAIL:")
        print("\n".join(failures))
        raise SystemExit(1)
    print(f"OK ({len(cases)} cases passed)")
