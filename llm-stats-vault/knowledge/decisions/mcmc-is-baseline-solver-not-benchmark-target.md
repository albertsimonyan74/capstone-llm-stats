---
tags: [decision, benchmark, scope, mcmc, bayesian]
date: 2026-04-26
---

# MCMC Is Baseline Solver, Not Benchmark Target

## Decision
MCMC methods (Gibbs, Metropolis-Hastings, HMC, RJMCMC) are **out of scope** for benchmark tasks asking LLMs to answer questions.

However, MCMC is used internally as the ground-truth computation engine for Phase 2 advanced tasks.

## Why
- Documented in `bayesian_scope.md`
- Asking an LLM to "run MCMC" is not meaningful in a text-only benchmark — they can't actually execute sampling algorithms
- The benchmark tests reasoning about statistical methods, not code execution ability
- Phase 2 tasks ask LLMs to compute/reason about the *results* of these methods (e.g., "given this Gibbs sampler setup, what is the conditional mean?") — not to implement them

## How It Works in Phase 2
- `code/data_preprocessing/bayesian/advanced_methods.py` implements 7 computational Bayes solvers:
  - `GibbsSampler`, `MetropolisHastings`, `HamiltonianMC`, `RJMCMC`
  - `VariationalBayes`, `ABCMethod`, `HierarchicalBayes`
- All solvers call `np.random.seed(42)` in `solve()` for reproducibility
- True values are MC estimates (seeded), not analytic — intentional for computational methods
- Tolerance is 0.05 for MCMC methods, 0.10 for VB and ABC (more approximate)

## How to Apply
- New task types involving MCMC: cast as "reasoning about results" not "implementing the algorithm"
- Ground-truth computation can still use MCMC internally via `advanced_methods.py`

## Related
- [[five-research-questions-define-benchmark-scope]] — RQ scope
- [[adding-a-new-task-type-requires-4-changes]] — how to add tasks
