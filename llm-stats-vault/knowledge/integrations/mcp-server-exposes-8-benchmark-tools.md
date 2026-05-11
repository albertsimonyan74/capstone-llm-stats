---
tags: [integration, mcp, server, tools]
date: 2026-04-26
---

# MCP Server Exposes 8 Benchmark Tools

## Connection Details
- **File**: `code/capstone_mcp/server.py`
- **Framework**: FastMCP
- **Start**: `python -m capstone_mcp.server`
- **Tests**: `code/capstone_mcp/test_server.py` — 29 tests, all passing

## Available Tools

| Tool | Purpose |
|------|---------|
| `get_task` | Get single task spec by task_id |
| `list_tasks` | List/filter tasks by type, tier, difficulty |
| `score_response` | Score an LLM response against a task's ground truth |
| `get_results` | Get results from results.json |
| `get_summary` | Get summary statistics |
| `compare_models` | Compare model performance across tasks |
| `get_failures` | List tasks where a model failed (score < 0.5) |
| `run_single_task` | Live-query a model on a specific task |

## Usage in Claude Code
These tools are available in this session via `mcp__capstone__*` prefix:
- `mcp__capstone__list_tasks` — explore available tasks
- `mcp__capstone__get_task` — inspect a specific task
- `mcp__capstone__score_response` — test scoring logic
- `mcp__capstone__get_summary` — current results summary

## Notes
- `run_single_task` makes live API calls — requires env vars set
- `get_results` + `compare_models` read `results.json` which is currently empty
- Tests cover all 8 tools; run with `pytest code/capstone_mcp/test_server.py -v`
