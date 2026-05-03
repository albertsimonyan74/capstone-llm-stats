---
tags: [decision, scoring, architecture, evaluation]
date: 2026-04-26
---

# Dual Scoring Paths Exist for Separation of Concerns

## Decision
Two separate scoring implementations co-exist and must stay in sync:
1. **Path A** — `llm_runner/response_parser.py` (`full_score()`)
2. **Path B** — `evaluation/metrics.py` (`score_all_models()`)

## Why
- **Path A** runs during live API calls — needs to be fast and operate on raw strings
- **Path B** runs post-hoc in batch — operates on typed `TaskRun` dataclasses with full validation
- Separating live scoring from formal evaluation enables independent optimization of each
- Path B supports perturbation grouping and tier-weighted aggregation that aren't needed in live runs

## Trade-offs
- **Con**: Two files to keep in sync — risk of divergence
- **Mitigation**: Cross-reference comment in both files + CLAUDE.md §7 rule + identical `WEIGHTS` dict

## How to Apply
- Whenever modifying scoring logic or weights: update **both** files simultaneously
- See [[scoring-weights-must-be-updated-in-two-files]]
- See [[scoring-pipeline]] for full details on each path

## Current State
- Both paths confirmed identical weights as of 2026-05-03 (Approach A migration)
- Sole canonical scheme: A=0.30, R=0.25, M=0.20, C=0.15, N=0.10 (literature-derived)
- Pre-2026-05-03 history: equal weights N=M=A=C=R=0.20 (see
  [[all-scoring-weights-are-equal-at-0.20]] RESOLVED section)
- Path B (run_benchmark.py) has never successfully written results.json — it's currently empty
- Root cause: Gemini runs incomplete → blocked downstream
