# Chain-of-Thought Prompting Elicits Reasoning in Large Language Models

## Metadata
- Authors: Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten Bosma, Brian Ichter, Fei Xia, Ed H. Chi, Quoc V. Le, Denny Zhou
- Year: 2022
- Venue: NeurIPS 2022
- arXiv ID: 2201.11903
- URL: https://arxiv.org/abs/2201.11903
- Date added to vault: 2026-05-01
- Source category: ORIGINAL_REFERENCE

## One-line summary
Foundational paper showing that prompting LLMs to "think step by step" elicits emergent multi-step reasoning.

## Key findings
- CoT prompting produces emergent reasoning gains at sufficient scale (~100B params).
- Few-shot CoT with 8 exemplars beats standard prompting on GSM8K, SVAMP, ASDiv.
- Zero-shot CoT (Kojima et al.) extension makes the technique trigger-phrase only.
- Establishes CoT as default reasoning prompt for math/symbolic tasks.

## How it grounds this project
Foundational. Zero-shot CoT is the baseline prompting mode for all 1,230 benchmark runs in this project. The system prompt directs every model to "Solve problems step by step, showing all working." Cite as the methodology anchor in any prompting discussion.

## Citation in poster
(Wei et al., 2022)

## Citation in paper
Wei et al. (2022) introduce chain-of-thought prompting; we adopt zero-shot CoT as our baseline reasoning mode for all 5 evaluated models.

## Bibtex key
wei2022cot

## Project artifacts that cite this
- Methodology section (foundational citation)
- code/models/run_all_tasks.py
- code/models/prompt_builder.py
- System-prompt definition (CLAUDE.md)

## Tags
#foundational #cot #prompting #methodology
