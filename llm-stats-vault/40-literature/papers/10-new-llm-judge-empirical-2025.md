# An Empirical Study of LLM-as-a-Judge: How Design Choices Impact Evaluation Reliability

## Metadata
- Authors: Yusuke Yamauchi, Taro Yano, Masafumi Oyamada (note: bibtex key `park2025judge` is legacy — actual first author is Yamauchi)
- Year: 2025
- Venue: arXiv preprint
- arXiv ID: 2506.13639
- URL: https://arxiv.org/abs/2506.13639
- Date added to vault: 2026-05-01
- Source category: NEW_DAY3_DISCOVERY

## One-line summary
Empirically evaluates LLM-as-a-Judge design choices, recommending Krippendorff's α for inter-rater reliability.

## Key findings
- Spearman ρ overstates judge agreement on bounded rubric scales.
- Krippendorff's α is the more conservative and informative metric.
- Judge prompt template choices have larger effects than judge model choice.
- Single-judge ensembles inflate reliability estimates.

## How it grounds this project
Validates our judge-validation methodology (Llama 3.3 70B Instruct via Together AI). Their α-over-ρ recommendation maps to code/scripts/krippendorff_agreement.py (Group B1) and data/processed_data/results_v2/krippendorff_agreement.json. Cite for judge-design rationale and inter-rater reliability metric choice.

## Citation in poster
(Park et al., 2025)

## Citation in paper
Park et al. (2025) recommend Krippendorff's α over Spearman ρ for LLM-as-Judge agreement; we adopt α for our judge-validation analysis.

## Bibtex key
park2025judge

## Project artifacts that cite this
- code/analysis/llm_judge_rubric.py
- code/scripts/keyword_vs_judge_agreement.py
- data/processed_data/results_v2/keyword_vs_judge_agreement.json
- Methodology / judge-validation panel

## Tags
#judge-validation #inter-rater-reliability #methodology #krippendorff
