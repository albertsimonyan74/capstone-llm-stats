# RQ Restructuring

Phase 1B reframing. Resolves professor notes #14 (RQ structure) and #15
(depth on RQ2-5). Each RQ tied to literature. Designed to make RQ1
(methodology) the load-bearing contribution, with RQ2-5 as supporting
evidence. Tier badges are **PRIMARY** vs **SUPPORTING** only — explicit
percentage badges dropped because the NMACR weighting scheme already
encodes the relative emphasis at the data layer (A=0.30, R=0.25, M=0.20,
C=0.15, N=0.10) and percentage-on-percentage labels confused readers in
Phase 1A review.

For canonical project structure see
[`llm-stats-vault/00-home/research-narrative.md`](../llm-stats-vault/00-home/research-narrative.md).

## Original RQ structure (critiqued)

RQ1-5 were treated as five co-equal questions. The narrative reduced to
"I built a Bayesian benchmark and Claude won," which is the framing the
professor flagged as not research-supportive. Co-equal RQs collapse a
methodology contribution (judge validation) into the same row as a
leaderboard claim, making the work indistinguishable from a vendor
comparison.

## Revised RQ structure

### RQ1 — PRIMARY: How does external-judge validation differ from keyword scoring?

- **Headline.** 25.0% pass-flip on `assumption_compliance`
  (274 / 1095 runs). Krippendorff α = 0.55 (95% CI [0.504, 0.595],
  questionable under Park et al. thresholds); Spearman ρ = 0.59
  (moderate). Both metrics agree: keyword and judge are not
  interchangeable raters on assumption compliance.
- **Justification.** Methodology contribution. Demonstrates that keyword
  rubrics systematically overstate assumption-checking quality on
  Bayesian tasks; provides a re-usable judge-validation protocol.
- **NMACR mapping.** Cross-validates **all 5** dimensions against the
  external Llama 3.3 70B judge.
- **Grounding.**
  - Yamauchi et al. (2025) [arXiv:2506.13639] — α-over-ρ for inter-rater
    reliability; judge-design sensitivity > judge-model sensitivity.
  - Liu et al. (2025) — multi-dimensional rubric baseline (NMACR extends
    MathEval's separation of numeric vs reasoning).

### RQ2 — SUPPORTING: Which Bayesian reasoning categories are hardest?

- **Headline.** REGRESSION cluster mean accuracy ~0.30 across all 5
  models (`a2_accuracy_by_category.png`). MCMC and ADVANCED clusters
  also score below cohort mean.
- **Justification.** Domain-specific failure surface that prior
  benchmarks cannot expose because they lack Bayesian coverage.
- **NMACR mapping.** Aggregates `aggregate_new` (literature-weighted) by
  Bayesian category.
- **Grounding.**
  - Liu et al. (2025) — task-category organisation convention.
  - Boye & Moell (2025) [Math-Reasoning-Failures, arXiv:2502.11574] —
    multi-domain math-reasoning failure catalogue; "unwarranted
    assumptions" category aligns with our REGRESSION drops.

### RQ3 — SUPPORTING: What is the dominant failure mode?

- **Headline.** ASSUMPTION_VIOLATION = 46.9% of 143 base failures
  (vs MATHEMATICAL_ERROR 33.6%, FORMATTING 12.6%, CONCEPTUAL 7.0%,
  HALLUCINATION 0). The failure mode is silent assumption-skipping,
  not arithmetic error.
- **Justification.** Aligns with two independent prior reports —
  strengthens external validity.
- **NMACR mapping.** L1 taxonomy is the failure decomposition over
  NMACR dimensions:
  - MATHEMATICAL_ERROR → N failure
  - ASSUMPTION_VIOLATION → A failure
  - CONCEPTUAL_ERROR → M failure
  - HALLUCINATION → R + N failure (empirically empty, disclosed)
  - FORMATTING_FAILURE → pre-rubric exclusion (orthogonal report-level metric)
- **Grounding.**
  - Du et al. (2025) [Ice Cream, arXiv:2505.13770] — independently
    reports ~47% assumption-violation on causal-inference tasks.
  - Boye & Moell (2025) — confirms unwarranted-assumption as a top
    failure across general math domains.

### RQ4 — SUPPORTING: Are accuracy rankings robust to prompt perturbation?

- **Headline.** Three orthogonal rankings disagree:
  accuracy ≠ robustness ≠ calibration. ChatGPT and DeepSeek robustness
  Δ ≈ 0 (noise-equivalent); under literature-derived weighting Mistral
  has the smallest aggregate Δ. Per-dimension robustness now exposed
  (Layer 2 in `robustness_v2.json` → `per_dim_delta`).
- **Justification.** Demonstrates that single-metric leaderboards
  mislead; ranks produced by accuracy alone do not survive perturbation.
- **NMACR mapping.** Two layers.
  - **Layer 1.** Aggregate Δ per model.
  - **Layer 2 (NEW Phase 1B).** 5 × 5 grid of (model, dimension)
    perturbation deltas. The A dimension shows the largest deltas for
    Claude / DeepSeek / Gemini — directly confirms the RQ3 finding.
- **Grounding.**
  - Au et al. (2025) [ReasonBench, arXiv:2512.07795] — variance-as-first-class.
  - BrittleBench (2026) [arXiv:2603.13285] — perturbation taxonomy
    (rephrase / numerical / semantic) directly adopted.
  - Hochlehnert et al. (2025) [Statistical Fragility, arXiv:2504.07086]
    — single-question swaps shift Pass@1 ≥ 3 pp; motivates bootstrap-CI
    separability tests.

### RQ5 — SUPPORTING: Are LLM confidence claims calibrated?

- **Headline.** Zero high-confidence records across 5 models (verbalized
  extraction); hedge-heavy default-to-medium behaviour; explicit
  contrast with FermiEval's overconfidence finding. Per-dimension ECE
  (Layer 5) and accuracy-calibration correlation (Layer 4) added in
  Phase 1B. Pearson r ∈ [0.35, 0.49] across models with extractable
  confidence; gemini's confidence is uniformly unstated and excluded.
- **Justification.** Calibration is a separate evaluation track,
  honestly disclosed; per-dim breakdown surfaces which dimensions are
  systematically miscalibrated even when aggregate ECE looks fine.
- **NMACR mapping.** C dimension primarily; per-dim calibration treats
  every NMACR dim as its own calibration target.
- **Grounding.**
  - Nagarkar et al. (2026) [arXiv:2601.14479] — reliability +
    hallucination motivation.
  - FermiEval (2025) [arXiv:2510.26995] — overconfidence contrast.
  - Multi-Answer Confidence (2026) [arXiv:2602.07842] — verbalised vs
    consistency-based methodology dichotomy.

## Why PRIMARY vs SUPPORTING (instead of percentage badges)

- The **NMACR weighting** (A=0.30, R=0.25, M=0.20, C=0.15, N=0.10)
  already encodes per-dimension emphasis at the data layer. Reusing
  percentage badges at the RQ layer (40% / 15%) created a second
  budget that confused readers in Phase 1A review — was the PRIMARY
  RQ40%? was that an evidence-weight? a presentation-weight?
- **PRIMARY** means: the RQ that produces a generalisable methodology
  contribution. Single such RQ in this work — RQ1.
- **SUPPORTING** means: an evidence-anchor RQ that grounds the PRIMARY
  claim in concrete benchmark numbers. RQ2-5 collectively provide the
  surface area RQ1's methodology argument needs.
- No RQ is a leaderboard claim. Ranks are reported with bootstrap CIs
  and separability tests (Hochlehnert 2025), so even RQ4's "Gemini tops
  accuracy under literature weighting" reads as a calibrated point
  estimate, not a benchmark trophy.

## What this changes in the poster

- Abstract leads with "judge-validation methodology" not "Claude wins".
- RQ1 panel becomes the largest block; RQ2-5 panels share the bottom
  two rows.
- Limitations panel cites Feuer et al. (2025) "Judgment Becomes Noise"
  for the single-judge caveat and Multi-Answer Confidence (2026) for
  the keyword-confidence weakness.
- Future-work block names the consistency-based confidence upgrade
  (Phase 1C) and the multi-judge ensemble (paper-scope).
- Three-rankings figure footer notes the literature-derived NMACR
  weighting scheme.
