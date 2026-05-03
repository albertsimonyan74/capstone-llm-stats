# IEEE-Grade Research Question Formulations

## Purpose

Operationalized, citation-verified research questions suitable for inclusion
in the IEEE paper draft. Paper-grade formulations distinct from the website's
accessible card phrasings (which prioritize clarity over precision). Output
of the Day-4 (2026-05-03) citation-honesty pass requested after the
"Park-et-al.-α-threshold" hallucination near-miss.

## Scope and conventions

- **Scope.** Five RQs (RQ1 PRIMARY methodology; RQ2–5 SUPPORTING evidence).
  Operationalization, hypothesis, metric, population, citations,
  limitations, and convergence-with-prior-work for each.
- **Citations.** Every cited claim is traceable to a vault note in
  `llm-stats-vault/40-literature/`. Bibtex keys point to
  `llm-stats-vault/40-literature/bibtex.bib`.
- **Numerical values.** Every quantitative claim cross-checked against the
  canonical JSON in `experiments/results_v2/` (verification logged below
  each RQ as "Source file"). The 22.16% combined keyword-judge disagreement is preferred
  over the 25.02% base-only headline because it pools base + perturbation
  evidence (3,195 eligible runs vs 1,095) and is the canonical Phase 1.5
  result.
- **Authorship convention.** Bibtex keys `du2025icecream` and
  `park2025judge` are legacy; actual first authors are **Du** and
  **Yamauchi** respectively. In-text citations use the actual first
  author; bibtex `\cite{}` keys retained for stability.

## Citation honesty disclosures

This file was drafted after a citation hallucination near-miss in which
the phrase "questionable per Park et al. 2025 thresholds" was used to
justify a specific Krippendorff α threshold (0.667). The vault note for
Yamauchi et al. (2025) [arXiv:2506.13639] recommends α over ρ as a metric
choice but does **not** define a specific α threshold. Thresholds at
0.667 / 0.800 come from Krippendorff's own methodological writing
(2004/2013), which the project does not currently have in the vault. RQ1
below therefore uses **threshold-free framing**: report α with bootstrap
CI and let CI-vs-zero do the interpretation. Negative α with CI excluding
zero is "systematically worse than chance" by α's definition; no
external threshold needed.

`[VERIFY]` flags below mark claims that look plausible but were not
fully traceable in the present vault. They block paper submission until
resolved.

---

## RQ1 — Does external LLM-judge validation diverge structurally from keyword-rubric scoring on Bayesian reasoning?

**Research question.** Across N·M·A·C·R rubric dimensions, does an
external LLM judge (Llama 3.3 70B Instruct) produce per-run scores that
agree with a keyword-based rubric beyond chance, and is the disagreement
concentrated on a particular dimension?

**Hypotheses.**
- H₀: Per-dimension Krippendorff α between keyword and judge raters is
  ≥ 0 with CI containing positive values across all rubric dimensions.
- H₁: At least one dimension has α with bootstrap CI strictly below 0
  (raters systematically worse than chance) or close to 0 (raters not
  meaningfully aligned).

**Operationalization.**
- Constructs.
  - *Keyword rubric* — `llm_runner/response_parser.full_score` plus
    `extract_confidence`. Path A canonical scorer used to produce the
    1,230-run base benchmark plus 2,365 perturbation runs.
  - *External LLM judge* — `evaluation/llm_judge_rubric.py` against
    `meta-llama/Llama-3.3-70B-Instruct-Turbo` via Together AI at
    temperature 0. Four rubric dimensions: `method_structure`,
    `assumption_compliance`, `reasoning_quality`,
    `reasoning_completeness`.
  - *Keyword-judge disagreement* — keyword PASS (≥ 0.5) and judge FAIL (< 0.5) on the same
    (run_id, dimension), or vice versa.
- Excluded population. 135 base runs whose tasks have empty
  `required_assumption_checks` (CONCEPTUAL × 10, MINIMAX × 5, BAYES_RISK
  × 5, MARKOV × 1, plus per-model expansions); these score 1.0 trivially
  under both rubrics and would inflate agreement.

**Metrics.**
- Krippendorff's α (ordinal, 11-bin discretization of [0, 1]) per
  dimension, with bootstrap CI (B = 1,000, seed = 42).
- Combined keyword-judge disagreement rate over 3,195 eligible runs (base ∪ perturbation,
  no run-id collisions verified).
- Per-perturbation-type keyword-judge disagreement rates.

**Population.** 5 frontier LLMs × 171 base tasks (1,095 base eligible)
plus 5 × 420 perturbation tasks (2,100 perturbation eligible) = 3,195
eligible (model, run) pairs. Sample size justified by the bootstrap-CI
target (Longjohn et al. 2025; Hochlehnert et al. 2025).

**Findings (canonical values).**
- Combined keyword-judge disagreement: **708 / 3,195 = 22.16%** (Phase 1.5).
  Inverse flip (keyword FAIL, judge PASS): 143 / 3,195 = 4.48%.
  Net signal: keyword ≈ 5× more lenient than judge.
- Per-perturbation-type keyword-judge disagreement: rephrase 21.6% (162 / 750), numerical
  22.7% (136 / 600), semantic 18.1% (136 / 750). Disagreement is a
  stable rubric property, not a base-prompt artifact.
- Krippendorff α (ordinal, B = 1,000):
  - `assumption_compliance`: α = **0.55** [0.504, 0.595], n = 1,095.
  - `method_structure`:      α = **−0.04** [−0.097, +0.015], n = 1,095.
  - `reasoning_quality`:     α = **−0.13** [−0.228, −0.039], n = 460.
- The CI for `reasoning_quality` excludes zero — agreement is
  systematically worse than chance. The CI for `method_structure`
  contains zero — agreement is statistically indistinguishable from
  chance. Only `assumption_compliance` reaches positive agreement, and
  even there both rubrics find the dimension hard (judge mean 0.441,
  keyword mean 0.565).

**Result vs hypotheses.** Reject H₀ for `reasoning_quality` (CI excludes
0). Cannot reject H₀ for `method_structure` (CI contains 0, but point
estimate is negative — interpret as "no meaningful agreement"). H₀
holds positively for `assumption_compliance` (CI excludes 0 from
*above*).

**Citations used.**
- **Yamauchi et al. (2025)** [arXiv:2506.13639] — recommends Krippendorff
  α over Spearman ρ for LLM-as-Judge inter-rater reliability; reports
  judge-prompt-template effects exceeding judge-model-choice effects.
  Vault: `papers/10-new-llm-judge-empirical-2025.md`. Bibtex:
  `park2025judge`. *Used to justify metric choice (α over ρ); not used
  to justify any specific α threshold (vault note does not contain a
  threshold table).*
- **Feuer et al. (2025)** "Judgment Becomes Noise" [arXiv:2509.20293] —
  single-judge benchmarks introduce systematic noise; recommends
  multi-judge ensembles. Vault:
  `papers/14-new-judgment-becomes-noise-2025.md`. Bibtex:
  `judgment2025noise`. *Used in limitations.*
- **Lu et al. (2025)** StatEval [arXiv:2510.09517] — multiple-choice
  format underestimates failure modes hidden in free-response. Vault:
  `papers/01-original-stateval-2025.md`. Bibtex: `lu2025stateval`. *Used
  to motivate the free-response design choice.*
- **Liu et al. (2025)** MathEval [DOI:10.1007/s44366-025-0053-z] —
  multi-dimensional rubric design (numeric vs reasoning separation).
  Vault: `papers/03-original-matheval-2025.md`. Bibtex:
  `liu2025matheval`. *Used to motivate the N·M·A·C·R decomposition.*
- **Krippendorff threshold framing — DROPPED 2026-05-03.**
  `experiments/results_v2/krippendorff_agreement.json` no longer carries a
  `thresholds` block or Park-et-al. attribution. The canonical
  `interpretation` block now uses threshold-free CI-vs-zero labels
  ("positive_agreement", "indistinguishable_from_chance",
  "systematic_disagreement"). Krippendorff (2004, 2013) is referenced
  directly in the new `_methodology_note`; no separate vault entry was
  created because no specific threshold value is cited project-wide
  any longer. Single-judge limitations cite Feuer et al. (2025) directly.

**Limitations specific to RQ1.**
- Single judge model. Cite Feuer et al. (2025) — multi-judge ensemble is
  paper-scope future work.
- Ordinal α (11-bin discretization of [0, 1]) — alternative levels-of-
  measurement (interval, ratio) yield slightly different α values; the
  ordinal choice is the most conservative for bounded rubric scales
  (Yamauchi et al. 2025).
- Inverse flip (4.48%) and net flip (22.16%) are not symmetric; the
  asymmetry could in principle reflect judge strictness rather than
  keyword leniency. We disclose this and report the 5-of-7 strictness
  spot-check (judge agrees with the rubric on the cases where it
  rejects implicit-assumption arguments).

**Convergence with prior work.**
- Yamauchi et al. (2025) report judge-template-choice effects exceeding
  judge-model-choice effects in general LLM-as-Judge work. The same
  pattern is observed here: cross-provider comparison (Groq vs Together
  with the same Llama-3.3-70B model) yields nearly identical scores.
- Feuer et al. (2025) frame single-judge bias as a validity concern;
  this work inherits that limitation and discloses it explicitly.

**Source files.**
- `experiments/results_v2/combined_pass_flip_analysis.json`
  (`combined.pct_pass_flip = 0.221596…`,
  `combined.n_pass_flip = 708`, `combined.n_eligible = 3195`).
- `experiments/results_v2/krippendorff_agreement.json`
  (`overall.assumption_compliance.alpha = 0.5502`,
  `overall.method_structure.alpha = -0.0420`,
  `overall.reasoning_quality.alpha = -0.1330`).
- `audit/recompute_log.md` §"Phase 1.5".

---

## RQ2 — Are there Bayesian task categories on which all evaluated frontier LLMs perform comparably poorly?

**Research question.** When tasks are aggregated by Bayesian-method
category, does any category produce uniformly low cohort accuracy under
the literature-weighted N·M·A·C·R aggregate, indicating a structural
domain weakness rather than a per-model failure?

**Hypotheses.**
- H₀: Cohort mean aggregate accuracy is approximately uniform across
  task categories (i.e., per-category cohort means are within ±0.10 of
  the global cohort mean).
- H₁: At least one category has cohort mean ≥ 0.10 below global mean.

**Operationalization.**
- *Category bucket* — Bayesian-method grouping over 38 task types
  (REGRESSION cluster; MCMC: GIBBS, MH, HMC, RJMCMC; ADVANCED:
  HIERARCHICAL, VB, ABC; CONCEPTUAL; conjugate-prior cluster; …).
  Mapping in `report_materials/figures/a2_accuracy_by_category.png`.
- *Aggregate accuracy* — `aggregate_new` from `nmacr_scores_v2.jsonl`
  (literature-weighted: A = 0.30, R = 0.25, M = 0.20, C = 0.15,
  N = 0.10).
- *Cohort mean* — average of per-model means within each category.

**Metrics.**
- Per-category cohort mean accuracy.
- Bootstrap CI on per-category means (paper-scope; current figure is
  point-estimate only).

**Population.** 1,230 base runs (171 tasks × 5 models, 0 errored after
the VB_04 / Mistral re-judge of 2026-04-30).

**Findings.** REGRESSION cluster cohort mean ≈ 0.30 — substantially
below cohort grand mean ≈ 0.70 (literature-weighted). MCMC and ADVANCED
clusters also score below cohort mean. CONCEPTUAL has no N dimension
and uses the renormalized M·A·C·R weights (mirrors `full_score()`
behavior in `llm_runner/response_parser.py`).

**Result vs hypotheses.** Reject H₀: REGRESSION delta vs cohort mean
exceeds 0.10. The MCMC cluster delta is smaller but still material; the
gap is reported conservatively without claiming statistical separability
in the current draft (paper-scope: bootstrap CI on category means).

**Citations used.**
- **Liu et al. (2025)** MathEval [DOI:10.1007/s44366-025-0053-z] — task
  category as a first-class organizational axis; multi-dimensional
  scoring exposes category-level weaknesses invisible in raw accuracy.
  Vault: `papers/03-original-matheval-2025.md`. *Used for the
  by-category aggregation convention.*
- **Boye & Moell (2025)** [arXiv:2502.11574] — "unwarranted assumptions"
  is a top failure mode across math reasoning domains; multi-domain
  catalogue of failure clusters. Vault:
  `papers/13-new-math-reasoning-failures-2026.md`. Bibtex:
  `mathfail2025`. *Used to align the REGRESSION drops with their
  general-math finding.*
- **Bishop (2006) PRML** — canonical method-class taxonomy used to
  bucket VB_*, BAYES_REG, LOG_ML, DIRICHLET_*. Vault:
  `textbooks/bishop-prml.md`. *Used to ground the category mapping for
  Phase 2 tasks.*

**Limitations specific to RQ2.**
- No bootstrap CI on per-category means in the current draft. Adjacent
  categories below cohort mean (MCMC, ADVANCED) cannot be claimed as
  separable from REGRESSION without that test.
- 5-model cohort is small; cohort means are sensitive to outlier model
  behavior. Per-model breakdown is in
  `report_materials/figures/a3_failure_heatmap.png`.

**Convergence with prior work.**
- Boye & Moell (2025) report unwarranted-assumption clusters as
  cross-domain top failures; the REGRESSION deficit reported here
  aligns with their finding that derivation-heavy problems concentrate
  failures even
  when raw arithmetic is correct.
- Liu et al. (2025) demonstrate that category-level views expose
  weaknesses that per-task or per-model views obscure; the same
  pattern is replicated here in the Bayesian setting.

**Source file.** `experiments/results_v2/nmacr_scores_v2.jsonl`
aggregated per category; visualized in
`report_materials/figures/a2_accuracy_by_category.png`.

---

## RQ3 — Among observed failures, what is the empirical distribution over a closed-form failure taxonomy, and which mode dominates?

**Research question.** When a base run fails (final aggregate < 0.5),
which L1 failure category claims the largest share of failures, and is
that share consistent with prior reports of dominant LLM failure modes
on adjacent reasoning domains?

**Hypotheses.**
- H₀: Failure mode distribution is approximately uniform over the four
  populated L1 categories (each ≈ 25% of failures).
- H₁: One L1 category claims ≥ 40% of all classified failures.

**Operationalization.**
- *Failure* — base-run aggregate score `< 0.5` under Path A canonical
  scoring (`response_parser.full_score`). 143 such failures across the
  1,230-run base benchmark.
- *L1 taxonomy* (closed-form, 4 populated categories + 1 empty):
  ASSUMPTION_VIOLATION, MATHEMATICAL_ERROR, FORMATTING_FAILURE,
  CONCEPTUAL_ERROR, HALLUCINATION (= 0). Schema:
  `experiments/results_v2/error_taxonomy_v2.json` →
  `l1_to_l2_mapping`.
- *Classifier* — Llama 3.3 70B Instruct judge with hierarchical L1+L2
  prompt (`scripts/error_taxonomy.py`).

**Metrics.**
- L1 share = (count_L1 / total_classified_failures).
- Per-model L1 distribution (`by_model_l1`).

**Population.** 143 base-benchmark failures across 5 models. Excludes
perturbation-set failures (analyzed separately in
`combined_pass_flip_analysis.json`).

**Findings.**
- ASSUMPTION_VIOLATION: 67 / 143 = **46.85%** (rounds to 46.9%).
- MATHEMATICAL_ERROR: 48 / 143 = 33.57%.
- FORMATTING_FAILURE: 18 / 143 = 12.59% (reported separately as
  `formatting_failure_rate`; not folded into NMACR — pre-rubric
  exclusion).
- CONCEPTUAL_ERROR: 10 / 143 = 6.99%.
- HALLUCINATION: 0 / 143 = 0% (see Limitations).

**Result vs hypotheses.** Reject H₀. ASSUMPTION_VIOLATION ≥ 40%
threshold met (46.85%). Distribution is unambiguously
non-uniform under any reasonable rounding.

**Citations used.**
- **Du et al. (2025)** "Ice Cream" [arXiv:2505.13770] — independently
  reports ~47% assumption-violation share on causal-inference tasks;
  failure mode is "convincing yet misleading" — correct numeric answer
  with wrong causal interpretation. Vault:
  `papers/09-new-ice-cream-causal-2025.md`. Bibtex:
  `du2025icecream` (legacy key, actual first author Du). *Used for
  external-validity replication.*
- **Boye & Moell (2025)** [arXiv:2502.11574] — "unwarranted assumptions"
  named as a top failure mode in mathematical reasoning generally.
  Vault: `papers/13-new-math-reasoning-failures-2026.md`. Bibtex:
  `mathfail2025`. *Used as second-source convergence.*
- **Nagarkar et al. (2026)** [arXiv:2601.14479] — LLMs hallucinate
  statistical justifications even when numeric answers are correct;
  reliability degrades on assumption-verification tasks. Vault:
  `papers/02-original-can-llm-reasoning-2026.md`. Bibtex:
  `nagarkar2026canllm`. *Used to frame the methodological motivation
  for an explicit assumption-compliance dimension.*

**Limitations specific to RQ3.**
- HALLUCINATION = 0 / 143 is honestly ambiguous. May reflect a real
  property of closed-form Bayesian tasks (every task has a
  deterministic ground truth — models fail by skipping assumptions or
  miscomputing rather than fabricating distributions or data) **or**
  a single-judge classification limitation (the Llama 3.3 70B judge
  prompt explicitly flags E5 / E8 / E9 as "use only if nothing else
  fits"). Multi-judge ensemble is required to disambiguate. See
  `audit/limitations_disclosures.md` (a).
- Perturbation-run failures are not pooled into the L1 distribution
  here; the 46.9% headline applies to base only. Combined keyword-judge disagreement
  analysis (RQ1) includes perturbations.

**Convergence with prior work.**
- Du et al. (2025) ~47% assumption-violation on causal inference —
  numerically nearly identical to the 46.85% reported here. Domain shifts
  (causal pitfalls vs Bayesian inference); failure-mode-share invariant.
- Boye & Moell (2025) name the same failure cluster across general math
  reasoning. Three-way external corroboration of a single finding
  across three reasoning domains.

**Source files.**
- `experiments/results_v2/error_taxonomy_v2.json` (`l1_totals`,
  `n_failures_classified`).
- `report_materials/figures/error_taxonomy_hierarchical.png`.

---

## RQ4 — Are model rankings stable across three orthogonal evaluation axes (accuracy, robustness, calibration), and are pairwise rank differences statistically separable from sampling noise?

**Research question.** Do per-model rankings under literature-weighted
NMACR accuracy agree with rankings under perturbation robustness Δ and
verbalized confidence ECE, and which pairwise comparisons remain
significant under bootstrap-CI separability tests?

**Hypotheses.**
- H₀: The three rankings are concordant (Spearman ρ between any two ≈ 1).
- H₁: At least two of the three rankings disagree on the top-ranked
  model, and at least one pairwise comparison along each axis falls
  inside the bootstrap-CI noise band.

**Operationalization.**
- *Accuracy axis* — bootstrap mean of per-run `aggregate_new`
  (literature-weighted), B = 10,000, seed = 42.
- *Robustness axis* — `mean_delta = base_mean − perturbation_mean` per
  model, lower-is-better. Bootstrap CI (B = 10,000, seed = 42).
- *Calibration axis* — verbalized confidence ECE (4 buckets keyed to
  claimed p ∈ {0.3, 0.5, 0.6, 0.9}; 0.9 bucket empty across all 5
  models). Lower-is-better.
- *Separability* — pairwise bootstrap-CI overlap test; pair labeled
  `separable` if 95% CIs do not overlap, `not_separable` otherwise.

**Metrics.**
- Per-axis ranking (1 → 5).
- Pairwise separability label per axis (10 pairs × 3 axes = 30 calls).

**Population.** 5 models × 246 base tasks (literature-weighted aggregate
applies to base set). Robustness uses 5 × 473 perturbation pairs.
Calibration uses 1,230 base runs.

**Findings (canonical, `bootstrap_ci.json`, weighting_scheme =
`literature_v1`).**
- Accuracy: gemini 0.776 [0.753, 0.799] > claude 0.712 [0.689, 0.736] >
  chatgpt 0.691 [0.668, 0.715] > mistral 0.675 [0.652, 0.699] >
  deepseek 0.663 [0.639, 0.686]. Top model: **gemini**.
- Robustness Δ: mistral 0.0070 [−0.006, 0.019] < chatgpt 0.0114
  [−0.001, 0.024] < claude 0.0401 [0.027, 0.054] < deepseek 0.0423
  [0.027, 0.058] < gemini 0.0568 [0.041, 0.072]. Top model:
  **mistral**.
- Calibration ECE (verbalized): chatgpt 0.063 < claude 0.067 <
  mistral 0.084 < gemini 0.097 < deepseek 0.180. Top model:
  **chatgpt**.
- Three different top models — H₀ rejected.
- Separability matrix (accuracy): claude–chatgpt **not_separable**;
  claude–mistral **not_separable**; chatgpt–deepseek **not_separable**;
  chatgpt–mistral **not_separable**; deepseek–mistral **not_separable**.
  Five of ten accuracy pairs not separable.
- Separability matrix (robustness): chatgpt–mistral **not_separable**;
  claude–gemini **not_separable**; claude–deepseek **not_separable**;
  gemini–deepseek **not_separable**. Both top robustness pairs
  (mistral and chatgpt) have CIs spanning zero — within-noise of "no
  perturbation effect." Cite Hochlehnert et al. (2025): single-question
  swaps shift Pass@1 ≥ 3 pp — same noise scale observed here.

**Result vs hypotheses.** Reject H₀. The three rankings are not
concordant — the top-ranked model differs across all three axes
(gemini / mistral / chatgpt). Bootstrap-CI separability shows that
many pairwise rank differences are noise-equivalent on each axis.

**Citations used.**
- **Au et al. (2025)** ReasonBench [arXiv:2512.07795] — variance and
  reproducibility as first-class evaluation dimensions; run-to-run
  variance can flip rankings on the same prompts. Vault:
  `papers/07-new-reasonbench-2025.md`. Bibtex: `reasonbench2025`.
  *Used to motivate the three-rankings frame.*
- **Romanou et al. (2026)** BrittleBench [arXiv:2603.13285] —
  perturbation taxonomy (rephrase / numerical / semantic) directly
  adopted; robustness deltas often within stochastic noise. Vault:
  `papers/08-new-brittlebench-2026.md`. Bibtex: `brittlebench2026`.
  *Used for the perturbation methodology.*
- **Hochlehnert et al. (2025)** [arXiv:2504.07086] — single-question
  swaps shift Pass@1 by ≥ 3 percentage points; published "wins" often
  within stochastic noise. Vault:
  `papers/15-new-statistical-fragility-2025.md`. Bibtex:
  `fragility2025`. *Used to motivate bootstrap-CI separability tests.*
- **Longjohn et al. (2025)** [arXiv:2511.10661] — point-estimate
  accuracies obscure between-run variance; recommends always reporting
  CI alongside accuracy. Vault:
  `papers/06-new-longjohn-bayesian-eval-2025.md`. Bibtex:
  `longjohn2025bayesian`. *Used to motivate the bootstrap-CI design.*

**Limitations specific to RQ4.**
- Robustness top-2 (mistral, chatgpt) have CIs containing zero — within
  this sample size, neither model is statistically distinguishable
  from "no perturbation effect." Cite Hochlehnert et al. (2025).
- Calibration ECE here is verbalized only (the "weakest baseline" per
  Wang et al. 2026, Multi-Answer Confidence). Consistency-based ECE
  yields a different ranking — see RQ5.
- Bootstrap CI overlaps are evaluated pairwise without multiple-testing
  correction. With 10 pairs per axis, family-wise error rate is
  inflated; bootstrap is used here as a soft significance heuristic,
  not as a hypothesis test — disclosed accordingly.

**Convergence with prior work.**
- Au et al. (2025) and Hochlehnert et al. (2025) both report
  ranking-flip behavior on small-sample-size benchmarks. Our results
  match: in 5 of 10 accuracy pairs, ranks are within bootstrap noise.
- Romanou et al. (2026) report robustness deltas often within
  stochastic noise; the chatgpt and mistral robustness CIs reported
  here span zero, matching that pattern.

**Source file.** `experiments/results_v2/bootstrap_ci.json`
(`weighting_scheme = "literature_v1"`, `B = 10000`, `seed = 42`).

---

## RQ5 — Is LLM confidence on Bayesian inference tasks calibrated, and does the conclusion depend on confidence-extraction methodology?

**Research question.** Does verbalized confidence (keyword-based
extraction) and consistency-based confidence (3-rerun agreement at
T = 0.7) agree on per-model expected calibration error rankings, and
do their conclusions about overall calibration quality coincide?

**Hypotheses.**
- H₀: Verbalized ECE and consistency ECE per model are positively
  correlated (Spearman ρ > 0.5) and agree on overall direction
  ("calibrated" vs "miscalibrated").
- H₁: The two methods produce qualitatively different conclusions
  (e.g., verbalized → "hedge-heavy / underconfident", consistency →
  "severely overconfident") and disagree on per-model ranking.

**Operationalization.**
- *Verbalized confidence* — keyword-based extraction in
  `llm_runner/response_parser.extract_confidence`. Buckets keyed to
  claimed probability ∈ {0.3, 0.5, 0.6, 0.9}.
- *Consistency confidence* — 3 reruns per task at T = 0.7, top_p = 1.0;
  consistency = max-frequency answer count / 3 ∈ {0.33, 0.67, 1.0}.
  Implementation: `scripts/self_consistency_full.py`.
- *ECE* — Σ_b (n_b / N) · |center_b − accuracy_b|.

**Metrics.**
- Per-model ECE under each method.
- Per-model "high-confidence" bucket population (verbalized: claimed
  p = 0.9; consistency: 3-of-3 agreement).

**Population.**
- Verbalized: 1,230 base runs (5 × 246).
- Consistency: 161 numeric-target tasks × 5 models × 3 reruns = 2,415
  rerun outputs (10 CONCEPTUAL tasks excluded — no numerical answer
  against which 3-rerun agreement can be measured). Phase 1C cost:
  $11.69; 99.92% success (chatgpt 1, mistral 1 errored).

**Findings.**
| Model    | Verbalized ECE | Consistency ECE (full) |
|----------|---------------:|-----------------------:|
| claude   | 0.067          | 0.734                  |
| chatgpt  | 0.063          | 0.721                  |
| gemini   | 0.097          | 0.618                  |
| deepseek | 0.180          | 0.726                  |
| mistral  | 0.084          | 0.663                  |

- Verbalized: chatgpt < claude < mistral < gemini < deepseek
  (best → worst). All in [0.063, 0.180].
- Consistency: gemini < mistral < chatgpt < deepseek < claude
  (best → worst). All in [0.618, 0.734].
- Verbalized: hedge-heavy default to "unstated" bucket; 0 records in
  high (claimed p = 0.9) bucket across all 5 models. Gemini has 0
  verbalized signals at all (all 246 unstated).
- Consistency: all 5 models severely overconfident (ECE > 0.6).
  Confident agreement does not predict accuracy.
- Gemini reverses rank between methods: outlier "0 verbalized signals"
  → BEST consistency ECE (0.618 vs 0.66–0.73 for others).

**Result vs hypotheses.** Reject H₀. The two methods produce
qualitatively different per-model conclusions and disagree on overall
direction (verbalized: hedge-heavy / underconfident on populated buckets;
consistency: severely overconfident across the board). Spearman ρ
between the two ECE rankings is negative (gemini reverses).

**Citations used.**
- **Nagarkar et al. (2026)** [arXiv:2601.14479] — confidence claims
  rarely track empirical accuracy in statistical-domain LLM reasoning.
  Vault: `papers/02-original-can-llm-reasoning-2026.md`. Bibtex:
  `nagarkar2026canllm`. *Used for the calibration-as-separate-track
  motivation.*
- **Epstein et al. (2025)** FermiEval [arXiv:2510.26995] — LLMs are
  systematically overconfident on Fermi estimation tasks; 90% claimed
  CIs cover ~50% of ground truth. Vault:
  `papers/11-new-fermieval-2025.md`. Bibtex: `fermieval2025`. *Used as
  contrast finding under verbalized extraction (this work observes
  hedge-heavy, not overconfident); convergence finding under consistency
  extraction (this work observes overconfident, matching FermiEval
  direction).*
- **Wang et al. (2026)** Multi-Answer Confidence [arXiv:2602.07842] —
  verbalized confidence systematically underestimates uncertainty
  diversity; consistency-based confidence dominates verbalized
  methods; single-call keyword extraction is the weakest baseline.
  Vault: `papers/12-new-multi-answer-confidence-2026.md`. Bibtex:
  `multianswer2026`. *Used to (a) frame the methodology dichotomy and
  (b) cite token-level logprobs as the next-step upgrade.*

**Limitations specific to RQ5.**
- 10 CONCEPTUAL tasks excluded from consistency analysis — they have
  no numerical answer against which 3-rerun agreement can be measured.
  Inherent to consistency-based extraction; token-level logprobs (Wang
  et al. 2026) are the recommended upgrade path. Disclosed in
  `audit/limitations_disclosures.md` (f).
- The bibtex key `du2025icecream` is for the Du et al. *Ice Cream*
  paper (RQ3), not the Wang et al. *Multi-Answer* paper (RQ5). Two
  distinct first-author "Wang" entries — disambiguate carefully in
  paper prose.
- Verbalized extraction empties the high bucket across all 5 models;
  ECE there is effectively a 3-bucket weighted MAE (0.3 / 0.5 / 0.6).
  Disclosed in `audit/limitations_disclosures.md` (b).
- Both methods are post-hoc proxies for true probabilistic calibration.
  True logprob-based ECE requires uniform vendor-API support that is
  not currently available across the 5 evaluated models.

**Convergence with prior work.**
- Epstein et al. (2025) report systematic overconfidence on Fermi
  estimation. Under the consistency-extraction lens used here, all 5
  models are severely overconfident (ECE 0.62–0.73) — domain-invariant
  overconfidence.
- Wang et al. (2026) name verbalized as the weakest baseline of three
  methods reviewed; this work explicitly adopts that framing and
  discloses that the verbalized result is the weakest of the two
  reported.
- Nagarkar et al. (2026) flag confidence-vs-accuracy decoupling on
  statistical-domain tasks; the accuracy-calibration correlation
  reported here, Pearson r ∈ [0.35, 0.49], confirms decoupling is
  moderate (not
  catastrophic) where confidence is extractable, and total (Gemini)
  where it is not.

**Source files.**
- `experiments/results_v2/calibration.json` (verbalized ECE per model;
  formatting_failure_rate_per_model; accuracy_calibration_correlation).
- `experiments/results_v2/self_consistency_calibration.json`
  (`ece_comparison_full` per model; n_excluded_conceptual = 10).
- `experiments/results_v2/per_dim_calibration.json` (Phase 1B Layer 5
  per-dimension ECE).

---

## Citation Audit

Every paper used in any of the five RQs above, with the specific claim
each citation supports, vault file path, and confidence level.

| Paper (in-text) | Bibtex key | Vault path | Specific claim supported | Confidence | RQs |
|---|---|---|---|---|---|
| Lu et al. (2025) StatEval | `lu2025stateval` | `papers/01-original-stateval-2025.md` | Multiple-choice format underestimates failure modes hidden in free-response; closest prior work in statistical-reasoning benchmarking. | high | 1 |
| Nagarkar et al. (2026) | `nagarkar2026canllm` | `papers/02-original-can-llm-reasoning-2026.md` | Statistical-domain LLM reliability concerns; confidence rarely tracks accuracy; reliability degrades on assumption-verification tasks. | high | 3, 5 |
| Liu et al. (2025) MathEval | `liu2025matheval` | `papers/03-original-matheval-2025.md` | Multi-dimensional rubric with numeric vs reasoning separation; category-level views expose weaknesses invisible in raw accuracy; numerical correctness as necessary-but-trivially-checkable. | high | 1, 2 |
| Chen et al. (2022) PoT | `chen2022pot` | `papers/04-original-program-of-thoughts-2022.md` | Method-selection observability from response structure (used as part of the M-dimension defense). Not directly cited in the RQ formulations above; appears in methodology continuity. | medium | (continuity) |
| Wei et al. (2022) CoT | `wei2022cot` | `papers/05-original-chain-of-thought-2022.md` | Zero-shot CoT as the baseline reasoning prompt. Not directly cited in the RQ formulations above; appears in methodology continuity. | high | (continuity) |
| Longjohn et al. (2025) | `longjohn2025bayesian` | `papers/06-new-longjohn-bayesian-eval-2025.md` | Point-estimate accuracies obscure variance; bootstrap CI alongside accuracy is recommended. | high | 4 |
| Au et al. (2025) ReasonBench | `reasonbench2025` | `papers/07-new-reasonbench-2025.md` | Run-to-run variance can flip rankings; reproducibility deserves an explicit dimension; three-rankings framing. | high | 4 |
| Romanou et al. (2026) BrittleBench | `brittlebench2026` | `papers/08-new-brittlebench-2026.md` | Perturbation taxonomy (rephrase / numerical / semantic); robustness deltas often within stochastic noise. | high | 4 |
| Du et al. (2025) "Ice Cream" | `du2025icecream` (legacy key, actual first author Du) | `papers/09-new-ice-cream-causal-2025.md` | ~47% assumption-violation share on causal-inference tasks; failure mode is "convincing yet misleading". | high | 3 |
| Yamauchi et al. (2025) | `park2025judge` (legacy key, actual first author Yamauchi) | `papers/10-new-llm-judge-empirical-2025.md` | Krippendorff α over Spearman ρ for inter-rater reliability; judge-prompt-template effects exceed judge-model-choice effects. **NOT used to justify any specific α threshold** — the vault note does not contain a threshold table. | high (for metric choice); n/a (for thresholds — not in vault) | 1 |
| Epstein et al. (2025) FermiEval | `fermieval2025` | `papers/11-new-fermieval-2025.md` | Systematic overconfidence on Fermi estimation; 90% claimed CIs cover ~50% of ground truth. | high | 5 |
| Wang et al. (2026) Multi-Answer | `multianswer2026` | `papers/12-new-multi-answer-confidence-2026.md` | Verbalized vs consistency-based confidence framing; verbalized is the weakest baseline of three methods reviewed; token-level logprobs as upgrade path. | high | 5 |
| Boye & Moell (2025) | `mathfail2025` | `papers/13-new-math-reasoning-failures-2026.md` | "Unwarranted assumptions" as top failure mode in math reasoning; multi-dimensional rubrics expose more failures than answer-correctness alone. | high | 2, 3 |
| Feuer et al. (2025) Judgment-Noise | `judgment2025noise` | `papers/14-new-judgment-becomes-noise-2025.md` | Single-judge benchmarks introduce systematic noise; multi-judge ensembles recommended. | high | 1 (limitations) |
| Hochlehnert et al. (2025) | `fragility2025` | `papers/15-new-statistical-fragility-2025.md` | Single-question swaps shift Pass@1 ≥ 3 pp; bootstrap-CI separability matrix recommended for ranking claims. | high | 4 |
| Bishop (2006) PRML | `bishop2006prml` | `textbooks/bishop-prml.md` | Canonical method-class taxonomy; method-selection grounding for VB_*, BAYES_REG, LOG_ML, DIRICHLET_*. | high | 2 |

**Total unique sources cited across the 5 RQs: 13 papers + 1 textbook = 14
of 22 vault sources.** Wei (2022), Chen (2022), and the remaining 6
textbooks (Bolstad, Ghosh, Hoff, Carlin & Louis, Goldstein & Wooff, Lee)
appear in methodology-continuity prose but are not directly cited in
RQ formulations.

---

## Open verification items

| # | Claim or citation | Required action before paper submission |
|---|---|---|
| 1 | ~~Krippendorff α threshold table (≥ 0.667 tentative, ≥ 0.800 unqualified)…~~ | **RESOLVED 2026-05-03.** `experiments/results_v2/krippendorff_agreement.json` cleaned: removed `_methodology_citation` (Park et al.) and `thresholds` block; replaced `interpretation` labels with threshold-free CI-vs-zero language ("positive_agreement" / "indistinguishable_from_chance" / "systematic_disagreement"). Added `_methodology_note` referencing Krippendorff (2004, 2013) directly + Feuer et al. (2025) for single-judge limitation. Mirror in `capstone-website/backend/static_data/` synced. |
| 2 | ~~Bibtex key `wang2025icecream` actually points to Du et al. (Ice Cream)…~~ | **RESOLVED 2026-05-03.** Bibtex key renamed `wang2025icecream` → `du2025icecream`. Vault note `papers/09-new-ice-cream-causal-2025.md` updated (bibtex key field, Citation-in-poster, Citation-in-paper, Authors comment). README + poster-citations updated to "Du et al. (2025)". static_data mirror synced. |
| 3 | ~~Bibtex key `park2025judge` actually points to Yamauchi et al.~~ | **VERIFIED 2026-05-03 (no rename).** Bibtex key `park2025judge` retained for citation stability per Day-3 housekeeping convention; bibtex `author={...}` field correctly says "Yamauchi" so any LaTeX `\cite{park2025judge}` resolves to "Yamauchi et al." in printed references. All in-text references across project use "Yamauchi et al. (2025)". No further action needed pre-submission unless reviewer queries the key mismatch. |
| 4 | ~~Boye & Moell — bibtex year 2026 vs arXiv Feb 2025…~~ | **RESOLVED 2026-05-03.** Bibtex key renamed `mathfail2026` → `mathfail2025`; year field updated `2026 → 2025`. Vault note `papers/13-new-math-reasoning-failures-2026.md` Year + Citation-in-poster + Citation-in-paper + Bibtex-key fields all aligned to 2025. Filename retains legacy `-2026` suffix for stability (logged in metadata). README + poster-citations + audit/literature_comparison.md + audit/personal_todo_status.md updated. static_data mirror synced. |
| 5 | The 22.16% combined keyword-judge disagreement uses `pct_pass_flip` from `combined_pass_flip_analysis.json`; the older 25.02% uses base-only `keyword_vs_judge_agreement.json`. Both are canonical at their own scope. | Paper should pick one for the headline (recommend 22.16%, larger denominator) and footnote the other. Website currently shows both via the `useKeyFindings` hook. |
| 6 | Gemini "all 246 base responses unstated" — verify this exactly matches `calibration.json` per_bucket counts (gemini.unstated.n = 246 expected). | Pre-paper sanity check: confirm gemini bucket totals sum to 246. |
| 7 | Phase 1C self-consistency cost reported as $11.688 in `recompute_log.md`; verify this matches the run-log artifacts before citing in paper. | Cross-check `experiments/results_v2/self_consistency_runs.jsonl` token counts against vendor-quoted $/M-token rates. |

---

## Convergence patterns across RQs

The same paper supports multiple RQs in several places — these
cross-references strengthen the paper's narrative and should be
foregrounded in the Discussion section.

- **Boye & Moell (2025)** supports both RQ2 (REGRESSION-cluster failure)
  and RQ3 (assumption-violation as dominant L1). Their multi-domain
  catalogue is the single strongest external corroboration of the
  failure-mode story reported here.
- **Du et al. (2025)** "Ice Cream" supports RQ3's 46.85% headline with
  a near-identical 47% from causal inference. Two domains, same
  failure-mode share — strong external validity claim available.
- **Yamauchi et al. (2025)** supports RQ1 (metric choice) and is
  cross-referenced in the judge-validation methodology and limitations
  framing of this work. Crucial that paper prose distinguishes
  *metric choice*
  (supported) from *threshold attribution* (NOT supported by vault).
- **Hochlehnert et al. (2025)** is the load-bearing citation for
  bootstrap-CI separability across RQ1 (CI on Krippendorff α) and RQ4
  (CI on accuracy / robustness). Their "single-question swaps shift
  Pass@1 ≥ 3 pp" finding is the same noise-scale observed here.
- **Wang et al. (2026)** Multi-Answer is the load-bearing citation for
  RQ5's verbalized-vs-consistency dichotomy. Future work toward
  token-logprob calibration also cites this paper.
- **Liu et al. (2025)** MathEval supports RQ1 (multi-dimensional rubric
  baseline) and RQ2 (category-level aggregation convention). The
  multi-dimensional decomposition is a defining methodological
  borrow from MathEval.
