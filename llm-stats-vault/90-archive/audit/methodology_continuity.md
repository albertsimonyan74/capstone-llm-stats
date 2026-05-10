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

## NMACR weighting — literature-derived (sole canonical scheme)

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

### History — pre-Approach-A dual-path
Phase 1A initially scored runs under equal weights (N=M=A=C=R=0.20) at
runtime, with the literature-weighted aggregate produced post-hoc by
`scripts/recompute_nmacr.py` (Phase 1B, 2026-05-01). On 2026-05-03,
Approach A consolidated both paths: the literature-weighted scheme is
now applied at runtime in `evaluation/metrics.py` and
`llm_runner/response_parser.py`, and is the SOLE canonical scheme.
The post-hoc script is archived at
`llm-stats-vault/90-archive/superseded_scripts/recompute_nmacr.py`. See
[`audit/recompute_log.md`](recompute_log.md) §"Phase 1.6 — Approach A"
for the migration audit trail.

### History — Phase 1.7 Tier 1 coverage fixes (2026-05-03)
A diagnostic pass on the same date surfaced two compounding bugs in the
score-coverage layer: (1) `_make_run_record()` in
`llm_runner/run_all_tasks.py` chronically omitted `reasoning_score` and
`confidence_score` from logged records; (2)
`scripts/recompute_scores.py:23` pointed at the Phase-1-only
`tasks.json` instead of `tasks_all.json`, so post-hoc backfill only
covered 136/171 task_ids. Combined effect: Gemini (the only model fully
re-issued after the most recent recompute, RPD quota recovery on
2026-04-26) appeared to have 0/246 reasoning + confidence signals; the
other 4 models retained partial coverage from earlier runs.

Tier 1 fixes (Fix A/B/C/D) corrected the path, regenerated all 1,230
records from intact `raw_response` text (no API calls), extended
Krippendorff α reporting to base/perturbation/combined scopes, and
acknowledged MARKOV_04 in the Limitations exclusion list. Numbers shifted
1–4pp on accuracy and robustness; the "Gemini calibration inversion" and
"Gemini 0 verbalized signals" claims were FALSIFIED and reframed
cohort-wide. The 22.16% combined keyword-judge disagreement headline was
UNCHANGED (independent of fix scope). Full audit trail in
[`audit/recompute_log.md`](recompute_log.md) §"Phase 1.7" and
[`audit/gemini_forensic_2026-05-03.md`](gemini_forensic_2026-05-03.md).

### History — Phase 1.8 V1 perturbation deprecation (2026-05-04)
A diagnostic pass identified that `runs.jsonl` co-mingled 855 truly-base
scoring rows with 375 v1-perturbation scoring rows (75 task_ids × 5
models). Every "base scope" headline downstream was therefore measured
on a contaminated denominator. The v1 perturbation set was byte-identical
to a subset of `perturbations_all.json` (preserved verbatim by the v2
generation script), making the v1 file redundant on top of contaminating.

The deprecation re-pointed 11 scripts to `perturbations_all.json` and
filtered v1-pert task_ids at `runs.jsonl` load in 5 consumer scripts +
backend + R pipeline (Strategy C, consumer-side filter). The 0.01pp STOP
gate triggered with 1,075 numerical changes across 7 canonical files.
Headline shifts: combined disagreement 22.16% → 20.74% (n 3,195 → 2,850);
α reasoning_quality −0.099 → −0.125 (negative finding STRENGTHENED);
α method_structure −0.042 → −0.009 (now essentially chance-level — CI
contains zero); ChatGPT/Mistral swap top-2 robustness (both noise-
equivalent). The "Mistral uniquely improves under perturbation" claim was
REMOVED (Δ flipped sign). Three-rankings story preserved with reframed
top-2 robustness. Full audit trail in
[`audit/recompute_log.md`](recompute_log.md) §"Phase 1.8" and
[`audit/v1_deprecation_diff_report.md`](v1_deprecation_diff_report.md).
