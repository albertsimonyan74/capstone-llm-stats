# Poster figures — DS 299 capstone

**Title:** Reason or pattern-match? Dimensional evaluation of LLM Bayesian reasoning
**Format:** A0 vertical (841 × 1189 mm), light theme, HTML/CSS poster
**Output:** SVG primary + PNG@600dpi fallback per figure

## Figure inventory

| # | Figure                              | Generator                                              | Source data / derived                                                                  | Status                             |
|---|-------------------------------------|--------------------------------------------------------|----------------------------------------------------------------------------------------|------------------------------------|
| 1 | NMACR weight bar                    | nmacr_weights_print.py                                 | hardcoded weights (A=30, R=25, M=20, C=15, N=10)                                       | DONE                               |
| 2 | Krippendorff α gradient strip       | krippendorff_strip_print.py                            | experiments/results_v2/krippendorff_agreement.json                                     | DONE                               |
| 3 | Disagreement matrix 2×2             | disagreement_matrix_print.py + derive_disagreement_matrix_2x2.py | poster/figures/derived/disagreement_matrix_2x2.json (n=2,850 combined eligible) | DONE                               |
| 4 | 4-panel keyword × judge heatmap     | keyword_judge_heatmap_4panel_print.py + derive_keyword_judge_heatmap_4panel.py | poster/figures/derived/keyword_judge_heatmap_4panel.json (n=1,230 base joined) | DONE                               |
| 5 | 3-panel dimension leaderboard       | dimension_leaderboard_print.py                         | bootstrap_ci.json + robustness_v2.json + calibration.json                              | DONE                               |
| 6 | Robustness Δ heatmap (38 × 5)       | robustness_heatmap_print.py + derive_robustness_heatmap.py | poster/figures/derived/robustness_heatmap_data.json (aggregated from robustness_v2.json:per_task_type_heatmap) | DONE |
| 7 | Verbalized vs self-consistency ECE  | calibration_ece_paired_print.py                        | calibration.json + self_consistency_calibration.json                                   | DONE                               |
| 8 | Failure taxonomy stacked            | failure_taxonomy_stacked_print.py + derive_failure_taxonomy_per_task.py | poster/figures/derived/failure_taxonomy_per_task.json (n=143 audited) | DONE                               |

## Conventions

- All figures use `apply_print_theme()` from `print_theme.py`
- Model colors via `MODEL_COLORS_PRINT` (darker -600 tailwind shades)
- Dual-save via `dual_save(fig, basename)` to `poster/figures/`
- Fonts kept as text in SVG (`svg.fonttype: none`) — selectable, lossless
- Figsize chosen for poster column width: ~14 inches for full-width rows

## Phase status

- [x] Phase 1: scaffold + print theme + dimension leaderboard
- [x] Phase 2: NMACR weights, Krippendorff strip, 4-panel heatmap, 2×2 disagreement matrix
- [x] Phase 3: robustness heatmap, calibration ECE paired, failure taxonomy stacked
- [ ] Phase 4: HTML poster assembly
