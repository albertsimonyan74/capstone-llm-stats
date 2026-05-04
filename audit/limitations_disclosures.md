# Limitations Disclosures

Poster-ready text. 2–3 sentences each. Drop into the Limitations / Caveats
block of the poster and the Limitations section of the canonical narrative.

---

### a) Empty HALLUCINATION bucket in error taxonomy

The error taxonomy returned zero HALLUCINATION classifications across all
143 audited failures (L1 totals: ASSUMPTION_VIOLATION 67,
MATHEMATICAL_ERROR 48, FORMATTING_FAILURE 18, CONCEPTUAL_ERROR 10,
HALLUCINATION 0). The 0 across 143 is honestly ambiguous: it may reflect
a real property of closed-form Bayesian tasks — every task has a
deterministic ground truth, so models fail by skipping required
assumptions or miscomputing rather than fabricating priors, distributions,
or data — **or** it may reflect a single-judge classification limitation
(the Llama 3.3 70B judge prompt flags E5/E8/E9 "use only if nothing else
fits" and may systematically prefer the more concrete L1 buckets). A
multi-judge ensemble is required to disambiguate the two explanations;
that is paper-scope future work.

### b) Verbalized confidence is hedging-language-sensitive (empty high-confidence bucket)

All five models produced 0 responses classified as high-confidence
(claimed p ≥ 0.85) by our keyword-based extractor, leaving the 0.9 ECE
bucket empty for every model. Reported ECE values (0.06–0.18) are
weighted MAEs over three populated buckets (0.3 / 0.5 / 0.6) rather
than a full four-bucket calibration curve — they capture how well models
calibrate across the low-to-moderate confidence range only. Verbalized
extraction is also sensitive to hedging language: models with less
hedging produce fewer high-confidence signals (Gemini, for instance,
defaults 119 of 246 base responses to "unstated" and tends toward
moderate-bucket placement when it does hedge). Multi-Answer Confidence
(2026) names the consistency-based proxy as the upgrade path; we run a
stratified version under Phase 1C (top-failure tasks only) and disclose
the random-sample re-run as a separate caveat (e). True probabilistic
calibration would require token-level logprobs over the answer span,
which is not uniformly available across the five vendor APIs we benchmark.

[Tier 1 update 2026-05-03: prior version of this disclosure stated
"Gemini specifically returned 0 verbalized confidence signals across
246 base runs and is excluded from the accuracy-calibration correlation
block." That claim was an artifact of the runner schema gap + stale
recompute path documented in `audit/gemini_forensic_2026-05-03.md`, not
a property of Gemini's responses. Post-fix coverage: Gemini has 127/246
extractable signals and accuracy_calibration_correlation r = 0.337,
in-band with the other four models (0.31–0.43).]

[Phase 1.8 update 2026-05-04: post-v1-deprecation truly-base scope
yields 74 of 171 unstated for Gemini (was 119 of 246 under
pre-deprecation contaminated scope). Gemini extractable signals
recompute to 97/171; accuracy_calibration_correlation r = 0.3876,
in-band with the cohort (0.36–0.42). Tier 1 numbers above (119/246,
127/246, r=0.337, cohort 0.31–0.43) stand as historical reference;
the Phase 1.8 numbers are canonical.]

### c) Robustness ranking — top-2 not statistically separable

Post-Phase-1.8, ChatGPT (Δ=+0.0003, CI [−0.013, +0.014]) and Mistral
(Δ=+0.0013, CI [−0.012, +0.014]) hold the top two robustness slots
and are noise-equivalent: both CIs cross zero, the pair is
not_separable per bootstrap. Gemini (Δ=+0.013) is also CI-crosses-zero
and not separable from ChatGPT or Mistral. Only Claude (Δ=+0.030) and
DeepSeek (Δ=+0.039) clearly separate from zero. We report the point
estimates for completeness but caution that any "model X is more
robust than model Y" claim within the noise-equivalent top-3 band is
unsupported at this sample size. Cite Hochlehnert et al. (2025,
Statistical Fragility): single-question swaps shift Pass@1 ≥ 3 pp.

### d) Single-judge caveat on the keyword-judge disagreement headline

Keyword-judge disagreement is computed on 750 of 855 truly-base runs.
The 105 excluded runs come from 21 distinct task_ids × 5 models
(CONCEPTUAL / MINIMAX / BAYES_RISK families plus the MARKOV_04 outlier),
all sharing empty `required_assumption_checks`. The same eligibility
filter applies to perturbations (2,100 of 2,365 eligible), yielding
2,850 / 3,220 combined eligibility (88.5%). Tasks that do not require
assumption articulation cannot be compared across the two scoring
methods. The combined headline (20.74% disagreement on
assumption_compliance, 591 / 2,850 runs) rests on a single external
judge model — Llama 3.3 70B Instruct via Together AI. We verified
cross-provider agreement (Groq vs Together) and ran strictness
spot-checks on borderline cases, but true cross-judge validation
against an independent family (e.g., GPT-4-class or Claude Opus as
judge) is paper-scope future work. Cite Yamauchi et al. (2025) and
Feuer et al. (2025) "Judgment Becomes Noise": single-judge benchmarks
introduce systematic noise. The headline number should be read as
evidence that keyword rubrics and a strong LLM judge disagree
substantially, not as a calibrated estimate of "true"
assumption-compliance error.

### e) Stratified self-consistency caveat (RQ5) — RESOLVED via Phase 1C

The original B3 self-consistency analysis used 30 stratified-hard tasks and
found ECE values in the 0.33–0.64 range. Phase 1C expanded coverage to all
161 numeric-target tasks. Result: ECE values are HIGHER under full coverage
(0.62–0.73 range, all 5 models). The stratified B3 was understating
overconfidence, not overstating it. The full-coverage finding is the
canonical RQ5 result; B3 stratified data is preserved in
`llm-stats-vault/90-archive/phase_1c_superseded/`.

### f) CONCEPTUAL task exclusion from self-consistency (RQ5)

Self-consistency calibration is computed on 161 of 171 tasks (the
numeric-target subset). The 10 CONCEPTUAL tasks (CONCEPTUAL_01–10) ask the
model to explain or justify rather than compute — they have no numerical
answer against which to measure 3-rerun agreement. This is a methodological
property of consistency-based confidence extraction, not a project shortcut.
Token-level logprobs (Multi-Answer Confidence 2026) would be required to
extend calibration analysis to free-form explanatory tasks.

### g) Length-correlation in RQ scoring (gemini verification)

Gemini's `reasoning_quality` lead under literature-derived NMACR weighting
(R=25%) is supported by 5/5 substantive hand-spot-checks and a uniformly
distributed advantage across 34/38 task types. However, the rubric design
rewards step-by-step derivation, which correlates with response length:
gemini averages 2.4× the cohort response length. Pooled length–RQ
correlation is r=0.184 (weak); within-gemini length–RQ correlation is
r=0.012 (effectively zero), indicating length does not drive gemini's own
variance. Length-controlled per-task analysis and multi-judge ensemble are
deferred to future work.

[Tier 1 update 2026-05-03: this disclosure was authored against pre-fix
coverage. Post-fix Gemini accuracy under literature-weighted NMACR is
0.7326 [0.7117, 0.7532] (was 0.7763); the lead over Claude (#2 0.6945
[0.6722, 0.7169]) narrows to 3.8pp but remains separable. Length-vs-RQ
correlations themselves were not recomputed since Tier 1 fixes did not
touch raw_response text.]

[Phase 1.8 update 2026-05-04: post-v1-deprecation (truly-base scope),
Gemini accuracy is 0.7314 [0.7060, 0.7565] and Claude is 0.6976 [0.6694,
0.7249]. The lead narrows to 3.4pp and Gemini–Claude is now
not_separable per bootstrap (CIs overlap); Gemini still separates
from ChatGPT, DeepSeek, and Mistral. Length-vs-RQ correlations not
recomputed; deprecation removed contaminating rows but did not modify
raw_response text.]
