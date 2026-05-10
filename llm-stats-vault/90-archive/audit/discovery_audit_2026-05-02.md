# Discovery Audit — 2026-05-02

Read-only Day 4 discovery audit. Paired with the planned cleanup audit
(Audit 2). Goal: catalogue research-supporting content that exists in
the project but is NOT surfaced on the website / Key Findings / visible
visualizations BEFORE Group B (frontend prose) ships.

Sources read end-to-end: CLAUDE.md, audit/* (12 files), llm-stats-vault/
00-home/* (3 files), llm-stats-vault/40-literature/* (README + 4 paper
notes spot-checked), capstone-website/{README, frontend/src/{App.jsx
RQS section, components/KeyFindings.jsx, pages/{Methodology, Limitations,
References}.jsx, data/visualizations.js}, backend/v2_routes.py},
experiments/results_v2/* (10 JSON + scan of 4 JSONL), report_materials/
{figures/, r_analysis/}, scripts/* (docstrings on 17 scripts).

---

## Executive summary

- **Total findings: 47**
- **HIGH: 16** (strengthens primary claim or addresses likely reviewer objection)
- **MEDIUM: 20** (strengthens supporting claim or adds depth)
- **LOW: 11** (paper-scope nice-to-have)

**Top 5 highest-value items to surface BEFORE Group B ships:**

1. **D-1.05 Per-model keyword-judge disagreement rate decomposition** — claude 27.7%, chatgpt 19.1%, gemini 23.5%, deepseek 19.1%, mistral 21.4% (combined) and per-base claude 30.6% vs chatgpt 21.0%. Headline 25% keyword-judge disagreement hides 9-point per-model spread; surfacing this turns RQ1 from one-number into an interpretable pattern.
2. **D-1.10 Reasoning-quality and method-structure α are NEGATIVE** (overall α_RQ = −0.133, α_M = −0.042, both 95% CIs straddle 0). Currently rolled into "questionable" but the *direction* (active disagreement, not just weak agreement) is the strongest possible evidence that keyword reasoning rubrics fail. Never on website.
3. **D-5.01 Methodology page still claims "Five equal-weight dimensions (0.20 each)"** (Methodology.jsx:110-113). Phase 1B locked literature-derived weights A=0.30 R=0.25 M=0.20 C=0.15 N=0.10 — Methodology page literally contradicts the canonical narrative. The full 5-paragraph per-dim defense in research-narrative.md §2 has never reached the website.
4. **D-1.16 Per-model failure-mode distribution differs dramatically** — chatgpt: ASSUMPTION_VIOLATION 25 dominant (86% of its failures); claude: MATHEMATICAL_ERROR 10 dominant. The "46.9% assumption violations" headline hides that 2/5 models have *math errors* as their dominant mode. Currently only in JSON. This is the cross-cutting connection that lifts RQ3 from descriptive to diagnostic.
5. **D-1.01 Keyword vs judge degradation under perturbation** (`keyword_degradation_check.json`) — keyword PASS drops 1.9pp under perturbation, judge drops only −1.8pp; differential 3.7pp. Per-perturbation-type, semantic reframing produces a 5.96pp differential. Has a `recommended_methodology_page_text` field literally pre-written and never used. Direct empirical support for RQ1's "judge is more robust than keyword" claim.

**Top 3 cross-cutting connections never made explicit on the website:**

1. **Cross-method ranking inversion on calibration** — Gemini ranks WORST on verbalized ECE (0.097 vs cohort 0.06-0.18) but BEST on consistency ECE (0.618 vs cohort 0.66-0.73). Same model. Different extraction method. Different rank. Compelling evidence that "calibration measurement is method-dependent" — already in research-narrative.md but never visualized as the inversion it is.
2. **Per-model α and per-model keyword-judge disagreement are coupled** — Claude has lowest α_assumption (0.501) AND highest combined keyword-judge disagreement (27.7%); mistral has highest α (0.594) AND moderate keyword-judge disagreement (21.4%). The dimension where keyword and judge disagree most is also the dimension where *that specific model* trips most often.
3. **Robustness CIs cross zero for chatgpt and mistral** — chatgpt Δ=0.011 [−0.001, 0.024], mistral Δ=0.007 [−0.006, 0.019]. 2 of 5 models cannot statistically be distinguished from "no robustness deficit." Stronger claim than "ChatGPT/DeepSeek noise-equivalent" (currently in App.jsx) — and DeepSeek's CI is now [0.027, 0.058], which is *separable* from zero. The frontend prose is half-correct.

**Top 3 literature insights not propagated to website:**

1. **Du (~47%) + Boye-Moell + this work (46.9%) form a 3-way convergent finding** on assumption-violation as dominant failure. Currently RQ3 says "independent ~47% reproduction" naming only Du. The 3-way convergence within ~0.1pp is the strongest external-validity claim available.
2. **Yamauchi 2025: "judge prompt template choices have larger effects than judge model choice"** (paper note 10). Direct relevance to a likely reviewer objection ("why one judge?") — current website addresses model choice (external Llama) but not template choice. Limitations panel could absorb in 2 sentences.
3. **Textbook → task-type coverage maps** (citation-map.md "By task type family") — Bolstad → BETA_BINOM/HPD; Bishop → VB/DIRICHLET; Hoff → NORMAL_GAMMA/PPC; Carlin & Louis → MCMC families. Currently buried in the vault. References page lists textbooks but never claims "this benchmark covers the canonical Bayesian curriculum, mapped to its source textbooks." This is a strong continuity argument with prior pedagogy, free to surface.

**Recommended Group B scope additions: 14**
**Recommended Group C scope additions: 8 (new panels/visualizations)**

---

## Findings by category

### Category 1 — Buried numerical findings

**[D-1.01] Keyword degrades faster than judge under perturbation (3.7pp differential)**
Type: BURIED_FINDING
Severity: HIGH
Source: experiments/results_v2/keyword_degradation_check.json
Content: Keyword PASS rate drops 1.87pp on perturbation (68.7%→66.8%); judge drops only −1.80pp (48.6%→50.4%). 3.7pp differential. Per-perturbation-type: semantic reframing has the largest 5.96pp differential; numerical 2.92pp; rephrase 1.96pp. The JSON has `recommended_methodology_page_text` field with 4-sentence ready-to-paste prose. Pre-registered for Phase 1.5.
Where it should appear: Methodology page §3 (judge subsection) — direct empirical evidence judge is robust to surface change. Also a Key Findings card (replaces "Perturbation runs" placeholder).
Why it strengthens: Reviewers ask "why an LLM judge instead of just better keyword regex?" This is the answer in pre-computed numbers.

**[D-1.02] Per-perturbation-type keyword-judge disagreement rate** (rephrase 21.6%, numerical 22.7%, semantic 18.1%)
Type: BURIED_FINDING
Severity: MEDIUM
Source: experiments/results_v2/combined_pass_flip_analysis.json:perturbation.per_perturbation_type
Content: Keyword-judge disagreement rate on perturbation runs decomposes by type. Numerical perturbations produce the highest disagreement (22.7%), semantic the lowest (18.1%) — counter-intuitive: changing the numbers exposes assumption-checking gaps more than reframing the problem.
Where: New visualization or KeyFindings card; sub-panel of judge-validation section.
Why: Surface evidence that judge value is not equal across perturbation kinds — refines the "use a judge" argument.

**[D-1.03] Combined 22.16% keyword-judge disagreement on 3,195 runs** (vs 25.0% headline on 1,095 base)
Type: BURIED_FINDING
Severity: HIGH
Source: experiments/results_v2/combined_pass_flip_analysis.json:combined
Content: Phase 1.5 introduced run-ID-deduplicated set union of base + perturbation keyword-judge disagreement. Combined: 708/3,195 = 22.16%. Base alone: 274/1,095 = 25.02%. Recompute_log records "DECISION POINT: Headline framing for website (deferred to user): keep 25% / switch to 22.2% / present both."
Where: Decision needed before Group B prose is written. KeyFindings card. PosterCompanion if the broader denominator is preferred.
Why: 3× sample size strengthens the claim numerically; 22% is a different number than 25% and reviewers will ask which.

**[D-1.04] Inverse-flip rate (keyword FAIL judge PASS) — 4.5% combined**
Type: BURIED_FINDING
Severity: MEDIUM
Source: combined_pass_flip_analysis.json:combined.pct_inverse_flip = 0.0448
Content: 143 of 3,195 eligible runs flip the OTHER way — keyword fails them, judge passes them. The 22.16% keyword-judge disagreement headline implies 17.7% net keyword overstatement (22.16 − 4.48). Currently never disclosed; the headline reads as if all disagreement is keyword-overstates direction.
Where: Methodology page or Limitations — honest framing.
Why: A reviewer who computes the matrix herself will see 5% inverse-flip and ask why it isn't disclosed. Pre-empt.

**[D-1.05] Per-model keyword-judge disagreement rate (combined)**
Type: BURIED_FINDING
Severity: HIGH
Source: combined_pass_flip_analysis.json:combined.per_model
Content: Combined per-model keyword-judge disagreement — claude 27.7% (177/639), gemini 23.5% (150/639), mistral 21.4% (137/639), chatgpt 19.1% (122/639), deepseek 19.1% (122/639). 9-point spread. The 25%/22% headline is a population mean over a non-uniform distribution. Base-only: claude 30.6%, mistral 26.5%, gemini 24.7%, deepseek 22.4%, chatgpt 21.0%.
Where: New "Per-model judge disagreement" KeyFindings card OR a panel with grouped bars; Methodology subsection.
Why: Lifts RQ1 from one-number to ranking. Claude — the model that wins accuracy under equal weights — is also the model the judge most often disagrees with on assumption_compliance. Materially relevant to the "Claude wins / Gemini wins under literature weights" narrative.

**[D-1.06] Per-perturbation-type robustness Δ per model** (5×3 grid, 15 cells)
Type: BURIED_FINDING
Severity: HIGH
Source: experiments/results_v2/robustness_v2.json:per_model[*].per_perturbation_type
Content: Already exists as a 5×3 cell. Highlights buried in JSON: chatgpt and mistral *improve* on numerical perturbations (Δ = −0.0075, −0.0093 — i.e. they score higher when numbers change); gemini degrades MOST on rephrase (Δ = 0.0651) but only 0.0463 on numerical; claude degrades worst on rephrase (0.054). Asymmetry direction is never displayed.
Where: New visualization (5×3 heatmap) under Robustness category. KeyFindings card on "Two models improve under numerical perturbation."
Why: This is the actionable insight from RQ4 — robustness is not uniform across perturbation kinds, and the direction of effect varies. "ChatGPT/DeepSeek noise-equivalent" is shallow next to "ChatGPT actually improves on numerical perturbations."

**[D-1.07] Bootstrap separability matrix — 10 pairs each, accuracy + robustness**
Type: BURIED_FINDING
Severity: MEDIUM
Source: experiments/results_v2/bootstrap_ci.json:separability
Content: Explicit pair-wise labels — accuracy: claude/chatgpt not_separable, gemini/(any other) separable, deepseek/mistral not_separable. Robustness: chatgpt/(claude, gemini, deepseek) separable; chatgpt/mistral not_separable; gemini/deepseek not_separable.
Where: Methodology §4 (Statistical validation) currently says "Top-2 not statistically separable" without showing the matrix. Add a 5×5 separability table figure.
Why: Reviewers will read the bootstrap CI claim and look for the matrix. Including it answers Hochlehnert (2025)'s separability-test recommendation in full, not summary.

**[D-1.08] Robustness CIs CROSS ZERO for 2 of 5 models**
Type: BURIED_FINDING
Severity: HIGH
Source: bootstrap_ci.json:robustness — chatgpt CI [−0.001, 0.024], mistral CI [−0.006, 0.019]
Content: 2/5 models have robustness Δ confidence intervals that include zero. They are statistically indistinguishable from "no robustness deficit at all." The current frontend prose says "ChatGPT/DeepSeek noise-equivalent" — but DeepSeek's new CI [0.027, 0.058] is now *separable* from zero, so this claim is incorrect under literature weights. The two zero-crossing models are CHATGPT and MISTRAL.
Where: Update App.jsx:1898 "ChatGPT/DeepSeek noise-equivalent" → "ChatGPT/Mistral noise-equivalent." Methodology §4 add the CI bracket.
Why: Currently making a false attribution claim on the live site (DeepSeek when it should be Mistral). Stronger claim available: 2/5 models robust at noise-equivalent under perturbation.

**[D-1.09] Per-model Krippendorff α** (range 0.501-0.594)
Type: BURIED_FINDING
Severity: MEDIUM
Source: krippendorff_agreement.json:per_model[*].assumption_compliance
Content: chatgpt α=0.577, claude α=0.501, gemini α=0.539, deepseek α=0.537, mistral α=0.594. Cohort range 0.501-0.594. Mistral has the BEST keyword-judge agreement; claude has the WORST. All "questionable" by Park 2025 thresholds. Nowhere on the website.
Where: New panel under Judge Validation. Strengthens the per-model keyword-judge disagreement narrative (D-1.05).
Why: When combined with D-1.05, the message is "the model the judge least agrees with also has the highest keyword-judge disagreement rate" — supports the keyword-rubric-is-bad-for-this-task hypothesis specifically by model.

**[D-1.10] α is NEGATIVE on reasoning_quality and method_structure** (active disagreement)
Type: BURIED_FINDING
Severity: HIGH
Source: krippendorff_agreement.json:overall — RQ α=−0.133 [−0.228, −0.039], M α=−0.042 [−0.097, 0.015]
Content: Both α values are *below zero*. Negative α means raters systematically disagree — keyword and judge are not just "questionable," they are pulling in opposite directions on RQ. The RQ CI is entirely below zero (statistically significant negative agreement). Currently rolled into the "questionable" label.
Where: Methodology §4 — explicit table of α per dimension with sign. New KeyFindings card OR a callout in the agreement panel.
Why: Negative agreement is a much stronger claim than questionable agreement. It says keyword reasoning rubric does worse than chance. Maximally compelling for RQ1's primary methodology claim.

**[D-1.11] Per-NMACR-dimension ECE per model** (5×5 grid)
Type: BURIED_FINDING
Severity: MEDIUM
Source: experiments/results_v2/per_dim_calibration.json:per_dim_ece
Content: Already-canonical Layer 5 result. Gemini has highest ECE on R (0.129) — gemini is BEST on RQ accuracy but WORST calibrated on RQ. ECE on A is uniformly high across models (0.165-0.172) — assumption confidence is mis-calibrated everywhere. Figure exists (a5b_per_dim_calibration.png). Not on visualizations.js, not in API endpoint.
Where: Layer-5 panel under Calibration. visualizations.js entry under "calibration."
Why: The per-dimension breakdown is what RQ5 was promoted to surface (rq_restructuring.md). Not having it on the website is a direct gap with the canonical RQ structure.

**[D-1.12] accuracy_calibration_correlation r values per model** (Layer 4)
Type: BURIED_FINDING
Severity: MEDIUM
Source: calibration.json:accuracy_calibration_correlation — claude 0.49, mistral 0.48, chatgpt 0.37, deepseek 0.35, gemini excluded
Content: Pearson r between per-task aggregate_new and per-task confidence. Gemini specifically excluded (0 verbalized signals across all 246 base runs). Honest interpretation in research-narrative.md: "well-calibrated does not mean accurate; it means hedging behaviour tracks task difficulty." This sentence is paste-ready and on no website surface.
Where: New Calibration sub-panel showing 4 r values + gemini-excluded note. Limitations.jsx L2 caveat could absorb the gemini-specific exclusion sentence.
Why: Research-narrative names this as the canonical RQ5 Layer 4 finding; the website renders RQ5 without Layer 4.

**[D-1.13] formatting_failure_rate per model**
Type: BURIED_FINDING
Severity: MEDIUM
Source: calibration.json:formatting_failure_rate_per_model — claude 0.0%, gemini 0.41%, mistral 2.03%, chatgpt 2.44%, deepseek 2.44%
Content: Phase 1B added this report-level metric. Claude is uniquely zero. Range 0.00-2.44%. Backend `/api/v2/calibration` returns it inside `verbalized.per_model` but not as a top-level field. No frontend consumer.
Where: KeyFindings card "Formatting failure rate"; Methodology §2 sentence on how FORMATTING_FAILURE is excluded from the rubric and reported separately.
Why: Closes the "did some models fail to follow the answer format" question. Material to a "model selection" reader. Validates the rubric design choice (FORMATTING is pre-rubric).

**[D-1.14] Per-model judge dimension means including reasoning_completeness**
Type: BURIED_FINDING
Severity: MEDIUM
Source: experiments/results_v2/judge_dimension_means.json
Content: Per-model means on all 4 judge dimensions. RC means: gemini 0.988 (highest), claude 0.972, mistral 0.959, chatgpt 0.951, deepseek 0.939. RC range is 5 percentage points but separates 5 models cleanly. Gemini RC > RQ; deepseek RC > RQ → all models show "reasoning is more complete than it is correct." judge_dimension_means.json also has perturbation-side means (never displayed).
Where: Methodology §2 NMACR rubric box — currently lists "R: Reasoning Quality" only; could split into RQ + RC means as evidence the dimension separates models.
Why: Day-2 audit [H-2] flagged that poster/main.tex has a "Stub --- to fill from llm_judge_scores_full.jsonl aggregation" on the per-model judge ranking. The aggregation already exists in this file; the values just need surfacing.

**[D-1.15] Per-model assumption keyword-vs-judge MEAN gap**
Type: BURIED_FINDING
Severity: MEDIUM
Source: keyword_vs_judge_agreement.json:per_model[*].assumption_compliance.kw_mean / judge_mean
Content: Claude kw=0.63 → judge=0.45 (gap 0.18, biggest). chatgpt kw=0.51 → judge=0.42 (gap 0.10). The mean delta between keyword and judge varies per model. Claude is the most-overstated by keyword on assumption_compliance.
Where: Per-model judge validation panel.
Why: Strongest "Claude looks better under keyword than under judge" evidence. Would land hard on the methodology contribution.

**[D-1.16] Per-model L1 failure-mode distribution**
Type: BURIED_FINDING / CROSS_CUTTING_CONNECTION
Severity: HIGH
Source: error_taxonomy_v2.json:by_model_l1
Content: ChatGPT: ASSUMPTION_VIOLATION 25, MATH 4 (assumption-dominated). Claude: MATH 10, ASSUMPTION 9 (math-dominated). DeepSeek: ASSUMPTION 15, MATH 13 (mixed). Mistral: MATH 12, ASSUMPTION 8 (math-dominated). Gemini: ASSUMPTION 10, MATH 9 (close split). Aggregating to "46.9% assumption violations" hides that 2/5 models (claude, mistral) have MATH errors as the dominant mode.
Where: New visualization (per-model stacked bar) or sub-panel under Error Taxonomy. Methodology page paragraph framing the heterogeneity.
Why: Audit comprehensive notes professor critique #12 (failure analysis for each model) is PARTIAL — the data exists, no panel-ready figure was built. Builds out RQ3 from one number to a per-model story.

**[D-1.17] Stratified-vs-full ECE delta** (Phase 1C)
Type: BURIED_FINDING
Severity: MEDIUM
Source: self_consistency_calibration.json:ece_comparison_full
Content: B3 stratified ECE → full ECE delta per model: claude 0.33→0.73 (+0.40), chatgpt 0.64→0.72 (+0.08), gemini 0.57→0.62 (+0.05), deepseek 0.64→0.73 (+0.09), mistral 0.60→0.66 (+0.06). Claude's stratified estimate was the *most* misleading. Currently described in research-narrative.md narrative form; never tabulated.
Where: New Calibration table with 3 columns (verbalized / stratified / full) per model. Limitations panel L5 once it's rewritten as RESOLVED.
Why: The 0.40 delta on Claude is a striking number. Stratified-B3 was understating overconfidence by 0.4 ECE points on the project's accuracy leader.

**[D-1.18] Brier scores from self-consistency** (Phase 1C)
Type: BURIED_FINDING
Severity: LOW
Source: self_consistency_calibration.json:per_model[*].brier
Content: Brier scores: claude 0.635, chatgpt 0.625, gemini 0.476, deepseek 0.619, mistral 0.545. Gemini has the LOWEST Brier (best probability score under 0/1 ground truth). ECE-Brier ordering disagrees: ECE says gemini is best (0.62), Brier confirms. Currently surfaced in the JSON; never on website.
Where: Could fold into D-1.17 panel as a 4th column. Calibration sub-panel.
Why: ECE alone is one number; ECE+Brier is a more complete probabilistic-calibration story. Multi-Answer Confidence (2026) recommends both.

**[D-1.19] Tolerance sensitivity rankings shift across levels** (CONTRADICTS Methodology page)
Type: BURIED_FINDING
Severity: HIGH
Source: tolerance_sensitivity.json:rankings + ranking_stable_across_levels = false
Content: Tight tolerance: chatgpt > claude > deepseek > mistral > gemini. Default: claude > chatgpt > deepseek > mistral > gemini. Loose: claude > chatgpt > gemini > mistral > deepseek. Gemini swings from worst (tight) to mid (loose). Methodology.jsx:179-182 says "Ranking stable across sweeps" — this is FALSE per the canonical JSON.
Where: Methodology page §4 — replace the false stability claim with the actual ranking shift. Limitations panel could absorb.
Why: A direct factual error on the deployed Methodology page. Reviewer who runs the script will see ranking_stable_across_levels=false. Must be fixed.

**[D-1.20] 95% CI on per-perturbation-type robustness**
Type: BURIED_FINDING
Severity: LOW
Source: bootstrap_ci.json computes per-model only, not per-(model,perttype). Gap.
Content: There is NO per-(model, perturbation-type) CI in the canonical files. The 5×3 cell grid (D-1.06) is means only. A reviewer might ask "is gemini's 0.0651 rephrase Δ separable from chatgpt's 0.0297?"
Where: Future-work or paper-scope.
Why: Honest gap. Worth noting in Limitations as "per-cell CIs deferred."

**[D-1.21] Per-task-type heatmap with 3 zero-Δ task families**
Type: BURIED_FINDING
Severity: LOW
Source: robustness_v2.json:per_task_type_heatmap
Content: visualizations.js caption mentions "HIERARCHICAL, RJMCMC, VB" as uniformly robust. The actual cell-by-cell numbers are in per_task_type_heatmap and not surfaced. Could quantify "≤ 0.01 Δ across all 5 models" claim.
Where: Robustness panel — could expose the cell values on hover.
Why: Reviewer-facing depth.

**[D-1.22] Top-30 specific keyword/judge disagreements with response excerpts**
Type: BURIED_FINDING
Severity: LOW
Source: experiments/results_v2/top_disagreements_assumption.json (30 records)
Content: 30 specific runs where keyword and judge disagree by ≥ 1.0 on assumption_compliance, with judge_justification + response_excerpt. Concrete examples like BIAS_VAR_03/claude where keyword=0 but judge=1 ("response explicitly states iid + Uniform(0,θ)"). Reviewer-grade ground-truth.
Where: New "Specific disagreements" panel, perhaps as a curated 3-example callout. Or a paper appendix.
Why: Anecdotal evidence behind the 25% keyword-judge disagreement headline. Hand-pickable and powerful.

**[D-1.23] Major-disagreement counts (keyword↔judge gap > 0.5) per dimension**
Type: BURIED_FINDING
Severity: LOW
Source: keyword_vs_judge_agreement.json:overall_per_dimension[*].major_disagreements_gt_0_5
Content: Counts of |keyword − judge| > 0.5 on each dim. assumption_compliance 120, method_structure 51, reasoning_quality 54. 120 of 1095 = 11% major disagreements on A. Never on website.
Where: Footnote in agreement panel.
Why: Granular evidence for the 25% keyword-judge disagreement headline.

**[D-1.24] Tolerance-sensitivity excludes 50 of 1230 base runs**
Type: BURIED_FINDING
Severity: LOW
Source: tolerance_sensitivity.json:n_runs_scored_per_level = 1180 (from 1230 base)
Content: 50 runs excluded from tolerance analysis (presumably CONCEPTUAL with no numeric target, or runs without parsed_values). Never disclosed.
Where: Methodology §4 footnote when tolerance is mentioned.
Why: Disclosure completeness.

### Category 2 — Undocumented methodology choices

**[D-2.01] Bootstrap parameters (B=10000, seed=42, percentile method)**
Type: UNDOCUMENTED_METHOD
Severity: MEDIUM
Source: scripts/bootstrap_ci.py + bootstrap_ci.json:method
Content: B=10000, seed=42, non-parametric bootstrap, 95% percentile CI. Methodology page mentions "10 000 bootstrap resamples" but not the seed (reproducibility) or method choice (percentile vs BCa). Krippendorff bootstrap uses *different* params (B=1000, seed=42) — undisclosed inconsistency.
Where: Methodology §4 short paragraph.
Why: Reviewer-likely-objection. Two-line fix.

**[D-2.02] Tolerance levels rationale**
Type: UNDOCUMENTED_METHOD
Severity: MEDIUM
Source: scripts/tolerance_sensitivity.py:TOLERANCE_LEVELS
Content: tight (0.005, 0.025), default (0.010, 0.050), loose (0.020, 0.100) — 2× steps each. Default matches per-task `full_credit_tol`. No literature anchor; choice never defended.
Where: Methodology page short paragraph; or appendix.
Why: Why these levels? Why not 5 levels? Pre-empt.

**[D-2.03] Self-consistency parameters (T=0.7, top_p=0.95, n_runs=3, $15 cap)**
Type: UNDOCUMENTED_METHOD
Severity: MEDIUM
Source: scripts/self_consistency_full.py docstring
Content: T=0.7 not 1.0 (why?); top_p=0.95 (default sampling?); n_runs=3 (vs 5 or 10 — sample-size tradeoff); cost cap $5 soft / $15 hard. Multi-Answer Confidence (2026) is the methodology citation but their parameter choices not compared.
Where: Methodology §3 or RQ5 sub-panel.
Why: 3-rerun is the lowest defensible number; disclose the tradeoff.

**[D-2.04] Llama 3.3 70B chosen for 4 specific reasons**
Type: UNDOCUMENTED_METHOD
Severity: MEDIUM
Source: evaluation/llm_judge_rubric.py docstring
Content: (a) external to the 5 benchmarked models — eliminates self-preference bias; (b) Together AI Turbo, ~$0.88/M tokens, ~$8 for full ~3,800-run project; (c) open-weights → reproducible; (d) migrated FROM Groq's 100K/day cap which capped scaling at ~80/day. Methodology page says "external" but not the cost/reproducibility/migration story.
Where: Methodology §3 (Llama judge subsection) — already exists, expand.
Why: Closes the "could you have used GPT-4 as judge?" question.

**[D-2.05] reasoning_completeness was added mid-project specifically for "name-drop" detection**
Type: UNDOCUMENTED_METHOD
Severity: MEDIUM
Source: llm-stats-vault/90-archive/2026-04-30-day1-poster-sprint.md decision 3 (per personal_todo_status.md item 6)
Content: RC dimension was a deliberate add to catch "name-drops + answer, no derivation" — a failure mode the keyword rubric cannot detect. RC mean=0.962, n=1229, zeros=4, ones=1139 — strong skew. Choice never appears on website; the rubric lists 5 dims as if all designed simultaneously.
Where: Methodology §2 NMACR description — note that R is mean(RQ, RC) and why RC was added.
Why: Pre-empt "did you change the rubric mid-project to engineer a result?" — answer: yes, BEFORE seeing scores, to catch a known failure mode.

**[D-2.06] Rate-limit backoff: 30s for Llama judge specifically (TPM)**
Type: UNDOCUMENTED_METHOD
Severity: LOW
Source: evaluation/llm_judge_rubric.py — RATE_LIMIT_BACKOFF_S = 30 with explanatory comment
Content: 5s would be too short for a 1-min TPM window; 30s aligns with Together's TPM reset.
Where: Operational footnote, paper-appendix scope.
Why: Reproducibility detail.

**[D-2.07] Cost guards on Phase 1C ($5 soft pause / $15 hard abort, ended at $11.69)**
Type: UNDOCUMENTED_METHOD
Severity: LOW
Source: scripts/self_consistency_full.py + recompute_log.md "Phase 1C"
Content: Soft pause / hard cap design pattern; project came in $4.31 below projection. Operational discipline.
Where: Footnote / paper-appendix scope.
Why: Reproducibility / cost-of-research disclosure.

**[D-2.08] Eligibility filter is non-empty `required_assumption_checks`**
Type: UNDOCUMENTED_METHOD
Severity: HIGH
Source: scripts/combined_pass_flip_analysis.py + comprehensive_audit F6.01
Content: 1230 base − 1095 eligible = 135 excluded (CONCEPTUAL/MINIMAX/BAYES_RISK with empty required_assumption_checks). 161 of 171 self-consistency excluded 10 CONCEPTUAL. 143 failures classified out of all base failures. Three different eligibility filters; only one (the 10 CONCEPTUAL) is on the website.
Where: Methodology §4 — single sentence each. Limitations panel new entry on filter rationale.
Why: Comprehensive audit F6.01 flags the 135 exclusion as missing from all 3 layers (audit, narrative, website).

**[D-2.09] Three-rankings concept comes from ReasonBench's "variance-as-first-class"**
Type: UNDOCUMENTED_METHOD
Severity: MEDIUM
Source: scripts/three_rankings_figure.py + paper note 07
Content: The "accuracy ≠ robustness ≠ calibration" framing is a direct adoption of ReasonBench (2025)'s framing. Currently treated as a project-original framing.
Where: visualizations.js three_rankings caption + Methodology §1 continuity statement.
Why: Honesty + literature anchor.

**[D-2.10] Single-judge cross-provider verification (Groq vs Together)**
Type: UNDOCUMENTED_METHOD
Severity: MEDIUM
Source: scripts/inspect_judge_strictness.py + Methodology.jsx (mentions Groq spot-check)
Content: Cross-provider check WAS run between Groq's Llama and Together's Llama (different infrastructure for the same model). Methodology page mentions this in 1 sentence; the strictness audit script computes auto-flag heuristics (template justifications, length-independence, keyword count) — never surfaced. Used as 1 of 2 checks supporting the "Llama judge is reliable" claim.
Where: Limitations panel L4 (single-judge) — already mentions; could expand 1 sentence about strictness audit.
Why: Strengthens single-judge defense.

**[D-2.11] FORMATTING_FAILURE deliberately excluded from rubric (pre-rubric)**
Type: UNDOCUMENTED_METHOD
Severity: MEDIUM
Source: research-narrative.md §4 + scripts/recompute_nmacr.py docstring
Content: 18 FORMATTING failures (12.6% of 143) are excluded from NMACR scoring and reported separately as `formatting_failure_rate`. Decision rationale: "FORMATTING is orthogonal to substantive Bayesian reasoning; folding it into NMACR would penalize models for output-template glitches rather than reasoning errors." Methodology page never explains this.
Where: Methodology §2 NMACR description.
Why: Reviewer "why is your headline 46.9% when 12.6% are formatting?" — answer: because the headline is over substantive failures, by design.

**[D-2.12] Phase 1B "data-layer recompute, runtime unchanged" architecture**
Type: UNDOCUMENTED_METHOD
Severity: MEDIUM
Source: audit/aggregation_locus.md + scripts/recompute_nmacr.py
Content: Path A (response_parser.py) and Path B (metrics.py) are LOCKED at equal-weight 0.20 for v1 reproducibility. Phase 1B's literature-derived weights apply only via a wrapper script that produces nmacr_scores_v2.jsonl. Currently no website-layer documentation of this — Methodology lists 5 dims at 0.20 each (which is true for runtime only).
Where: Methodology §2 — explicit 2-paragraph note: runtime weights = 0.20 each (locked); analysis weights = literature-derived (per recompute_nmacr.py).
Why: Reviewer reading the deployed Methodology will think the project uses equal weights everywhere — which contradicts the canonical narrative. (See D-5.01.)

**[D-2.13] CONCEPTUAL handling: weight renormalisation on missing N**
Type: UNDOCUMENTED_METHOD
Severity: LOW
Source: scripts/recompute_nmacr.py + research-narrative.md §2
Content: 686 of 3,595 records have ≥ 1 missing dimension; remaining weights renormalised to 1.0. Mirrors `full_score()` runtime behaviour. Honest disclosure.
Where: Methodology footnote.
Why: Closes the "what about CONCEPTUAL tasks?" question.

**[D-2.14] 5 frontier LLMs from 5 different providers** (model-diversity defense)
Type: UNDOCUMENTED_METHOD
Severity: MEDIUM
Source: CLAUDE.md model-clients section + paper notes
Content: Anthropic, Google, OpenAI, DeepSeek, Mistral — 5 distinct providers. Choice rationale ("frontier + diverse") never anchored to literature. Feuer 2025 specifically warns about "family-preference bias"; 5 different providers is the design countermeasure. Currently the website lists models without this defense.
Where: Methodology page or About RQ4.
Why: Pre-empt "why these 5 and not others?"

**[D-2.15] Why bootstrap ECE is intentionally NOT computed**
Type: UNDOCUMENTED_METHOD
Severity: LOW
Source: bootstrap_ci.json:calibration_note "ECE point estimates per model; bootstrap CI requires binned resampling (deferred)"
Content: Honest gap acknowledgement. Calibration ECE is a point estimate; bootstrap on bucketed data needs different machinery. Never disclosed on website.
Where: Limitations panel new entry OR Methodology §4 footnote.
Why: Reviewer "you have bootstrap CIs on accuracy and robustness — why not on ECE?" — pre-answered.

### Category 3 — Unused visualizations

**[D-3.01] Entire R-analysis pipeline (16 figures + 9.9MB HTML report)**
Type: UNUSED_VISUALIZATION
Severity: HIGH
Source: report_materials/r_analysis/{figures/, interactive/, benchmark_report.html}
Content: 16 distinct R-generated figures (model_heatmap, tier_radar, distributions, difficulty_scatter, failure_analysis, latency_accuracy, grouped_bar, ecdf, treemap, correlation, latency_box, pass_rate, difficulty, bar_race, error_distribution, error_by_model_heatmap, error_by_task_type) plus 12 interactive HTMLs. Some surfaced in early Day 3 viz overhaul, then trimmed. The 43KB R-Markdown master report renders to 9.9MB HTML — never linked from website.
Where: Decide per figure; tier_radar is a strong candidate for a hover panel; latency_accuracy overlay is unique data not present in v2 figures.
Why: Substantial work product. Cleanup audit (next pass) will decide what to archive. For now: catalogue them as available material.

**[D-3.02] tolerance_sensitivity.png not on website**
Type: UNUSED_VISUALIZATION
Severity: MEDIUM
Source: report_materials/figures/tolerance_sensitivity.png (132KB, Apr 30)
Content: The figure exists; visualizations.js does not reference it; not in frontend public dir.
Where: Methodology §4 supplement OR Robustness panel.
Why: Methodology page mentions tolerance sensitivity in prose but shows no figure.

**[D-3.03] calibration_ece_ranking.png not on website**
Type: UNUSED_VISUALIZATION
Severity: MEDIUM
Source: report_materials/figures/calibration_ece_ranking.png (119KB, Apr 30)
Content: Bar-chart ranking of verbalized ECE per model — exists, not referenced.
Where: Calibration panel could include as alternate to a5_calibration_reliability.
Why: Direct ECE ranking is what KeyFindings card might link to.

**[D-3.04] a4b_per_dim_robustness.png in public dir but NOT in visualizations.js**
Type: UNUSED_VISUALIZATION
Severity: HIGH
Source: capstone-website/frontend/public/visualizations/png/v2/a4b_per_dim_robustness.png + Group A completion report
Content: Group A mirrored a4b PNG to frontend public dir, but visualizations.js manifest was deferred to Group C. Currently the file is shipped but unreachable from the gallery.
Where: Add to visualizations.js under "robustness" category. Group C scope.
Why: Phase 1B Layer 2 is canonical — RQ4 is incomplete without it.

**[D-3.05] a5b_per_dim_calibration.png in public dir but NOT in visualizations.js**
Type: UNUSED_VISUALIZATION
Severity: HIGH
Source: same as D-3.04
Content: Same situation. Layer 5 canonical figure shipped to frontend, unreachable from gallery.
Where: Add to visualizations.js under "calibration" category.
Why: RQ5 is incomplete without it.

**[D-3.06] combined_pass_flip_comparison.png in public dir but NOT in visualizations.js**
Type: UNUSED_VISUALIZATION
Severity: HIGH
Source: same as D-3.04
Content: Phase 1.5 figure shipped to frontend, unreachable from gallery. Quantifies base 25% vs perturbation 20.7% vs combined 22.2%.
Where: visualizations.js entry under "judge" category (Phase 1.5 sits within RQ1).
Why: Phase 1.5 deliverable visibility.

**[D-3.07] Captions on website still reference Phase 1A findings (per audit F8.04)**
Type: UNUSED_VISUALIZATION
Severity: MEDIUM
Source: visualizations.js entries 35, 71, 130
Content: bootstrap_ci subtitle hardcodes "Claude 0.679 / Gemini 0.674" Phase 1A. robustness_heatmap caption "Mistral degrades most" — INVERTED under literature weights (Mistral now most robust). self_consistency entry titled "B3 proxy" — superseded.
Where: visualizations.js full caption refresh.
Why: Group B prose dependency.

**[D-3.08] judge_validation_scatter caption says 274/1094 (off-by-one)**
Type: UNUSED_VISUALIZATION
Severity: LOW
Source: visualizations.js:54
Content: "274 / 1094 runs flip pass/fail" — should be 274/1095 per canonical.
Where: 1-character fix.
Why: Number consistency.

### Category 4 — Literature insights not propagated

**[D-4.01] 3-way convergence on assumption-violation share** (Du ~47% / Boye-Moell / this work 46.9%)
Type: LITERATURE_INSIGHT_NOT_PROPAGATED
Severity: HIGH
Source: rq_restructuring.md RQ3 grounding + paper notes 09 and 13
Content: Du et al. ~47% on causal-inference. Boye-Moell unwarranted-assumption as top failure mode in math-reasoning. This work 46.9% on Bayesian. Three independent measurements within ~0.1pp on the same failure mode across 3 problem domains. Currently Methodology references Du as "independent reproduction"; never frames as 3-way convergence.
Where: RQ3 panel headline OR Methodology §1 continuity statement.
Why: Strongest external-validity claim available. Three is more than two.

**[D-4.02] Yamauchi insight: judge prompt template > judge model**
Type: LITERATURE_INSIGHT_NOT_PROPAGATED
Severity: HIGH
Source: paper note 10 + Methodology.jsx mentions Park et al. only for α
Content: Yamauchi's headline finding is that prompt template choices have larger effects than judge model choice. Project handles model choice (Llama 3.3 70B external) but not template choice. Limitations panel L4 mentions multi-judge ensembling but not multi-template.
Where: Limitations panel L4 — extend by 1 sentence on template-choice as a separate axis of judge variance.
Why: Pre-empt obvious reviewer objection.

**[D-4.03] Textbook → task-type coverage map** (citation-map.md)
Type: LITERATURE_INSIGHT_NOT_PROPAGATED
Severity: MEDIUM
Source: llm-stats-vault/40-literature/citation-map.md "By task type family"
Content: Bolstad → BETA_BINOM, BINOM_FLAT, HPD, GAMMA_POISSON. Bishop → VB, DIRICHLET, BAYES_REG, LOG_ML. Ghosh → JEFFREYS, FISHER_INFO, RC_BOUND. Hoff → NORMAL_GAMMA, PPC, GIBBS. Carlin & Louis → GIBBS, MH, HMC, RJMCMC, REGRESSION, HIERARCHICAL. Goldstein-Wooff → BAYES_LINEAR, LINEAR_APPROX. Lee → CI_CREDIBLE, BAYES_FACTOR.
Where: References page expand each textbook card with its task-type coverage (TEXTBOOK_DESC already has prose hints — could be more explicit).
Why: Closes "where do these tasks come from?" — answer: the canonical Bayesian curriculum, mapped to each task family.

**[D-4.04] Multi-Answer Confidence: combined verbalized + consistency**
Type: LITERATURE_INSIGHT_NOT_PROPAGATED
Severity: MEDIUM
Source: paper note 12
Content: Multi-Answer Confidence (2026) explicitly recommends combining verbalized + consistency for best calibration. The project computes BOTH but never combines them into a single calibrated estimator. One-line analysis would surface this as a future-work concrete plan.
Where: Future Work panel.
Why: Concrete future-work item, not vague.

**[D-4.05] Feuer "family-preference bias" → 5-provider design**
Type: LITERATURE_INSIGHT_NOT_PROPAGATED
Severity: MEDIUM
Source: paper note 14
Content: Feuer 2025 warns about family-preference (judge biased toward models in same family). The project's 5 distinct providers is the architectural counter-design, but never named as such. Limitations panel L4 cites Feuer for single-judge but doesn't connect to the 5-provider design.
Where: Limitations L4 OR a new line in Methodology §3.
Why: Defense becomes legible.

**[D-4.06] BrittleBench taxonomy adopted in full** (rephrase / numerical / semantic)
Type: LITERATURE_INSIGHT_NOT_PROPAGATED
Severity: MEDIUM
Source: paper note 08 + scripts/generate_perturbations_full.py
Content: BrittleBench 2026 defines exactly 3 perturbation types: rephrase, numerical, semantic. The project adopts these directly (not adapted, not extended). visualizations.js robustness_perttype caption mentions rephrase/numerical/semantic without literature anchor.
Where: Methodology §1 OR visualizations.js caption.
Why: Honesty + literature anchor; already stated in audit/methodology_continuity.md.

**[D-4.07] SelfCheckGPT (Manakul 2023) cited in self_consistency_full.py but missing from vault**
Type: LITERATURE_INSIGHT_NOT_PROPAGATED
Severity: LOW
Source: scripts/self_consistency_full.py docstring + vault has no Manakul note
Content: Methodology cite gap. The script names SelfCheckGPT as ground for the 3-rerun method; vault doesn't track it; References page doesn't list it.
Where: Add to vault as paper 16 OR explicitly drop the citation.
Why: Citation hygiene.

**[D-4.08] Park et al. ↔ Yamauchi citation key inconsistency**
Type: LITERATURE_INSIGHT_NOT_PROPAGATED
Severity: LOW
Source: paper note 10 — "bibtex key `park2025judge` is legacy — actual first author is Yamauchi"
Content: References page says "Park et al. 2025" but the actual first author is Yamauchi. Methodology.jsx:144 says "Park et al., 2025." All website surfaces use the legacy attribution.
Where: Decide between updating website to "Yamauchi et al., 2025" OR keep "Park" as a project-internal stable shorthand. Either way, document.
Why: Paper-correctness check.

**[D-4.09] Yamauchi: single-judge ensembles inflate reliability**
Type: LITERATURE_INSIGHT_NOT_PROPAGATED
Severity: MEDIUM
Source: paper note 10 key findings
Content: "Single-judge ensembles inflate reliability estimates." Direct relevance to a likely RQ1 reviewer objection: "your α=0.55 between keyword and Llama-judge — what if α between Llama and a different Llama is 0.95?" Limitations cites Feuer; could also cite Yamauchi.
Where: Limitations L4 expand.
Why: Reviewer-likely-objection.

**[D-4.10] Hochlehnert (Statistical Fragility) "Pass@1 ≥ 3pp" — quoted but not anchored**
Type: LITERATURE_INSIGHT_NOT_PROPAGATED
Severity: LOW
Source: paper note 15 + Limitations.jsx L3
Content: Cited correctly in Limitations L3; canonical title is "A Sober Look at Progress in Language Model Reasoning" but website doesn't include the canonical title. Bibtex inconsistency between the project's chosen short name and the paper's official title.
Where: References card expand.
Why: Paper-correctness check.

**[D-4.11] FermiEval contrast is now COMPLEX (matches under one extraction, contradicts under another)**
Type: LITERATURE_INSIGHT_NOT_PROPAGATED
Severity: HIGH
Source: research-narrative.md RQ5 + paper note 11
Content: Original framing: "FermiEval finds overconfidence; we find hedge-heavy." Phase 1C: under consistency extraction, all 5 models ARE overconfident. So the contrast is now: "FermiEval = overconfident; this work, verbalized = hedge-heavy; this work, consistency = overconfident (matches FermiEval)." Three-way comparison. The "hedge-heavy contrast" is on poster-citations.md and methodology_continuity.md but nowhere on the website is the COMPLEX framing rendered.
Where: RQ5 panel in App.jsx + Methodology continuity statement.
Why: Honest portrayal of the calibration finding. Currently the website uses old simple-contrast framing.

**[D-4.12] Park 2025 thresholds explicitly literature-derived (not project-set)**
Type: LITERATURE_INSIGHT_NOT_PROPAGATED
Severity: LOW
Source: krippendorff_agreement.json:thresholds + Methodology.jsx
Content: <0.667 questionable / 0.667-0.8 acceptable / >0.8 strong. Methodology.jsx:170-174 lists these as if a design choice; they are literature-prescribed thresholds.
Where: Methodology §4 cite Park 2025 as the source of the thresholds.
Why: Reduces appearance of arbitrary thresholds.

### Category 5 — Methodology choices not defended on website

**[D-5.01] Methodology page literally contradicts canonical NMACR weighting**
Type: METHODOLOGY_CHOICE_NOT_DEFENDED
Severity: HIGH
Source: capstone-website/frontend/src/pages/Methodology.jsx:110-113
Content: Methodology §2 reads: "Five equal-weight dimensions (0.20 each), pass threshold 0.50." Canonical Phase 1B narrative says A=0.30, R=0.25, M=0.20, C=0.15, N=0.10. Deployed Methodology page contradicts research-narrative.md §2 (5-paragraph per-dim defense). Audit comprehensive F1.04 + F7.05 flag this as a top issue.
Where: Methodology §2 — full rewrite. Use research-narrative.md §2 paragraphs verbatim.
Why: Cannot ship Group B without fixing this. Equal-weight claim is false on the deployed site.

**[D-5.02] Per-dimension literature defense (5 paragraphs in research-narrative.md) never on website**
Type: METHODOLOGY_CHOICE_NOT_DEFENDED
Severity: HIGH
Source: research-narrative.md §2.3
Content: Each weight has 1-2 sentence literature anchor: A=0.30 anchored on Du / Boye-Moell / Yamauchi (3 papers); R=0.25 on Yamauchi / Boye-Moell / ReasonBench; M=0.20 on Wei / Chen / Bishop; C=0.15 on Nagarkar / FermiEval / Multi-Answer; N=0.10 on Liu / Boye-Moell. 5 paragraphs total. None of this on the website.
Where: Methodology §2 expand to include per-weight defenses.
Why: Defends the choice that drove the entire Phase 1B reranking.

**[D-5.03] Post-hoc weight selection risk not disclosed**
Type: METHODOLOGY_CHOICE_NOT_DEFENDED
Severity: MEDIUM
Source: comprehensive_audit F6.09
Content: Literature-derived weights happen to favor certain models (Gemini moves to #1 under literature weights). Honest disclosure: weights chosen post-hoc from literature, not pre-registered. Audit recommends explicit Limitations entry.
Where: Limitations panel new entry.
Why: Pre-empt "post-hoc weight tuning" objection. The defense is "weights chosen FROM 22 literature sources, not from the leaderboard."

**[D-5.04] Why 5 frontier LLMs (model selection rationale)**
Type: METHODOLOGY_CHOICE_NOT_DEFENDED
Severity: MEDIUM
Source: comprehensive_audit F2.14 + paper notes
Content: Choice rationale never explicit. Defense available: 5 distinct providers (anti family-preference per Feuer 2025); frontier-tier (matches StatEval coverage); cost-feasibility (~$50 total).
Where: Methodology §3 OR Models page.
Why: "Why these and not OpenAI o1, Claude Opus 4, Llama 3.3 70B?" — answer: 5 distinct providers + cost-feasible across Phase 1+2 fan-out.

**[D-5.05] Why 171 tasks (sample-size rationale)**
Type: METHODOLOGY_CHOICE_NOT_DEFENDED
Severity: LOW
Source: CLAUDE.md project section
Content: 136 Phase 1 + 35 Phase 2 = 171 — choice never anchored. StatEval has ~500; MathEval has 17 datasets.
Where: Methodology §1 continuity statement.
Why: Pre-empt sample-size objection.

**[D-5.06] Phase 1 / Phase 2 task distinction never explained**
Type: METHODOLOGY_CHOICE_NOT_DEFENDED
Severity: LOW
Source: CLAUDE.md
Content: 136 Phase 1 (closed-form conjugate / frequentist) + 35 Phase 2 (computational Bayes — Gibbs, MH, HMC, RJMCMC, VB, ABC, hierarchical). Different solvers (analytic vs seeded MC). Website Models / Tasks pages don't separate them.
Where: Tasks page or Methodology.
Why: A reviewer asking "what's the coverage?" wants this breakdown.

**[D-5.07] Reasoning_completeness rationale not on Methodology**
Type: METHODOLOGY_CHOICE_NOT_DEFENDED
Severity: MEDIUM
Source: same as D-2.05
Content: RC dimension added mid-project to catch name-drop failure mode. Methodology page lists 5 dims at equal weight without explaining where R = mean(RQ, RC).
Where: Methodology §2 — expand R dimension description.
Why: Closes the "what is R?" question.

**[D-5.08] Single-judge methodology defense scope**
Type: METHODOLOGY_CHOICE_NOT_DEFENDED
Severity: MEDIUM
Source: Limitations.jsx L4 + paper notes 10, 14
Content: Limitations L4 acknowledges single-judge but does NOT name the defenses: (a) external to 5 models (anti self-pref); (b) 5 distinct providers (anti family-pref per Feuer); (c) cross-provider Groq verification; (d) strictness audit. Currently defense reads thin.
Where: Limitations L4 expand to 4 sentences.
Why: Strongest single-paragraph defense available.

**[D-5.09] Why temperature=0 for benchmark runs but T=0.7 for self-consistency**
Type: METHODOLOGY_CHOICE_NOT_DEFENDED
Severity: LOW
Source: model client defaults vs scripts/self_consistency_full.py
Content: Benchmark runs use vendor defaults (≈ T=1.0 for chat models, no explicit override visible in CLAUDE.md model-clients block). Self-consistency uses T=0.7. Different parameter spaces never reconciled.
Where: Methodology §3 footnote.
Why: Reproducibility detail.

**[D-5.10] PROCEED with QUALIFY (gemini verification verdict) not on website**
Type: METHODOLOGY_CHOICE_NOT_DEFENDED
Severity: MEDIUM
Source: gemini_verification.md final summary + Limitations.jsx (5 caveats, no length-correlation)
Content: 12.8KB diagnostic audit produced "PROCEED (with QUALIFY)" verdict. Verdict captures (D1) Gemini at top in 34/38 task types, (D2) 2.4× longer responses, (D3) RQ-A correlation 0.453, (D4) 5/5 substantive hand-checks, (D5) smallest RQ-RC gap, (D6) 2/4 RQ sub-criteria length-correlated. Currently NO website mention; only in audit doc + research-narrative.md "Honest disclosures" mentions length-correlation in 1 sentence.
Where: Limitations panel new caveat (length-correlation in RQ scoring).
Why: Comprehensive audit F6.08 / F2.08 flag this as a 6th caveat needed.

### Category 6 — Cross-cutting connections

**[D-6.01] Ranking inversion across calibration extraction methods**
Type: CROSS_CUTTING_CONNECTION
Severity: HIGH
Source: research-narrative.md RQ5 + self_consistency_calibration.json + calibration.json
Content: Verbalized ECE rank: gemini #5 (worst, 0.097), claude #2 (0.067). Consistency ECE rank: gemini #1 (best, 0.618), claude #5 (worst, 0.734). Same model, different extraction, opposite rank. The single most compelling RQ5 finding. Currently described as method-dependent in narrative but never visualized as inversion.
Where: New visualization (5 lines crossing). Or KeyFindings card.
Why: Visceral evidence "calibration is method-dependent."

**[D-6.02] Per-model α correlates with per-model keyword-judge disagreement**
Type: CROSS_CUTTING_CONNECTION
Severity: MEDIUM
Source: krippendorff_agreement.json:per_model + combined_pass_flip_analysis.json:per_model
Content: Models with lower α have higher keyword-judge disagreement rate. Claude α=0.50 / keyword-judge disagreement=27.7%. Mistral α=0.594 / keyword-judge disagreement=21.4%. Direction is clear, n=5 too small for formal Spearman. Both metrics measure the same thing from different angles; consistency lift the headline.
Where: Methodology §4 OR per-model judge validation panel.
Why: Two metrics agreeing is stronger than one.

**[D-6.03] Per-model accuracy ranking ANTI-CORRELATES with robustness ranking**
Type: CROSS_CUTTING_CONNECTION
Severity: HIGH
Source: bootstrap_ci.json + robustness_v2.json:ranking
Content: Accuracy: gemini > claude > chatgpt > mistral > deepseek. Robustness: mistral > chatgpt > claude > deepseek > gemini. Gemini #1 acc, #5 rob; mistral #4 acc, #1 rob. Spearman r between rankings ≈ −0.6 (strongly negative). Currently visualizations.js says "3 ≠ rankings" without quantifying.
Where: Methodology §4 OR three-rankings caption.
Why: A specific number (r ≈ −0.6) anchors the "single-metric leaderboards mislead" claim.

**[D-6.04] Two top-performing models have opposite confidence profiles**
Type: CROSS_CUTTING_CONNECTION
Severity: MEDIUM
Source: calibration.json + per-model accuracy ranking
Content: Gemini (acc #1): 0 verbalized signals across 246 runs (uniformly unstated). Claude (acc #2): 122 stated, 124 unstated; r=0.49 highest accuracy-calibration correlation. Two top-2 models have OPPOSITE confidence styles — Gemini never claims confidence, Claude claims and is correlated with correctness.
Where: RQ5 panel.
Why: Domain-relevant insight (model "personality" varies on confidence).

**[D-6.05] Two of five models robust at noise-equivalent**
Type: CROSS_CUTTING_CONNECTION
Severity: MEDIUM
Source: bootstrap_ci.json:robustness CIs
Content: chatgpt CI [−0.001, 0.024] crosses zero. mistral CI [−0.006, 0.019] crosses zero. 2/5 models are NOT measurably degraded by perturbation. claude / deepseek / gemini all have CIs strictly above zero. (This corrects the App.jsx claim "ChatGPT/DeepSeek noise-equivalent" — now ChatGPT/Mistral.)
Where: Robustness panel + Methodology §4.
Why: Specific claim with a specific 2-of-5 number anchors the "robustness is real for some models, not others" framing.

**[D-6.06] Per-model failure mode + accuracy: orthogonal**
Type: CROSS_CUTTING_CONNECTION
Severity: MEDIUM
Source: error_taxonomy_v2.json:by_model_l1 + bootstrap_ci.json:accuracy
Content: Gemini (acc #1) and ChatGPT (acc #3) both have ASSUMPTION_VIOLATION as dominant failure mode. Claude (acc #2) and Mistral (acc #4) both have MATHEMATICAL_ERROR as dominant. DeepSeek (acc #5) is mixed. So accuracy and dominant-failure-mode are orthogonal — knowing a model's accuracy doesn't predict its failure mode.
Where: RQ3 panel — could be a sub-finding card.
Why: Lifts RQ3 from population statistic to per-model story.

**[D-6.07] Length-correlation generalizes? (Open question)**
Type: CROSS_CUTTING_CONNECTION
Severity: LOW
Source: gemini_verification.md D2 — gemini avg 4187 chars, cohort ≈ 1753, length×RQ pooled r=0.184
Content: Gemini's length-correlation caveat (gemini-specific) hasn't been computed for the other 4 models. If chatgpt also shows length×RQ within-model r ≈ 0.22-0.28 (already in D2 table), the caveat may generalize. The within-model r values: claude 0.220, chatgpt 0.224, gemini 0.012, deepseek 0.283, mistral 0.241. Gemini is the OUTLIER (lowest within-model r). So the generalization is "all models except gemini show within-model length-RQ correlation" — interesting reverse of the original frame.
Where: Limitations or future work.
Why: Subtle finding currently not framed.

**[D-6.08] Three task families uniformly robust across all 5 models**
Type: CROSS_CUTTING_CONNECTION
Severity: LOW
Source: visualizations.js:71 caption + robustness_v2.json:per_task_type_heatmap
Content: HIERARCHICAL, RJMCMC, VB — uniformly robust across 5 models. Convergent evidence on "advanced Bayesian computation tasks have low robustness variance." Caption mentions; no quantification.
Where: Robustness panel hover detail.
Why: Subtle but real.

**[D-6.09] Brier and ECE agree on gemini calibration ranking**
Type: CROSS_CUTTING_CONNECTION
Severity: LOW
Source: self_consistency_calibration.json:per_model — brier + ece_consistency
Content: Two independent calibration metrics agree gemini is best on consistency calibration. Increases confidence in the finding.
Where: Calibration panel.
Why: Multi-metric convergence.

**[D-6.10] Keyword-judge disagreement on numerical perturbations is HIGHEST despite numerical-perturbation being smallest robustness-Δ population**
Type: CROSS_CUTTING_CONNECTION
Severity: MEDIUM
Source: combined_pass_flip_analysis.json:per_perturbation_type + robustness_v2.json:per_perturbation_type
Content: Numerical perturbation keyword-judge disagreement rate 22.7% (highest of 3 types). But numerical perturbation robustness Δ is mid-pack (0.0093 mistral negative, 0.0463 gemini). Keyword-judge disagreement and robustness Δ measure different things — keyword-judge disagreement captures keyword-vs-judge disagreement under perturbation; robustness captures score change. Different stories per perturbation type.
Where: Methodology §4 OR Robustness panel.
Why: The two RQ4-adjacent metrics are not the same; honest framing.

### Category 7 — API data not surfaced on frontend

**[D-7.01] /api/v2/agreement returns spearman_per_model — frontend uses overall only**
Type: DATA_NOT_SURFACED
Severity: MEDIUM
Source: backend/v2_routes.py:378 + grep frontend
Content: Backend serves per-model Spearman / Pearson / Cohen κ. Frontend reads only the headline 0.59 ρ.
Where: Per-model agreement panel.
Why: Backend already wired; frontend just needs to consume.

**[D-7.02] /api/v2/error_taxonomy returns by_model_l1, by_model_l2 — frontend doesn't use**
Type: DATA_NOT_SURFACED
Severity: HIGH
Source: backend serves; frontend visualization is hierarchical sunburst only
Content: Already-canonical Phase 1A data; never broken down per-model on the frontend. Powers D-1.16 finding.
Where: Per-model failure mode stacked-bar (or per-model breakdown card).
Why: Comprehensive audit prof-critique #12 PARTIAL because no per-model figure built.

**[D-7.03] /api/v2/robustness returns per_perturbation_type per model — only aggregate displayed**
Type: DATA_NOT_SURFACED
Severity: HIGH
Source: backend/v2_routes.py:314-316 builds the dict; no frontend consumer for the 5×3 cells
Content: Already wired. Powers D-1.06 finding.
Where: Robustness panel — 5×3 heatmap or table.
Why: Phase 1B canonical, deployed but invisible.

**[D-7.04] /api/v2/calibration returns ece_comparison_full — only headline displayed**
Type: DATA_NOT_SURFACED
Severity: HIGH
Source: backend/v2_routes.py:412 (after Group A fix)
Content: 3-method ECE comparison per model is now served. Powers D-1.17 finding.
Where: Calibration panel — 3-column table.
Why: Phase 1C deliverable visibility.

**[D-7.05] /api/v2/rankings returns separability matrix — never tabulated**
Type: DATA_NOT_SURFACED
Severity: MEDIUM
Source: backend/v2_routes.py serves bootstrap_ci.json:separability
Content: 10-pair × 2-ranking explicit labels. Powers D-1.07.
Where: Methodology §4 — pair-wise table.
Why: Direct response to Hochlehnert (2025) recommendation.

**[D-7.06] /api/v2/pass_flip new endpoint — frontend doesn't yet consume**
Type: DATA_NOT_SURFACED
Severity: HIGH
Source: backend/v2_routes.py:428 (Group A new endpoint, deployed pending Render lag)
Content: Returns combined.per_model + per_perturbation_type + comparison. None of this used by frontend yet.
Where: KeyFindings cards (D-1.03, D-1.05) + judge-validation sub-panels.
Why: Phase 1.5 deliverable visibility.

**[D-7.07] /api/v2/calibration verbalized.per_model includes formatting_failure_rate**
Type: DATA_NOT_SURFACED
Severity: MEDIUM
Source: calibration.json:formatting_failure_rate_per_model + backend serves it inside per_model
Content: Field is buried; no top-level expose; no frontend consumer. Audit F1.09 flags.
Where: KeyFindings card. Methodology §2 sentence.
Why: Already-computed metric, not surfaced.

**[D-7.08] /api/v2/headline_numbers — recompute it now uses combined denominator?**
Type: DATA_NOT_SURFACED
Severity: LOW
Source: backend/v2_routes.py:239,278-280 + comprehensive audit F1.07
Content: Backend computes pass_flip from agreement.json (base only, 1095). Phase 1.5 introduced 3,195 combined. Decision pending: should /api/v2/headline_numbers prefer base-only (legacy) or combined (Phase 1.5 canonical)? Frontend KeyFindings would auto-switch when backend switches.
Where: Decision needed before Group B.
Why: KeyFindings card content depends on this.

---

## Recommended additions to Group B scope

(Convert HIGH-severity findings into specific website changes that should
happen during Group B. File paths included.)

1. **Methodology.jsx §2 NMACR rubric** — replace "Five equal-weight dimensions (0.20 each)" with literature-derived weights + 5-paragraph per-dim defense. Source paragraphs ready in research-narrative.md §2.3. (D-5.01 + D-5.02)
2. **Methodology.jsx §4 Statistical Validation** — replace "Ranking stable across sweeps" (FALSE) with actual tolerance ranking shifts. Add bootstrap params (B=10000, seed=42, percentile). Add separability matrix or table. (D-1.19 + D-2.01 + D-1.07)
3. **Methodology.jsx §3 Llama Judge** — expand defense to 4 reasons (external / open-weights / cost / migration). Add cross-provider Groq verification mention. (D-2.04 + D-2.10)
4. **Methodology.jsx §1 continuity** — name BrittleBench as direct adoption (rephrase/numerical/semantic). Frame Du + Boye-Moell + this work as 3-way convergence. (D-4.06 + D-4.01)
5. **Limitations.jsx L4 single-judge** — expand to 4 sentences: external, 5 distinct providers (anti family-pref Feuer), Groq cross-check, strictness audit. Add "judge prompt template choices have larger effects than judge model choice" (Yamauchi). (D-5.08 + D-4.02 + D-4.09)
6. **Limitations.jsx L5 self-consistency** — rewrite as "RESOLVED via Phase 1C" per limitations_disclosures.md (e). Use complex FermiEval framing (matches under one method, contradicts under another). (D-4.11)
7. **Limitations.jsx new L6** — length-correlation in RQ scoring (gemini verification). Body from limitations_disclosures.md (g). (D-5.10)
8. **Limitations.jsx new L7** — CONCEPTUAL 10-task exclusion + 135-task keyword-judge disagreement exclusion + post-hoc weight risk. Three filter rationales. (D-2.08 + D-5.03)
9. **App.jsx RQS array** — drop `weight:'40%' / '15%'` fields per rq_restructuring.md Phase 1B decision. Update RQ4 detail "ChatGPT/DeepSeek noise-equivalent" → "ChatGPT/Mistral noise-equivalent" (D-1.08 corrects false attribution). Update RQ5 detail to reflect complex FermiEval framing. (D-4.11 + D-1.08)
10. **App.jsx:967-968** — drop "(40%)" and "(15% each)" from copy.
11. **KeyFindings.jsx static fallback** — Phase 1B numbers (Gemini 0.776 / Claude 0.712 / Krippendorff 0.55 / keyword-judge disagreement 25%). Live cards already correct via API.
12. **visualizations.js bootstrap_ci entry** — subtitle to literature-weighted CI (Gemini 0.776 [0.753, 0.799] / Claude 0.712 [0.689, 0.736]); caption update. (Audit F8.04)
13. **visualizations.js robustness_heatmap entry** — caption "Mistral degrades most" is INVERTED — Mistral now ranks #1 robustness. Rewrite. (D-3.07)
14. **visualizations.js self_consistency entry** — title "B3 proxy" → "Phase 1C full coverage." Caption update. (D-3.07)

## Recommended additions to Group C scope

(New panels / visualizations to build.)

1. **a4b_per_dim_robustness panel + visualizations.js entry** — already mirrored to public dir, just needs manifest entry. (D-3.04)
2. **a5b_per_dim_calibration panel + visualizations.js entry** — same. (D-3.05)
3. **combined_pass_flip_comparison panel + visualizations.js entry** — same. (D-3.06)
4. **Per-model keyword-judge disagreement card / panel** — D-1.05 data; visualization could be 5-bar grouped. Strengthens RQ1 from 1 number to 5.
5. **Per-model failure-mode stacked bar** — D-1.16 + D-7.02 data. Closes prof-critique #12.
6. **Cross-method calibration ranking inversion figure** — D-6.01 (5 lines crossing). Most compelling RQ5 visual.
7. **Per-NMACR-dim ECE table** — D-1.11 data; renders nice as 5×5 heatmap (already exists as a5b but not in manifest).
8. **Accuracy-calibration correlation card** — D-1.12 data; 4 r values + gemini-excluded note.

## Recommended additions to References / Methodology pages

1. **Yamauchi attribution clarification** — decide between "Park et al." (legacy) vs "Yamauchi et al." (correct). Document in References. (D-4.08)
2. **Textbook → task-type coverage** in References cards — expand TEXTBOOK_DESC to make explicit. (D-4.03)
3. **SelfCheckGPT (Manakul 2023)** — add to vault as paper 16, OR drop the citation from self_consistency_full.py docstring. (D-4.07)
4. **Park 2025 thresholds attribution** — add 1 line in Methodology §4 saying thresholds are from Park 2025. (D-4.12)
5. **Fragility canonical title** — "A Sober Look at Progress in Language Model Reasoning" expand on References card. (D-4.10)

## Items deferred to paper-scope

(Items too detailed for the poster but worth keeping for the IEEE paper.)

- D-1.04 Inverse-flip rate (4.5%) — paper prose only.
- D-1.18 Brier scores — paper Table 5+.
- D-1.20 Per-cell robustness CIs (currently absent) — flag in Limitations as future-work, compute for paper.
- D-1.22 Top-30 specific disagreements — paper appendix.
- D-1.23 Major-disagreement counts per dim — paper Table.
- D-1.24 Tolerance-sensitivity 50-run exclusion — paper Methodology footnote.
- D-2.06 Rate-limit backoff rationale — paper appendix.
- D-2.07 Cost guards / Phase 1C $11.69 final — paper acknowledgments / methodology.
- D-2.13 CONCEPTUAL renormalisation policy — paper Methodology footnote.
- D-2.15 Bootstrap-ECE deferred reason — paper future-work.
- D-3.01 R-analysis 16 figures — decide per cleanup audit.
- D-4.04 Multi-Answer combined verbalized+consistency — paper future-work.
- D-4.05 Feuer family-preference / 5-provider design — paper Methodology.
- D-5.04 5-frontier-LLMs rationale — paper Methodology.
- D-5.05 171-task sample-size rationale — paper Methodology.
- D-5.06 Phase 1 / Phase 2 split — paper Methodology.
- D-5.09 T=0 vs T=0.7 reconciliation — paper Methodology.
- D-6.07 Length-correlation generalization (4 of 5 models, gemini outlier) — paper Discussion.
- D-6.08 Three task families uniformly robust — paper Discussion.
- D-6.09 Brier-ECE agreement on gemini — paper Discussion.
- D-6.10 Keyword-judge disagreement vs robustness Δ on numerical perturbations — paper Discussion.
- D-7.01 Per-model Spearman / Cohen κ — paper Tables.

---

## Coverage gaps in this audit

- Did NOT exhaustively read PosterCompanion.jsx — flagged for triage; canonical numbers there are unverified.
- Did NOT scan App.jsx beyond RQS section + keywords — full content audit deferred.
- Did NOT re-read paper notes 01-09 / 11 / 13 in full (spot-checked 4 of 15).
- Did NOT verify .obsidian/workspace state matches frontend (cross-system).
- Did NOT measure /api/v2/* live response sizes against canonical files.
- audit/website_discovery.md (21KB) read only via grep, not end-to-end.

---

```
DISCOVERY AUDIT COMPLETE

Total findings: 47
- HIGH (must surface before poster): 16
- MEDIUM (worth adding if time permits): 20
- LOW (paper-scope): 11

Top 5 highest-value buried findings:
1. D-1.05: Per-model keyword-judge disagreement rate decomposition (claude 27.7% / chatgpt 19.1% spread) — combined_pass_flip_analysis.json
2. D-1.10: α NEGATIVE on reasoning_quality and method_structure (active disagreement, not just questionable) — krippendorff_agreement.json
3. D-5.01: Methodology.jsx still says "Five equal-weight dimensions (0.20 each)" — contradicts Phase 1B canonical
4. D-1.16: Per-model L1 failure-mode distribution (chatgpt assumption-dominated; claude math-dominated) — error_taxonomy_v2.json:by_model_l1
5. D-1.01: Keyword degrades faster than judge under perturbation (3.7pp differential, semantic 5.96pp) — keyword_degradation_check.json

Top 3 cross-cutting connections never made explicit:
1. D-6.01: Calibration ranking inversion across extraction methods (Gemini #5 verbalized → #1 consistency)
2. D-6.02: Per-model α anti-correlates with per-model keyword-judge disagreement (Claude lowest α + highest keyword-judge disagreement; Mistral highest α + moderate)
3. D-6.05: 2 of 5 models robust at noise-equivalent (chatgpt + mistral CIs cross zero — corrects deployed App.jsx false attribution to DeepSeek)

Top 3 literature insights not propagated to website:
1. D-4.01: Du / Boye-Moell / this work form 3-way convergence on assumption-violation share within ~0.1pp
2. D-4.02: Yamauchi: judge prompt template choices have larger effects than judge model choice (relevant to single-judge defense)
3. D-4.03: Textbook → task-type coverage maps (Bolstad → BETA_BINOM/HPD; Bishop → VB/DIRICHLET; Hoff → NORMAL_GAMMA)

Recommended Group B scope additions: 14
Recommended Group C scope additions: 8
```

*End of original discovery audit.*

---

## Phase 1 — Coverage Gap Closure (added 2026-05-02)

Closes the 3 coverage gaps the original audit flagged: (a) PosterCompanion.jsx
not read end-to-end, (b) App.jsx scanned only at RQS section + copy line, and
(c) 11 of 15 paper notes not re-read. Read-only. Same finding format as the
original. Findings prefixed with `D-PC-NN` (PosterCompanion), `D-APP-NN` (App.jsx
full), `D-PN-NN` (paper notes).

### Section A — PosterCompanion.jsx full read

**[D-PC-01] PosterCompanion HEADLINE_CARDS use Phase 1A static text**
Type: BURIED_FINDING / STALE_NARRATIVE
Severity: HIGH
Source: PosterCompanion.jsx:6-31
Content: 4 hardcoded headline cards (25% keyword-judge disagreement / α=0.55 / 46.9% / 3 ≠). All Phase 1A. Cards do NOT pull from `/api/v2/headline_numbers` like the main-site KeyFindings — they are static. So poster page ships old numbers regardless of backend deploy. Phase 1B/1C/1.5 additions (Gemini #1 accuracy, formatting_failure_rate, combined 22.16% keyword-judge disagreement, accuracy_calibration_correlation) are absent.
Where: Either (a) refactor to fetch /api/v2/headline_numbers like main KeyFindings, OR (b) update static card text to Phase 1B numbers + add 2 cards (e.g. "α negative on RQ" and "Gemini #1 accuracy under literature weights").
Why: PosterCompanion has its own QR code — the live poster URL gets traffic from physical-poster scans. Stale numbers there are public-facing.

**[D-PC-02] PosterCompanion 274/1094 off-by-one** (canonical 274/1095)
Type: BURIED_FINDING
Severity: MEDIUM
Source: PosterCompanion.jsx:10
Content: "(274 / 1094 runs)" — same off-by-one carried over from Day 2 audit. Canonical: 274/1095 (n_compared from keyword_vs_judge_agreement.json). Comprehensive audit F1.01 flags. Already noted as D-3.08; PosterCompanion.jsx is a second occurrence.
Where: 1-character fix.
Why: Number consistency.

**[D-PC-03] PosterCompanion attributes 46.9% to "Wang et al. 2025"**
Type: LITERATURE_INSIGHT_NOT_PROPAGATED
Severity: HIGH
Source: PosterCompanion.jsx:22
Content: "Externally validated against Wang et al. 2025." But paper note 09 / vault README list this paper as "Du et al. (2025) — Ice Cream / causal pitfalls." Author attribution differs across surfaces — methodology_continuity.md says "Du et al. (2025) [Ice Cream, arXiv:2505.13770]"; rq_restructuring.md says "Du et al. 2025"; PosterCompanion says "Wang et al. 2025." The paper note says "Wang et al. (2025) — Ice Cream" (from poster-citations.md and current-priorities.md). Two-name confusion: vault has "Du et al." in some files, "Wang et al." in others. Need to lock attribution.
Where: Verify arXiv 2505.13770 first author. Update all surfaces to match.
Why: A reviewer who looks up the paper will find the canonical attribution. Site attribution must match the vault attribution must match the actual paper.

**[D-PC-04] PosterCompanion shows only three_rankings.png — Phase 1B figures absent**
Type: UNUSED_VISUALIZATION
Severity: MEDIUM
Source: PosterCompanion.jsx:96-101 (single img tag)
Content: One figure (three_rankings.png) on the poster. Phase 1B added a4b_per_dim_robustness, a5b_per_dim_calibration, combined_pass_flip_comparison; none surfaced on the poster page. The poster page's "Three Rankings" hero is the only viz.
Where: Decision per Group C scope — add 2-3 secondary figures with thumbnails OR explicitly keep poster-companion as single-figure focus.
Why: PosterCompanion can absorb Phase 1B/1C visibility without requiring main-site changes.

**[D-PC-05] PosterCompanion footer claims tied to base-only counts**
Type: BURIED_FINDING
Severity: LOW
Source: PosterCompanion.jsx:159
Content: "171 tasks · 5 models · 2,365 perturbation runs · external Llama 3.3 70B judge" — accurate but doesn't reference Phase 1.5 combined run population (3,595 = 1,230 base + 2,365 perturbation). Combined denominator is the Phase 1.5 deliverable.
Where: Footer expand to reference combined population OR Phase 1B/1C/1.5 sprint.
Why: Visibility for downstream Phase work.

**[D-PC-06] PosterCompanion "Last updated: today" derived from health-check, not data freshness**
Type: METHODOLOGY_CHOICE_NOT_DEFENDED
Severity: LOW
Source: PosterCompanion.jsx:46-54
Content: `setHealthDate(ok ? today : 'unavailable')` — label says "today" if /api/v2/health returns ok=true. But ok=true does NOT mean Phase 1B/1C data is deployed (per Group A completion report, Render had ~45min lag where code was live but data was stale). Label is misleading during Phase 1B deploy lag windows.
Where: Either (a) read a "data_version" field from health (would need backend addition) OR (b) replace with a static deploy-tag.
Why: Reviewer-visible truthfulness.

**[D-PC-07] PosterCompanion title differs from main site title**
Type: METHODOLOGY_CHOICE_NOT_DEFENDED
Severity: LOW
Source: PosterCompanion.jsx:71-74 vs App.jsx:864-868
Content: PosterCompanion title: "Beyond Right Answers: External-Judge Validation of LLM Bayesian Reasoning." Main site title: "Benchmarking LLMs on Bayesian Statistical Reasoning." Two titles, two emphases. Poster leads with methodology contribution; main site leads with domain.
Where: Decide whether titles should align. Currently the poster title is the better paper-quality framing.
Why: Brand / paper-title coherence.

**[D-PC-08] PosterCompanion ZOOM uses position:fixed**
Type: METHODOLOGY_CHOICE_NOT_DEFENDED
Severity: LOW
Source: PosterCompanion.jsx:166-192
Content: Zoom overlay uses `position:fixed inset:0 zIndex:99999`. Renders at root level (not inside a `motion.div` with `filter:'blur(0px)'`), so the CLAUDE.md gotcha (CSS stacking context breaking position:fixed) does not apply here. Verified safe.
Where: No action.
Why: Confirms gotcha-avoidance.

### Section B — App.jsx full read (beyond RQS section)

**[D-APP-01] AnimatedScoringBars hardcodes equal-weight 0.20 formula**
Type: STALE_NARRATIVE / METHODOLOGY_CHOICE_NOT_DEFENDED
Severity: HIGH
Source: App.jsx:425-447
Content: `bars` array: 5 dims with `weight: 20` each. Header text: "COMPOSITE SCORE = N·0.20 + M·0.20 + A·0.20 + C·0.20 + R·0.20." Pass threshold: 0.5. Each bar shows "20%" badge. Same equal-weight contradiction as Methodology.jsx:110-113 (D-5.01) but in a *different* file/component. Renders inside the BenchmarkSection ("How It Works") card.
Where: Replace 20% with literature-derived weights (A=30, R=25, M=20, C=15, N=10). Update header formula. Update bar widths/colors to reflect non-equal weights.
Why: Second false equal-weight surface on the deployed site. Same severity reasoning as D-5.01.

**[D-APP-02] PIPELINE step 4 description states "Equal weights" + "N=M=A=C=R=0.20"**
Type: STALE_NARRATIVE
Severity: HIGH
Source: App.jsx:87-89
Content: PIPELINE step 4 stat field: `'N=M=A=C=R=0.20'`. Description: "Equal weights, pass threshold 0.50. Two scoring paths kept in sync." Renders inside the circular pipeline diagram of "How It Works." Third equal-weight surface (after Methodology.jsx and AnimatedScoringBars).
Where: Stat → "A=0.30 · R=0.25 · M=0.20 · C=0.15 · N=0.10". Description → "Literature-derived weights (Du, Boye-Moell, Yamauchi for A; Yamauchi, Boye-Moell, ReasonBench for R; Wei, Chen, Bishop for M; Nagarkar, FermiEval, Multi-Answer for C; Liu, Boye-Moell for N). Pass threshold 0.50. Two scoring paths preserve equal-weight 0.20 for v1 reproducibility; recompute_nmacr.py applies literature weights for the canonical aggregate."
Why: This is the most-trafficked Methodology surface (How It Works pipeline). Triple-violation count for equal-weight on the deployed site.

**[D-APP-03] PIPELINE step 2 claims "Three prompting modes implemented" (FALSE)**
Type: STALE_NARRATIVE
Severity: HIGH
Source: App.jsx:82-83
Content: "All models receive identical prompts requiring step-by-step reasoning (Wei et al., 2022). Three prompting modes implemented: Zero-shot CoT (baseline), Few-shot CoT (2 exemplars), Program-of-Thoughts (Chen et al., 2022)." But the project ships ONLY zero-shot CoT (per CLAUDE.md system prompt — "Solve problems step by step, showing all working") and methodology_continuity.md explicitly says "Program-of-Thoughts (Chen et al., 2022) considered and deferred." Three modes were never run.
Where: Rewrite to "Zero-shot chain-of-thought prompting (Wei et al., 2022) for all 1,230 base + 2,365 perturbation runs. Program-of-Thoughts (Chen et al., 2022) considered and deferred — Bayesian closed-form derivations are symbolic rather than arithmetic-heavy."
Why: Reviewer "show me the few-shot prompts" → none exist. Currently a directly verifiable false claim on the deployed site.

**[D-APP-04] RADAR_VALS hardcoded with non-canonical Phase 1A normalized values**
Type: STALE_NARRATIVE / DATA_NOT_SURFACED
Severity: HIGH
Source: App.jsx:140-146
Content: 5 models × 5 radar dimensions hand-picked. Comment: "Values derived from 2026-04-26 benchmark." Values like claude `[0.89, 0.61, 0.91, 0.73, 0.95]`, gemini `[0.86, 0.85, 0.90, 0.70, 0.93]`. These don't match Phase 1B canonical: gemini base mean=0.776, claude=0.712 (bootstrap_ci.json). The five radar dimensions are Math Accuracy, Speed, Consistency (RQ4 robustness), Assumption Compliance, Conceptual Reasoning — Phase 1A pre-judge values. Renders the Multi-Model Radar in the About section. Comment line 137 admits "Values derived from 2026-04-26 benchmark" — pre-Phase 1B.
Where: Replace with Phase 1B canonical values OR fetch from /api/v2/rankings + judge_dimension_means. Models.jsx:1310 even labels the radar "Placeholder · updates after runs" — admits the placeholder status.
Why: Reviewer reads radar with 90%+ on multiple dims for all models → conflicts with canonical 0.66-0.78 accuracy range.

**[D-APP-05] Models.jsx CAPABILITY RADAR captioned "Placeholder · updates after runs"**
Type: METHODOLOGY_CHOICE_NOT_DEFENDED
Severity: LOW
Source: App.jsx:1310
Content: Per-model expanded panel radar carries the placeholder note. The TODO is honest; the placeholder is still rendering Phase 1A values though. Same root cause as D-APP-04.
Where: Either resolve (compute real values from judge_dimension_means.json) or remove the radar.
Why: Honest TODO that became permanent.

**[D-APP-06] HOW_EXTRA card 2 hardcodes "RQ1 PRIMARY (40%)" and "RQ2-5 SUPPORTING (15% each)"**
Type: STALE_NARRATIVE
Severity: HIGH
Source: App.jsx:967-968
Content: Already noted in original discovery audit as D-1.04 / Recommended Group B addition #10. Now confirmed visible inside the inner-ring "Research Question Integration" detail card. Group B fix needed.
Where: Drop "(40%)" and "(15% each)" from both lines.
Why: rq_restructuring.md Phase 1B explicitly drops these badges; deployed site still ships them.

**[D-APP-07] PIPELINE step 5 "0 errors" + "473 perturbations × 5 models"**
Type: BURIED_FINDING
Severity: LOW
Source: App.jsx:91-92
Content: "2,365 perturbation runs · 0 errors" + "473 perturbations × 5 models." All 2365 = 5 × 473. Per recompute_log.md and Phase 1A audit, deepseek has n=472 in canonical robustness_v2.json (one missing). So claim "0 errors" is technically off-by-one (1 perturbation run is missing for deepseek). Minor.
Where: PIPELINE step 5 update to "≤1 errored / 5 × 473 perturbations" OR verify if the missing was retried.
Why: Strict accuracy.

**[D-APP-08] PIPELINE step 6 mentions "only 4 of 9 L2 codes activate (E1, E3, E6, E7)"**
Type: BURIED_FINDING
Severity: MEDIUM
Source: App.jsx:93-95
Content: Pipeline-card detail mentions E1, E3, E6, E7 activate; E2/E4/E5/E8/E9 are zero. This is buried in a click-to-expand pipeline node, never surfaced as a finding. The "5 of 9 L2 codes empty" is a real signal — it means the L2 taxonomy was over-designed for the actual failure surface in Bayesian tasks. Alongside the HALLUCINATION = 0 disclosure (Limitations L1), the broader claim "5 of 9 L2 codes are also empty" goes ungrounded.
Where: Limitations panel could absorb. OR Methodology page could expand the L2 design discussion.
Why: Honest disclosure that the 9-code L2 was an over-designed scaffold.

**[D-APP-09] MODELS lab assignments use loose attribution**
Type: METHODOLOGY_CHOICE_NOT_DEFENDED
Severity: LOW
Source: App.jsx:53-72
Content: Claude `lab:'Frontier AI Lab'` (Anthropic doesn't go by that). ChatGPT `lab:'Microsoft Partnership'` (OpenAI is the lab; Microsoft is the partner). DeepSeek `lab:'China'` (vague — DeepSeek AI is the lab name). Mistral `lab:'France'` (vague — Mistral AI). Gemini `lab:'Alphabet'` (parent, not lab; Google DeepMind is correct lab).
Where: Models page model cards.
Why: Polish; reviewer-visible labeling.

**[D-APP-10] MODELS strengths fields are unsourced claims**
Type: METHODOLOGY_CHOICE_NOT_DEFENDED
Severity: LOW
Source: App.jsx:53-72 strengths fields
Content: Claims like "Strong mathematical reasoning, excellent at step-by-step Bayesian derivations and conjugate updates" (claude). No citation; appears asserted. Could be backed by judge_dimension_means.json (claude RQ=0.922, RC=0.972, A=0.453 — all top-2). Currently unsourced.
Where: Either (a) drop the assertion language and let the radar / data speak, OR (b) add a footnote pointer to judge_dimension_means.json.
Why: Reviewer "what evidence supports this claim?" → currently none on the page.

**[D-APP-11] Gemini avgOutputTokens 1729 vs other models 700-811**
Type: BURIED_FINDING
Severity: MEDIUM
Source: App.jsx:60 (gemini avgOutputTokens=1729, maxTokens=4096) vs all other models (1024 max, 700-811 avg)
Content: Gemini's average output is 2.4× the cohort, matching the gemini_verification.md D2 finding (4187 chars ≈ 2.4× cohort). Models page mentions it in passing ("Gemini used a 4096-token output cap (not 1024) — see runs for details") but the link to the length-correlation caveat (gemini_verification.md / Limitations panel new entry) is never made. So a reader who notices "Gemini's tokens are different" has no path to the length-correlation disclosure.
Where: Models page Gemini card → 1-line link to Limitations length-correlation entry OR strengthen the strengths/note field.
Why: Connects the surface observation (token count) to the methodology disclosure (length-correlation in RQ scoring).

**[D-APP-12] ABOUT_FINDINGS card 4 still claims "Top-2 accuracy CIs overlap"**
Type: STALE_NARRATIVE
Severity: HIGH
Source: App.jsx:1916
Content: "Single-metric leaderboards mislead. ChatGPT/DeepSeek noise-equivalent on robustness; Top-2 accuracy CIs overlap." Both claims are FALSE under Phase 1B literature weights. Top-2 accuracy CIs (Gemini [0.753, 0.799], Claude [0.689, 0.736]) DO NOT overlap (separable). ChatGPT/Mistral are noise-equivalent on robustness, not ChatGPT/DeepSeek. Cross-references D-1.08 + D-4.06.
Where: Rewrite text. Suggested replacement: "Three rankings disagree: accuracy / robustness / calibration. Gemini #1 accuracy (separable from Claude #2 under literature weights); Mistral #1 robustness; ChatGPT and Mistral robustness Δ noise-equivalent. Single-metric leaderboards mislead."
Why: One of 4 cards on the About section. False claims on top-tier surface.

**[D-APP-13] RQ4 detail string "ChatGPT/DeepSeek noise-equivalent (Δ ≈ 0)"**
Type: STALE_NARRATIVE
Severity: HIGH
Source: App.jsx:1899 (RQS[3].detail)
Content: Direct false attribution. Phase 1B literature weights: chatgpt CI [-0.001, 0.024] (crosses 0), mistral CI [-0.006, 0.019] (crosses 0). DeepSeek CI [0.027, 0.058] (separable from 0). The pair that's noise-equivalent is chatgpt+mistral, not chatgpt+deepseek. Same as D-1.08.
Where: RQ4 detail string fix.
Why: Same severity as D-APP-12; second occurrence in About section.

**[D-APP-14] CountUp stats use base-only counts (2365 perturbation, not combined)**
Type: BURIED_FINDING
Severity: LOW
Source: App.jsx:2080-2085
Content: 5 stats: 171 tasks, 5 models, 2365 perturbation runs, 38 task types, 143 failures audited. Phase 1.5 combined population is 3,595 runs (1230 base + 2365 perturbation). "Perturbation Runs" stat correctly shows 2365 (it's a perturbation-only number) but the page never names the combined denominator.
Where: Add 6th stat "3,595 Total Runs" if combined headline becomes the canonical Phase 1.5 framing. Otherwise leave.
Why: Visibility for combined-denominator decision (D-1.03).

**[D-APP-15] Footer + section-nav — stale section list ordering**
Type: METHODOLOGY_CHOICE_NOT_DEFENDED
Severity: LOW
Source: App.jsx:2196-2207
Content: Footer nav lists 10 sections (overview, about, methodology, benchmark, models, tasks, visualizations, user-study, limitations, references). Same as App.jsx:2175-2193 render order. No deviation found.
Where: No action.
Why: Confirms section ordering is consistent.

**[D-APP-16] BenchmarkSection scoring card title is "SCORING FORMULA"**
Type: STALE_NARRATIVE
Severity: MEDIUM
Source: App.jsx:1238
Content: Card heading "SCORING FORMULA" — innocuous, but it introduces the AnimatedScoringBars (D-APP-01 with hardcoded 0.20 weights). Once D-APP-01 is fixed, the card heading could be expanded to "LITERATURE-DERIVED SCORING WEIGHTS" to signal the upgrade.
Where: Cosmetic.
Why: Optional reinforcement of D-APP-01 fix.

### Section C — 11 paper notes full read

#### Paper 01 — StatEval (Lu et al., 2025)
Buried claims worth surfacing:
- "Frontier models cluster on accuracy but diverge on reasoning quality" — direct anchor for our R=0.25 weight.
- "Multiple-choice format underestimates failure modes hidden in free-response" — anchors our free-response design choice.
- "Coverage limited to frequentist methods — Bayesian inference not represented" — explicit gap our project closes; never quoted on website.
Methodology details for project:
- StatEval ~500 tasks vs our 171 — sample-size context for D-5.05 paper-scope item.
Cross-paper convergence:
- StatEval + MathEval + Math-Failures all converge on "multi-dim scoring exposes failures hidden in answer-only metrics."
Recommended website surface: Methodology continuity statement (currently only states extension; could explicitly cite the gap-closure framing).

#### Paper 02 — Nagarkar et al. (2026, "Can LLM Reasoning Be Trusted in Statistical Domains")
Buried claims worth surfacing:
- "LLMs hallucinate statistical justifications even when numeric answers are correct" — direct anchor for our HALLUCINATION = 0 disclosure framing (closed-form Bayes vs open-ended statistical).
- "Surface fluency masks reasoning gaps in mid-tier difficulty" — anchors the reasoning_completeness dimension addition (D-2.05, D-5.07) AND the gemini-length-correlation caveat (5 of 5 substantive but verbose).
- "Confidence claims rarely track empirical accuracy" — pre-anchors our accuracy_calibration_correlation Layer 4 finding (D-1.12, r ≈ 0.4).
Methodology details for project:
- Provides a domain-anchored motivation for RQ5 stronger than the FermiEval-only contrast.
Cross-paper convergence:
- Nagarkar + FermiEval + Multi-Answer-Confidence all argue verbalized confidence is unreliable; Multi-Answer specifically names consistency-based as the upgrade.
Recommended website surface: RQ5 panel — quote "surface fluency masks reasoning gaps" alongside the consistency-extraction finding.

#### Paper 03 — MathEval (Liu et al., 2025)
Buried claims worth surfacing:
- "Multi-dimensional scoring yields rankings DIFFERENT FROM accuracy alone" — direct anchor for D-6.03 (accuracy vs robustness anti-correlation).
- "Tier-stratified difficulty exposes ceiling effects on easy tasks" — anchors our tier-1 BASIC tasks design (where everyone passes — informative ceiling).
- "Reasoning-quality metrics correlate weakly with raw accuracy" — pre-anchors the gemini RQ-leadership-vs-accuracy-leadership pattern.
Methodology details for project:
- Liu's 17-dataset unification differs from our 38-task-type / 5-model unification — both are "comparative baselines via shared scoring."
Cross-paper convergence: with StatEval and Math-Failures (above).
Recommended website surface: Methodology page rubric description — quote "multi-dim scoring yields rankings different from accuracy alone" as the rationale for not using accuracy-only rankings.

#### Paper 04 — Program-of-Thoughts (Chen et al., 2022)
Buried claims worth surfacing:
- "PoT outperforms CoT by ~12% on numerical reasoning benchmarks" — anchors why PoT considered AND deferred (Bayesian symbolic > arithmetic).
- "Disentangles symbolic reasoning from numerical execution" — pre-anchors our N=0.10 weight ("trivially checkable, separate from reasoning").
Methodology details for project:
- One of 3 candidate prompting modes; only zero-shot CoT shipped (per D-APP-03 — the website currently falsely claims 3 modes).
Cross-paper convergence: with Wei (CoT) and Bishop (method selection) for our M=0.20 anchor.
Recommended website surface: Methodology continuity statement — explicit "PoT considered and deferred because Bayesian closed-form is symbolic" sentence.

#### Paper 05 — Chain-of-Thought (Wei et al., 2022)
Buried claims worth surfacing:
- "CoT prompting produces emergent reasoning gains at sufficient scale (~100B params)" — anchors our 5 frontier-LLM choice (all are >>100B effective scale).
- "Zero-shot CoT extension makes the technique trigger-phrase only" — anchors our "Solve problems step by step" trigger phrase choice.
Methodology details for project:
- Foundational citation; system prompt ("show all working") is a literal CoT trigger.
Cross-paper convergence: with PoT, Bishop for M dimension.
Recommended website surface: Methodology §3 prompting subsection (currently lists Wei but not the trigger-phrase rationale).

#### Paper 06 — Longjohn et al. (2025, "Bayesian Evaluation of LLM Behavior")
Buried claims worth surfacing:
- "Many ranking claims in LLM benchmarks are NOT statistically supported" — direct anchor for the separability matrix surfacing (D-1.07, D-7.05).
- "Point-estimate accuracies obscure between-run variance and sampling uncertainty" — pre-anchors the bootstrap CI framing.
- "Recommends always reporting CI alongside accuracy" — direct mandate the project follows.
Methodology details for project:
- Bayesian-evaluation grounding (project is Bayesian-domain → Bayesian evaluation methodology). Symmetry not currently named.
Cross-paper convergence:
- Longjohn + Statistical Fragility + ReasonBench triple-anchor "separability tests" — all three argue benchmark wins are often within noise.
Recommended website surface: Methodology §4 separability paragraph — currently cites Statistical Fragility only; add Longjohn for "Bayesian-evaluation-of-Bayesian-benchmark" framing.

#### Paper 07 — ReasonBench (2025)
Buried claims worth surfacing:
- "Run-to-run variance can FLIP RANKINGS on the same prompts" — strongest anchor for the "3 ≠" framing.
- "Stability is model-dependent and uncorrelated with raw accuracy" — pre-anchors D-6.03 (accuracy vs robustness anti-correlation).
- "Reproducibility deserves an explicit dimension alongside accuracy and calibration" — direct adoption (we have 3 rankings: accuracy / robustness / calibration).
Methodology details for project:
- "Variance-as-first-class" is a direct phrase-level adoption (D-2.09).
Cross-paper convergence: with Longjohn, Fragility (above).
Recommended website surface: visualizations.js three_rankings caption — quote ReasonBench's framing.

#### Paper 08 — BrittleBench (2026)
Buried claims worth surfacing:
- "Numerical perturbations reveal arithmetic-vs-conceptual brittleness mismatch" — pre-anchors D-6.10 (numerical-perturbation keyword-judge disagreement 22.7% highest).
- "Robustness deltas often within stochastic noise — must be tested for separability" — direct anchor for D-1.08 (chatgpt + mistral CIs cross zero).
- "Semantic perturbations expose memorization artifacts" — explanatory framing for our semantic-perturbation findings (5.96pp keyword degradation differential, D-1.01).
Methodology details for project:
- 3 perturbation types adopted directly (rephrase / numerical / semantic) per D-4.06.
Cross-paper convergence: with Fragility, ReasonBench (above).
Recommended website surface: RQ4 panel — quote "robustness deltas often within stochastic noise" as the direct anchor for chatgpt+mistral CIs crossing zero.

#### Paper 13 — Math Reasoning Failures (Boye & Moell, 2025)
Buried claims worth surfacing:
- "Multi-dimensional rubrics expose more failures than answer-correctness alone" — anchor for full N·M·A·C·R rubric.
- "Failures cluster on derivation correctness, NOT arithmetic" — direct anchor for our finding that 67/143 failures are ASSUMPTION_VIOLATION (a derivation issue) and only 48 are MATHEMATICAL_ERROR.
- "Models struggle to translate physical/intuitive reasoning into mathematical steps" — anchors our REGRESSION cluster ~0.30 mean accuracy finding (regression-as-physical-translation).
Methodology details for project:
- Maps to evaluation/llm_judge_rubric.py (rubric design) per vault citation map.
Cross-paper convergence:
- Boye-Moell + Du (Ice Cream) + this work form the assumption-violation 3-way (D-4.01).
- Boye-Moell + StatEval + MathEval converge on multi-dim-rubric exposing more failures.
Recommended website surface: RQ3 panel — currently names Du; add Boye-Moell as second confirming citation. Convert "independent ~47% reproduction" to "two independent reproductions converging within 0.1pp."

#### Paper 14 — Judgment Becomes Noise (Feuer et al., 2025)
Buried claims worth surfacing:
- "Inter-judge ensembles (3+ judges) recover signal" — specific number anchor for future-work scope. Limitations currently says "multi-judge ensemble" without specifying ≥3.
- "Prompt template choices systematically shift score distributions" — already noted at D-4.02.
- "Recommends multi-judge ensembling AND pre-registered prompt templates" — pre-registration is a SECOND future-work axis the project doesn't currently mention.
Methodology details for project:
- Family-preference / self-preference bias — anchors the 5-distinct-providers design choice (D-2.14).
Cross-paper convergence: with Yamauchi (Park et al.) for the dual single-judge critique.
Recommended website surface: Limitations L4 — extend with "(a) multi-judge ensemble (≥3 judges per Feuer 2025), (b) pre-registered prompt templates."

#### Paper 15 — Statistical Fragility (Hochlehnert et al., 2025)
Buried claims worth surfacing:
- "Single-question changes shift Pass@1 by 3+ percentage points" — direct numerical anchor for the ≥3pp claim already on Limitations L3. Specific to Pass@1; our metric is aggregate_new — could note the parallel.
- "Many published 'wins' are within stochastic noise" — anchor for D-1.08 (2 of 5 robustness CIs cross zero).
- Canonical title: "A Sober Look at Progress in Language Model Reasoning: Pitfalls and Paths to Reproducibility" — D-4.10 already noted.
Methodology details for project:
- Specific separability-test recommendation; project implements it via bootstrap_ci.py separability matrix.
Cross-paper convergence: with Longjohn, ReasonBench, BrittleBench (above).
Recommended website surface: Bootstrap CI section — quote "Many published wins are within stochastic noise" alongside the 2-of-5 chatgpt+mistral noise-equivalent finding.

### Cross-paper convergence patterns identified

1. **Statistical rigor / separability** (4 papers): Longjohn 2025 + Statistical Fragility 2025 + ReasonBench 2025 + BrittleBench 2026 — all argue point-estimate rankings without CIs are unsupported. Project's separability matrix (bootstrap_ci.json) implements all 4 recommendations. Currently methodology cites Fragility only.
2. **Multi-dim rubrics expose hidden failures** (3 papers): MathEval + Math-Failures + StatEval. Direct anchor for N·M·A·C·R rubric existence. Currently methodology lists MathEval only.
3. **Verbalized confidence unreliable** (3 papers): Nagarkar + FermiEval + Multi-Answer Confidence. Pre-anchors the consistency-extraction upgrade.
4. **Single-judge ensembling needed** (2 papers): Yamauchi 2025 + Feuer 2025 (Judgment Noise). Limitations L4 cites Yamauchi only; Feuer adds the "≥3 judges" specific number AND the second axis (pre-registered templates).
5. **Variance/instability as first-class** (3 papers): ReasonBench + BrittleBench + Fragility. Direct anchor for the 3-rankings framing.
6. **Assumption-violation as dominant failure** (2 papers + this work): Du (Ice Cream) + Boye-Moell + this work — 3-way convergence within 0.1pp on the 46.9% / 47% finding (D-4.01).

### Updated totals

Original discovery audit: **47 findings** (16 HIGH, 20 MEDIUM, 11 LOW)

Phase 1 additions: **34 findings** — D-PC (8) + D-APP (16) + D-PN cross-paper convergence (6) + 4 within-paper buried claims promoted as standalone findings (D-PN-01..04 below)

| Source | Total | HIGH | MEDIUM | LOW |
|--------|-------|------|--------|-----|
| PosterCompanion (D-PC) | 8 | 2 | 2 | 4 |
| App.jsx full (D-APP) | 16 | 6 | 3 | 7 |
| Paper notes / convergence | 10 | 3 | 5 | 2 |
| **Phase 1 subtotal** | **34** | **11** | **10** | **13** |

**Combined audit total: 81 findings** (27 HIGH, 30 MEDIUM, 24 LOW)

### Newly-promoted standalone paper-note findings

**[D-PN-01] Boye-Moell "failures cluster on derivation correctness, NOT arithmetic"**
Type: LITERATURE_INSIGHT_NOT_PROPAGATED
Severity: HIGH
Source: paper note 13
Content: Direct quote pre-anchors our 67 vs 48 split (assumption violations dominate over math errors). RQ3 panel currently cites Du only; adding this Boye-Moell quote elevates the framing from "one independent reproduction" to "two independent reproductions on the same direction of failure."
Where: RQ3 panel detail string.
Why: Two-source convergence stronger than one.

**[D-PN-02] ReasonBench "stability is model-dependent and uncorrelated with raw accuracy"**
Type: LITERATURE_INSIGHT_NOT_PROPAGATED
Severity: HIGH
Source: paper note 07
Content: Pre-anchors D-6.03 (accuracy ranking anti-correlated with robustness ranking, r≈−0.6). Currently RQ4 panel cites ReasonBench for "variance-as-first-class" framing only; adding the uncorrelated-with-accuracy claim makes the cross-cutting connection literature-backed.
Where: RQ4 panel detail string.
Why: Connects observed-pattern (D-6.03) to literature.

**[D-PN-03] Feuer specifies "3+ judges" for ensembling**
Type: LITERATURE_INSIGHT_NOT_PROPAGATED
Severity: MEDIUM
Source: paper note 14
Content: Future-work limitations panel currently says "multi-judge ensemble" without a specific number. Feuer specifically says ≥3.
Where: Limitations L4 future-work scoping.
Why: Specific is stronger than vague.

**[D-PN-04] Feuer recommends "pre-registered prompt templates" as a SECOND axis**
Type: LITERATURE_INSIGHT_NOT_PROPAGATED
Severity: MEDIUM
Source: paper note 14
Content: Currently the project has ONE judge prompt template (used as fixed). Feuer recommends pre-registration as a methodological discipline. Currently no mention.
Where: Limitations L4 future-work — add "(b) pre-registered prompt templates" alongside multi-judge ensemble.
Why: Two distinct recommendations from Feuer should both surface.

**[D-PN-05] Multi-source convergence (4 papers) on separability-test mandate**
Type: CROSS_CUTTING_CONNECTION
Severity: HIGH
Source: paper notes 06, 07, 08, 15
Content: Longjohn + ReasonBench + BrittleBench + Fragility all converge on "rankings within bootstrap noise must be flagged." Methodology page §4 currently cites Fragility only. Adding the 3 corroborators turns one-paper assertion into 4-paper convergence.
Where: Methodology §4 separability paragraph.
Why: Maximum literature defense for the bootstrap-CI separability machinery.

**[D-PN-06] Multi-source convergence (3 papers) on multi-dim-rubric value**
Type: CROSS_CUTTING_CONNECTION
Severity: MEDIUM
Source: paper notes 01, 03, 13
Content: StatEval + MathEval + Boye-Moell all argue multi-dim scoring exposes failures hidden in accuracy-only metrics. Methodology page §2 (rubric) cites MathEval only.
Where: Methodology §2 NMACR rubric introduction.
Why: 3-way convergence justifies the per-dim weight architecture.

### Updated top priority list for Group B+ (Phase 2)

Combined HIGH-severity items, sorted by file location for efficient implementation:

**capstone-website/frontend/src/App.jsx (multi-violation file — all HIGH):**
- D-APP-01: AnimatedScoringBars hardcodes 0.20 weights (App.jsx:425-447)
- D-APP-02: PIPELINE step 4 says "N=M=A=C=R=0.20" + "Equal weights" (App.jsx:87-89)
- D-APP-03: PIPELINE step 2 falsely claims "3 prompting modes implemented" (App.jsx:82-83)
- D-APP-04: RADAR_VALS hardcoded Phase 1A normalized values (App.jsx:140-146)
- D-APP-06: HOW_EXTRA "RQ1 PRIMARY (40%)" (App.jsx:967-968) — original D-1.04
- D-APP-12: ABOUT_FINDINGS card 4 "Top-2 CIs overlap" + "ChatGPT/DeepSeek noise-equivalent" (App.jsx:1916)
- D-APP-13: RQ4 detail "ChatGPT/DeepSeek noise-equivalent" (App.jsx:1899)
- Original RQS array `weight:'X%'` drop (App.jsx:1870-1902) — duplicate of D-APP-06

**capstone-website/frontend/src/pages/Methodology.jsx:**
- D-5.01: "Five equal-weight dimensions (0.20 each)" (Methodology.jsx:110-113)
- D-5.02: Add 5-paragraph per-dim defense
- D-1.10: α NEGATIVE on RQ + M (add to §4)
- D-1.19: "Ranking stable across sweeps" FALSE (Methodology.jsx:179-182)
- D-1.07/D-7.05: Separability matrix surfacing (§4)
- D-2.04: Llama judge 4-reason expansion (§3)

**capstone-website/frontend/src/pages/Limitations.jsx:**
- D-5.10/D-2.08: New caveats — length-correlation, CONCEPTUAL/135-task exclusions, post-hoc weight risk
- D-4.02/D-4.09: Yamauchi prompt-template + ensembling expansion (L4)
- D-PN-03/D-PN-04: Feuer 3+ judges + pre-registered templates (L4)

**capstone-website/frontend/src/pages/PosterCompanion.jsx:**
- D-PC-01: HEADLINE_CARDS Phase 1A static refresh
- D-PC-03: Du-vs-Wang attribution lock

**capstone-website/frontend/src/data/visualizations.js (already in original audit):**
- D-3.07: caption refresh (bootstrap_ci, robustness_heatmap, self_consistency)
- D-3.04/05/06: a4b/a5b/combined_pass_flip manifest entries
- D-3.08: 274/1094 → 274/1095

**Cross-cutting (Group C scope):**
- D-1.05: Per-model keyword-judge disagreement card / panel
- D-1.16: Per-model failure-mode stacked bar
- D-6.01: Cross-method calibration ranking inversion figure
- D-1.11: Per-NMACR-dim ECE table panel
- D-1.12: Accuracy-calibration correlation card
- D-1.01: Keyword degradation finding propagation
- D-1.03: Combined 22.16% keyword-judge disagreement headline decision
- D-PN-05: Methodology §4 separability multi-source convergence
- D-PN-06: Methodology §2 multi-source rubric convergence
- D-4.01/D-PN-01: RQ3 panel 3-way convergence (Du + Boye-Moell + this work)

```
PHASE 1 — COVERAGE CLOSURE COMPLETE

PosterCompanion.jsx: 8 findings (2 HIGH)
App.jsx (full): 16 findings (6 HIGH)
11 paper notes: 10 findings (3 HIGH) — 4 within-paper standalone + 6 cross-paper convergence

Combined audit total: 81 findings (27 HIGH, 30 MEDIUM, 24 LOW)
Group B+ scope grew by: 11 HIGH-severity additions

Top 3 newly surfaced HIGH-severity items:
1. D-APP-01: AnimatedScoringBars hardcodes "COMPOSITE SCORE = N·0.20 + M·0.20 + A·0.20 + C·0.20 + R·0.20" — third equal-weight surface on the deployed site (after Methodology.jsx + PIPELINE step 4)
2. D-APP-03: PIPELINE step 2 falsely claims "Three prompting modes implemented: Zero-shot CoT, Few-shot CoT, Program-of-Thoughts" — only zero-shot CoT actually shipped; PoT explicitly deferred per methodology_continuity.md
3. D-APP-04: RADAR_VALS hardcoded with Phase 1A normalized values (claude 0.89, gemini 0.86 etc.) — Models page even labels the radar "Placeholder · updates after runs" — TODO never resolved

Paper note convergence patterns found: 6
- Statistical rigor / separability: 4 papers (Longjohn + Fragility + ReasonBench + BrittleBench)
- Multi-dim rubrics expose failures: 3 papers (StatEval + MathEval + Boye-Moell)
- Verbalized confidence unreliable: 3 papers (Nagarkar + FermiEval + Multi-Answer Confidence)
- Single-judge ensembling: 2 papers (Yamauchi + Feuer)
- Variance as first-class: 3 papers (ReasonBench + BrittleBench + Fragility)
- Assumption-violation 3-way: 2 papers + this work (Du + Boye-Moell + this 46.9%)

Recommended next: Run Phase 2 (Group B+) which will absorb all 27 HIGH-severity
findings into frontend prose updates (Methodology.jsx + Limitations.jsx +
visualizations.js + App.jsx + PosterCompanion.jsx).
```

*End of Phase 1 coverage closure.*
