# Benchmarking the (In)Stability of LLM Reasoning (ReasonBench)

## Metadata
- Authors: Nearchos Potamitis, Lars Klein, Akhil Arora
- Year: 2025
- Venue: arXiv preprint
- arXiv ID: 2512.07795
- URL: https://arxiv.org/abs/2512.07795
- Date added to vault: 2026-05-01
- Source category: NEW_DAY3_DISCOVERY

## One-line summary
Treats reproducibility and reasoning variance as first-class evaluation dimensions, not nuisance noise.

## Key findings
- Run-to-run variance can flip rankings on the same prompts.
- Stability is model-dependent and uncorrelated with raw accuracy.
- Reproducibility deserves an explicit dimension alongside accuracy and calibration.
- Benchmarks reporting only mean accuracy mask substantial instability.

## How it grounds this project
Validates our three-rankings framework (accuracy / robustness / calibration). ReasonBench's framing of variance as first-class is the same lens our RQ4 robustness analysis applies. Maps to scripts/three_rankings_figure.py and the bias-variance framing in the poster's RQ4 panel.

## Citation in poster
(ReasonBench, 2025)

## Citation in paper
ReasonBench (2025) frames reasoning instability as a first-class evaluation dimension; our three-rankings analysis adopts this perspective for Bayesian tasks.

## Bibtex key
reasonbench2025

## Project artifacts that cite this
- scripts/three_rankings_figure.py
- report_materials/figures/three_rankings.png
- RQ4 robustness panel
- Abstract / methodology framing

## Tags
#robustness #stability #variance #three-rankings
