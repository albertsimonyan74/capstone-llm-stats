# LLM Reasoning Benchmarks are Statistically Fragile

## Metadata
- Authors: Andreas Hochlehnert, Hardik Bhatnagar, Vishaal Udandarao, Samuel Albanie, Ameya Prabhu, Matthias Bethge (Tübingen AI Center / Cambridge)
- Year: 2025
- Venue: arXiv preprint
- arXiv ID: 2504.07086
- Canonical title: "A Sober Look at Progress in Language Model Reasoning: Pitfalls and Paths to Reproducibility"
- URL: https://arxiv.org/abs/2504.07086
- Date added to vault: 2026-05-01
- Source category: NEW_DAY3_DISCOVERY

## One-line summary
Demonstrates that single-question swaps can flip Pass@1 rankings on standard LLM reasoning benchmarks.

## Key findings
- Single-question changes shift Pass@1 by 3+ percentage points on common benchmarks.
- Benchmark rankings rarely survive bootstrap-CI separability tests.
- Many published "wins" are within stochastic noise.
- Recommends bootstrap CIs and separability matrices for all benchmark claims.

## How it grounds this project
Direct motivation for the bootstrap-CI separability analysis (P-2 audit finding). Their result that ChatGPT vs DeepSeek deltas can be within noise validates our claim that robustness rankings need separability tests. Maps to experiments/results_v2/bootstrap_ci.json separability matrix and report_materials/figures/bootstrap_ci.png.

## Citation in poster
(Statistical Fragility, 2025)

## Citation in paper
Recent work (2025) shows that single-question swaps can shift Pass@1 by 3+ points on standard benchmarks; we adopt their separability-test recommendation for all model-comparison claims.

## Bibtex key
fragility2025

## Project artifacts that cite this
- scripts/bootstrap_ci.py
- experiments/results_v2/bootstrap_ci.json
- report_materials/figures/bootstrap_ci.png
- audit/day2_audit_report.md (P-2 finding)
- Three-rankings panel

## Tags
#statistical-rigor #separability #benchmark-validity #bootstrap
