# Gemini reasoning_score / confidence_score nulling — forensic investigation

**Date:** 2026-05-03
**Triggered by:** Tier 1 coverage diagnostic. Gemini had `reasoning_score=None` and `confidence_score=None` across all 246 records in `experiments/results_v1/runs.jsonl`, while keyword scoring infrastructure (`reasoning_quality_score()` in `llm_runner/response_parser.py`) cannot produce `None` — it always returns a float.

## Question

Why does Gemini have 0/246 `reasoning_score` and 0/246 `confidence_score`, while non-gemini models have 136/246 set?

## Investigation

### Step 1 — Search for explicit nulling

`grep -rn 'reasoning_score.*=.*None\|confidence_score.*=.*None' scripts/ llm_runner/` found exactly two assignments, both in `scripts/recompute_scores.py`:
- Line 48: error/no-raw_response branch
- Line 57: missing-task branch

Neither is gemini-specific.

### Step 2 — Compare current state vs Apr 26 backup

`runs.jsonl.bak_20260426_211605` showed Gemini at 18/128 reasoning_score populated. Backup had 90 shared task_ids with current; on shared tasks: 0 both-set, 18 bak-set/cur-None, 72 neither.

Sample shared task `BETA_BINOM_01`:
| field | backup | current |
|---|---|---|
| run_id | `83f20afd...` | `67320268...` |
| timestamp | 2026-04-24 | 2026-04-26 |
| reasoning_score | 1.0 | None |
| confidence_score | 0.832 | None |
| raw_response_len | 6261 | 5176 |
| raw_responses equal | False | — |

Same task, **different run** (different run_id, different timestamp, different raw_response). Gemini was completely re-issued on Apr 26 (RPD quota recovery). The backup is the pre-rerun state.

### Step 3 — Inspect the runner record schema

`llm_runner/run_all_tasks.py:_make_run_record()` (lines 111–144) does NOT include `reasoning_score` or `confidence_score` keys in the dict it writes to JSONL. Any record produced by `run_all_tasks` lacks those two fields by construction; downstream `.get("reasoning_score")` returns `None` for missing key.

### Step 4 — Verify recompute_scores.py was never re-run after Apr 26 gemini rerun

Manually replicated `recompute_scores.py` logic on a gemini Phase 1 record using current `raw_response`. `full_score()` produced `reasoning_score=1.0` and `confidence_score=0.76` for `BETA_BINOM_01`. Current canonical has `None` for both. **recompute_scores.py has not been executed against current runs.jsonl since Gemini's Apr 26 re-run.**

## Root cause

Two compounding bugs:

1. **Runner schema gap (chronic):** `_make_run_record()` in `llm_runner/run_all_tasks.py` omits `reasoning_score` and `confidence_score` fields when logging. Any time a model is re-run, the new records lack these fields.

2. **Stale path in recompute (latent):** `scripts/recompute_scores.py:23` points at `data/benchmark_v1/tasks.json` (Phase 1, 136 tasks). Phase 2 task_ids and v1 perturbation task_ids fall through the `task is None` branch, which sets reasoning + confidence to `None` even when they could be scored.

The combination means: every `run_all_tasks` re-run silently drops reasoning/confidence; only `recompute_scores.py` can backfill them; but `recompute_scores.py` only backfills Phase 1.

## Why Gemini specifically appears uniquely affected

Gemini was the only model fully re-issued after the most recent `recompute_scores.py` execution (RPD quota recovery on Apr 26 forced a full Gemini re-run; other models were not re-run during that window). So all 246 Gemini records carry the post-rerun state with no reasoning/confidence; the other four models retain reasoning/confidence on their 136 Phase 1 records from earlier recompute_scores.py executions.

The asymmetry is **not** a gemini-specific filter or exclusion — it is the timing artifact of who got re-run last.

## Innocent suspects (verified non-causes)

- No script in `scripts/`, `llm_runner/`, or `evaluation/` filters by `model="gemini"` to null scores.
- No git history available (`runs.jsonl` is in `.gitignore`).
- No stash/uncommitted changes touched these fields.

## What we cannot know

- Whether any deleted one-off scripts existed that could have nulled gemini. The reproducible explanation above (runner schema gap + stale recompute path) is sufficient to fully account for the observed pattern, so a deleted script is unnecessary as an explanation.

## Fix

- **No API calls needed.** Raw responses are intact. `full_score()` regenerates reasoning + confidence deterministically from `raw_response` text.
- Apply Fix A (`recompute_scores.py:23 → tasks_all.json`), then re-run `recompute_scores.py`. Fix B is a side effect of running the fixed Fix A script.
- Independently consider patching `_make_run_record()` to include reasoning + confidence at log time, eliminating the chronic runner schema gap. (Out of Tier 1 scope — flag for future cleanup.)

## State pre-regen

| model | reasoning set | confidence set | total |
|---|---|---|---|
| claude | 136/246 | 136/246 | 246 |
| chatgpt | 136/246 | 136/246 | 246 |
| gemini | 0/246 | 0/246 | 246 |
| deepseek | 136/246 | 136/246 | 246 |
| mistral | 136/246 | 136/246 | 246 |

## State post-regen (2026-05-03 19:55)

| model | reasoning set | confidence set | total |
|---|---|---|---|
| claude | 246/246 | 246/246 | 246 |
| chatgpt | 246/246 | 246/246 | 246 |
| gemini | 246/246 | 246/246 | 246 |
| deepseek | 246/246 | 246/246 | 246 |
| mistral | 246/246 | 246/246 | 246 |

Single execution of `python scripts/recompute_scores.py` (after Fix A path correction) recovered both fields for all 1,230 records. Output: `Recomputed: 1230 | skipped (errors): 0 | missing task: 0`. No API calls. Raw responses were sufficient.

Pre-Fix backup retained at `experiments/results_v1/runs.jsonl.pre_tier1_<timestamp>`.
