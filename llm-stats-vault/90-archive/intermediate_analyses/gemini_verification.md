# Gemini Verification — Why does Gemini lead reasoning_quality?

Read-only diagnostic. Phase 1B's literature-derived NMACR weights moved
Gemini to #1 on accuracy. Mechanism: R is now weighted 25% (not 20%) and
Gemini's `reasoning_quality` mean is 0.956 (highest of 5 models). This
audit checks whether that ranking shift reflects genuine reasoning
strength or a scoring artifact.

Source data: `experiments/results_v2/llm_judge_scores_full.jsonl` (1230
records), `experiments/results_v1/runs.jsonl` (1230 raw responses),
`evaluation/llm_judge_rubric.py` (judge prompt).

---

## D1 — Per-task-type reasoning_quality breakdown

**Question.** Does Gemini lead RQ uniformly, or only on a few task types?

**Method.** Computed per-(task_type, model) mean RQ from
`llm_judge_scores_full.jsonl`, using `task_type_from_id()`. Tied #1 counted
as winning (max within numerical tolerance 1e-6).

**Data.**
- 38 task types analysed.
- Gemini at #1 (clean lead): **9 / 38**
- Gemini tied for #1: **25 / 38**
- Gemini below #1: **4 / 38** (MINIMAX, MSE_COMPARE, OPT_SCALED, ORDER_STAT —
  all by Δ = 0.031, i.e. one sub-criterion of 0.25 difference averaged
  over a small task family)
- Combined "at the top": **34 / 38** task types.

**Interpretation.** Gemini's RQ lead is **near-uniform across task types**.
The 4 losses are all by a single 0.25-credit RQ sub-criterion difference
on small task families. Robust finding under the "uniform across all 38
task types" criterion.

---

## D2 — Response length analysis

**Question.** Are Gemini's responses much longer than other models', and
is RQ correlated with length?

**Method.** For each base run, computed `len(raw_response)` in chars.
Pearson r between length and RQ, per model and pooled.

**Data — per-model length (base runs, n=246/model).**

| Model    | Mean chars | Median chars |
|----------|-----------:|-------------:|
| claude   |      1 685 |        1 552 |
| chatgpt  |      1 682 |        1 624 |
| **gemini** | **4 187** |    **3 178** |
| deepseek |      1 783 |        1 778 |
| mistral  |      1 863 |        1 863 |

Gemini's mean response is **2.4× longer** than the other-four mean.

**Data — length × RQ Pearson r.**

| Scope          |   r    |
|----------------|-------:|
| claude         | 0.220 |
| chatgpt        | 0.224 |
| gemini         | **0.012** |
| deepseek       | 0.283 |
| mistral        | 0.241 |
| pooled (all)   | 0.184 |

**Interpretation.** Two findings pull in opposite directions.
1. Gemini's responses are **dramatically longer** than the cohort.
   The judge prompt rewards "(a) shows mathematical work step by step"
   and "(d) interprets the result in plain language" — both are easier
   to satisfy in long responses. Cross-model bias is plausible.
2. **Within Gemini**, length and RQ are uncorrelated (r ≈ 0.012). So
   Gemini doesn't just "ride length" — its high-RQ runs are not its
   long ones, and its low-RQ runs are not its short ones.
3. Pooled r = 0.184 is moderate-low: length explains some RQ variation
   across all models, but is not a dominant driver.

**Caveat to disclose.** Cross-model length bias is a plausible
contributor to Gemini's mean-RQ lead but does not explain Gemini's
within-model RQ variance. Worth noting in Limitations.

---

## D3 — RQ vs assumption_compliance correlation

**Question.** Does Gemini score high on RQ despite low on A
(suggesting RQ is decoupled from substantive Bayesian content)?

**Method.** Pearson r between per-run RQ and per-run A scores, per model.

**Data.**

| Model    | r(RQ, A) | n    |
|----------|---------:|-----:|
| claude   |  0.492 | 246 |
| chatgpt  |  0.573 | 246 |
| **gemini** |  **0.453** | 246 |
| deepseek |  0.552 | 246 |
| mistral  |  0.492 | 246 |

**Interpretation.** Gemini's RQ-A correlation (0.453) is on the **low end
of the cohort** but not dramatically decoupled. The cohort range is
[0.45, 0.57]. Gemini's RQ is meaningfully tied to assumption articulation —
just slightly less than chatgpt or deepseek. Not artifact-level decoupling.

---

## D4 — Hand spot-check: 5 high-RQ low-A Gemini responses

**Question.** Sampled 5 Gemini runs with RQ > 0.9 AND A < 0.3. Are these
substantively reasoned, or verbose-but-shallow?

**Method.** Filtered candidates from `llm_judge_scores_full.jsonl`,
shuffled with `random.Random(42)`, took the first 5. Read each response
text.

68 candidates total — i.e. ~28% of Gemini's 246 base runs scored
RQ > 0.9 with A < 0.3.

| # | task_id | RQ | A | M | RC | length | Assessment |
|---|---------|---:|--:|--:|---:|-------:|-----------|
| 1 | MARKOV_03 | 1.00 | 0.00 | 1.00 | 1.00 | 1 447 | Substantive. Defines parameters, derives the gambler's-ruin probability formula step by step, computes the powers explicitly. The A=0 reflects no explicit "we assume independent ±£1 steps" sentence — the assumption is used implicitly. |
| 2 | DISC_MEDIAN_01_semantic | 1.00 | 0.00 | 1.00 | 1.00 | 1 614 | Substantive. Restates the posterior PMF, states the discrete-median definition, computes the CDF row by row. A=0 because no explicit "values_are_ordered" sentence. |
| 3 | MLE_MAP_04 | 1.00 | 0.00 | 1.00 | 1.00 | 1 510 | Substantive. Lists data, lists prior parameters, derives MLE from sample proportion, derives MAP from Beta-Binomial conjugacy. A=0 because iid + distributional family not stated as assumptions. |
| 4 | JEFFREYS_02 | 1.00 | 0.00 | 1.00 | 1.00 | 1 940 | Substantive. States Jeffreys prior Beta(0.5, 0.5), states the binomial likelihood, applies Beta-Binomial update mechanically, derives the posterior. A=0 because the regularity conditions for Jeffreys are not stated. |
| 5 | BAYES_RISK_02 | 1.00 | 0.00 | 1.00 | 1.00 | 1 035 | Substantive. States the Bayes-risk formula, expands term-by-term over (θᵢ, π(θᵢ)) pairs, sums. A=0 because no "we assume the prior is correct" sentence. |

**Interpretation.** **5 / 5 are substantively reasoned.** Every one
contains real Bayesian or stochastic-process derivation steps that match
the ground-truth method. The A=0 score reflects a genuine failure mode
(missing explicit assumption articulation) — exactly the RQ3 finding —
not a Gemini-specific artifact. The judge is rewarding correct
substantive reasoning while correctly penalising missing assumption
statements.

This is the strongest single piece of evidence that Gemini's RQ lead is
real. Lengths range 1 035 – 1 940 chars (below Gemini's 4 187 mean),
showing the high-RQ-low-A subset is not skewed toward Gemini's longest
responses.

---

## D5 — RQ vs RC gap

**Question.** Phase 1B collapses `reasoning_quality` and
`reasoning_completeness` into R = 25%. Does Gemini have a hidden gap
where RQ is high but RC is lower (suggests judge rewards prose quality
but not actual derivation completeness)?

**Method.** Per-model means of both RQ and RC; report RQ − RC.

**Data.**

| Model    | RQ      | RC      | RQ − RC |
|----------|--------:|--------:|--------:|
| claude   | 0.9217 | 0.9715 | −0.0498 |
| chatgpt  | 0.8750 | 0.9512 | −0.0762 |
| **gemini** | **0.9563** | **0.9878** | **−0.0315** |
| deepseek | 0.8689 | 0.9390 | −0.0701 |
| mistral  | 0.8913 | 0.9593 | −0.0681 |

**Interpretation.** Gemini has the **highest RC AND the highest RQ AND
the smallest RQ-RC gap** of any model. The hypothesised "rewarded for
prose without derivation" mode would show high RQ + lower RC — Gemini
shows the opposite. Reinforces the substantive-finding interpretation.

---

## D6 — Judge prompt audit for length-bias language

**Question.** Does the RQ rubric in `evaluation/llm_judge_rubric.py`
contain language that biases scoring toward longer responses?

**Method.** Read the `JUDGE_PROMPT_TEMPLATE` block. Quote the RQ rubric.

**Quote.**

```
3. REASONING_QUALITY: Score is the fraction of these four sub-criteria
   satisfied:
   (a) shows mathematical work step by step
   (b) identifies the model/distribution being used
   (c) states the relevant formula
   (d) interprets the result in plain language
   Possible scores: 0.0, 0.25, 0.5, 0.75, 1.0
```

```
4. REASONING_COMPLETENESS: Does the response actually walk through the
   reasoning, or just name-drop concepts and produce a number?
   1.0 = full derivation with intermediate steps
   0.5 = partial derivation, some steps skipped
   0.0 = answer-only or suspiciously brief
```

**Assessment.**
- Sub-criterion (a) "shows mathematical work step by step" — length-correlated.
  A 200-char response cannot satisfy this; a 4 000-char response usually does.
- Sub-criterion (d) "interprets the result in plain language" — length-correlated.
  Adding a final-paragraph plain-English summary is ~50–200 chars but
  meaningfully harder for short responses to fit in.
- Sub-criteria (b) and (c) are atomic ("identifies model", "states formula")
  and not length-correlated.
- RC explicitly rewards "full derivation with intermediate steps" and
  penalises "answer-only or suspiciously brief" — strongly length-correlated
  by design.

**Estimate.** 2 of 4 RQ sub-criteria + the RC rubric have length-correlated
criteria. This is consistent with the pooled length × RQ r = 0.184
finding — moderate, not dominant, length contribution. The judge is
**not** length-biased in a pathological way (the within-model length × RQ
correlations are 0.01 – 0.28, not 0.7+), but the cohort-mean comparison
is partly inflated by Gemini's verbosity.

---

## Final summary

### Verdict: **PROCEED (with QUALIFY)**

Gemini's #1 accuracy ranking under literature-derived NMACR weights is
**substantively defensible**:

- D1: Gemini at top in **34 / 38** task types — near-uniform lead, not
  concentrated. The 4 task-type losses are by a single sub-criterion
  Δ = 0.031.
- D3: RQ × A correlation 0.453 — on the low end of the cohort but not
  decoupled. Within the [0.45, 0.57] cohort range.
- D4: **5 / 5 hand-checked high-RQ low-A Gemini responses are
  substantively reasoned**. They lose A because they skip assumption
  articulation — the same failure mode RQ3 documents across all
  models, not a Gemini-specific artifact.
- D5: Gemini has the **highest RC AND highest RQ AND smallest RQ-RC
  gap** — opposite of the "rewarded for prose without derivation" mode.

Two qualifications must be disclosed:

- D2: **Gemini's responses are 2.4× longer** than the cohort. Two of
  the four RQ sub-criteria ((a) shows work, (d) interprets) and the RC
  rubric have length-correlated criteria. This contributes to (but does
  not solely drive) Gemini's RQ lead. Pooled length × RQ r = 0.184.
- D6: Judge prompt has length-correlated language in 2 of 4 RQ
  sub-criteria + the entire RC criterion. Disclose this as a
  judge-design caveat.

### Recommended action: **PROCEED to Phase 1C with QUALIFY**

Do not adjust weights or re-prompt the judge. Move to Phase 1C as planned.
Add the two qualifications below to the limitations disclosure (already
in `audit/limitations_disclosures.md` — extend with a (f) entry).

### Specific concerns to disclose

**(f) Length-correlated RQ scoring.** Gemini produces responses 2.4×
longer than the cohort mean. Two of four `reasoning_quality`
sub-criteria ("shows mathematical work step by step", "interprets the
result in plain language") and the entire `reasoning_completeness`
rubric reward longer responses by construction. Pooled
length × RQ Pearson r = 0.184 across all 1 230 base runs (within Gemini
specifically, r = 0.012). Gemini's #1 accuracy ranking under
literature-derived NMACR weighting is therefore robust to within-model
analyses (D1, D3, D4, D5) but cohort-mean comparisons should be read
as "Gemini reasons more thoroughly *and* writes more thoroughly" rather
than "Gemini reasons better". Multi-judge ensemble (Phase 1C / paper
scope) and length-controlled sub-analysis are the recommended
follow-ups.

---

## Diagnostic results (one-line summary)

| Diagnostic | Finding |
|------------|---------|
| D1 task-type breakdown | Gemini at top (clean lead or tied) in **34 / 38** task types. |
| D2 response length | Gemini mean = 4 187 chars vs cohort mean ≈ 1 753; length × RQ pooled r = 0.184; within Gemini r = 0.012. |
| D3 RQ-A correlation | Gemini r = 0.453 vs cohort range [0.45, 0.57]. Slightly low but not decoupled. |
| D4 hand-spot check | **5 / 5 substantive**, 0 / 5 surface. A=0 reflects missing assumption articulation, not absent reasoning. |
| D5 RQ vs RC gap | Gemini RQ−RC = −0.0315 (smallest gap; highest RC AND highest RQ). |
| D6 judge prompt audit | 2 of 4 RQ sub-criteria + entire RC rubric have length-correlated criteria. Quoted in section. |

**VERDICT: PROCEED (with QUALIFY)**

**CONCERNS TO DISCLOSE:** (f) length-correlated RQ scoring; cohort-mean
comparison conflates "reasons more" and "writes more". Multi-judge
ensemble + length-controlled sub-analysis recommended as follow-up.
