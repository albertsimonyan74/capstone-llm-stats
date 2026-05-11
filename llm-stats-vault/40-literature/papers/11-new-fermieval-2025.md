# LLMs are Overconfident: Evaluating Confidence Interval Calibration with FermiEval

## Metadata
- Authors: Elliot L. Epstein, John Winnicki, Thanawat Sornwanee, Rajat Dwaraknath
- Year: 2025
- Venue: arXiv preprint
- arXiv ID: 2510.26995
- URL: https://arxiv.org/abs/2510.26995
- Date added to vault: 2026-05-01
- Source category: NEW_DAY3_DISCOVERY

## One-line summary
Calibration benchmark for LLM confidence intervals on Fermi-style estimation tasks.

## Key findings
- LLMs are systematically overconfident on estimation tasks (CIs too narrow).
- Verbalized confidence rarely tracks empirical accuracy.
- Overconfidence persists across model families and scales.
- 90% claimed CIs cover ~50% of ground truth.

## How it grounds this project
Contrast finding. FermiEval reports overconfidence on estimation; we observe the opposite — zero high-confidence records on Bayesian tasks (hedge-heavy, default-to-medium behavior). The contrast itself is the citation: domain shifts confidence behavior. Maps to data/processed_data/results_v2/calibration.json and ../../90-archive/audit/limitations_disclosures.md (empty high-confidence bucket).

## Citation in poster
(FermiEval, 2025)

## Citation in paper
FermiEval (2025) report systematic LLM overconfidence on Fermi estimation; we observe the opposite hedge-heavy pattern on Bayesian tasks, suggesting domain-dependent confidence behavior.

## Bibtex key
fermieval2025

## Project artifacts that cite this
- code/scripts/calibration_analysis.py
- data/processed_data/results_v2/calibration.json
- ../../90-archive/audit/limitations_disclosures.md
- RQ5 calibration panel
- Discussion (contrast finding)

## Tags
#calibration #overconfidence #contrast-finding #rq5
