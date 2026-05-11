#!/usr/bin/env python3
# baseline/bayesian/build_tasks_advanced.py
"""
Generate 35 advanced computational-Bayes tasks (5 per method × 7 methods).
Writes to data/raw_data/benchmark_v1/tasks_advanced.json.
Run from project root:
  python -m baseline.bayesian.build_tasks_advanced
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List

import numpy as np

from data_preprocessing.bayesian.advanced_methods import (
    GibbsSampler,
    MetropolisHastings,
    HamiltonianMC,
    RJMCMC,
    VariationalBayes,
    ABCMethod,
    HierarchicalBayes,
)

OUT_PATH = "data/raw_data/benchmark_v1/tasks_advanced.json"


# ── shared builder ────────────────────────────────────────────────────────────

def make_task(
    task_id: str,
    task_type: str,
    tier: int,
    difficulty: str,
    inputs: Dict[str, Any],
    numeric_targets: Dict[str, float],
    structure_checks: List[str],
    assumption_checks: List[str],
    prompt: str,
    tol: float = 0.05,
    zero: float = 0.20,
) -> Dict[str, Any]:
    return {
        "task_id": task_id,
        "task_type": task_type,
        "category": "computational_bayes",
        "tier": tier,
        "difficulty": difficulty,
        "inputs": inputs,
        "numeric_targets": [
            {
                "key": k,
                "true_value": float(v),
                "full_credit_tol": tol,
                "zero_credit_scale": zero,
            }
            for k, v in numeric_targets.items()
        ],
        "required_structure_checks": structure_checks,
        "required_assumption_checks": assumption_checks,
        "prompt": prompt,
    }


# ── 1. GIBBS tasks ────────────────────────────────────────────────────────────

def gen_gibbs_tasks() -> List[Dict[str, Any]]:
    configs = [
        dict(mu_x=0.0,  mu_y=0.0,  sigma_x=1.0, sigma_y=1.0, rho=0.5,  n_samples=2000, n_burnin=500,  tier=2, difficulty="basic"),
        dict(mu_x=2.0,  mu_y=-1.0, sigma_x=1.5, sigma_y=0.8, rho=0.7,  n_samples=3000, n_burnin=500,  tier=2, difficulty="intermediate"),
        dict(mu_x=-1.0, mu_y=3.0,  sigma_x=2.0, sigma_y=1.0, rho=0.3,  n_samples=2000, n_burnin=500,  tier=3, difficulty="intermediate"),
        dict(mu_x=5.0,  mu_y=5.0,  sigma_x=1.0, sigma_y=2.0, rho=-0.6, n_samples=4000, n_burnin=1000, tier=3, difficulty="advanced"),
        dict(mu_x=0.0,  mu_y=0.0,  sigma_x=3.0, sigma_y=3.0, rho=0.9,  n_samples=5000, n_burnin=1000, tier=4, difficulty="advanced"),
    ]
    tasks = []
    for i, cfg in enumerate(configs, start=1):
        solver = GibbsSampler(cfg)
        result = solver.solve()
        assert solver.validate(), f"GIBBS_{i:02d} failed validate()"
        prompt = (
            f"Use Gibbs sampling to sample from a bivariate normal distribution with "
            f"mu_x={cfg['mu_x']}, mu_y={cfg['mu_y']}, sigma_x={cfg['sigma_x']}, "
            f"sigma_y={cfg['sigma_y']}, rho={cfg['rho']}. "
            f"Run {cfg['n_samples']} samples after {cfg['n_burnin']} burn-in steps "
            f"(seed 42). "
            f"Report posterior_mean_x, posterior_mean_y, and posterior_var_x."
        )
        tasks.append(make_task(
            task_id=f"GIBBS_{i:02d}",
            task_type="GIBBS",
            tier=cfg["tier"],
            difficulty=cfg["difficulty"],
            inputs={k: cfg[k] for k in cfg if k not in ("tier", "difficulty")},
            numeric_targets={
                "posterior_mean_x": result["posterior_mean_x"],
                "posterior_mean_y": result["posterior_mean_y"],
                "posterior_var_x":  result["posterior_var_x"],
            },
            structure_checks=[
                "defines_conditional_distributions",
                "implements_alternating_sampling",
                "applies_burn_in",
            ],
            assumption_checks=[
                "uses_bivariate_normal_conditionals",
                "seeds_rng_for_reproducibility",
            ],
            prompt=prompt,
        ))
    return tasks


# ── 2. MH tasks ───────────────────────────────────────────────────────────────

def gen_mh_tasks() -> List[Dict[str, Any]]:
    configs = [
        dict(prior_mean=0.0, prior_std=1.0, n_obs=10, n_success=7,  proposal_std=0.3, n_samples=4000, tier=2, difficulty="basic"),
        dict(prior_mean=0.0, prior_std=2.0, n_obs=20, n_success=12, proposal_std=0.5, n_samples=5000, tier=2, difficulty="intermediate"),
        dict(prior_mean=0.0, prior_std=1.0, n_obs=50, n_success=30, proposal_std=0.4, n_samples=6000, tier=3, difficulty="intermediate"),
        dict(prior_mean=1.0, prior_std=1.5, n_obs=30, n_success=25, proposal_std=0.3, n_samples=5000, tier=3, difficulty="advanced"),
        dict(prior_mean=0.0, prior_std=3.0, n_obs=100,n_success=60, proposal_std=0.2, n_samples=8000, tier=4, difficulty="advanced"),
    ]
    tasks = []
    for i, cfg in enumerate(configs, start=1):
        solver = MetropolisHastings(cfg)
        result = solver.solve()
        assert solver.validate(), f"MH_{i:02d} failed validate()"
        prompt = (
            f"Use Metropolis-Hastings (in logit space) to sample from the posterior of "
            f"theta given {cfg['n_success']} successes in {cfg['n_obs']} Bernoulli trials, "
            f"with Normal({cfg['prior_mean']}, {cfg['prior_std']}^2) prior on logit(theta). "
            f"Proposal std = {cfg['proposal_std']}, {cfg['n_samples']} post-burnin samples, seed 42. "
            f"Report posterior_mean, posterior_std, and acceptance_rate."
        )
        tasks.append(make_task(
            task_id=f"MH_{i:02d}",
            task_type="MH",
            tier=cfg["tier"],
            difficulty=cfg["difficulty"],
            inputs={k: cfg[k] for k in cfg if k not in ("tier", "difficulty")},
            numeric_targets={
                "posterior_mean":  result["posterior_mean"],
                "posterior_std":   result["posterior_std"],
                "acceptance_rate": result["acceptance_rate"],
            },
            structure_checks=[
                "proposes_in_logit_space",
                "computes_log_acceptance_ratio",
                "tracks_acceptance_rate",
            ],
            assumption_checks=[
                "applies_binomial_log_likelihood",
                "transforms_via_sigmoid",
            ],
            prompt=prompt,
            tol=0.05,
        ))
    return tasks


# ── 3. HMC tasks ──────────────────────────────────────────────────────────────

def gen_hmc_tasks() -> List[Dict[str, Any]]:
    configs = [
        dict(prior_mean=0.0, prior_std=2.0, likelihood_std=1.0, obs_mean=2.0, n_obs=10,  step_size=0.1, n_leapfrog=5,  tier=3, difficulty="intermediate"),
        dict(prior_mean=1.0, prior_std=3.0, likelihood_std=0.5, obs_mean=3.0, n_obs=20,  step_size=0.05,n_leapfrog=10, tier=3, difficulty="intermediate"),
        dict(prior_mean=0.0, prior_std=1.0, likelihood_std=2.0, obs_mean=1.0, n_obs=5,   step_size=0.2, n_leapfrog=5,  tier=2, difficulty="basic"),
        dict(prior_mean=0.0, prior_std=5.0, likelihood_std=1.0, obs_mean=4.0, n_obs=50,  step_size=0.05,n_leapfrog=20, tier=4, difficulty="advanced"),
        dict(prior_mean=2.0, prior_std=2.0, likelihood_std=1.5, obs_mean=5.0, n_obs=30,  step_size=0.1, n_leapfrog=10, tier=3, difficulty="advanced"),
    ]
    tasks = []
    for i, cfg in enumerate(configs, start=1):
        solver = HamiltonianMC(cfg)
        result = solver.solve()
        assert solver.validate(), f"HMC_{i:02d} failed validate()"
        prompt = (
            f"Use Hamiltonian Monte Carlo to sample from a Normal posterior "
            f"(prior N({cfg['prior_mean']}, {cfg['prior_std']}^2), "
            f"likelihood N(theta, {cfg['likelihood_std']}^2), "
            f"observed mean={cfg['obs_mean']} from {cfg['n_obs']} observations). "
            f"Step size={cfg['step_size']}, {cfg['n_leapfrog']} leapfrog steps, seed 42. "
            f"Report posterior_mean, posterior_std, and mean energy_error."
        )
        tasks.append(make_task(
            task_id=f"HMC_{i:02d}",
            task_type="HMC",
            tier=cfg["tier"],
            difficulty=cfg["difficulty"],
            inputs={k: cfg[k] for k in cfg if k not in ("tier", "difficulty")},
            numeric_targets={
                "posterior_mean": result["posterior_mean"],
                "posterior_std":  result["posterior_std"],
                "energy_error":   result["energy_error"],
            },
            structure_checks=[
                "implements_leapfrog_integrator",
                "computes_hamiltonian_energy",
                "applies_metropolis_correction",
            ],
            assumption_checks=[
                "uses_gradient_of_log_posterior",
                "refreshes_momentum_each_iteration",
            ],
            prompt=prompt,
            tol=0.05,
        ))
    return tasks


# ── 4. RJMCMC tasks ───────────────────────────────────────────────────────────

def gen_rjmcmc_tasks() -> List[Dict[str, Any]]:
    rng = np.random.default_rng(0)
    datasets = [
        rng.normal(0.0, 1.0, 12).tolist(),
        rng.normal(2.0, 1.0, 16).tolist(),
        rng.normal(0.0, 2.0, 20).tolist(),
        rng.normal(5.0, 1.5, 10).tolist(),
        (np.concatenate([rng.normal(0.0, 1.0, 8), rng.normal(4.0, 1.0, 8)])).tolist(),
    ]
    prior_prob_m1s = [0.5, 0.5, 0.6, 0.4, 0.5]
    tiers      = [2, 2, 3, 3, 4]
    diffs      = ["basic", "intermediate", "intermediate", "advanced", "advanced"]

    tasks = []
    for i, (data, p1, tier, diff) in enumerate(
        zip(datasets, prior_prob_m1s, tiers, diffs), start=1
    ):
        cfg = dict(data=data, prior_prob_m1=p1, proposal_std=0.3)
        solver = RJMCMC(cfg)
        result = solver.solve()
        assert solver.validate(), f"RJMCMC_{i:02d} failed validate()"
        prompt = (
            f"Compute the analytical Bayes factor between M1 (single Normal mean over "
            f"all {len(data)} observations) and M2 (separate Normal means for two halves). "
            f"Prior P(M1)={p1}. "
            f"Data: {[round(x, 4) for x in data]}. "
            f"Report posterior_prob_m1, posterior_prob_m2, and bayes_factor."
        )
        tasks.append(make_task(
            task_id=f"RJMCMC_{i:02d}",
            task_type="RJMCMC",
            tier=tier,
            difficulty=diff,
            inputs={"data": data, "prior_prob_m1": p1, "proposal_std": 0.3},
            numeric_targets={
                "posterior_prob_m1": result["posterior_prob_m1"],
                "posterior_prob_m2": result["posterior_prob_m2"],
                "bayes_factor":      result["bayes_factor"],
            },
            structure_checks=[
                "computes_marginal_likelihood_for_each_model",
                "applies_bayes_theorem_for_model_probabilities",
                "reports_bayes_factor",
            ],
            assumption_checks=[
                "uses_normal_marginal_likelihood_formula",
                "posterior_probs_sum_to_one",
            ],
            prompt=prompt,
            tol=0.05,
        ))
    return tasks


# ── 5. VB tasks ───────────────────────────────────────────────────────────────

def gen_vb_tasks() -> List[Dict[str, Any]]:
    rng = np.random.default_rng(1)
    configs = [
        dict(prior_mean=0.0, prior_var=1.0,  likelihood_var=1.0, observations=rng.normal(2.0, 1.0, 10).tolist(),  n_iter=50, tier=2, difficulty="basic"),
        dict(prior_mean=1.0, prior_var=2.0,  likelihood_var=0.5, observations=rng.normal(3.0, 0.7, 20).tolist(),  n_iter=50, tier=2, difficulty="intermediate"),
        dict(prior_mean=0.0, prior_var=5.0,  likelihood_var=2.0, observations=rng.normal(-1.0, 1.4, 15).tolist(), n_iter=50, tier=3, difficulty="intermediate"),
        dict(prior_mean=2.0, prior_var=0.5,  likelihood_var=1.0, observations=rng.normal(4.0, 1.0, 30).tolist(),  n_iter=50, tier=3, difficulty="advanced"),
        dict(prior_mean=0.0, prior_var=10.0, likelihood_var=1.0, observations=rng.normal(5.0, 1.0, 50).tolist(),  n_iter=100,tier=4, difficulty="advanced"),
    ]
    tasks = []
    for i, cfg in enumerate(configs, start=1):
        solver = VariationalBayes(cfg)
        result = solver.solve()
        assert solver.validate(), f"VB_{i:02d} failed validate()"
        obs_short = [round(x, 4) for x in cfg["observations"][:5]]
        prompt = (
            f"Apply CAVI variational inference to a Normal-Normal model: "
            f"prior N({cfg['prior_mean']}, {cfg['prior_var']}), "
            f"likelihood N(theta, {cfg['likelihood_var']}), "
            f"{len(cfg['observations'])} observations (first 5: {obs_short}...). "
            f"Run {cfg['n_iter']} iterations. "
            f"Report variational_mean, variational_var, and final_elbo."
        )
        tasks.append(make_task(
            task_id=f"VB_{i:02d}",
            task_type="VB",
            tier=cfg["tier"],
            difficulty=cfg["difficulty"],
            inputs={
                "prior_mean": cfg["prior_mean"],
                "prior_var": cfg["prior_var"],
                "likelihood_var": cfg["likelihood_var"],
                "observations": cfg["observations"],
                "n_iter": cfg["n_iter"],
            },
            numeric_targets={
                "variational_mean": result["variational_mean"],
                "variational_var":  result["variational_var"],
                "final_elbo":       result["final_elbo"],
            },
            structure_checks=[
                "derives_variational_posterior_parameters",
                "computes_elbo",
                "iterates_cavi_updates",
            ],
            assumption_checks=[
                "assumes_mean_field_factorization",
                "uses_conjugate_updates",
            ],
            prompt=prompt,
            tol=0.10,
        ))
    return tasks


# ── 6. ABC tasks ──────────────────────────────────────────────────────────────

def gen_abc_tasks() -> List[Dict[str, Any]]:
    configs = [
        dict(observed_mean=2.0,  observed_std=1.0, n_obs=20, prior_low=0.0,  prior_high=5.0, n_simulations=20000, epsilon=0.2,  tier=2, difficulty="basic"),
        dict(observed_mean=3.5,  observed_std=0.5, n_obs=30, prior_low=1.0,  prior_high=6.0, n_simulations=20000, epsilon=0.15, tier=2, difficulty="intermediate"),
        dict(observed_mean=0.0,  observed_std=2.0, n_obs=10, prior_low=-5.0, prior_high=5.0, n_simulations=20000, epsilon=0.3,  tier=3, difficulty="intermediate"),
        dict(observed_mean=10.0, observed_std=1.5, n_obs=50, prior_low=7.0,  prior_high=13.0,n_simulations=30000, epsilon=0.2,  tier=3, difficulty="advanced"),
        dict(observed_mean=5.0,  observed_std=1.0, n_obs=100,prior_low=3.0,  prior_high=7.0, n_simulations=50000, epsilon=0.1,  tier=4, difficulty="advanced"),
    ]
    tasks = []
    for i, cfg in enumerate(configs, start=1):
        solver = ABCMethod(cfg)
        result = solver.solve()
        assert solver.validate(), f"ABC_{i:02d} failed validate()"
        prompt = (
            f"Use ABC rejection sampling to approximate the posterior of theta "
            f"given observed mean={cfg['observed_mean']} from {cfg['n_obs']} observations "
            f"(observed std={cfg['observed_std']}). "
            f"Prior: Uniform({cfg['prior_low']}, {cfg['prior_high']}). "
            f"Run {cfg['n_simulations']} simulations with epsilon={cfg['epsilon']}, seed 42. "
            f"Report abc_posterior_mean and abc_posterior_std."
        )
        tasks.append(make_task(
            task_id=f"ABC_{i:02d}",
            task_type="ABC",
            tier=cfg["tier"],
            difficulty=cfg["difficulty"],
            inputs={k: cfg[k] for k in cfg if k not in ("tier", "difficulty")},
            numeric_targets={
                "abc_posterior_mean": result["abc_posterior_mean"],
                "abc_posterior_std":  result["abc_posterior_std"],
            },
            structure_checks=[
                "draws_from_prior",
                "simulates_data_from_likelihood",
                "applies_acceptance_criterion",
            ],
            assumption_checks=[
                "uses_sufficient_statistic_for_comparison",
                "epsilon_defines_tolerance_region",
            ],
            prompt=prompt,
            tol=0.10,
        ))
    return tasks


# ── 7. HIERARCHICAL tasks ─────────────────────────────────────────────────────

def gen_hierarchical_tasks() -> List[Dict[str, Any]]:
    configs = [
        dict(group_means=[1.0, 2.0, 3.0],            group_sizes=[10, 10, 10],          hyperprior_mean=2.0, hyperprior_var=1.0,  tier=2, difficulty="basic"),
        dict(group_means=[0.5, 1.5, 2.5, 3.5],       group_sizes=[20, 15, 25, 10],      hyperprior_mean=2.0, hyperprior_var=2.0,  tier=2, difficulty="intermediate"),
        dict(group_means=[5.0, 6.0, 4.5, 7.0, 5.5],  group_sizes=[30, 25, 20, 35, 15], hyperprior_mean=5.6, hyperprior_var=1.0,  tier=3, difficulty="intermediate"),
        dict(group_means=[10.0, 11.0, 9.5, 10.5],    group_sizes=[50, 40, 60, 45],      hyperprior_mean=10.25,hyperprior_var=0.5, tier=3, difficulty="advanced"),
        dict(group_means=[2.0, 4.0, 6.0, 8.0, 10.0], group_sizes=[5, 10, 15, 20, 25],  hyperprior_mean=6.0, hyperprior_var=5.0,  tier=4, difficulty="advanced"),
    ]
    tasks = []
    for i, cfg in enumerate(configs, start=1):
        solver = HierarchicalBayes(cfg)
        result = solver.solve()
        assert solver.validate(), f"HIERARCHICAL_{i:02d} failed validate()"
        prompt = (
            f"Fit a hierarchical Normal model (empirical Bayes). "
            f"Group means: {cfg['group_means']}, group sizes: {cfg['group_sizes']}. "
            f"Hyperprior: N({cfg['hyperprior_mean']}, {cfg['hyperprior_var']}). "
            f"Report hyperpost_mean, hyperpost_var, and shrinkage_factor."
        )
        tasks.append(make_task(
            task_id=f"HIERARCHICAL_{i:02d}",
            task_type="HIERARCHICAL",
            tier=cfg["tier"],
            difficulty=cfg["difficulty"],
            inputs={k: cfg[k] for k in cfg if k not in ("tier", "difficulty")},
            numeric_targets={
                "hyperpost_mean":   result["hyperpost_mean"],
                "hyperpost_var":    result["hyperpost_var"],
                "shrinkage_factor": result["shrinkage_factor"],
            },
            structure_checks=[
                "computes_group_level_sampling_variances",
                "derives_hyperparameter_posterior",
                "computes_shrinkage_weights",
            ],
            assumption_checks=[
                "normal_normal_hierarchy_stated",
                "shrinkage_factor_between_0_and_1",
            ],
            prompt=prompt,
            tol=0.05,
        ))
    return tasks


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    tasks: List[Dict[str, Any]] = []
    generators = [
        ("GIBBS",        gen_gibbs_tasks),
        ("MH",           gen_mh_tasks),
        ("HMC",          gen_hmc_tasks),
        ("RJMCMC",       gen_rjmcmc_tasks),
        ("VB",           gen_vb_tasks),
        ("ABC",          gen_abc_tasks),
        ("HIERARCHICAL", gen_hierarchical_tasks),
    ]

    for name, gen_fn in generators:
        group = gen_fn()
        tasks.extend(group)
        print(f"  {name:<14}: {len(group)} tasks generated")

    # Validate no duplicate task_ids
    ids = [t["task_id"] for t in tasks]
    assert len(ids) == len(set(ids)), "Duplicate task IDs found!"
    assert len(tasks) == 35, f"Expected 35 tasks, got {len(tasks)}"

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

    print(f"\nWrote {len(tasks)} tasks → {OUT_PATH}")
    tiers = {}
    diffs = {}
    for t in tasks:
        tiers[t["tier"]] = tiers.get(t["tier"], 0) + 1
        diffs[t["difficulty"]] = diffs.get(t["difficulty"], 0) + 1
    print(f"  Tiers: {dict(sorted(tiers.items()))}")
    print(f"  Difficulties: {diffs}")


if __name__ == "__main__":
    main()
