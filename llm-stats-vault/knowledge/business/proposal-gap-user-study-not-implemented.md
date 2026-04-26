---
tags: [proposal, gap, user-study, rq5, future-work]
date: 2026-04-26
---

# Proposal Gap: User Study Not Implemented

## What the Proposal Says

Proposal abstract: "A small-scale user study with statistics students will assess practical usefulness and trust alignment."

Proposal methodology: Listed alongside numerical accuracy, method selection, assumption compliance, interpretation accuracy, robustness, calibration as an evaluation dimension.

Proposal timeline: "Early Apr – Mid Apr: Extended benchmarking; robustness analysis; **user study**."

## Current State

**Not implemented.** No survey instrument, no data collection, no analysis code.

RQ5 (Confidence Calibration) is implemented via `extract_confidence()` + `confidence_calibration_score()` in `response_parser.py` — but this measures self-reported model confidence vs. correctness, NOT user trust alignment.

## What Would Need to Be Built

1. Survey instrument (Google Form / Qualtrics): 5–10 statistics students
2. Task presentation: 3–5 benchmark tasks per participant, student attempts solution
3. Data: student answer + confidence rating + "did you use LLM?" flag
4. LLM comparison: same tasks queried to all 5 models
5. Metrics: trust calibration (student confidence vs. LLM correctness), error overlap
6. Output: `data/user_study/results.json`, paper §5

## Risk Mitigation (from proposal)

"User recruitment challenges: Short voluntary study within statistics courses."

Post-semester recruitment is harder. If infeasible → document as "future work" in paper §5.

## Related

- RQ5 confidence calibration (C score) partially addresses trust angle — model's own confidence alignment
- `evaluation/error_taxonomy.py` — error patterns could inform which LLM failures students caught
