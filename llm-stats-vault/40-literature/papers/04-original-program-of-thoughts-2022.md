# Program of Thoughts Prompting: Disentangling Computation from Reasoning

## Metadata
- Authors: Wenhu Chen et al.
- Year: 2022
- Venue: arXiv preprint (later TMLR 2023)
- arXiv ID: 2211.12588
- URL: https://arxiv.org/abs/2211.12588
- Date added to vault: 2026-05-01
- Source category: ORIGINAL_REFERENCE

## One-line summary
Introduces Program-of-Thoughts (PoT) prompting where the LLM emits executable code instead of natural-language arithmetic.

## Key findings
- Offloading computation to a Python interpreter reduces arithmetic errors substantially over CoT.
- PoT outperforms CoT by ~12% on numerical reasoning benchmarks.
- Disentangles symbolic reasoning (model) from numerical execution (interpreter).
- Most useful when answers require multi-step arithmetic.

## How it grounds this project
One of three prompting strategies considered for the benchmark runner. Provides theoretical grounding for why we chose zero-shot CoT (not PoT) as the primary mode — Bayesian closed-form derivations rely on symbolic manipulation more than arithmetic, narrowing PoT's advantage.

## Citation in poster
(Chen et al., 2022)

## Citation in paper
Chen et al. (2022) introduce Program-of-Thoughts prompting, which we contrast with our zero-shot CoT baseline.

## Bibtex key
chen2022pot

## Project artifacts that cite this
- Methodology / prompting strategy section
- code/models/run_all_tasks.py
- code/models/prompt_builder.py

## Tags
#prompting #pot #methodology #baseline
