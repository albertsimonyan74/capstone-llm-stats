# Methodology Continuity Statement

This benchmark extends StatEval (Lu et al., 2025) from descriptive and
hypothesis-testing statistics to Bayesian inference. Where StatEval uses
multiple-choice format, we adopt free-response with a 5-dimensional rubric
(N·M·A·C·R) following the multi-dimensional convention of MathEval
(Liu et al., 2025). Our prompting baseline follows zero-shot
chain-of-thought (Wei et al., 2022), with Program-of-Thoughts (Chen et al.,
2022) considered and deferred because Bayesian closed-form derivations
rely on symbolic manipulation more than arithmetic. Methodology rigour
combines external-judge validation via Llama 3.3 70B (Yamauchi et al.,
2025), bootstrap-CI separability motivated by Statistical Fragility
(Hochlehnert et al., 2025) and Longjohn et al. (2025), perturbation
robustness adapted from BrittleBench (2026), and the variance-as-first-class
framing of ReasonBench (Au et al., 2025). Calibration concerns are raised
by Nagarkar et al. (2026) and contrast with FermiEval's (2025)
overconfidence finding — our Bayesian-task setting produces hedge-heavy
behaviour instead. Limitations around single-judge bias are framed by
Judgment-Becomes-Noise (Feuer et al., 2025); future work toward
multi-judge ensembling and consistency-based confidence (Multi-Answer
Confidence, 2026) is explicitly scoped.

## NMACR weighting — literature-derived (Phase 1B)

The five NMACR dimensions are not weighted equally. The locked scheme
A=0.30, R=0.25, M=0.20, C=0.15, N=0.10 is anchored in the prior literature
on LLM evaluation: Du (2025), Boye & Moell (2025), and Yamauchi (2025) all
identify assumption articulation as the dominant failure mode and the
hardest dimension for keyword rubrics to score honestly — A=0.30. Yamauchi
(2025), Boye & Moell (2025), and Au et al. (2025, ReasonBench) elevate
reasoning quality as the most externally-judgeable dimension — R=0.25.
Method selection follows Wei (2022), Chen (2022), and Bishop (2006), is
partially redundant with reasoning, and weighted moderately — M=0.20.
Confidence calibration is a separate evaluation track in Nagarkar (2026),
FermiEval (2025), and Multi-Answer Confidence (2026); we honestly disclose
that verbalized extraction is the weakest baseline — C=0.15. Numerical
correctness is necessary but trivially checkable per Liu (2025) and
Boye & Moell (2025) — N=0.10. See
[`llm-stats-vault/00-home/research-narrative.md`](../llm-stats-vault/00-home/research-narrative.md)
§2 for the full per-dimension defense and
[`audit/recompute_log.md`](recompute_log.md) for the data-layer effect.
