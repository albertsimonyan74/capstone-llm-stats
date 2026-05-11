# Ice Cream Doesn't Cause Drowning: Benchmarking LLMs Against Statistical Pitfalls in Causal Inference

## Metadata
- Authors: Jin Du, Li Chen, Xun Xian, An Luo, Fangqiao Tian, Ganghua Wang, Charles Doss, Xiaotong Shen, Jie Ding
- Year: 2025
- Venue: arXiv preprint
- arXiv ID: 2505.13770
- URL: https://arxiv.org/abs/2505.13770
- Date added to vault: 2026-05-01
- Source category: NEW_DAY3_DISCOVERY

## One-line summary
Benchmarks LLMs on classic statistical-causal pitfalls (confounding, selection bias, Simpson's paradox).

## Key findings
- LLMs produce "convincing yet misleading causal conclusions" on standard pitfalls.
- Failure mode is dominantly silent assumption violation, not arithmetic error.
- ~47% of failures classified as assumption-violation in their taxonomy.
- Correct numeric answer often coexists with wrong causal interpretation.

## How it grounds this project
Independent confirmation of our finding that ASSUMPTION_VIOLATION is the dominant failure mode (matches our 46.9%). Their "convincing yet misleading" framing mirrors our error taxonomy. Maps to data/processed_data/results_v2/error_taxonomy_v2.json and paper/figures/error_taxonomy_hierarchical.png.

## Citation in poster
(Du et al., 2025)

## Citation in paper
Du et al. (2025) independently report assumption-violation as the dominant LLM failure mode in causal inference, mirroring our Bayesian-task taxonomy.

## Bibtex key
du2025icecream

## Project artifacts that cite this
- code/scripts/error_taxonomy.py
- data/processed_data/results_v2/error_taxonomy_v2.json
- paper/figures/error_taxonomy_hierarchical.png
- RQ3 failure-taxonomy panel

## Tags
#causal-inference #failure-modes #assumption-violation #statistical-reasoning
