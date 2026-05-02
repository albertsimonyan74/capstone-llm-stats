# Poster — Beyond Right Answers

## Overleaf upload

Create a new Overleaf project (Blank Project), set the compiler to **pdfLaTeX** (Menu → Settings → Compiler), upload `main.tex` to the project root, then click **Recompile**. The poster uses the standard `tikzposter` class and only CTAN packages (`amsmath`, `tikz`, `booktabs`, `enumitem`, `multicol`, `hyperref`, `graphicx`), so no extra setup is needed; output is one A0 landscape page (~46.8" × 33.1"). Confirm scale-up to 48" × 36" with the print shop before producing the final PDF — set Overleaf's geometry override or print at 102.5% if the shop needs an exact 48×36 master.

## Stub status

- **Real content:** Abstract, RQs, N·M·A·C·R rubric (Row 1); Methodology + Judge Validation (Row 2); RQ5 ECE table; Keyword vs Judge stats and pass-flip (Row 5 left).
- **Stubs (`\figstub{...}`):** Three Rankings figure, Failure Taxonomy chart, RQ2/RQ3/RQ4/RQ5 sub-figures, 4-panel scatter. Replace each `\figstub{caption}{height}` with `\includegraphics[width=\linewidth]{path/to/figure.png}` once the figures are exported from `report_materials/figures/`.
- **Reasoning-quality ranking** in the Three Rankings panel is a stub (one bullet) — fill from `experiments/results_v2/llm_judge_scores_full.jsonl` per-model means.
