# Can LLM Reasoning Be Trusted in Statistical Domains

## Metadata
- Authors: Crish Nagarkar, Leonid Bogachev, Serge Sharoff
- Year: 2026
- Venue: arXiv preprint
- arXiv ID: 2601.14479
- URL: https://arxiv.org/abs/2601.14479
- Date added to vault: 2026-05-01
- Source category: ORIGINAL_REFERENCE

## One-line summary
Investigates reliability and hallucination patterns when LLMs perform statistical reasoning tasks.

## Key findings
- LLMs hallucinate statistical justifications even when numeric answers are correct.
- Confidence claims rarely track empirical accuracy.
- Reliability degrades sharply on tasks requiring assumption verification.
- Surface fluency masks reasoning gaps in mid-tier difficulty.

## How it grounds this project
Motivates RQ5 (confidence calibration). Findings parallel our keyword-confidence extraction limitations and the empty high-confidence bucket in data/processed_data/results_v2/calibration.json. Cite in RQ5 panel and discussion of model trustworthiness.

## Citation in poster
(Nagarkar et al., 2026)

## Citation in paper
Nagarkar et al. (2026) document systematic reliability failures in statistical-domain LLM reasoning, motivating dedicated calibration analysis.

## Bibtex key
nagarkar2026canllm

## Project artifacts that cite this
- RQ5 calibration panel
- scripts/calibration_analysis.py
- data/processed_data/results_v2/calibration.json
- Discussion / limitations

## Tags
#reliability #hallucination #calibration #rq5
