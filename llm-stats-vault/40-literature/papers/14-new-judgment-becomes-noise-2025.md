# When Judgment Becomes Noise: How Design Failures in LLM Judge Benchmarks Silently Undermine Validity

## Metadata
- Authors: Benjamin Feuer, Chiung-Yi Tseng, Astitwa Sarthak Lathe, Oussama Elachqar, John P. Dickerson
- Year: 2025
- Venue: arXiv preprint
- arXiv ID: 2509.20293
- URL: https://arxiv.org/abs/2509.20293
- Date added to vault: 2026-05-01
- Source category: NEW_DAY3_DISCOVERY

## One-line summary
Critiques single-judge LLM benchmarks, arguing design failures convert judgment signal into noise.

## Key findings
- Single-judge benchmarks bias toward judge-model preferences (self-preference and family-preference bias).
- Inter-judge ensembles (3+ judges) recover signal lost to single-judge noise.
- Prompt template choices systematically shift score distributions.
- Recommends multi-judge ensembling and pre-registered prompt templates.

## How it grounds this project
Strengthens our P-7 audit finding (single-judge limitation). Llama 3.3 70B is one judge; their recommendation is to ensemble. Cite in limitations + future-work sections.

## Citation in poster
(Judgment Becomes Noise, 2025)

## Citation in paper
Recent work (2025) shows that single-judge LLM benchmarks introduce systematic noise; we acknowledge this limitation and flag multi-judge ensembling for future work.

## Bibtex key
judgment2025noise

## Project artifacts that cite this
- audit/day2_audit_report.md (P-7 finding)
- audit/limitations_disclosures.md
- evaluation/llm_judge_rubric.py
- Limitations / future-work panel

## Tags
#judge-validation #limitations #single-judge-bias #future-work
