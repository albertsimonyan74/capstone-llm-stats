# V1 Perturbation Deprecation — STOP Gate Diff Report

**Date:** 2026-05-04
**Baseline:** `v1_deprecation_baseline_20260504_001522`
**Threshold:** 0.0001 (0.01pp)
**Result:** **STOP GATE TRIGGERED** — 1,075 numerical changes across 7 canonical files

## Root cause

v1 perturbation rows (75 task_ids × 5 models = 375 rows) were historically appended into
`experiments/results_v1/runs.jsonl` and silently included in the 'base' scope of every
downstream analysis. Filtering them out (Option (a) consumer-side filter) is the correct
mathematical operation but **changes every base-scope headline number** because the v1-pert
rows were inflating both the denominator (n_eligible) and the numerator (per-rater scores).

This is **expected drift**, not a bug — but it requires user review before propagation to
the website (B-2). The new numbers are the methodologically correct ones; the old numbers
represent a base scope contaminated by perturbation rows.

## Headline drift

| metric | baseline | new | delta | note |
|---|---|---|---|---|
| **Krippendorff α (base scope)** |   |   |   |   |
| base n_eligible | 1095.0000 | 750.0000 | -345.0000 | drop of 345 |
| α assumption | 0.5502 | 0.5730 | +0.0228 | still moderate |
| α reasoning_quality | -0.0989 | -0.1246 | -0.0257 | more negative |
| α method_structure | -0.0420 | -0.0090 | +0.0331 | less negative |
| **Combined pass-flip** |   |   |   |   |
| combined pct_pass_flip | 0.2216 | 0.2074 | -0.0142 | **22.16% → 20.74%** |
| combined n_eligible | 3195.0000 | 2850.0000 | -345.0000 | 3,195 → 2,850 |
| base pct_pass_flip | 0.2502 | 0.2093 | -0.0409 | 25.0% → 20.9% |
| **Accuracy means** |   |   |   |   |
| acc claude | 0.6945 | 0.6976 | +0.0031 |  |
| acc chatgpt | 0.6735 | 0.6733 | -0.0003 |  |
| acc gemini | 0.7326 | 0.7314 | -0.0012 |  |
| acc deepseek | 0.6501 | 0.6686 | +0.0185 |  |
| acc mistral | 0.6582 | 0.6676 | +0.0094 |  |
| **Robustness Δ** |   |   |   |   |
| rob claude | 0.0285 | 0.0305 | +0.0020 |  |
| rob chatgpt | 0.0019 | 0.0003 | -0.0016 |  |
| rob gemini | 0.0110 | 0.0129 | +0.0019 |  |
| rob deepseek | 0.0352 | 0.0388 | +0.0036 |  |
| rob mistral | -0.0040 | 0.0013 | +0.0052 |  |
| **Verbalized ECE** |   |   |   |   |
| ece claude | 0.0666 | 0.0334 | -0.0332 |  |
| ece chatgpt | 0.0626 | 0.0339 | -0.0287 |  |
| ece gemini | 0.0973 | 0.0765 | -0.0208 |  |
| ece deepseek | 0.1795 | 0.1977 | +0.0182 |  |
| ece mistral | 0.0840 | 0.0811 | -0.0029 |  |

## Robustness ranking change

**Old ranking (Mistral #1):**
1. Mistral Δ=-0.0040
2. ChatGPT Δ=+0.0019
3. Gemini Δ=+0.0129
4. Claude Δ=+0.0285
5. DeepSeek Δ=+0.0388

**New ranking (ChatGPT #1):**
1. ChatGPT Δ=+0.0003
2. Mistral Δ=+0.0013
3. Gemini Δ=+0.0129
4. Claude Δ=+0.0305
5. DeepSeek Δ=+0.0388

ChatGPT and Mistral swap #1/#2 — both effectively zero (CI crosses zero).

## Files affected

| file | numerical changes | notable |
|---|---|---|
| krippendorff_agreement.json | 220 | n: 1095→750; α reasoning -0.099→-0.125 |
| keyword_vs_judge_agreement.json | 542 | n: 1095→750; per-model & per-task-type all shift |
| combined_pass_flip_analysis.json | 53 | combined pct: 22.16%→20.74% |
| bootstrap_ci.json | 45 | accuracy n: 246→171; robustness ranking shuffle |
| robustness_v2.json | 144 | n_perturbations: 2365→1990 |
| calibration.json | 46 | per-model ECE shifts (e.g. chatgpt 0.063→0.034) |
| per_dim_calibration.json | 25 | per-dim ECE shifts (small but >0.01pp) |

## Recommended next step

This is a methodology correction with significant downstream impact. Options:

1. **ACCEPT the drift.** Commit the engineering layer (B-1) with new canonical numbers,
   then run B-2 to update audit + vault + frontend with corrected figures. The new numbers
   are the methodologically sound ones (true base scope).

2. **REVERT.** `git checkout` the modified scripts + canonical files. v1-pert rows stay
   in 'base' scope. Status-quo preserved.

3. **PARTIAL.** Commit script edits + backend filter only (production /api/runs returns
   855 base rows correctly), but defer canonical-file regeneration until after wider review.
   Frontend numbers stay stale until B-2.

All three options are reversible via git. No commits or pushes have been made.
