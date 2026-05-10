# Tier 1 STOP-gate diff report

**Date:** 2026-05-03
**Baseline snapshot:** `audit/tier1_baseline_20260503_195141/`
**Threshold:** any headline change ≥0.5pp triggers user review.

## Executive verdict

**STOP gate triggered.** Three classes of headline changes ≥0.5pp:

1. **Krippendorff α reasoning_quality (base):** previously n=460 (gemini-excluded). Now n=1,095. Coverage fix.
2. **Per-model accuracy (literature-weighted):** all 5 models shifted on the order of 0.5–2pp because Fix B repopulated Gemini confidence/reasoning, and Fix A repopulated 110 records/model on Phase 2 + perturbations. Affects `bootstrap_ci.json`.
3. **Per-model robustness deltas:** corresponding shifts because base and perturbation aggregate scores both moved.

The 22.16% combined keyword-judge disagreement headline is **unchanged** — it depends on assumption_score (keyword) and judge_assumption, neither of which Fix A/B touched. Stable.

---

## Detailed diff: Krippendorff α (overall — base scope)

| dim | baseline α | new α | Δα | baseline n | new n | baseline CI | new CI |
|---|---|---|---|---|---|---|---|
| method_structure | −0.0420 | −0.0420 | 0.0000 | 1,095 | 1,095 | [−0.097, +0.015] | [−0.097, +0.015] |
| assumption_compliance | +0.5502 | +0.5502 | 0.0000 | 1,095 | 1,095 | [+0.504, +0.595] | [+0.504, +0.595] |
| reasoning_quality | **−0.1330** | **−0.0985** | **+0.0345** | **460** | **1,095** | [−0.228, −0.039] | [−0.152, −0.045] |

**reasoning_quality interpretation unchanged:** still negative, CI still excludes zero from below → "systematic disagreement (worse than chance)". But severity reduced; n more than doubled.

## New scope: α perturbation + combined

| dim | base α (n=1095) | perturbation α (n=2100) | combined α (n=3195) |
|---|---|---|---|
| method_structure | −0.042 [−0.097, +0.015] | −0.003 [−0.043, +0.039] | −0.016 [−0.048, +0.016] |
| assumption_compliance | +0.550 [+0.504, +0.595] | +0.634 [+0.605, +0.664] | +0.605 [+0.580, +0.632] |
| reasoning_quality | −0.099 [−0.152, −0.045] | −0.070 [−0.110, −0.032] | −0.080 [−0.114, −0.046] |

**Headline impact:** combined α on assumption_compliance is **+0.605** (slightly *higher* than base-only +0.550). Combined narrative now matches the disagreement headline scope.

---

## Detailed diff: bootstrap_ci.json (per-model accuracy, literature-weighted)

| model | baseline mean | new mean | Δ pp | baseline CI | new CI |
|---|---|---|---|---|---|
| claude | 0.7122 | 0.6945 | **−1.78** | [0.689, 0.736] | [0.672, 0.717] |
| chatgpt | 0.6913 | 0.6735 | **−1.78** | [0.668, 0.715] | [0.651, 0.696] |
| gemini | 0.7763 | 0.7326 | **−4.37** | [0.753, 0.799] | [0.712, 0.753] |
| deepseek | 0.6630 | 0.6501 | **−1.29** | [0.639, 0.686] | [0.627, 0.673] |
| mistral | 0.6754 | 0.6582 | **−1.72** | [0.652, 0.699] | [0.636, 0.680] |

**Ranking unchanged:** gemini > claude > chatgpt > mistral > deepseek. Top-1 lead (gemini vs claude) narrows from 6.4pp → 3.8pp under corrected scoring.

## Detailed diff: robustness_v2.json (per-model deltas)

| model | baseline delta | new delta | Δ pp | baseline rank | new rank |
|---|---|---|---|---|---|
| mistral | 0.0070 | **−0.0040** | **−1.10** | 1 | 1 |
| chatgpt | 0.0114 | 0.0019 | −0.95 | 2 | 2 |
| claude | 0.0401 | 0.0285 | −1.16 | 3 | 3 |
| deepseek | 0.0423 | 0.0352 | −0.71 | 4 | 5 |
| gemini | 0.0568 | 0.0110 | **−4.58** | 5 | 4 |

**Two narrative shifts:**
- **Mistral now has *negative* delta** (perturbations slightly improve mistral). Was +0.007.
- **Gemini robustness improves dramatically** (delta 0.057 → 0.011 = 5.2× tighter). Was rank-5 worst-robustness; now rank-4 with delta below claude.

## Detailed diff: calibration.json (accuracy-calibration correlation)

| model | baseline | new | note |
|---|---|---|---|
| claude | 0.491 | 0.427 | small drop |
| chatgpt | 0.371 | 0.345 | small drop |
| gemini | **n/a** | **0.337** | **HEADLINE: Gemini calibration newly measurable** |
| deepseek | 0.347 | 0.311 | small drop |
| mistral | 0.476 | 0.378 | non-trivial drop (−9.8pp) |

The "Gemini specifically returned 0 verbalized confidence signals" claim in `Limitations.jsx` Caveat 2 and `audit/recompute_log.md` is **falsified** by Fix B. Gemini's raw responses contain extractable confidence; prior result was an artifact of the runner schema gap.

---

## Detailed diff: calibration.json (accuracy_calibration_correlation)

| model | baseline | new | note |
|---|---|---|---|
| claude | 0.4259 | 0.4270 | small |
| chatgpt | 0.3712 | 0.3445 | small |
| gemini | **n/a (all confidence unstated)** | **0.3368** | **HEADLINE CHANGE — Gemini now has confidence signal** |
| deepseek | 0.3473 | 0.3107 | small |
| mistral | 0.4762 | 0.3782 | non-trivial drop |

**Critical finding:** Limitations.jsx Caveat 2 (and audit/recompute_log.md) state: *"Gemini specifically returned 0 verbalized confidence signals across 246 base runs and is excluded from the accuracy-calibration correlation."* This claim is **falsified** by Fix B. Gemini's raw responses contain extractable confidence; the prior "0 signals" finding was an artifact of the runner schema gap, not a property of Gemini.

This is a **research-finding-level change**, not a wording fix.

---

## Decision required from user

Two options:

### Option 1 — accept the corrected numbers as canonical
Update audit, vault, website, paper to reflect:
- Gemini calibration is measurable (correlation ≈ 0.34)
- α reasoning_quality narrative softens (still negative, but n doubled and effect smaller)
- α now reported on three scopes
- Per-model accuracy shifts under literature weighting

This is the technically-honest path. The pre-fix numbers were artifacts of two compounding bugs (runner schema gap + stale recompute path), not properties of the data.

### Option 2 — quarantine the corrected numbers, ship the prior canonical
Keep the original `bootstrap_ci.json`, `calibration.json`, `robustness_v2.json` as canonical for the IEEE paper deadline. Document the correction as paper-scope future work. Risk: the correction is genuine, and if a reviewer audits the data, the discrepancy surfaces.

### Option 3 — partial (recommended for poster)
- Adopt Fix C (α extension) and Fix D (Limitations wording) — pure additions / clarifications, no headline shift.
- Hold Fix A + Fix B until poster is locked. Post-poster, apply A+B and update everything.

---

## Files changed (uncommitted, currently in working tree)

| file | nature |
|---|---|
| scripts/recompute_scores.py | code: tasks_all + perturbations |
| scripts/krippendorff_agreement.py | code: 3-scope output |
| experiments/results_v1/runs.jsonl | data: full coverage on reasoning + confidence |
| experiments/results_v2/krippendorff_agreement.json | data: 3-scope schema, reasoning_quality α shifted |
| experiments/results_v2/keyword_vs_judge_agreement.json | data: alpha_overall augmented |
| experiments/results_v2/nmacr_scores_v2.jsonl | data: regenerated |
| experiments/results_v2/bootstrap_ci.json | data: regenerated under Fix A+B |
| experiments/results_v2/robustness_v2.json | data: regenerated |
| experiments/results_v2/per_dim_calibration.json | data: regenerated |
| experiments/results_v2/calibration.json | data: gemini correlation now present |
| experiments/results_v2/combined_pass_flip_analysis.json | unchanged (verified) |
| capstone-website/frontend/src/pages/Limitations.jsx | wording: MARKOV_04 + 27-task disclosure |
| audit/gemini_forensic_2026-05-03.md | NEW: forensic investigation log |
| audit/tier1_baseline_20260503_195141/ | NEW: baseline snapshot for comparison |
| audit/tier1_diff_report.md | NEW: this file |

Pre-fix `runs.jsonl` retained at `experiments/results_v1/runs.jsonl.pre_tier1_<timestamp>` for rollback if Option 2 chosen.

No commits made yet. No website / vault propagation made yet. Halted at STOP gate per user's safety protocol.
