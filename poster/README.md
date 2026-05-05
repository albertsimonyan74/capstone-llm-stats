# Poster figures — DS 299 capstone

**Title:** Reason or pattern-match? Dimensional evaluation of LLM Bayesian reasoning
**Format:** A0 vertical (841 × 1189 mm), light theme, HTML/CSS poster
**Output:** SVG primary + PNG@600dpi fallback per figure

## Six figures shortlist

| # | Figure                              | Source data                                              | Status                             |
|---|-------------------------------------|----------------------------------------------------------|------------------------------------|
| 1 | NMACR weight bar                    | hardcoded weights (A=30, R=25, M=20, C=15, N=10)         | NEW — JSX only on site             |
| 2 | Forest plot of Krippendorff α       | experiments/results_v2/krippendorff_agreement.json       | NEW — JSX only on site             |
| 3 | Disagreement matrix 2×2             | experiments/results_v2/keyword_vs_judge_agreement.json   | NEW — JSX only on site             |
| 4 | 3-panel dimension leaderboard       | scripts/dimension_leaderboard.py                         | EXISTS — needs print-theme version |
| 5 | Verbalized vs self-consistency ECE  | experiments/results_v2/calibration.json                  | NEW — JSX only on site             |
| 6 | Failure taxonomy                    | error_taxonomy_classifications.json (143 audited)        | NEW — no generator yet             |

## Conventions

- All figures use `apply_print_theme()` from `print_theme.py`
- Model colors via `MODEL_COLORS_PRINT` (darker -600 tailwind shades)
- Dual-save via `dual_save(fig, basename)` to `poster/figures/`
- Fonts kept as text in SVG (`svg.fonttype: none`) — selectable, lossless
- Figsize chosen for poster column width: ~14 inches for full-width rows

## Phase status

- [x] Phase 1: scaffold + print theme + figure 4 (proof-of-concept)
- [ ] Phase 2: figures 1, 2, 3 (JSX-only — new generators)
- [ ] Phase 3: figures 5, 6
- [ ] Phase 4: HTML poster assembly
