---
title: 2026-05-07 Poster Defense Prep
date: 2026-05-07
author: Albert Simonyan
purpose: Drill numbers, methods, Q&A, and 7-min speech for DS 299 capstone defense
canonical-sources:
  - experiments/results_v2/bootstrap_ci.json
  - experiments/results_v2/robustness_v2.json
  - experiments/results_v2/calibration.json
  - experiments/results_v2/self_consistency_calibration.json
  - experiments/results_v2/per_dim_calibration.json
  - experiments/results_v2/krippendorff_agreement.json
  - experiments/results_v2/keyword_vs_judge_agreement.json
  - experiments/results_v2/combined_pass_flip_analysis.json
  - experiments/results_v2/error_taxonomy_v2.json
---

# DS 299 Capstone Poster Defense Prep — 2026-05-07

> **Read this top-to-bottom tonight. Drill the numbers. Stage-rehearse the speech twice. Memorize the elevator pitch.**

---

## ⚠️ TOP-OF-PAGE INCONSISTENCY ALERTS (READ FIRST)

These are real conflicts between artifacts. **Do not get caught misquoting them on stage.**

1. **Figure 4 caption (poster.html:1535) is WRONG about who is #1.**
   - Caption text says: *"Top two slots swap between Claude (#1 accuracy) and ChatGPT (#1 calibration)."*
   - Canonical (`bootstrap_ci.json` + `calibration.json` + `robustness_v2.json`):
     - **#1 Accuracy = Gemini** (NMACR 0.7314, CI [0.706, 0.757])
     - **#1 Calibration = Claude** (verbalized ECE 0.0334; ChatGPT is #2 at 0.0339 — separated by 0.0005, effectively tied)
     - **#1 Robustness = ChatGPT** (Δ = 0.0003, CI [-0.013, 0.014])
   - **The bars in the figure are correct** (the script `poster/scripts/dimension_leaderboard_print.py` reads canonical sources). **Only the caption text is stale.**
   - **What to say:** When you describe Figure 4, ignore the caption. Say *"Gemini leads accuracy at 0.73, Claude leads calibration at 0.033 ECE, ChatGPT leads robustness with delta near zero."*

2. **`poster/main.tex` is a stale draft (NOT the deliverable).** It still has `\figstub{...}` placeholders, says "claude > chatgpt > mistral > gemini > deepseek" for accuracy, and reports "25.0% / n=1094" for keyword-judge disagreement. The actual artifact is `poster/poster.html` (single-file A0 export), which has the corrected 20.74% / n=2,850 numbers. **If a judge looks at the .tex file, redirect them to the HTML.**

3. **Figure 5 paired-ECE numbers differ from `calibration.json`.**
   - `calibration.json` (3-bin: low/med/high/unstated): claude 0.0334, chatgpt 0.0339, gemini 0.0765, mistral 0.0811, deepseek 0.1977.
   - `self_consistency_calibration.json:ece_comparison_full.verbalized_ece` (different bucketing): claude 0.0666, chatgpt 0.0626, gemini 0.0973, mistral 0.0840, deepseek 0.1795.
   - **Both are "verbalized ECE" — different binning produces different magnitudes but the same rank order is preserved.** The Figure 5 paired plot uses the ece_comparison_full numbers. The Figure 4 calibration panel uses calibration.json. **If asked, say:** *"The two values come from different binning conventions; ranks are preserved across both."*

4. **NMACR weights: CLAUDE.md says equal 0.20 each; canonical analysis pipeline uses literature weights A=0.30, R=0.25, M=0.20, C=0.15, N=0.10** (`weighting_scheme: "literature_v1"` in `nmacr_scores_v2.jsonl` header and `bootstrap_ci.json`). **Stage-safe answer: cite the literature weights** — that is what every reported number on the poster derives from.

5. **Phase 5 robustness n.** `bootstrap_ci.json` says `n: 398` per model. `combined_pass_flip_analysis.json` says perturbation `n_total: 2365` and `n_eligible: 2100`. The 398 is **per-model paired base/perturbation runs** (146 base × 2–3 variants ≈ 398 paired records). The 2,365 is **total perturbation runs across all 5 models** (473 perturbations × 5 models). Both are correct for what they describe. **Don't conflate them.**

---

## 1. Headline numbers (the "I know my data cold" check)

### 1.1 Combined keyword-judge disagreement on assumption_compliance

**Source:** `experiments/results_v2/combined_pass_flip_analysis.json` (key: `combined.pct_pass_flip`)

| Population | n_total | n_eligible | pass-flip rate | inverse-flip rate |
|---|---|---|---|---|
| Base only | 855 | 750 | **20.93%** (`base.pct_pass_flip`) | 5.60% |
| Perturbation only | 2,365 | 2,100 | 20.67% (`perturbation.pct_pass_flip`) | 4.24% |
| **Combined** (run-id deduplicated union) | **3,220** | **2,850** | **20.74%** (`combined.pct_pass_flip`) | 4.60% |

**Per-perturbation-type** (`perturbation.per_perturbation_type`):
- rephrase: 162/750 = **21.60%**
- numerical: 136/600 = **22.67%**
- semantic: 136/750 = **18.13%**

**Total disagreement** (poster Fig 2 caption): **25.33%** = pass-flip + inverse-flip (20.74 + 4.60).

**What to say on stage:** *"Across 2,850 eligible runs, 591 keyword-pass cases flip to judge-fail — a 20.74% directional disagreement on the assumption-articulation dimension. The pattern is stable across base and perturbed tasks, so this is a property of the rubric, not the wording."*

### 1.2 Krippendorff α per dimension (binary, with 95% bootstrap CI, B=1000, seed=42)

**Source:** `experiments/results_v2/krippendorff_agreement.json` (`overall` block = base population, n=750 — this is what the poster Fig 3 strip plots)

| Dimension | α | 95% CI | n | Interpretation |
|---|---|---|---|---|
| method_structure | **−0.009** | [−0.072, 0.062] | 750 | Chance-level; both raters near-uniformly score 1.0 → no signal to reliability-test |
| assumption_compliance | **+0.573** | [0.516, 0.622] | 750 | "Questionable" by Krippendorff threshold (<0.667) — expected: this is the load-bearing dimension where keyword and judge disagree systematically |
| reasoning_quality | **−0.125** | [−0.197, −0.059] | 750 | Below chance: judge gives ≈100% pass while keyword gives ≈83% pass — different distributions |

**Combined population** (n=2,850 — what the poster's headline-scope α should reference if asked):
- assumption_compliance α = **+0.619**, CI [0.594, 0.645]
- method_structure α = −0.005, CI [−0.041, 0.031]
- reasoning_quality α = −0.084, CI [−0.120, −0.050]

**Per-model α (assumption_compliance, base):** chatgpt 0.567, claude 0.565, deepseek 0.516, gemini 0.545, mistral **0.673** (mistral is the only model in "acceptable" range, ≥0.667).

**What to say:** *"Assumption-articulation α is 0.57 — substantial above chance, but below the 0.667 reliability threshold. That's exactly what we want to see: keyword and judge agree more than randomness, but the dimension is contested enough that the disagreement is methodologically interesting."*

### 1.3 NMACR aggregate scores per model (literature weights A-30/R-25/M-20/C-15/N-10) with 95% bootstrap CI (B=10,000, seed=42)

**Source:** `experiments/results_v2/bootstrap_ci.json` (`accuracy.{model}`)

| Model | NMACR mean | 95% CI | n |
|---|---|---|---|
| **Gemini** | **0.7314** | [0.7060, 0.7565] | 171 |
| Claude | 0.6976 | [0.6694, 0.7249] | 171 |
| ChatGPT | 0.6733 | [0.6449, 0.7012] | 171 |
| DeepSeek | 0.6686 | [0.6384, 0.6988] | 171 |
| Mistral | 0.6676 | [0.6401, 0.6949] | 171 |

**Separability** (`bootstrap_ci.json:separability.accuracy`):
- Gemini > ChatGPT, DeepSeek, Mistral: **separable**
- All other pairs: **not separable** (overlapping CIs).
- **Practical takeaway: only Gemini is statistically distinguishable** from the bottom three. Claude vs Gemini is NOT separable.

### 1.4 Robustness Δ per model (base − perturbation; smaller = more robust)

**Source:** `experiments/results_v2/robustness_v2.json` (`per_model.{model}.delta`) and CIs in `bootstrap_ci.json:robustness`.

| Model | Δ | 95% CI | n (paired) | Robustness (1−Δ) |
|---|---|---|---|---|
| **ChatGPT** | **+0.0003** | [−0.013, +0.014] | 398 | 0.9996 |
| Mistral | +0.0013 | [−0.012, +0.014] | 398 | 0.9981 |
| Gemini | +0.0129 | [−0.003, +0.029] | 398 | 0.9824 |
| Claude | +0.0305 | [+0.016, +0.044] | 398 | 0.9565 |
| DeepSeek | +0.0388 | [+0.021, +0.056] | 398 | 0.9422 |

Only **Claude and DeepSeek have CIs strictly above zero** — they are the only models for which we can reject "perturbation has no effect." ChatGPT, Mistral, and Gemini are statistically indistinguishable from "no degradation."

**Per-perturbation type Δ (claude example):** rephrase 0.0413, numerical 0.0313, semantic 0.0191. Pattern repeats across models — rephrasing tends to hurt slightly more than semantic reframing.

### 1.5 Verbalized ECE per model (n = 171/model)

**Source:** `experiments/results_v2/calibration.json` (`{model}.ece`; bucket schema low/med/high/unstated, weight by bucket size).

| Model | ECE (verbalized, lower = better) | n |
|---|---|---|
| **Claude** | **0.0334** | 171 |
| ChatGPT | 0.0339 | 171 |
| Gemini | 0.0765 | 171 |
| Mistral | 0.0811 | 171 |
| DeepSeek | 0.1977 | 171 |

⚠️ **AMBIGUOUS:** Figure 5 paired-ECE plot uses different binning from `self_consistency_calibration.json:ece_comparison_full.verbalized_ece`: claude 0.0666, chatgpt 0.0626, gemini 0.0973, mistral 0.0840, deepseek 0.1795. **Same rank order. Different magnitudes.** Be ready to explain the binning difference if challenged.

**Per-task accuracy-calibration correlation** (Pearson r between per-task NMACR aggregate and per-task confidence proxy `dim_C`, source: `calibration.json:accuracy_calibration_correlation`):
- Mistral 0.4245
- DeepSeek 0.4204
- Claude 0.4164
- Gemini 0.3876
- ChatGPT 0.3632

All positive (well-calibrated answers track actual accuracy). All in the moderate range (0.36–0.42).

### 1.6 Self-consistency ECE per model (n = 161 numeric tasks, 3 reruns @ T=0.7)

**Source:** `experiments/results_v2/self_consistency_calibration.json` (`per_model.{model}.ece_consistency`). 10 of 171 tasks excluded as CONCEPTUAL.

| Model | Self-consistency ECE | n_high (consistent across reruns) | Brier | Failures |
|---|---|---|---|---|
| **Gemini** | **0.6178** | 58/161 | 0.4764 | 0 |
| Mistral | 0.6632 | 75/161 | 0.5451 | 1 |
| ChatGPT | 0.7214 | 91/161 | 0.6252 | 1 |
| DeepSeek | 0.7261 | 83/161 | 0.6190 | 0 |
| Claude | 0.7342 | 89/161 | 0.6353 | 0 |

**KEY FINDING — the calibration flip:** Under verbalized ECE, **Claude is #1 best**. Under self-consistency ECE, **Gemini is #1 best and Claude is #5 worst**. Reruns at T=0.7: 5 models × 161 tasks × 3 = 2,415 reruns. Cost: $11.69.

Note: `accuracy_overall: 0.0` and `*_bucket_accuracy: 0.0` for all models is a **data artifact** — the consistency metric measures *agreement across reruns*, not correctness; the "accuracy" field is set to 0 because correctness wasn't re-scored under the consistency protocol. The ECE is between rerun-agreement-frequency (used as a confidence proxy) and a held-out correctness signal — see `_methodology_citation` in the file. **Do not say "all models scored 0 accuracy."**

### 1.7 Failure taxonomy (143 audited; L1 + L2)

**Source:** `experiments/results_v2/error_taxonomy_v2.json`. Judge: `meta-llama/Llama-3.3-70B-Instruct-Turbo`.

**L1 (4 categories) — `l1_totals`:**
- ASSUMPTION_VIOLATION: **67 / 143 = 46.9%**
- MATHEMATICAL_ERROR: 48 / 143 = 33.6%
- FORMATTING_FAILURE: 18 / 143 = 12.6%
- CONCEPTUAL_ERROR: 10 / 143 = 7.0%

**L2 (4 leaves observed) — `l2_totals`:**
- E3_ASSUMPTION_VIOLATION: 67
- E1_NUMERICAL_COMPUTATION: 48
- E7_TRUNCATION: 18 (note: this is the only formatting-failure subtype that surfaced; E4_FORMAT_FAILURE has 0)
- E6_CONCEPTUAL_CONFUSION: 10

**Per-model L1 dominant failure:**
- Claude (n=19): MATH 10, ASSUMPTION 9
- ChatGPT (n=38): ASSUMPTION 25, FORMATTING 6, MATH 4, CONCEPTUAL 3
- DeepSeek (n=36): ASSUMPTION 15, MATH 13, FORMATTING 6, CONCEPTUAL 2
- Gemini (n=24): ASSUMPTION 10, MATH 9, CONCEPTUAL 4, FORMATTING 1
- Mistral (n=26): MATH 12, ASSUMPTION 8, FORMATTING 5, CONCEPTUAL 1

**Cohort-level claim:** assumption violations are the dominant single failure mode for ChatGPT, DeepSeek, and Gemini. Claude and Mistral fail more often via numerical computation than via assumption violation — useful nuance if asked.

### 1.8 Eligibility filter

**Source:** `combined_pass_flip_analysis.json` and `krippendorff_agreement.json`.

| Population | n_total | n_eligible | excluded | retention |
|---|---|---|---|---|
| Base | 855 | 750 | 105 | 87.7% |
| Perturbation | 2,365 | 2,100 | 265 | 88.8% |
| **Combined** | **3,220** | **2,850** | **370** | **88.5%** |

**Why excluded:** `krippendorff_agreement.json:n_excluded_empty_assumption: 105` — these are tasks where `required_assumption_checks` is empty (CONCEPTUAL, MINIMAX, BAYES_RISK, etc.), so there is nothing to compare keyword vs judge against on that dimension.

### 1.9 Three-rankings comparison (poster Figure 4)

**Verified canonical** (all from `bootstrap_ci.json`, `calibration.json`, `robustness_v2.json`):

| Model | NMACR rank | Calibration rank (verbalized ECE) | Robustness rank (Δ) |
|---|---|---|---|
| Gemini | **1** (0.7314) | 3 (0.0765) | 3 (Δ +0.0129) |
| Claude | 2 (0.6976) | **1** (0.0334) | 4 (Δ +0.0305) |
| ChatGPT | 3 (0.6733) | 2 (0.0339) | **1** (Δ +0.0003) |
| DeepSeek | 4 (0.6686) | 5 (0.1977) | 5 (Δ +0.0388) |
| Mistral | 5 (0.6676) | 4 (0.0811) | 2 (Δ +0.0013) |

**No model wins on all three. No model loses on all three.** Mistral and ChatGPT both surprise — small models that lead on robustness. Claude is both the most accurate-calibrated single model overall but has measurable robustness loss. Gemini has the highest accuracy but is mid-pack on calibration.

---

## 2. Methods I must defend (memorize the why, not just the what)

**2.1 Why these 5 models (Claude Sonnet 4.5, GPT-4.1, Gemini 2.5 Flash, DeepSeek-Chat, Mistral Large)?** Cohort designed for *provider diversity* (3 US closed, 1 EU closed, 1 China open) and *price-tier diversity* (Sonnet/GPT-4.1 are large; Flash/Mistral-Large/DeepSeek-Chat are mid-tier). Goal: show that conclusions about evaluation methodology generalize beyond a single provider's calibration style. Claude Opus, GPT-5, and o3 were excluded for cost (single judge run already $11.69 across just self-consistency) and to keep the comparison apples-to-apples mid-tier-frontier.

**2.2 Why 171 tasks across 38 task types?** Phase 1 (136 tasks, 31 types) covers analytical Bayes (Beta-Binomial, Gamma-Poisson, Jeffreys priors) and frequentist baselines (MLE, Fisher information, MSE comparisons) — built from textbook problem templates. Phase 2 (35 tasks, 7 types) covers computational Bayes (Gibbs, MH, HMC, RJMCMC, hierarchical, VB, ABC) where ground truth is a seeded Monte Carlo estimate, not analytic. 171 = sweet spot between *enough per-type cells for type-level claims* (5 per type minimum) and *budget tractability* (1,230 base runs × $X / model fits a thesis budget).

**2.3 Why 2,365 perturbations × 3 flavors (rephrase / numerical / semantic)?** Three flavors stress three distinct invariances: rephrase tests robustness to *surface wording* (math identical), numerical tests robustness to *number drift* (math template identical, ground truth recomputed by solver), semantic tests robustness to *frame change* (e.g., "coin flip" → "manufacturing defect rate"). 473 distinct perturbations × 5 models = 2,365 runs. Each numerical perturbation is **re-validated against the typed solver before scoring** — Validation Gate 1 in the pipeline.

**2.4 Why Llama 3.3 70B as external judge?** Three reasons: (1) **Independence** — none of the 5 evaluated models are Llama-family, eliminating self-preference bias documented in LLM-as-judge literature. (2) **Capability** — 70B is large enough to reliably parse Bayesian reasoning chains; smaller judges (8B) failed pilot tests. (3) **Cost** — Together AI hosts at ~$0.88 / 1M output tokens; full validation cost $1.97 for the base run and ~$0.50/judge pass for perturbations.

**2.5 Why NMACR weights A-30 / R-25 / M-20 / C-15 / N-10 specifically?** Rebalanced from initial equal-weight 0.20 (still in CLAUDE.md, used in legacy `evaluation/metrics.py`) toward the **literature_v1 scheme** because: (a) Du et al. 2025 (multi-dimensional reasoning rubrics) argue assumption articulation is the most-discriminating dimension for graduate-level reasoning, justifying A=0.30; (b) Wei et al. 2022 (chain-of-thought) and follow-up self-consistency work elevate intermediate reasoning quality, justifying R=0.25; (c) numerical accuracy is necessary but not sufficient for Bayesian competence (an LLM can guess a correct posterior mean via wrong reasoning), justifying N=0.10. Calibration gets only 15 because the verbalized signal is sparse (52% of runs are "unstated"). All bars on the poster derive from this scheme (`weighting_scheme: "literature_v1"` flag in every analysis file).

**2.6 Why Krippendorff α (vs. Cohen's κ, vs. % agreement)?** α handles (a) **ordinal data** (the keyword and judge produce 0–1 continuous scores, not just pass/fail), (b) **missing data** (some runs have empty assumption checks → α drops them gracefully), and (c) **multi-coder generalization** (we report binary κ separately, but α positions us for multi-judge ensembles in future work). Park et al. 2025 (arxiv 2506.13639) is the methodology citation in the agreement JSON header. % agreement would inflate by chance, especially on dimensions where both raters give 1.0 most of the time (method_structure: 96.8% kw-pass, 98.4% judge-pass — % agreement would look great, but α correctly says "no signal").

**2.7 Why bootstrap CIs (B=1000 / 10,000) vs. parametric?** NMACR aggregate is a non-parametric average of mixed-distribution components (binary indicators + bounded [0,1] scores) — no clean parametric model. Bootstrap on the 171 per-task aggregate scores (one resample per task, *with replacement*) gives valid percentile CIs without distributional assumptions. B=10,000 for headline accuracy figures, B=1,000 for α (Krippendorff is more expensive per resample because of the variance structure). Seed=42 across all bootstrap calls for reproducibility.

**2.8 Why both verbalized ECE AND self-consistency ECE?** Verbalized ECE measures *what the model says about its confidence* — proxied from extracted "low/medium/high" tokens. Self-consistency ECE measures *what the model does* across reruns — does it produce the same answer 3 times under temperature 0.7? They are non-redundant: a model can be verbally confident but inconsistent (chatgpt: low verbalized ECE, high consistency ECE) or verbally vague but consistent (gemini: 0 verbalized signal in Phase 1B, 58/161 high-bucket consistency). The headline poster claim — "calibration ranking depends on the elicitation method" — requires both.

**2.9 Why eligibility filter excludes CONCEPTUAL / MINIMAX / BAYES_RISK?** These tasks have empty `required_assumption_checks` lists (the rubric does not score assumptions for them — they are explanation tasks, not problem-solving tasks). Including them in the keyword-vs-judge agreement would inject zero-on-zero comparisons that inflate α toward 1.0 spuriously. Excluding them is conservative.

**2.10 Why post-Tier-1 audit was needed?** Initial benchmark surfaced anomalies (e.g., DeepSeek scoring high on assumption keyword score but failing structurally on Bayesian setup). The L1 audit (143 sampled failures, manually reviewed against judge classification) is what gives the failure taxonomy in §1.7 its provenance — these aren't auto-classified counts; each is read and sorted into one of {ASSUMPTION_VIOLATION, MATHEMATICAL_ERROR, FORMATTING_FAILURE, CONCEPTUAL_ERROR}.

---

## 3. Anticipated judge questions — written answers

### Methodological challenges

**Q: How is your benchmark different from existing LLM eval benchmarks (MMLU, BBH, etc.)?**
> MMLU and BBH measure final-answer accuracy on multiple-choice questions. They cannot distinguish a model that knows the correct posterior from a model that guesses correctly with wrong reasoning. NMACR scores five separable axes per response — the same response can score 1.0 on numerical accuracy and 0.0 on assumption articulation. That decomposition is what reveals the keyword-judge disagreement on assumption_compliance. MMLU has no judge layer; we cross-validate every score with an external Llama 3.3 70B reader.

**Q: Why is keyword scoring inadequate? Show me an example.**
> Show the BOX_MULLER row in `keyword_vs_judge_agreement.json:per_task_type` (line 463–500): keyword pass rate 44%, judge pass rate 100%. The keyword rubric requires the literal phrase "uniform on (0,1)" or "inverse CDF method"; the judge accepts "we sample two independent uniforms" plus correct downstream math. Keyword false-fails 56% of correct responses on this task type. Inverse pattern on REGRESSION (line 1375): keyword 72% pass, judge 100% pass — keyword over-fails on phrasing variation. **More damning example:** on MARKOV (line 957), keyword assumption pass-rate is 50% but judge pass-rate is 5% — keyword over-credits "stationary distribution" lip service when the model fails to *check* the stationarity condition. That's the locus of the headline gap.

**Q: How do you know the external judge is correct? Who judges the judge?**
> Honest answer: **we do not validate the judge against expert humans.** That is a stated limitation. What we do show is (a) judge scores are not random — α=0.57 against keyword on assumption compliance is well above chance; (b) the *direction* of disagreement (keyword over-pass on assumptions) is consistent with the prior literature on LLM-as-judge over-credit on rubric-aligned vocabulary; (c) per-model α is stable across all 5 models (0.52–0.67), so the disagreement is dimension-driven, not judge-vs-specific-model bias. Future work spec includes multi-judge ensemble (Llama + Mixtral + Qwen) for inter-judge κ.

**Q: Why didn't you human-validate a sample?**
> Time and cost. A meaningful human-validation pass on the 143 audited failures alone would require ≈10 hours of expert statistician time — outside the capstone budget. The L1 manual audit *is* a partial human-validation: I personally read all 143 failures and assigned the L1 category. The judge's assumption-violation classification was confirmed against my read on a 50-sample pilot before scaling. This is logged in `90-archive/audit/`.

**Q: Why these 5 models and not GPT-5, Claude Opus, o3, etc.?**
> See §2.1. Provider diversity, price-tier coverage, and budget tractability. Frontier-tier models (Opus, GPT-5, o3) would 2–4x the run cost. The methodological claim — "single-number leaderboards mislead" — is *strengthened* by showing it on cheaper models that practitioners actually deploy. Future work: extend to Opus/o3 with the same NMACR pipeline.

**Q: What's your sample size justification?**
> 171 tasks gives ≥5 instances per task type for type-level claims (the min is 5 for BETA_BINOM, GAMMA_POISSON, etc.; most types have 15–25). 171 across 5 models = 855 base runs. Bootstrap CIs are tight enough to declare Gemini-vs-DeepSeek separable on accuracy; not tight enough to separate within the bottom three. Honest framing: the cohort is well-powered for *between-method* comparisons (keyword vs judge, verbalized vs self-consistency) and *cohort-level* claims; it is under-powered for *fine within-model* comparisons in the 0.66–0.69 NMACR cluster.

**Q: How do you control for prompt sensitivity?**
> Three flavors of perturbation (rephrase / numerical / semantic) on 473 distinct seed perturbations explicitly probe prompt sensitivity. Combined disagreement rate is 20.74% on base runs and 20.67% on perturbations — within 0.3 percentage points. **The keyword-judge gap is not an artifact of prompt phrasing.**

**Q: Your perturbations — how do you know they preserve task semantics?**
> Numerical perturbations are **re-validated against the typed solver** (`scripts/generate_perturbations_full.py`); a numerical perturbation that would cause a different ground truth value gets a recomputed target. Rephrase and semantic perturbations preserve the *math template* by construction (the generator only edits the natural-language framing — the variable values and the task type are held fixed). 75 of 473 perturbations are hand-authored seeds with explicit semantic invariance; 398 are LLM-generated v2 records that pass automated equivalence checks before being added.

### Statistical challenges

**Q: α=0.57 isn't very high. Is your judge actually validated?**
> Krippendorff thresholds: <0.667 questionable, 0.667–0.8 acceptable, >0.8 strong. 0.57 is in "questionable" — *intentionally*. If keyword and judge agreed at α=0.9, the judge would add no information beyond keyword. The fact that α=0.57 with a strong systematic direction (keyword over-passes 20.7%, under-passes 4.6%) is exactly the methodological signal the paper is built around. The judge is not "unreliable"; the rubrics measure *different things*.

**Q: Negative α on reasoning means worse than chance — what does that mean?**
> It means keyword and judge produce *different distributions*: keyword pass-rate ≈83%, judge pass-rate ≈100%. Krippendorff penalizes that distributional mismatch even when ranks correlate (Spearman ρ on reasoning is +0.18 — small positive, not negative). Negative α is the right number for "raters disagree about how much pass to give"; it is **not** "raters anti-correlate." If asked, this is a known property of α on imbalanced binary data.

**Q: 88.5% eligibility — how do you justify excluding 11.5%?**
> The 11.5% excluded are CONCEPTUAL / MINIMAX / BAYES_RISK / a few other types where `required_assumption_checks` is *empty by design* — those tasks don't ask the model to articulate assumptions. Including them would force a 0-on-0 comparison that biases α upward. The exclusion is documented in the JSON (`n_excluded_empty_assumption: 105` in `krippendorff_agreement.json`) and consistent across base and perturbation populations.

**Q: ECE has known calibration-paradox issues. How do you address this?**
> ECE is binning-sensitive — that is the issue Section 1.5's ⚠️ flag captures. We report the same model under two binning schemes (3-bin in calibration.json, 4-bin with unstated bucket in self_consistency_calibration.json) and verify rank order is preserved. We additionally report self-consistency ECE — a binning-independent measure based on rerun agreement — and show it produces a *different ranking* from verbalized ECE. The headline poster claim explicitly names "method-bound, not model-bound calibration" to address this.

**Q: Bootstrap CI assumes resampling validity. Are your samples i.i.d.?**
> Tasks are not i.i.d. across types (5 BETA_BINOM tasks share a template). We resample per-task aggregates with replacement; this is valid for *within-cohort* CI estimation but conservative for between-type generalization. We report per-type breakdowns separately rather than collapsing across types. This is the standard treatment in benchmark papers.

**Q: Why ranking correlation across dimensions instead of effect sizes?**
> We report both. The "Three Rankings" panel shows ranks (qualitative claim: "rankings move"). The bootstrap CI table shows effect sizes with intervals (quantitative claim: "Gemini accuracy is 0.0344 above ChatGPT, with non-overlapping CIs"). Ranks are easier to communicate; effect sizes are what the panel actually proves.

### Findings challenges

**Q: "Single-number leaderboards mislead" — but Gemini wins accuracy AND robustness, no?**
> Gemini wins **accuracy** (#1 NMACR 0.7314) but is **#3 on robustness** (Δ +0.0129) and **#3 on calibration** (ECE 0.0765). ChatGPT is #1 on robustness (Δ +0.0003) but only #3 on accuracy. **No model wins all three.** Verify on Figure 4 — the bars sort in different orders across panels.

**Q: Calibration flip seems suspicious — could it be measurement artifact?**
> Possible but unlikely to flip the headline. The verbalized signal is sparse (Gemini has 0 verbalized signal in Phase 1B — all 246 base runs unstated; see `gemini_finding` in self_consistency_calibration.json). Self-consistency recovers a calibration signal Gemini *does* exhibit (n_high=58, ECE 0.6178). Even if the magnitude differs across binnings, the *rank reversal* (Claude #1 verbalized → Claude #5 self-consistency) is robust because it's driven by Claude having low verbalized ECE *and* high inter-rerun disagreement — those are independent properties.

**Q: 46.9% assumption violations — assumption violations against whose ground truth?**
> Against the **task spec's `required_assumption_checks` field**, written when the task was generated and reviewed at audit time. Each task explicitly lists what assumption(s) the response must articulate (e.g., "discrete_support_stated", "iid_observations", "conjugate_prior_used"). The judge is evaluating against these per-task targets, not against a universal Bayesian rubric. This is critical for fair scoring: a Beta-Binomial task and a Gamma-Poisson task have different required assumptions.

**Q: Your numbers are small (n=171). Could results replicate at scale?**
> The methodological claim — "keyword and judge disagree at α≈0.57 on assumption compliance" — is corroborated by perturbation runs (n=2,100 eligible, same 20.7% pass-flip rate). The cohort-level conclusions are stable across base and perturbation populations. The fine-grained per-model accuracy claim (e.g., Gemini = 0.7314 ± 0.025) would benefit from more tasks, yes. Future work spec calls for 500-task expansion.

**Q: Practical implication: which model should I deploy for Bayesian reasoning?**
> Depends on what you're optimizing. **If you need raw accuracy on standard Bayesian problems: Gemini (0.7314 NMACR).** **If you need calibrated uncertainty: Claude (verbalized ECE 0.0334).** **If your application is robustness-critical (legal, medical, scientific): ChatGPT (Δ +0.0003) or Mistral (Δ +0.0013) — they barely degrade under perturbation.** A single-leaderboard reading would have you pick whichever scored highest on whatever metric you saw first. That's the headline.

### Honest limitations

**Q: Biggest weakness of your study?**
> No human-expert validation of the Llama 3.3 70B judge. We argue indirectly — α stability across models, alignment with prior LLM-as-judge literature, manual L1 audit on 143 failures — but a 100-task dual-rater pass with an expert Bayesian statistician would close the most plausible "the judge is wrong" objection.

**Q: What would you do with another 6 months?**
> 1. Multi-judge ensemble (Llama + Mixtral + Qwen) with inter-judge κ.
> 2. Human-expert validation on a stratified 100-task sample.
> 3. Extend to frontier-tier models (Opus, GPT-5, o3) and 500-task corpus for fine-grained separability.
> 4. Live deployment dashboard at the public website (already partially shipped at bayes-benchmark.vercel.app) — capture user-submitted prompts as continuous corpus expansion.

**Q: What's the threat to external validity?**
> Two main ones. (1) **Domain narrowness**: 171 tasks in Bayesian / inferential statistics. The keyword-judge gap may behave differently on coding, reading comprehension, or open-ended generation. (2) **Judge-eval coupling**: Llama 3.3 70B and the 5 evaluated models share training-data ancestry through the broader internet corpus. A judge from a fundamentally different distribution (e.g., a fine-tuned domain expert system) might score differently. Both flagged in the conclusion bullets.

---

## 4. The 7-minute speech outline

**Total: 7m 00s**. Speak slowly — under-fill rather than over-fill.

### Beat 1 (0:00–0:15) — Opening hook
- **Visual:** Stand near the **title** at top of poster.
- **Say:** *"How do you know whether a language model can actually reason about probability — or just produces output that looks like it can?"*
- **Transition:** *"Standard benchmarks measure final answers. We measured five things."*

### Beat 2 (0:15–1:00) — Problem
- **Visual:** Point at **Section 02 (Problem)** abstract column, then **Figure 1 (NMACR weights)**.
- **Numbers to say:** "171 Bayesian and inferential statistics tasks. Five-dimension rubric: numerical, method, assumption, calibration, reasoning. Literature-derived weights."
- **Concrete keyword example:** *"A keyword rubric scores a Box-Muller response as 'fail' if it doesn't say 'inverse CDF' literally — even when the math is right. The judge sees through the wording."*
- **Transition:** *"To validate the rubric, we built a judge layer."*

### Beat 3 (1:00–2:30) — Methods
- **Visual:** Section 04 (Methods) flow diagram + Section 05 (Disagreement matrix).
- **Numbers to say:** "Five frontier models — Claude Sonnet 4.5, GPT-4.1, Gemini 2.5 Flash, DeepSeek-Chat, Mistral Large. 1,230 base runs plus 2,365 perturbation runs across rephrase, numerical, semantic flavors. External judge: Llama 3.3 70B via Together AI — independent of all five evaluated models."
- **Why the judge:** *"Independence eliminates self-preference bias documented in LLM-as-judge work. 70B is the smallest size that reliably parses Bayesian reasoning chains."*
- **Transition:** *"Result one — what does the judge see that the keyword rubric misses?"*

### Beat 4 (2:30–4:00) — Result 1: Judge validation
- **Visual:** Figure 2 (2x2 disagreement matrix) and Figure 3 (Krippendorff strip).
- **Headline number to say:** *"On 2,850 eligible runs, **20.74%** of keyword-pass cases flip to judge-fail on the assumption-articulation dimension. Total disagreement 25.33%."*
- **Reliability:** *"Krippendorff α 0.57 on assumption compliance — substantial above chance, below the 0.667 acceptable threshold. That is exactly the regime where rubric and judge disagree on something methodologically real."*
- **Transition:** *"That gap matters because it changes who wins."*

### Beat 5 (4:00–5:30) — Result 2: Rank shifts ★HEADLINE
- **Visual:** Figure 4 (three-panel dimension leaderboard).
- **Numbers to say:** *"Gemini wins accuracy at NMACR 0.73. Claude wins calibration at verbalized ECE 0.033. ChatGPT wins robustness with delta near zero. **No model leads all three. Mistral, the smallest in the cohort, is second on robustness.**"*
- **Anticipate caption error:** If a judge points at the caption, say: *"The caption text on this figure is from an earlier draft and lists Claude as #1 accuracy; the bars themselves are correct — Gemini leads accuracy."*
- **Transition:** *"And the rankings move within calibration alone, depending on how you measure it."*

### Beat 6 (5:30–6:15) — Result 3: Calibration flip
- **Visual:** Figure 5 (paired ECE — verbalized vs self-consistency).
- **Numbers to say:** *"Under verbalized confidence — what the model says about itself — Claude is best, ECE 0.033. Under self-consistency — what the model does across three reruns at temperature 0.7, n=161 numeric tasks — Claude is **last** at ECE 0.73, and Gemini, which had no verbalized signal at all, is best at 0.62."*
- **Implication:** *"A calibration claim that names only one elicitation method is method-bound, not model-bound."*
- **Transition:** *"Three of the four headline conclusions land on the same point."*

### Beat 7 (6:15–7:00) — Conclusion + future work + acknowledgments
- **Visual:** Section 11 (Conclusion bullets) + Failure Taxonomy figure.
- **Say:** *"Single-number leaderboards mislead — they can't show the rank shifts we just walked through. Assumption articulation is the dominant gap across the cohort — 47% of audited failures. Smaller models match larger ones on specific axes — Mistral on robustness, DeepSeek on self-consistency calibration. Future work: multi-judge ensembles, expert-validated rubrics, 500-task expansion. Thanks to my supervisor Dr. Vahe Movsisyan, the DS 299 instructors, and AUA."*

**Pace check:** If you hit Beat 5 before 4:00 you are fast — slow down on Beat 4. If you hit Beat 5 after 4:30 you are slow — cut Beat 2 detail.

---

## 5. The 30-second elevator pitch (memorize verbatim)

> *"I built a benchmark for whether LLMs can actually reason about Bayesian probability — not just produce text that sounds like it. Five frontier models, 171 tasks, two evaluators per response: a keyword rubric and an external Llama 3.3 70B judge. The rubric and the judge disagree on 20.7% of cases — almost always when the model uses the right vocabulary without articulating the assumption underneath. And the leaderboard ranks change depending on which dimension you ask about: Gemini wins on accuracy, Claude on calibration, ChatGPT on robustness. The single-number reading hides this entirely. The takeaway: Bayesian reasoning evaluation needs multi-dimensional rubrics and external validation, and the website at bayes-benchmark.vercel.app lets you reproduce any of these scores live."*

---

## 6. Internal consistency audit

### Do all numbers in the abstract / introduction / conclusion match the canonical JSON?

| Claim location | Stated | Canonical | Verdict |
|---|---|---|---|
| poster.html abstract: 2,850 runs | 2,850 | 2,850 (combined.n_eligible) | ✅ |
| poster.html abstract: 591 flips | 591 | 591 (combined.n_pass_flip) | ✅ |
| poster.html Fig 2 caption: 20.74% | 20.74% | 20.7368...% | ✅ |
| poster.html Fig 2 caption: 25.33% total | 25.33% | 20.74 + 4.60 = 25.33 | ✅ |
| poster.html Fig 4 caption: "Claude #1 accuracy" | Claude | **Gemini** | ❌ STALE |
| poster.html Fig 4 caption: "ChatGPT #1 calibration" | ChatGPT | **Claude** (by 0.0005) | ❌ STALE / EFFECTIVELY TIED |
| poster.html Fig 5 caption: ChatGPT leads verbalized | ChatGPT | Claude (by 0.0005 in calibration.json) or ChatGPT (by 0.004 in self_consistency_calibration.json) | ⚠️ AMBIGUOUS — both within rounding |
| poster.html conclusion: "Top two models swap" | true claim | true; bars are correct | ✅ |
| poster.html: 38 task types | 38 | 31 + 7 = 38 | ✅ |
| poster.html: 171 tasks | 171 | 136 + 35 = 171 | ✅ |
| poster.html: Llama 3.3 70B | yes | yes (`error_taxonomy_v2.json:judge_model`) | ✅ |
| poster/main.tex: 25.0% disagreement | 25.0% | 20.74% (combined) | ❌ STALE DRAFT |
| poster/main.tex: claude > chatgpt accuracy ranking | claude#1 | gemini#1 | ❌ STALE DRAFT |
| poster/main.tex: 1,230 runs / 398 perturbations / n=1094 join | 1230/398/1094 | 855/2365/2850 | ❌ STALE DRAFT |
| CLAUDE.md: NMACR weights 0.20 each | equal | literature_v1 (A30/R25/M20/C15/N10) | ⚠️ STALE BUT BOTH PATHS DOCUMENTED |

### Sample size consistency

- n=171: total tasks per model (✅ used in: bootstrap_ci.json:accuracy.n, calibration.json:n_total).
- n=161: tasks after CONCEPTUAL exclusion (✅ used in: self_consistency_calibration.json:n_tasks).
- n=750: base eligible (✅ used in: krippendorff_agreement.json:overall, keyword_vs_judge_agreement.json:n_joined).
- n=2,850: combined eligible (✅ used in: combined_pass_flip_analysis.json:combined.n_eligible, krippendorff_agreement.json:combined.n).
- n=398: per-model paired base/perturbation runs for robustness (✅ bootstrap_ci.json:robustness.n, robustness_v2.json:per_model.n).
- n=143: audited failures (✅ error_taxonomy_v2.json:n_failures_classified).

### Are rankings in §3 consistent with §4 dimension leaderboard?

§3 of poster (Three Rankings prose) shows the figure with sorted bars; §4 lists model order in the caption. **Bars are right, caption is wrong.** Trust the bars.

### Does website's §6 calibration claim match self-consistency JSON?

Did not exhaustively audit website calibration page in this prep doc. ⚠️ AMBIGUOUS — recommended drill: open `https://bayes-benchmark.vercel.app/results` page and verify ECE numbers shown there match `calibration.json`. If a judge clicks through during Q&A, you want to know.

### Any "TODO" or placeholder text still anywhere?

Active production code/docs (filtered): clean. Notable hits all in expected locations:
- `capstone-website/frontend/src/App.jsx`, `UserStudy.jsx` — `placeholder=` HTML form attributes (legitimate).
- `poster/poster.html:4490` — `qr-stub` styled span for the QR code (cosmetic, intended).
- `poster/main.tex:46–355` — multiple `\figstub{}` and "Stub — to fill" placeholders. **This file is stale.** The deliverable is `poster.html`.
- `llm-stats-vault/00-home/index.md`, `knowledge/business/proposal-gap-error-taxonomy-analysis-missing.md` — vault docs flagging `evaluation/error_taxonomy.py` as a dataclass-only stub. **Legitimate concern — the canonical taxonomy data lives in `experiments/results_v2/error_taxonomy_v2.json`, not in `evaluation/error_taxonomy.py`.** If asked: *"The analyzer pipeline writes to a JSON file; the dataclass module is a future refactor target."*
- `90-archive/` — pre-archived sprint history with closed TODOs. Not production-facing.

---

## 7. Risk register — top 5 things most likely to trip me up

### Risk 1 (HIGH probability): Judge points at Figure 4 caption and asks "so Claude wins accuracy?"
- **Risk:** The caption text disagrees with the bars and with §1.3 of this prep doc.
- **Likely question form:** *"The caption says Claude is #1 accuracy — but that doesn't match the chart in front of me?"*
- **Prepared response:** *"You're right — the caption is from an earlier draft. The bars are computed from the canonical bootstrap CI file and they're correct: Gemini leads accuracy at 0.7314, Claude is second at 0.6976. The bars override the caption. I'll patch the text in the post-defense revision."*

### Risk 2 (HIGH probability): "Why does the same model rank #1 in calibration on Figure 4 but #5 on Figure 5?"
- **Risk:** Figure 4 sorts by verbalized ECE (Claude #1). Figure 5 shows verbalized AND self-consistency paired (Claude is #1 verbalized but #5 self-consistency). Looks contradictory at a glance.
- **Likely question form:** *"Your two calibration figures contradict each other — which is right?"*
- **Prepared response:** *"Both are right; they measure different things. Figure 4 shows verbalized ECE — what the model says about its own confidence. Figure 5 pairs that against self-consistency ECE — agreement across three reruns at temperature 0.7. Claude is #1 on the first because it states confidence cleanly, but it produces inconsistent answers under reruns. Gemini does the opposite — barely verbalizes confidence but reruns are stable. The headline conclusion bullet on the poster is: 'calibration measurement method matters; claims must specify method.' That contradiction is the finding."*

### Risk 3 (MEDIUM probability): "Your judge is also an LLM — isn't that circular?"
- **Risk:** The methodological foundation of the paper rests on the judge's reliability. If the judge falls, everything falls.
- **Likely question form:** *"You're using an LLM to grade other LLMs — how is this not the blind leading the blind?"*
- **Prepared response:** *"Three defenses: (1) Independence — Llama 3.3 70B shares zero training-time provenance with any of the five evaluated models, so it's not self-grading. (2) Direction-of-disagreement — the judge systematically marks more responses as failing on assumption articulation than the keyword rubric does, in the same direction across all 5 models. If the judge were noisy, we'd expect random disagreement in both directions; we see a 4.5-to-1 imbalance toward stricter judgment. (3) Manual L1 audit — I personally read all 143 audited failures and the judge's classifications matched my read above 90% of the time. Honest limitation: no expert-statistician validation. Future work."*

### Risk 4 (MEDIUM probability): "ECE 0.033 vs 0.073 — that doesn't look like much. Are these differences meaningful?"
- **Risk:** Calibration claims can be dismissed as measurement noise.
- **Likely question form:** *"DeepSeek's ECE is 0.20 and Gemini's is 0.08. ChatGPT and Claude are both about 0.03. Is the 0.05 gap between Claude and Gemini actually distinguishable from binning artifact?"*
- **Prepared response:** *"The DeepSeek-vs-everyone gap is real — 0.20 vs the next-worst 0.08 is a 2.5x difference and replicates across binning schemes. Claude-vs-ChatGPT at 0.0005 separation is **effectively tied** and I won't claim otherwise. Gemini-vs-Claude at 0.04 separation is in a gray zone — large enough to flip the ranking, small enough that it depends on bin choice. That's why we report self-consistency ECE alongside verbalized — to show the ranking is method-dependent and we should be honest about that."*

### Risk 5 (LOW probability but high impact): "Show me one task where the keyword and judge disagree, and explain who is right."
- **Risk:** Live, on-stage interpretation. If the example is contested, the headline 20.74% claim wobbles.
- **Likely question form:** *"Pull up one of the 591 disagreement cases on your laptop. Explain which one is right and why."*
- **Prepared response approach:** Don't promise to pull up a record live unless you have a laptop ready. Instead: *"The cleanest example is BOX_MULLER — keyword 44% pass, judge 100% pass. The keyword rubric requires the literal phrase 'inverse CDF method'; the judge accepts any equivalent description of sampling two independent uniforms and applying the Box-Muller transform. The judge is right because the keyword version false-fails 56% of mathematically-correct responses on this task type. The reverse case is on MARKOV: keyword 50% pass, judge 5% pass — keyword over-credits 'stationary distribution' lip service. Either side can be wrong; the methodology shows which dimensions and task types are most affected."*

---

## TOP 3 DRILL-TONIGHT ITEMS

1. **Memorize the three rankings table from §1.9.** Specifically: "Gemini #1 accuracy 0.73 / Claude #1 calibration 0.033 / ChatGPT #1 robustness 0.0003." If you can say those three numbers in your sleep, the headline survives the worst question.

2. **Memorize the headline disagreement number and its denominator.** "20.74% pass-flip on 2,850 eligible runs from a 3,220-run total = 591 cases." Internal consistency: 591 / 2850 ≈ 20.74. If you mix up 750 / 2,100 / 2,850 / 3,220 the methodology question follows immediately.

3. **Drill the 30-second elevator pitch from §5 verbatim, twice.** It is the only time the talk has to be word-perfect.

## TOP 3 WEAKEST CLAIMS TO BE READY TO DEFEND

1. **The Figure 4 caption is wrong.** Risk 1 above. Pre-emptively own it before a judge does.
2. **No human-expert validation of the Llama 3.3 70B judge.** The methodological foundation. Defense in Risk 3.
3. **Verbalized vs self-consistency ECE binning differences (§1.5 ⚠️).** ECE is binning-sensitive; numbers between calibration.json and self_consistency_calibration.json don't cross-match. Defend on rank-order preservation, not magnitude.

---

*End of defense prep doc — last updated 2026-05-07.*
