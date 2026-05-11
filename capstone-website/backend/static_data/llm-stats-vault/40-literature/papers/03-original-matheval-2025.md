# MathEval: A Comprehensive Benchmark for Mathematical Reasoning

## Metadata
- Authors: Tianqiao Liu, Zui Chen, Zhensheng Fang, Weiqi Luo, Mi Tian, Zitao Liu
- Year: 2025
- Venue: Springer (journal article)
- DOI: 10.1007/s44366-025-0053-z
- URL: https://doi.org/10.1007/s44366-025-0053-z
- Date added to vault: 2026-05-01
- Source category: ORIGINAL_REFERENCE

## One-line summary
Comprehensive mathematical-reasoning benchmark unifying 17 datasets under shared scoring schema.

## Key findings
- Cross-dataset normalization reveals model-specific strengths invisible in any single dataset.
- Multi-dimensional scoring (numeric correctness + reasoning quality) yields rankings different from accuracy alone.
- Tier-stratified difficulty exposes ceiling effects on easy tasks.
- Reasoning-quality metrics correlate weakly with raw accuracy.

## How it grounds this project
Provides the comparative baseline for our 5-dimensional Bayesian rubric (N·M·A·C·R). MathEval's multi-dimensional scoring inspires our rubric's separation of numeric vs structural vs assumption dimensions. Cite in methodology section and rubric-design rationale.

## Citation in poster
(Liu et al., 2025)

## Citation in paper
Liu et al. (2025) propose MathEval, whose multi-dimensional scoring approach informs our N·M·A·C·R rubric design.

## Bibtex key
liu2025matheval

## Project artifacts that cite this
- Methodology section
- code/analysis/metrics.py (rubric weights rationale)
- code/analysis/llm_judge_rubric.py
- code/models/response_parser.py

## Tags
#math-reasoning #rubric-design #baseline #methodology
