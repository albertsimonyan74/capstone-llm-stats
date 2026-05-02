# Evaluating and Calibrating LLM Confidence on Questions with Multiple Correct Answers

## Metadata
- Authors: Yuhan Wang, Shiyu Ni, Zhikai Ding, Zihang Zhan, Yuanzi Li, Keping Bi
- Year: 2026
- Venue: arXiv preprint
- arXiv ID: 2602.07842
- URL: https://arxiv.org/abs/2602.07842
- Date added to vault: 2026-05-01
- Source category: NEW_DAY3_DISCOVERY

## One-line summary
Compares verbalized vs consistency-based confidence extraction on multi-answer questions.

## Key findings
- Verbalized confidence (keyword/phrase based) systematically underestimates uncertainty diversity.
- Consistency-based confidence (sample multiple answers, measure agreement) dominates verbalized methods.
- Combined verbalized + consistency yields best calibration.
- Single-call keyword extraction (our approach) is the weakest baseline.

## How it grounds this project
Frames our calibration limitation. Our keyword extraction is verbalized; consistency-based is the natural upgrade. Maps to scripts/self_consistency_full.py (Phase 1C canonical; B3-stratified scripts/self_consistency_proxy.py archived 2026-05-02 to llm-stats-vault/90-archive/intermediate_analyses/scripts/) and the empty high-confidence bucket disclosure in audit/limitations_disclosures.md.

## Citation in poster
(Multi-Answer Confidence, 2026)

## Citation in paper
Recent work (2026) shows consistency-based confidence extraction dominates verbalized keyword extraction; our keyword approach is acknowledged as the weakest baseline and consistency-based methods are flagged for future work.

## Bibtex key
multianswer2026

## Project artifacts that cite this
- scripts/calibration_analysis.py
- audit/limitations_disclosures.md
- llm_runner/response_parser.py (extract_confidence)
- RQ5 / future work panel

## Tags
#calibration #confidence-estimation #methodology #rq5 #future-work
