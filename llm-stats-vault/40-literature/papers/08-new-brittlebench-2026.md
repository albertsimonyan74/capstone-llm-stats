# Quantifying LLM Robustness via Prompt Sensitivity (BrittleBench)

## Metadata
- Authors: Angelika Romanou, Mark Ibrahim, Candace Ross, Chantal Shaib, Kerem Oktar, Samuel J. Bell, Anaelia Ovalle, Jesse Dodge, Antoine Bosselut, Koustuv Sinha, Adina Williams
- Year: 2026
- Venue: arXiv preprint
- arXiv ID: 2603.13285
- URL: https://arxiv.org/abs/2603.13285
- Date added to vault: 2026-05-01
- Source category: NEW_DAY3_DISCOVERY

## One-line summary
General-purpose framework for quantifying LLM robustness via systematic prompt perturbations.

## Key findings
- Models show strong sensitivity to surface rephrasings even when semantics are preserved.
- Numerical perturbations reveal arithmetic-vs-conceptual brittleness mismatch.
- Semantic perturbations expose memorization artifacts.
- Robustness deltas often within stochastic noise — must be tested for separability.

## How it grounds this project
Our perturbation methodology (rephrase / numerical / semantic — 398 perturbations × 5 models) is a domain-specific instance of BrittleBench applied to Bayesian inference. Maps to code/scripts/generate_perturbations_full.py, data/raw_data/synthetic/perturbations_v2.json, and data/processed_data/results_v2/robustness_v2.json.

## Citation in poster
(BrittleBench, 2026)

## Citation in paper
BrittleBench (2026) provides the perturbation taxonomy we adapt for Bayesian-task robustness analysis.

## Bibtex key
brittlebench2026

## Project artifacts that cite this
- code/scripts/generate_perturbations_full.py
- code/scripts/score_perturbations.py
- code/scripts/robustness_analysis.py
- data/raw_data/synthetic/perturbations_v2.json
- data/processed_data/results_v2/robustness_v2.json
- report_materials/figures/robustness_heatmap.png
- RQ4 panel

## Tags
#robustness #perturbation #prompt-sensitivity
