# capstone_mcp/tools/scoring.py
"""Tool implementations for scoring LLM responses and running live tasks."""
from __future__ import annotations

from typing import Any, Dict

from models.response_parser import full_score
from models.prompt_builder import build_prompt
from models.model_clients import get_client
from capstone_mcp.tools.tasks import get_task


def score_response(task_id: str, response: str) -> Dict[str, Any]:
    """Score a raw LLM response against the ground truth for a given task."""
    task = get_task(task_id)
    result = full_score(response, task)
    return {
        "task_id":     task_id,
        "final_score": result["final_score"],
        "pass":        result["pass"],
        "numeric":     result["numeric"],
        "structure":   result["structure"],
        "assumptions": result["assumptions"],
    }


def run_single_task(
    task_id: str,
    model_name: str,
    prompt_style: str = "default",
) -> Dict[str, Any]:
    """Run a single benchmark task against a live LLM and return scored results.

    Requires the appropriate API key env var to be set:
      ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY, or DEEPSEEK_API_KEY.
    """
    try:
        task = get_task(task_id)
    except KeyError as exc:
        return {"task_id": task_id, "model_name": model_name, "error": str(exc)}

    prompt = build_prompt(task)

    try:
        client = get_client(model_name)
        run_result = client.query(prompt, task_id)
    except Exception as exc:
        return {
            "task_id":    task_id,
            "model_name": model_name,
            "error":      str(exc),
        }

    raw_response = run_result.get("raw_response", "")
    score = full_score(raw_response, task)

    return {
        "task_id":      task_id,
        "model_name":   model_name,
        "prompt_style": prompt_style,
        "raw_response": raw_response,
        "latency_ms":   run_result.get("latency_ms", 0.0),
        "input_tokens": run_result.get("input_tokens", 0),
        "output_tokens": run_result.get("output_tokens", 0),
        "final_score":  score["final_score"],
        "pass":         score["pass"],
        "numeric":      score["numeric"],
        "structure":    score["structure"],
        "assumptions":  score["assumptions"],
        "error":        run_result.get("error", ""),
    }
