---
tags: [debugging, anthropic, python, venv, import-error]
date: 2026-04-26
---

# anthropic Module Not in Venv by Default

## What Happened
When running the integration tests for `code/analysis/llm_judge.py` and `code/analysis/task_validator.py`, this error appeared:
```
ModuleNotFoundError: No module named 'anthropic'
```

## Root Cause
The `anthropic` Python SDK is installed in the conda base environment (`/opt/anaconda3/`) but **not** in the project's `.venv` (`/Users/albertsimonyan/Desktop/capstone-llm-stats/.venv/`).

The project uses `.venv` for isolation. When running `python` from within `.venv`, it can't see conda's packages.

## Fix
```bash
source .venv/bin/activate
.venv/bin/pip install anthropic -q
```

Or simply:
```bash
pip install anthropic
```
(while venv is activated)

## Why This Happens
- `llm_judge.py` and `task_validator.py` use the `anthropic` SDK (not httpx) for streaming/async features
- The main benchmark runner uses httpx only — no vendor SDKs
- See [[httpx-used-directly-no-vendor-sdks]]

## Affected Files
- `code/analysis/llm_judge.py`
- `code/analysis/task_validator.py`

## Prevention
The `anthropic` package should be added to `requirements.txt` (or a separate `requirements-judge.txt` to keep it optional).
