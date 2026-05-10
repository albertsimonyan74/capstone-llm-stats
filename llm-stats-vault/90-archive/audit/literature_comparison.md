# Literature Comparison Table

Positions this Bayesian benchmark against 7 prior systems across 10 dimensions.
Citation grounding for the Day 3 RQ-reweighting + methodology-continuity narrative.

Highlighted row: **THIS WORK** (DS 299 Bayesian benchmark).

| Dimension | StatEval (Lu 2025) | MathEval (Liu 2025) | ReasonBench (2025) | BrittleBench (2026) | Ice-Cream (Wang 2025) | FermiEval (2025) | Can-LLM-Reasoning (Nagarkar 2026) | **THIS WORK** |
|---|---|---|---|---|---|---|---|---|
| Domain specificity | Statistics (descriptive + freq.) | General math | General reasoning | General reasoning | Causal inference | Fermi estimation | Statistical reasoning | **Bayesian inference (target)** |
| # tasks | ~500 (frequentist) | 17 datasets unified | unspecified, multi-domain | multi-bench coverage | ~30 pitfalls | Fermi-style | unspecified | **171 (136 P1 + 35 P2)** |
| Ground-truth source | Hand-crafted MC keys | Mixed (existing datasets) | Mixed | Mixed | Hand-crafted | Closed-form bounds | Mixed | **Closed-form + seeded MC (np.random.seed=42)** |
| Format | Multiple-choice | Mixed (mostly free-resp) | Free-response | Free-response | Free-response | Numeric interval | Free-response | **Free-response, 5-dim rubric** |
| External judge | ✗ | ✓ (rubric) | partial | ✗ | ✗ | ✗ | ✗ | **✓ Llama 3.3 70B (Together AI)** |
| Perturbations | ✗ | ✗ | ✓ (variance focus) | ✓ (rephrase / numerical / semantic) | ✗ | ✗ | ✗ | **✓ 398 v2 (3 types)** |
| Statistical rigor | Single-point | Multi-dim aggregate | Variance-as-1st-class | Bootstrap recommended | Single-point | CI calibration | Single-point | **Bootstrap CI + Krippendorff α (Park 2025)** |
| Calibration analysis | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ verbalised CI | partial (reliability) | **✓ keyword + future consistency-based (MAC 2026)** |
| Error taxonomy | ✗ | partial | ✗ | ✗ | ✓ assumption-violation | ✗ | partial (hallucination) | **✓ 4-L1 / 9-L2 hierarchical** |
| Open data + reproducibility | ✓ | ✓ | partial | ✓ | ✓ | ✓ | partial | **✓ All artefacts open (data/, experiments/, scripts/)** |
| NMACR weighting scheme | equal / unspecified | equal / unspecified | unspecified | equal / unspecified | unspecified | unspecified | unspecified | **literature-derived (A=0.30, R=0.25, M=0.20, C=0.15, N=0.10)** |

## Summary

- **Closest neighbour**: StatEval — same statistical-reasoning lens, but limited to descriptive + frequentist methods and uses MC format. This benchmark extends StatEval to Bayesian inference and free-response.
- **Closest methodology siblings**: MathEval (multi-dim rubric) for scoring design; ReasonBench + BrittleBench for the perturbation + variance framing; Park et al. (2025) for the agreement-metric upgrade.
- **Closest discussion contrasts**: FermiEval (overconfidence on estimation) vs this work (hedge-heavy on Bayesian tasks).
- **Closest failure-mode confirmation**: Du et al. ("Ice Cream", 2025) and Boye & Moell (Math-Reasoning-Failures, 2025) both report assumption-violation as the dominant L1 — matches our 46.9 % share.

## What is novel here

1. First free-response Bayesian-inference benchmark with externally-validated rubric scoring.
2. Single-domain perturbation taxonomy (398 perturbations × 5 models) tied to Bayesian semantics, not generic surface rephrasings.
3. Bootstrap-CI ranking separability + Krippendorff α agreement run together — most prior work uses one or neither.
4. Four-bucket calibration disclosed transparently with an explicit upgrade path to consistency-based confidence (MAC 2026).
