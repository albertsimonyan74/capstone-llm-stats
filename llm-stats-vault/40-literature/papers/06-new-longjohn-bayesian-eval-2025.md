# Bayesian Evaluation of Large Language Model Behavior

## Metadata
- Authors: Rachel Longjohn, Shang Wu, Saatvik Kher, Catarina Belém, Padhraic Smyth (UC Irvine)
- Year: 2025
- Venue: arXiv preprint
- arXiv ID: 2511.10661
- URL: https://arxiv.org/abs/2511.10661
- Date added to vault: 2026-05-01
- Source category: NEW_DAY3_DISCOVERY

## One-line summary
Argues that standard LLM benchmarks under-quantify uncertainty and proposes Bayesian evaluation with credible intervals.

## Key findings
- Point-estimate accuracies obscure between-run variance and sampling uncertainty.
- Bootstrap CIs and Bayesian posteriors reveal benchmark separability gaps invisible in raw scores.
- Many "ranking" claims in LLM benchmarks are not statistically supported.
- Recommends always reporting CI alongside accuracy.

## How it grounds this project
Direct motivation for our bootstrap CI workstream (Window 4). Maps to code/scripts/bootstrap_ci.py and data/processed_data/results_v2/bootstrap_ci.json. Their argument that uncertainty quantification is missing from existing benchmarks is exactly the gap our P-2 audit finding addresses.

## Citation in poster
(Longjohn et al., 2025)

## Citation in paper
Longjohn et al. (2025) demonstrate that standard LLM evaluations neglect uncertainty quantification; we adopt their bootstrap-CI framing for ranking separability.

## Bibtex key
longjohn2025bayesian

## Project artifacts that cite this
- code/scripts/bootstrap_ci.py
- data/processed_data/results_v2/bootstrap_ci.json
- paper/figures/bootstrap_ci.png
- ../../90-archive/audit/day2_audit_report.md (P-2 finding)
- Three Rankings poster panel

## Tags
#methodology #statistical-rigor #uncertainty #bootstrap
