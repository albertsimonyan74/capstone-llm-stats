---
tags: [literature, poster, citations]
date: 2026-05-01
---

# Poster-ready short citations

Drop-in strings for poster panels.

---

## Papers (15)

### Original references (5)
- Lu et al. (2025)               — closest prior work, StatEval extension
- Nagarkar et al. (2026)         — RQ5 motivation
- Liu et al. (2025)              — MathEval baseline for rubric design
- Chen et al. (2022)             — Program-of-Thoughts prompting
- Wei et al. (2022)              — Chain-of-Thought baseline

### New discoveries (10)
- Longjohn et al. (2025)         — bootstrap CI motivation
- ReasonBench (2025)             — instability framing, three rankings
- BrittleBench (2026)            — perturbation methodology
- Wang et al. (2025) [Ice Cream] — causal pitfalls / assumption violation
- Park et al. (2025)             — Krippendorff α recommendation
- FermiEval (2025)               — overconfidence contrast
- Multi-Answer (2026)            — consistency-based confidence
- Math-Failures (2026)           — rubric design validation
- Judgment-Noise (2025)          — single-judge limitation
- Fragility (2025)               — separability motivation

## Textbooks (7) — typically cited in foundations footer

- Bolstad (2007)
- Bishop (2006)
- Ghosh et al. (2006)
- Hoff (2009)
- Carlin & Louis (2008)
- Goldstein & Wooff (2007)
- Lee (2012)

---

## Suggested poster footer line

> Methodology grounded in [Lu25, ReasonBench, Park25]; perturbations follow
> [BrittleBench]; statistical rigor in [Longjohn25, Fragility25]; calibration
> in [FermiEval, Nagarkar26, Multi-Answer26]; limitations framed by
> [Judgment-Noise25]. Bayesian foundations: Bolstad, Bishop, Hoff, Carlin &
> Louis, Lee, Ghosh et al., Goldstein & Wooff.

---

## Inline citation styles by venue

- **Poster (compact):** first-author surname + year only, e.g. "(Lu, 2025)".
- **Paper prose (formal):** full author list for first citation, "et al." after.
- **Methodology section:** cluster citations by theme using square brackets,
  e.g. "[Wei22, Chen22]" for prompting; "[Longjohn25, Fragility25]" for
  uncertainty quantification.

---

## Citation cluster recipes (paste-ready)

### Abstract / opening
> Building on StatEval (Lu et al., 2025) and motivated by reasoning-instability
> findings (ReasonBench, 2025; BrittleBench, 2026), we evaluate 5 frontier LLMs
> on 171 Bayesian inference tasks with statistical-rigor protocols
> (Longjohn et al., 2025; Statistical Fragility, 2025).

### RQ3 failure taxonomy
> Independent work confirms assumption-violation as the dominant failure mode
> in causal-statistical reasoning (Wang et al., 2025) and mathematical
> reasoning (Math-Failures, 2026).

### RQ5 calibration
> Unlike the systematic overconfidence FermiEval (2025) reports for estimation
> tasks, our Bayesian benchmark surfaces a hedge-heavy default; the Multi-Answer
> work (2026) provides the consistency-based upgrade path.

### Limitations
> Single-judge benchmarks introduce systematic noise (Judgment-Noise, 2025);
> our verbalized confidence extraction is the weakest baseline among options
> reviewed by Multi-Answer (2026).

### Foundations footer (one line)
> Bayesian foundations: Bolstad (2007), Bishop (2006), Ghosh et al. (2006),
> Hoff (2009), Carlin & Louis (2008), Goldstein & Wooff (2007), Lee (2012).
