# evaluation/llm_judge.py
"""
LLM-as-Judge fallback for failed answer extraction and weak structure scoring.
Addresses the N=0.0 gap caused by missing ANSWER: lines and keyword mismatch.
Reference: Nagarkar et al. (2026) — LLMs outperform BLEU/BERTScore on reasoning quality.
"""
import anthropic
import json
import re
from dotenv import load_dotenv
load_dotenv()

client = anthropic.Anthropic()

_MODEL = "claude-sonnet-4-6"


def judge_extract_answer(raw_response: str, task: dict) -> dict:
    """
    When parsed_values=[], call Claude to extract numeric answers.
    Returns {parsed_values, judge_assisted, judge_confidence}.
    """
    targets = task.get("numeric_targets", [])
    if isinstance(targets, dict):
        keys = list(targets.keys())
    else:
        keys = [t["key"] for t in targets if "key" in t]
    n = len(keys)

    prompt = f"""You are a precise answer extractor for statistical reasoning tasks.

Task expects {n} numerical value(s) for: {keys}

Model response:
{raw_response}

Extract the numerical answer(s) in the exact order listed above.
If the answer is present but not formatted as ANSWER: v1, v2, extract it anyway.
Return ONLY: ANSWER: val1, val2, ... (comma-separated floats)
If truly not answerable, return: ANSWER: NONE"""

    response = client.messages.create(
        model=_MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.content[0].text.strip()
    match = re.search(r"ANSWER:\s*(.+)", text, re.IGNORECASE)
    if not match or "NONE" in match.group(1).upper():
        return {"parsed_values": [], "judge_assisted": True, "judge_confidence": 0.0}

    try:
        values = [float(v.strip()) for v in match.group(1).split(",")]
        return {"parsed_values": values, "judge_assisted": True, "judge_confidence": 0.9}
    except ValueError:
        return {"parsed_values": [], "judge_assisted": True, "judge_confidence": 0.0}


def judge_score_structure(raw_response: str, task: dict) -> dict:
    """
    When structure_score < 0.3, call Claude to evaluate method correctness.
    Returns {structure_score, assumption_score, judge_reasoning, judge_assisted}.
    """
    checks_struct = task.get("required_structure_checks", [])
    checks_assump = task.get("required_assumption_checks", [])
    task_type = task.get("task_type", "unknown")

    prompt = f"""You are evaluating a student's statistical reasoning response.

Task type: {task_type}
Required method elements: {checks_struct}
Required assumption checks: {checks_assump}

Student response:
{raw_response}

Score each element:
1. For each required method element, did the student address it? (true/false)
2. For each required assumption check, did the student address it? (true/false)

Return ONLY valid JSON:
{{
  "structure_scores": {{"element": true, ...}},
  "assumption_scores": {{"element": true, ...}},
  "reasoning": "brief explanation"
}}"""

    response = client.messages.create(
        model=_MODEL,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.content[0].text.strip()
    try:
        clean = re.sub(r"```json|```", "", text).strip()
        data = json.loads(clean)
        struct_scores = data.get("structure_scores", {})
        assump_scores = data.get("assumption_scores", {})
        s_score = sum(struct_scores.values()) / max(len(struct_scores), 1)
        a_score = sum(assump_scores.values()) / max(len(assump_scores), 1)
        return {
            "structure_score": round(s_score, 4),
            "assumption_score": round(a_score, 4),
            "judge_reasoning": data.get("reasoning", ""),
            "judge_assisted": True,
        }
    except Exception:
        return {
            "structure_score": 0.5,
            "assumption_score": 0.5,
            "judge_assisted": True,
            "judge_reasoning": "parse_error",
        }


def needs_judge_extraction(run: dict) -> bool:
    pv = run.get("parsed_values", [])
    return not pv or len(pv) == 0


def needs_judge_scoring(run: dict) -> bool:
    return run.get("structure_score", 1.0) < 0.3
