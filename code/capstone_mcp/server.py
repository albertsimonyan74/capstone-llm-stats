# capstone_mcp/server.py
"""
MCP server for the capstone LLM benchmark pipeline.

Exposes 8 tools:
  get_task          — fetch a single task by ID
  list_tasks        — list tasks with optional filters
  score_response    — score a raw LLM response against ground truth
  get_results       — query scored results from results.json
  get_summary       — aggregate scores by model / tier / difficulty
  compare_models    — side-by-side model comparison
  get_failures      — retrieve failed tasks for a model
  run_single_task   — live-run a task against a real LLM model

Run with:
    python -m capstone_mcp.server
or configure in Claude Code settings as an MCP server.
"""
from __future__ import annotations

import json
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from capstone_mcp.tools.tasks import get_task as _get_task, list_tasks as _list_tasks
from capstone_mcp.tools.results import (
    get_results as _get_results,
    get_summary as _get_summary,
    compare_models as _compare_models,
    get_failures as _get_failures,
)
from capstone_mcp.tools.scoring import (
    score_response as _score_response,
    run_single_task as _run_single_task,
)

mcp = FastMCP(
    "Capstone LLM Benchmark",
    instructions=(
        "Tools for interacting with the capstone LLM statistics benchmark. "
        "Use get_task/list_tasks to explore tasks, score_response to evaluate "
        "an LLM answer, get_results/get_summary/compare_models/get_failures to "
        "analyse existing run data, and run_single_task to live-query a model."
    ),
)


# ── Task tools ────────────────────────────────────────────────────────────────

@mcp.tool()
def get_task(task_id: str) -> str:
    """Fetch a single benchmark task by its task_id.

    Args:
        task_id: The task identifier, e.g. 'BETA_BINOM_01' or 'CONCEPTUAL_03'.

    Returns:
        JSON string with the full task spec including numeric_targets,
        required_structure_checks, required_assumption_checks, tier, difficulty.
    """
    try:
        task = _get_task(task_id)
        return json.dumps(task, indent=2)
    except KeyError as exc:
        return json.dumps({"error": str(exc)})


@mcp.tool()
def list_tasks(
    task_type: Optional[str] = None,
    tier: Optional[int] = None,
    difficulty: Optional[str] = None,
    limit: int = 20,
) -> str:
    """List benchmark tasks with optional filters.

    Args:
        task_type:  Filter by type — 'numeric' or 'conceptual'. Omit for all.
        tier:       Filter by tier (1–4). Omit for all.
        difficulty: Filter by difficulty — 'basic', 'intermediate', 'advanced'.
        limit:      Maximum number of tasks to return (default 20, max 136).

    Returns:
        JSON array of matching task specs.
    """
    tasks = _list_tasks(task_type=task_type, tier=tier, difficulty=difficulty, limit=limit)
    return json.dumps(tasks, indent=2)


# ── Scoring tools ─────────────────────────────────────────────────────────────

@mcp.tool()
def score_response(task_id: str, response: str) -> str:
    """Score a raw LLM response against the benchmark ground truth.

    Computes three sub-scores:
      - numeric (0–1): correctness of extracted numeric values
      - structure (0–1): presence of required reasoning steps
      - assumptions (0–1): mention of required statistical assumptions
    Combined: 0.6 * numeric + 0.2 * structure + 0.2 * assumptions

    Args:
        task_id:  The benchmark task ID.
        response: The raw text response from an LLM.

    Returns:
        JSON with final_score, pass (bool), and per-component detail.
    """
    try:
        result = _score_response(task_id, response)
        return json.dumps(result, indent=2)
    except KeyError as exc:
        return json.dumps({"error": str(exc)})


@mcp.tool()
def run_single_task(
    task_id: str,
    model_name: str,
    prompt_style: str = "default",
) -> str:
    """Live-run a single benchmark task against an LLM and return scored results.

    Requires the appropriate API key env var:
      claude/anthropic → ANTHROPIC_API_KEY
      chatgpt/openai   → OPENAI_API_KEY
      gemini           → GEMINI_API_KEY
      deepseek         → DEEPSEEK_API_KEY

    Args:
        task_id:      The benchmark task ID.
        model_name:   Model family: 'claude', 'chatgpt', 'gemini', or 'deepseek'.
        prompt_style: Prompt variant (currently only 'default' supported).

    Returns:
        JSON with raw_response, latency_ms, token counts, and score breakdown.
    """
    result = _run_single_task(task_id, model_name, prompt_style)
    return json.dumps(result, indent=2)


# ── Results tools ─────────────────────────────────────────────────────────────

@mcp.tool()
def get_results(
    model_name: Optional[str] = None,
    task_id: Optional[str] = None,
    min_score: Optional[float] = None,
    limit: int = 50,
) -> str:
    """Query scored task results from results.json.

    Args:
        model_name: Filter by model (e.g. 'chatgpt', 'claude'). Omit for all.
        task_id:    Filter by specific task. Omit for all.
        min_score:  Return only results with final_weighted_score >= this value.
        limit:      Maximum results to return (default 50).

    Returns:
        JSON array of task-score records with components N/M/C/A/R.
    """
    results = _get_results(model_name=model_name, task_id=task_id, min_score=min_score, limit=limit)
    return json.dumps(results, indent=2)


@mcp.tool()
def get_summary(group_by: str = "model") -> str:
    """Aggregate benchmark scores grouped by a dimension.

    Args:
        group_by: Dimension to group by — 'model', 'tier', or 'difficulty'.

    Returns:
        JSON with aggregated mean/min/max scores per group.
    """
    summary = _get_summary(group_by=group_by)
    return json.dumps(summary, indent=2)


@mcp.tool()
def compare_models(
    task_id: Optional[str] = None,
    tier: Optional[int] = None,
) -> str:
    """Compare all models side-by-side for a specific task or tier.

    Args:
        task_id: Compare on a specific task. Omit for aggregate comparison.
        tier:    Restrict comparison to tasks in this tier (1–4).

    Returns:
        JSON with per-model n_tasks, mean_score, and individual task scores.
    """
    result = _compare_models(task_id=task_id, tier=tier)
    return json.dumps(result, indent=2)


@mcp.tool()
def get_failures(
    model_name: Optional[str] = None,
    threshold: float = 0.5,
    limit: int = 20,
) -> str:
    """Get failed tasks (score below threshold) for a given model.

    Args:
        model_name: Model to inspect (e.g. 'chatgpt'). Omit for all models.
        threshold:  Score cutoff — tasks below this are considered failures (default 0.5).
        limit:      Maximum number of failures to return (default 20).

    Returns:
        JSON array of failed task-score records, sorted by score ascending.
    """
    failures = _get_failures(model_name=model_name, threshold=threshold, limit=limit)
    return json.dumps(failures, indent=2)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
