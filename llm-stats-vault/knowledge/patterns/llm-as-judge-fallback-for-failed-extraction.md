---
tags: [pattern, llm-judge, evaluation, fallback, scoring]
date: 2026-04-26
---

# LLM-as-Judge Fallback for Failed Extraction

## The Pattern
When primary answer extraction fails or structure scoring is weak, `code/analysis/llm_judge.py` invokes Claude as an evaluator to improve scores.

## Trigger Conditions
```python
def needs_judge_extraction(run: dict) -> bool:
    pv = run.get("parsed_values", [])
    return not pv or len(pv) == 0   # extraction failed → N=0

def needs_judge_scoring(run: dict) -> bool:
    return run.get("structure_score", 1.0) < 0.3  # weak structure
```

## What Judge Does

### Answer Extraction (`judge_extract_answer`)
- Called when `parsed_values = []` (regex extraction found nothing)
- Sends raw LLM response to `claude-sonnet-4-6` with task context
- Returns `{parsed_values, judge_assisted, judge_confidence}`
- If judge finds values, they replace the empty `parsed_values`

### Structure Scoring (`judge_score_structure`)
- Called when `structure_score < 0.3`
- Judge evaluates reasoning quality and structure compliance
- Returns `{structure_score, assumption_score, judge_reasoning, judge_assisted}`

## Integration in run_benchmark.py
```python
# Controlled by --no-judge flag
if USE_JUDGE:
    if needs_judge_extraction(obj):
        result = judge_extract_answer(obj["raw_response"], task)
        if result["parsed_values"]:
            obj["parsed_values"] = result["parsed_values"]
            obj["judge_assisted"] = True

    if needs_judge_scoring(obj):
        scores = judge_score_structure(obj["raw_response"], task)
        obj["structure_score"] = scores["structure_score"]
        obj["judge_assisted"] = True
```

## Run With / Without Judge
```bash
python -m experiments.run_benchmark           # with judge (default)
python -m experiments.run_benchmark --no-judge  # faster, less accurate
```

## Implementation Reference
- File: `code/analysis/llm_judge.py`
- Model: `claude-sonnet-4-6` (via `anthropic` SDK)
- Paper basis: Nagarkar et al. (2026) — arXiv:2601.14479
- Tagged results: `judge_assisted = True` in run records

## Related
- [[all-scoring-weights-are-equal-at-0.20]] — the score formula
- [[anthropic-module-not-in-venv]] — required SDK
- [[scoring-pipeline]] — where judge fits in the pipeline
