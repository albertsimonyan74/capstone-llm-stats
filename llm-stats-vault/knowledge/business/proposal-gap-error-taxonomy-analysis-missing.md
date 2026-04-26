---
tags: [proposal, gap, error-taxonomy, analysis, deliverable]
date: 2026-04-26
---

# Proposal Gap: Error Taxonomy Analysis Missing

## What the Proposal Says

Proposal abstract: "The project aims to produce a reproducible benchmark dataset, an evaluation protocol, and **a systematic error taxonomy for LLM statistical reasoning**."

Error taxonomy is one of three named deliverables alongside benchmark dataset and evaluation protocol.

## Current State

`evaluation/error_taxonomy.py` — dataclass stub only:
- 12 top-level tag constants: `CONCEPTUAL`, `METHOD_SELECTION`, `MATHEMATICAL`, `COMPUTATIONAL`, `ASSUMPTION`, `INTERPRETATION`, `BAYES_PRIOR`, `BAYES_POSTERIOR`, `DECISION_THEORY`, `SIMULATION`, `ROBUSTNESS`, `HALLUCINATION`
- `ErrorAnnotation(task_id, model_name, run_id, tags, notes)` dataclass with `validate()`

**No analysis pipeline exists.** No script reads `runs.jsonl` and applies taxonomy tags. No output file. Not referenced in `run_benchmark.py` or `response_parser.py`.

## What Would Need to Be Built

`scripts/analyze_errors.py` — auto-tag failed runs:

```python
# Heuristic tag assignment from runs.jsonl fields:
# numeric_score == 0        → MATHEMATICAL
# structure_score < 0.3     → METHOD_SELECTION
# assumption_score == 0     → ASSUMPTION
# "cannot" in raw_response  → HALLUCINATION
# task_type in ["GIBBS","MH","HMC","RJMCMC"] and pass=False → SIMULATION
# task_type == "CONCEPTUAL" and pass=False → INTERPRETATION
```

Output: `experiments/results_v1/error_taxonomy.json`
```json
{
  "by_model": {"claude": {"MATHEMATICAL": 5, "ASSUMPTION": 12, ...}, ...},
  "by_task_type": {"GIBBS": {"SIMULATION": 3, ...}, ...},
  "annotations": [{"task_id": "...", "model": "...", "tags": [...], "notes": "..."}, ...]
}
```

Then: add taxonomy section to R master report + website.

## Priority

**Paper-blocking.** Proposal abstract lists it as a deliverable. Need at least heuristic auto-tagging to include a "§4 Error Analysis" section in the paper.

## Related

- `evaluation/error_taxonomy.py` — stub to build on
- `experiments/results_v1/runs.jsonl` — source data (1230 records, 375 synthetic flagged by suffix)
- `scripts/analyze_perturbations.py` — reference for how to process runs.jsonl
