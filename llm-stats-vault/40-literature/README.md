---
tags: [literature, references, index]
date: 2026-05-01
---

# Literature Library

Master index for the 22 sources grounding this benchmark project.
Organized by theme. Use citation-map.md for the reverse index
(project artifact → which sources cite it).

**Total sources: 22**
- 5 originally-cited papers (from website References section)
- 10 newly-discovered papers (Day 3 web search)
- 7 graduate textbooks (from website References section)

---

## Papers — by theme

### Closest prior work / methodology
- [Lu et al. (2025)](papers/01-original-stateval-2025.md) — StatEval, the closest prior LLM statistical-reasoning benchmark.
- [Liu et al. (2025)](papers/03-original-matheval-2025.md) — MathEval comparative baseline for multi-dimensional rubric design.
- [Park et al. (2025)](papers/10-new-llm-judge-empirical-2025.md) — LLM-as-Judge design, Krippendorff α recommendation.

### Robustness / stability
- [ReasonBench (2025)](papers/07-new-reasonbench-2025.md) — three-rankings framing (accuracy / robustness / calibration).
- [BrittleBench (2026)](papers/08-new-brittlebench-2026.md) — perturbation methodology blueprint.
- [Statistical Fragility (2025)](papers/15-new-statistical-fragility-2025.md) — single-question swaps shift Pass@1 by 3+ points.

### Statistical rigor / uncertainty
- [Longjohn et al. (2025)](papers/06-new-longjohn-bayesian-eval-2025.md) — Bayesian evaluation, bootstrap CI motivation.
- [Statistical Fragility (2025)](papers/15-new-statistical-fragility-2025.md) — separability tests for ranking claims.

### Failure taxonomy
- [Wang et al. (2025) — Ice Cream](papers/09-new-ice-cream-causal-2025.md) — assumption-violation as dominant failure mode (~47%).
- [Math Reasoning Failures (2026)](papers/13-new-math-reasoning-failures-2026.md) — unwarranted-assumptions failure mode validates rubric.

### Calibration (RQ5)
- [Nagarkar et al. (2026)](papers/02-original-can-llm-reasoning-2026.md) — reliability and hallucination motivate RQ5.
- [FermiEval (2025)](papers/11-new-fermieval-2025.md) — overconfidence on estimation (contrast finding).
- [Multi-Answer Confidence (2026)](papers/12-new-multi-answer-confidence-2026.md) — verbalized vs consistency-based confidence.

### Judge validation / limitations
- [Park et al. (2025)](papers/10-new-llm-judge-empirical-2025.md) — Krippendorff α design recommendation.
- [Judgment Becomes Noise (2025)](papers/14-new-judgment-becomes-noise-2025.md) — single-judge limitation.

### Prompting strategy
- [Wei et al. (2022)](papers/05-original-chain-of-thought-2022.md) — Chain-of-Thought (foundational).
- [Chen et al. (2022)](papers/04-original-program-of-thoughts-2022.md) — Program-of-Thoughts (alternative considered).

---

## Textbooks — by task-type coverage

| Textbook | Primary task types grounded |
|---|---|
| [Bolstad (2007)](textbooks/bolstad-bayesian-statistics.md) | BETA_BINOM, BINOM_FLAT, HPD, GAMMA_POISSON |
| [Bishop (2006) PRML](textbooks/bishop-prml.md) | VB_*, DIRICHLET_*, BAYES_REG, LOG_ML |
| [Ghosh, Delampady & Samanta (2006)](textbooks/ghosh-delampady-samanta-bayesian.md) | JEFFREYS_*, FISHER_INFO_*, RC_BOUND_*, MLE_EFFICIENCY |
| [Hoff (2009)](textbooks/hoff-bayesian-methods.md) | NORMAL_GAMMA_*, PPC_*, GIBBS_*, HIERARCHICAL |
| [Carlin & Louis (2008)](textbooks/carlin-louis-bayesian-data-analysis.md) | GIBBS, MH, HMC, RJMCMC, HIERARCHICAL, REGRESSION |
| [Goldstein & Wooff (2007)](textbooks/goldstein-wooff-bayes-linear.md) | BAYES_LINEAR_*, LINEAR_APPROX_* |
| [Lee (2012)](textbooks/lee-bayesian-statistics.md) | CI_CREDIBLE_*, BAYES_FACTOR_*, RJMCMC_* |

---

## Index files

- [citation-map.md](citation-map.md) — reverse index: artifact → sources.
- [bibtex.bib](bibtex.bib) — bibtex entries for all 22 sources.
- [poster-citations.md](poster-citations.md) — short-form strings ready for poster panels.

---

## How to cite from this vault

1. Open the relevant note (paper or textbook).
2. Copy the "Citation in poster" string for poster panels.
3. Copy the "Citation in paper" string for paper prose.
4. Use the bibtex key from bibtex.bib for LaTeX `\cite{key}`.

## When adding a new source

1. Copy the per-paper or per-textbook template (in this vault's session log
   or in the prompt that created this library).
2. Save as `papers/NN-tag-keyword-year.md` or `textbooks/firstauthor-topic.md`.
3. Update this README's theme sections.
4. Append the bibtex entry to bibtex.bib.
5. Update citation-map.md if the source maps to a specific artifact.

## TODO author-list confirmations

The following sources have placeholder author lists pending arXiv confirmation:
- Paper 01 (StatEval / Lu et al. 2025)
- Paper 02 (Nagarkar et al. 2026)
- Paper 03 (MathEval / Liu et al. 2025)
- Paper 06 (Longjohn et al. 2025)
- Paper 07 (ReasonBench 2025)
- Paper 08 (BrittleBench 2026)
- Paper 09 (Wang et al. 2025 — Ice Cream)
- Paper 10 (Park et al. 2025)
- Paper 11 (FermiEval 2025)
- Paper 12 (Multi-Answer 2026)
- Paper 13 (Math-Failures 2026)
- Paper 14 (Judgment-Noise 2025)
- Paper 15 (Statistical Fragility 2025 — also TODO original arXiv link)

Resolve these before final submission. Per task brief: max 2 web searches per
source — TODO flagged where metadata could not be fully verified within budget.
