---
tags: [home, narrative, canonical]
date: 2026-05-01
status: canonical
---

# Research Narrative — DS 299 Capstone

Single source of truth for the project's research structure. Audit docs,
poster, paper, and website all defer to this document for the canonical
shape of the work. Updated under Phase 1B (literature-derived NMACR
weighting + RQ4 Layer 2 / RQ5 Layer 4-5 enhancements).

---

## 1. Research arc — 9 steps

1. **Idea.** Benchmark frontier LLMs on a domain that distinguishes
   surface fluency from genuine reasoning.
2. **Domain choice.** Bayesian and inferential statistics — a domain with
   closed-form ground truth, multi-step derivations, and explicit assumptions.
3. **Framework.** 171 tasks across 38 task types (136 Phase 1 conjugate /
   frequentist + 35 Phase 2 computational Bayes), 5 frontier LLMs (Claude
   Sonnet 4.5, Gemini 2.5 Flash, GPT-4.1, DeepSeek V4, Mistral Large), the
   N·M·A·C·R rubric, and an external Llama 3.3 70B Instruct judge.
4. **Data collection.** 1,230 base runs + 2,365 perturbation runs = **3,595**
   scored runs. 1,230 of those judged by the external Llama judge.
5. **Aggregate analysis.** Literature-derived NMACR weighting
   (A=0.30, R=0.25, M=0.20, C=0.15, N=0.10) with bootstrap-CI separability
   tests (B=10 000, seed=42) and Krippendorff α inter-rater reliability.
6. **Findings.** Organised by RQ1 (PRIMARY methodology) and
   RQ2-5 (SUPPORTING evidence). See §3 below.
7. **Public artifact.** [bayes-benchmark.vercel.app](https://bayes-benchmark.vercel.app)
   — live deployment with poster companion at `/poster`.
8. **Poster.** May 8 deadline. Future-work section here.
9. **IEEE paper.** Future work. Future-work section here.

---

## 2. NMACR rubric

Five-dimensional rubric. Each response scored on five dimensions, each in
`[0, 1]`. The aggregate is the literature-weighted sum.

### Dimensions

| Dim | Name                   | Source path                              |
|-----|------------------------|------------------------------------------|
| N   | Numerical Correctness  | keyword `numeric_score`                   |
| M   | Method Selection       | judge `method_structure.score` ⊕ keyword |
| A   | Assumption Compliance  | judge `assumption_compliance.score` ⊕ keyword |
| C   | Confidence Calibration | keyword `confidence_score`                |
| R   | Reasoning Quality      | judge mean(`reasoning_quality`, `reasoning_completeness`) ⊕ keyword |

`⊕` = judge supersedes keyword when judge record exists.

### Weights — literature-derived

```
A = 0.30
R = 0.25
M = 0.20
C = 0.15
N = 0.10
Σ = 1.00
```

### Per-dimension literature defense

- **A = 0.30.** Du et al. (2025) "Ice Cream" reproduces ~47% assumption-violation
  share on causal-inference tasks. Boye & Moell (2025) catalogue
  unwarranted-assumption as a top failure mode in math-reasoning. Yamauchi
  et al. (2025) flag assumption articulation as the dimension where
  keyword and judge disagree most. Empirically our taxonomy confirms 46.9%
  of failures are assumption violations — heaviest weight justified.
- **R = 0.25.** Yamauchi et al. (2025) show reasoning-quality is the most
  externally-judgeable dimension (others are partly mechanical).
  ReasonBench (Au et al. 2025) treat reasoning instability as a first-class
  evaluation axis. Boye & Moell (2025) cite reasoning-completeness gaps
  as a load-bearing failure mode.
- **M = 0.20.** Wei et al. (2022, CoT) and Chen et al. (2022, PoT)
  established that method selection is observable from the prompt response;
  Bishop (2006) provides the canonical method-class taxonomy. Partially
  redundant with R (a correct derivation often implies the right method),
  hence moderate weight.
- **C = 0.15.** Nagarkar et al. (2026), FermiEval (2025), and Multi-Answer
  Confidence (2026) frame calibration as a separate evaluation track —
  important but not co-equal with reasoning. Keyword extraction is the
  weakest of the three baselines they review; we therefore weight this
  honestly, not heavily.
- **N = 0.10.** Liu et al. (2025, MathEval) and Boye & Moell (2025) treat
  numerical correctness as necessary but trivially checkable: it does not
  distinguish surface arithmetic from genuine derivation. Lowest weight
  reflects this.

### CONCEPTUAL handling
Tasks tagged CONCEPTUAL have no numeric target. Their N dimension is
absent; the remaining four weights are renormalised to 1.0. Mirrors
[`llm_runner/response_parser.py:full_score()`](../../llm_runner/response_parser.py).

---

## 3. Research questions

### RQ1 (PRIMARY) — How does external-judge validation differ from keyword scoring?
- **NMACR mapping:** RQ1 cross-validates **all 5** NMACR dimensions
  against the external Llama 3.3 70B judge.
- **Headline:** 25.0% keyword-judge disagreement on `assumption_compliance`
  (274 / 1095 runs). Krippendorff α = 0.55 (95% CI [0.504, 0.595]) —
  questionable agreement under Park et al. (2025) thresholds.
  Spearman ρ = 0.59. Both metrics agree: keyword and judge are not
  interchangeable raters.
- **Literature backbone:** Yamauchi et al. (2025) [arXiv:2506.13639]
  for the α-over-ρ recommendation; Liu et al. (2025) for the
  multi-dimensional rubric baseline.

### RQ2 (SUPPORTING) — Which Bayesian categories are hardest?
- **NMACR mapping:** RQ2 aggregates `aggregate_new` by Bayesian task category.
- **Headline:** REGRESSION cluster mean accuracy ~0.30 across all 5 models.
  MCMC and ADVANCED clusters also score below cohort mean.
- **Literature backbone:** Liu et al. (2025) for the category convention;
  Boye & Moell (2025) for the unwarranted-assumption alignment with
  REGRESSION drops.

### RQ3 (SUPPORTING) — What is the dominant failure mode?
- **NMACR mapping:** L1 taxonomy as failure decomposition over NMACR
  dimensions. See §4.
- **Headline:** ASSUMPTION_VIOLATION = 46.9% of 143 base failures
  (vs MATHEMATICAL_ERROR 33.6%, FORMATTING 12.6%, CONCEPTUAL 7.0%,
  HALLUCINATION 0).
- **Literature backbone:** Du et al. (2025) ~47% independent reproduction
  on causal-inference tasks; Boye & Moell (2025) confirm
  unwarranted-assumption as a top mode across general math domains.

### RQ4 (SUPPORTING) — Are accuracy rankings robust to prompt perturbation?
- **NMACR mapping:** Two layers.
  - **Layer 1 (existing):** aggregate robustness Δ per model.
  - **Layer 2 (NEW Phase 1B):** per-dimension robustness Δ per model
    (5 models × 5 dims = 25 deltas), exposed in `robustness_v2.json` →
    `per_dim_delta`.
- **Headline:** Three orthogonal rankings — accuracy ≠ robustness ≠
  calibration. ChatGPT and DeepSeek noise-equivalent on aggregate
  robustness (Δ ≈ 0); Mistral degrades most on numerical and method
  dimensions.
- **Literature backbone:** ReasonBench (2025) variance-as-first-class;
  BrittleBench (2026) perturbation taxonomy; Statistical Fragility (2025,
  Hochlehnert et al., arXiv:2504.07086) for separability tests.

### RQ5 (SUPPORTING) — Confidence Calibration

**Question.** Is the C dimension of NMACR (confidence calibration)
reliably measurable across extraction methods?

**Mapping.** Directly evaluates the C dimension across two extraction
methods (verbalized + consistency), with Phase 1B Layer 4
(accuracy-calibration correlation) and Layer 5 (per-dimension calibration)
as supporting evidence.

**Headline finding.** Method-dependent, with substantively different
conclusions:

- **Verbalized extraction** (keyword-based, n=1,230 base runs).
  Hedge-heavy. Gemini produces 0 verbalized confidence signals; the
  other 4 models produce some, but the high-confidence bucket is sparse
  across the board. ECE: 0.063–0.180.
- **Consistency extraction** (3-rerun agreement at T=0.7, n=2,415 across
  161 numeric-target tasks — Phase 1C). All 5 models severely
  overconfident. Confident agreement does NOT predict accuracy. ECE:
  0.618–0.734.

| Model    | Verbalized ECE | Consistency ECE (full) |
|----------|---------------:|-----------------------:|
| claude   | 0.067          | 0.734                  |
| chatgpt  | 0.063          | 0.721                  |
| gemini   | 0.097          | 0.618                  |
| deepseek | 0.180          | 0.726                  |
| mistral  | 0.084          | 0.663                  |

Gemini, the verbalized-extraction outlier ("0 signals"), produces the
BEST consistency ECE — extreme underconfidence under one method, mid-pack
under another.

**Why SUPPORTING and honest.** This RQ measures the C dimension across
two methods and finds they disagree dramatically. Verbalized extraction
suggests hedging; consistency extraction reveals overconfidence. The
honest answer is "calibration measurement is method-dependent, and our
project surfaces this ambiguity rather than resolving it." Future work
toward token-level logprobs (Multi-Answer Confidence 2026) is the
recommended next-step methodology.

**Coverage limitation.** 10 CONCEPTUAL tasks excluded from consistency
analysis (no numerical answers against which 3-rerun agreement can be
measured). These remain a calibration-measurement gap.

**Phase 1B supporting evidence.** Per-dimension ECE in
`per_dim_calibration.json` (Layer 5); Pearson r between aggregate accuracy
and dim_C positive on the four measurable models (claude 0.49,
mistral 0.48, chatgpt 0.37, deepseek 0.35; gemini not measurable —
all 246 verbalized responses unstated).

**Literature backbone.** FermiEval (2025) — overconfidence on
estimation tasks (consistency extraction confirms in the Bayesian
setting). Multi-Answer Confidence (2026) — verbalized vs consistency
framing. Nagarkar et al. (2026) — reliability motivation.

---

## 4. Failure taxonomy (RQ3 mapping detail)

| L1 bucket               | Count | NMACR-dimension mapping | Note |
|------------------------|-------|--------------------------|------|
| ASSUMPTION_VIOLATION   | 67    | A failure                | Dominant mode (46.9%). Validates A=0.30. |
| MATHEMATICAL_ERROR     | 48    | N failure                | Arithmetic / algebra mistake. |
| FORMATTING_FAILURE     | 18    | **pre-rubric exclusion** | Reported separately as `formatting_failure_rate`. NOT folded into NMACR. |
| CONCEPTUAL_ERROR       | 10    | M failure                | Wrong method / framework choice. |
| HALLUCINATION          | 0     | R + N failure            | Empirically empty across 143 audited failures. See Limitations. |

### `formatting_failure_rate` per model (base, n=246/model)
| Model    | Failures | Rate  |
|----------|----------|-------|
| chatgpt  | 6        | 2.44% |
| claude   | 0        | 0.00% |
| deepseek | 6        | 2.44% |
| gemini   | 1        | 0.41% |
| mistral  | 5        | 2.03% |

Surfaced in `experiments/results_v2/calibration.json` →
`formatting_failure_rate_per_model` and on the aggregate-ranking figure.

---

## 5. Methodology continuity

This benchmark extends StatEval (Lu et al., 2025) from descriptive and
hypothesis-testing statistics to Bayesian inference. Where StatEval uses
multiple-choice format, we adopt free-response with a 5-dimensional rubric
(N·M·A·C·R) following the multi-dimensional convention of MathEval
(Liu et al., 2025). Our prompting baseline follows zero-shot chain-of-thought
(Wei et al., 2022), with Program-of-Thoughts (Chen et al., 2022) considered
and deferred because Bayesian closed-form derivations rely on symbolic
manipulation more than arithmetic. Methodology rigour combines external-judge
validation via Llama 3.3 70B (Yamauchi et al., 2025), bootstrap-CI separability
motivated by Statistical Fragility (Hochlehnert et al., 2025) and Longjohn
et al. (2025), perturbation robustness adapted from BrittleBench (2026), and
the variance-as-first-class framing of ReasonBench (Au et al., 2025).
Calibration concerns are raised by Nagarkar et al. (2026) and contrast with
FermiEval's (2025) overconfidence finding — our Bayesian-task setting
produces hedge-heavy behaviour instead. Limitations around single-judge bias
are framed by Judgment-Becomes-Noise (Feuer et al., 2025); future work
toward multi-judge ensembling and consistency-based confidence (Multi-Answer
Confidence, 2026) is explicitly scoped.

The NMACR weight selection (A=0.30, R=0.25, M=0.20, C=0.15, N=0.10) is
literature-derived rather than equal-weight: Du (2025) + Boye & Moell (2025)
+ Yamauchi (2025) place A as the load-bearing dimension; ReasonBench
(2025) + Yamauchi (2025) elevate R; Wei (2022) + Chen (2022) + Bishop (2006)
weight M moderately given partial redundancy with R; Nagarkar (2026) +
FermiEval (2025) + Multi-Answer (2026) treat C as a separate, honestly-disclosed
track; Liu (2025) + Boye & Moell (2025) place N as necessary but trivially
checkable. See §2 for full per-dimension rationale.

---

## 6. Honest disclosures

- **Single-judge limitation.** All judge-side dimensions are scored by Llama
  3.3 70B Instruct via Together AI. Cite Yamauchi et al. (2025) and Feuer
  et al. (2025) "Judgment Becomes Noise". Multi-judge ensemble is paper-scope
  future work.
- **Empty high-confidence bucket.** Verbalized extraction gives zero
  records claiming p ≥ 0.85 across all five models. The reported ECE is
  a 3-bucket weighted MAE (0.3 / 0.5 / 0.6). Cite Multi-Answer Confidence
  (2026) for the consistency-based upgrade path. Gemini specifically: 0
  responses with any extracted confidence at all (all 246 unstated) —
  documented in `per_dim_calibration.json` and `accuracy_calibration_correlation`.
- **HALLUCINATION = 0 ambiguity.** Zero hallucinations across 143 audited
  failures may reflect either (a) a real property of closed-form Bayesian
  tasks (every task has a deterministic ground truth, models fail by
  skipping assumptions or miscomputing — not by fabricating distributions)
  OR (b) a single-judge classification limitation. Multi-judge ensemble
  required to disambiguate.
- **Self-consistency caveat — RESOLVED via Phase 1C.** The original
  B3 self-consistency proxy was run on 30 top-failure tasks (ECE
  0.33–0.64). Phase 1C expanded to all 161 numeric-target tasks and
  found ECE 0.62–0.73 for all 5 models — B3 was UNDERSTATING
  overconfidence, not overstating it. B3 artefacts archived in
  `llm-stats-vault/90-archive/phase_1c_superseded/`.
- **CONCEPTUAL exclusion from consistency calibration.** 10 of 171
  tasks (CONCEPTUAL_01–10) have no numerical answer; they cannot be
  scored under 3-rerun agreement. Inherent to consistency-based
  confidence extraction; token-level logprobs (Multi-Answer Confidence
  2026) is the recommended upgrade path.
- **Length-correlated RQ scoring (gemini verification).** Gemini's
  responses average 2.4× cohort length. Pooled length–RQ Pearson
  r=0.184 (weak); within-gemini r=0.012 (effectively zero). Hand-checked
  5/5 high-RQ low-A gemini responses are substantively reasoned. The
  cohort-mean RQ comparison should be read as "gemini reasons more
  thoroughly *and* writes more thoroughly". Multi-judge ensemble and
  length-controlled per-task analysis are paper-scope future work.
- **Bootstrap CI separability.** Top-2 accuracy CIs overlap on the
  bootstrap. Top-2 robustness deltas overlap with zero. Cite Statistical
  Fragility (Hochlehnert et al., 2025) — single-question swaps shift
  Pass@1 ≥ 3 pp. Reported point estimates are calibrated, not benchmark
  trophies.

---

## 7. Pointers

- Aggregation locus: [audit/aggregation_locus.md](../../audit/aggregation_locus.md)
- Recompute log: [audit/recompute_log.md](../../audit/recompute_log.md)
- RQ structuring: [audit/rq_restructuring.md](../../audit/rq_restructuring.md)
- Methodology continuity: [audit/methodology_continuity.md](../../audit/methodology_continuity.md)
- Limitations: [audit/limitations_disclosures.md](../../audit/limitations_disclosures.md)
- Literature comparison: [audit/literature_comparison.md](../../audit/literature_comparison.md)
- Literature library: [40-literature/README.md](../40-literature/README.md)
- Citation map: [40-literature/citation-map.md](../40-literature/citation-map.md)
- Sprint archive: [90-archive/](../90-archive/)
