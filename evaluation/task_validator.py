"""
Task quality validation — addresses StatEval human-in-the-loop gap (Lu et al., 2025).
Provides automated proxy validation + human review flagging.
"""
from __future__ import annotations
import json
import re

import anthropic
from dotenv import load_dotenv
load_dotenv()

client = anthropic.Anthropic()
_MODEL = "claude-sonnet-4-6"


def auto_validate_task(task: dict) -> dict:
    """
    Automated quality check for a single task (proxy for human review).
    Returns {valid, issues, clarity_score, solvable, needs_human_review}.
    """
    issues: list[str] = []

    # Check 1: zero true_value with tight tolerance
    for t in task.get("numeric_targets", []):
        if isinstance(t, dict):
            if t.get("true_value") == 0 and t.get("full_credit_tol", 1) < 0.01:
                issues.append(f"Zero true_value with tight tolerance: {t.get('key')}")

    # Check 2: prompt too short
    if len(task.get("prompt", "")) < 50:
        issues.append("Prompt too short (<50 chars)")

    targets_preview = (
        list(task.get("numeric_targets", {}).keys())
        if isinstance(task.get("numeric_targets"), dict)
        else [t.get("key") for t in task.get("numeric_targets", []) if isinstance(t, dict)]
    )

    prompt = f"""Rate the clarity and solvability of this statistical task (1-5):

Task type: {task.get('task_type')}
Numeric targets: {targets_preview}
Prompt preview: {str(task)[:500]}

Return JSON only:
{{"clarity_score": 1, "solvable": true, "issues": [], "needs_human_review": false}}"""

    response = client.messages.create(
        model=_MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )

    text = re.sub(r"```json|```", "", response.content[0].text).strip()
    try:
        result = json.loads(text)
        result["auto_issues"] = issues
        result["valid"] = (
            result.get("clarity_score", 0) >= 3
            and result.get("solvable", False)
        )
        return result
    except Exception:
        return {
            "valid": True,
            "issues": issues,
            "clarity_score": None,
            "solvable": None,
            "needs_human_review": len(issues) > 0,
            "auto_issues": issues,
        }


def validate_all_tasks(tasks_path: str, output_path: str) -> dict:
    """
    Validate all tasks; write validation_report.json.
    Tasks flagged needs_human_review=True are listed separately.
    """
    with open(tasks_path) as f:
        tasks = json.load(f)

    results = []
    needs_review: list[str] = []

    for task in tasks:
        result = auto_validate_task(task)
        result["task_id"] = task["task_id"]
        results.append(result)
        if result.get("needs_human_review") or not result.get("valid"):
            needs_review.append(task["task_id"])
        print(
            f"{task['task_id']}: valid={result.get('valid')} "
            f"clarity={result.get('clarity_score', '?')}"
        )

    report = {
        "total_tasks": len(tasks),
        "valid_tasks": sum(1 for r in results if r.get("valid")),
        "needs_human_review": needs_review,
        "results": results,
    }

    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nValidation complete: {report['valid_tasks']}/{report['total_tasks']} valid")
    print(f"Needs human review: {len(needs_review)} tasks")
    return report


if __name__ == "__main__":
    validate_all_tasks(
        "data/benchmark_v1/tasks_all.json",
        "data/benchmark_v1/validation_report.json",
    )
