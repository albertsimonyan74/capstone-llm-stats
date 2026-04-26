# TESTING

## Overview
DS 299 Capstone — two test suites, significant coverage gaps in core pipeline.

---

## Test Framework
`pytest` — run from project root with venv active.

```bash
source .venv/bin/activate
pytest baseline/frequentist/test_frequentist.py capstone_mcp/test_server.py -v
```

---

## Existing Tests

### `baseline/frequentist/test_frequentist.py` — 24 tests
Tests frequentist baseline modules:
- `fisher_information()` for binomial/poisson/normal/exponential/normal_var/gamma_rate
- `fisher_information("uniform")` raises `NotImplementedError` (intentional — Uniform not regular exponential family)
- `rao_cramer_bound()` output shape and values
- `order_statistic_pdf()`, `min_order_statistic_cdf()`, `max_order_statistic_cdf()` for uniform/exponential/normal
- `range_cdf()` for uniform
- `uniform_range_distribution()` simulation-based verification

**Status:** All 24 passing.

### `capstone_mcp/test_server.py` — 29 tests
Tests FastMCP server tools:
- `list_tasks`, `get_task`, `get_results`, `get_summary`, `compare_models`
- `get_failures`, `score_response`, `run_single_task`
- Edge cases: unknown task_id, empty runs, model filtering

**Status:** All 29 passing.

---

## What is NOT Tested

| Module | Gap |
|--------|-----|
| `evaluation/metrics.py` | No tests — `score_all_models()`, `TaskRun`, `ModelAggregate` untested |
| `baseline/bayesian/` | No tests — 15+ conjugate model functions, ground truth computations |
| `llm_runner/response_parser.py` | No tests — `full_score()`, `parse_and_score()`, `extract_confidence()` untested |
| `llm_runner/prompt_builder.py` | No tests — 30+ prompt builders untested |
| `llm_runner/model_clients.py` | No tests — API clients untested (would need mocking) |
| `evaluation/llm_judge.py` | No tests — judge functions untested (need ANTHROPIC_API_KEY) |
| `evaluation/task_validator.py` | No tests |
| `llm_runner/prompt_builder_fewshot.py` | No formal tests (manual integration test only) |
| `llm_runner/prompt_builder_pot.py` | No formal tests (manual integration test only) |
| `experiments/run_benchmark.py` | No tests — full pipeline integration untested |
| `baseline/bayesian/advanced_methods.py` | No tests — Phase 2 MCMC solvers untested |

---

## Integration Tests (Manual)

Validated during development — not in test suite:

```bash
# Prompt builder smoke test
python llm_runner/prompt_builder.py

# Dry-run benchmark (no API calls)
python llm_runner/run_all_tasks.py --models claude --dry-run --limit 3

# MCP server smoke test
python -m capstone_mcp.server

# Research gap closures (from commit bc470f1)
python3 -c "
from evaluation.llm_judge import needs_judge_extraction, needs_judge_scoring
from llm_runner.prompt_builder_pot import execute_pot_response
from llm_runner.prompt_builder_fewshot import build_fewshot_prompt
from evaluation.task_validator import auto_validate_task
print('All imports OK')
"
```

---

## How to Run

```bash
# All tests
pytest baseline/frequentist/test_frequentist.py capstone_mcp/test_server.py -v

# Single file
pytest capstone_mcp/test_server.py -v

# With coverage (if coverage installed)
pytest --cov=baseline/frequentist --cov=capstone_mcp -v

# Lint
ruff check .
```

---

## Coverage Gaps — Priority Order

1. **HIGH** — `evaluation/metrics.py`: scoring weights contract, TaskRun schema, aggregation math
2. **HIGH** — `llm_runner/response_parser.py`: `parse_and_score()`, `extract_confidence()`, `full_score()` with known inputs
3. **MEDIUM** — `baseline/bayesian/conjugate_models.py`: posterior update formulas
4. **MEDIUM** — `llm_runner/prompt_builder.py`: prompt templates produce expected strings
5. **LOW** — `baseline/bayesian/advanced_methods.py`: MCMC solver output ranges (seeded)

---

## Summary
53 tests total, all passing. Major gaps: no tests for evaluation/, bayesian/, or llm_runner/ core modules. Scoring pipeline (response_parser → metrics → run_benchmark) entirely untested by automated tests.
