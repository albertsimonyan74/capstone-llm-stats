# Phase 10 — Rename Map + Scope Analysis

**Date:** 2026-05-11
**Branch target:** `phase10-refactor`
**Pre-state:** `f884721 Phase 9: section 4.4 content shift to verbalized-vs-self-consistency calibration`

---

## Tier 1 — Directory moves

| Source | Destination |
|---|---|
| `code/data_preprocessing/` | `code/data_preprocessing/` |
| `code/analysis/` | `code/analysis/` |
| `code/models/` | `code/models/` |
| `code/capstone_mcp/` | `code/code/capstone_mcp/` |
| `code/scripts/` | `code/scripts/` |
| `code/visualization/` | `code/visualization/` |
| `data/processed_data/results_v1/` | `data/processed_data/results_v1/` |
| `data/processed_data/results_v2/` | `data/processed_data/results_v2/` |
| `code/scripts/run_benchmark.py` | `code/scripts/run_benchmark.py` |
| `code/scripts/runs_jsonl_adapter.py` | `code/scripts/runs_jsonl_adapter.py` |
| `code/scripts/__init__.py` | (delete) |
| `data/raw_data/benchmark_v1/` | `data/raw_data/benchmark_v1/` |
| `data/raw_data/synthetic/` | `data/raw_data/synthetic/` |

## Tier 2 — File renames inside paper/

| Source | Destination |
|---|---|
| `paper/bib/refs.bib` | `paper/references.bib` |

Plus in `paper/main.tex`: `\bibliography{bib/refs}` → `\bibliography{references}`.

## Unchanged (stay at root)

`poster/`, `literature/`, `llm-stats-vault/`, `llm-stats-vault/cleanup/`, `llm-stats-vault/logs/`,
`capstone-website/`, `paper/`, `bayesian_scope.md`, `CLAUDE.md`,
`README.md`, `requirements.txt`, `environment.yml`, `reproduce.sh`.
`renv.lock` currently lives at `code/visualization/renv.lock` —
will travel with `git mv` into `code/visualization/renv.lock`.

---

## Scope grep — total references per source path (all live file types)

| Source path | Total refs |
|---|---:|
| `baseline` | 334 |
| `evaluation` | 229 |
| `llm_runner` | 192 |
| `capstone_mcp` | 67 |
| `scripts` | 785 |
| `experiments` | 316 |
| `code/visualization` | 35 |
| `data/processed_data/results_v1` | 65 |
| `data/processed_data/results_v2` | 163 |
| `data/raw_data/benchmark_v1` | 72 |
| `data/raw_data/synthetic` | 47 |
| **Grand total** | **2,305** |

> **False-positive caveat:** raw counts use bare token match. Tokens
> like `baseline`, `evaluation`, `scripts`, `experiments` appear as
> English words in LaTeX prose, BST styles, and log files. Slash-suffixed
> match (e.g. `code/data_preprocessing/`) is the real-path count — see breakdown below.

## Python imports — package-level

| Package | Import statements |
|---|---:|
| `baseline` | 80 |
| `evaluation` | 6 |
| `llm_runner` | 22 |
| `capstone_mcp` | 17 |
| **Total** | **125** |

These all get rewritten by the sed pass in 10.D.3.

## Per-source × file-category breakdown

| Source | PY | R | SHELL | MD | TEX | CONFIG | WEBSITE | VAULT | PAPER |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `baseline` | 117 | 1 | 2 | 67 | 0 | 1 | 79 | 60 | 222 |
| `evaluation` | 26 | 1 | 2 | 64 | 2 | 2 | 56 | 55 | 14 |
| `llm_runner` | 34 | 0 | 2 | 101 | 0 | 0 | 9 | 44 | 1 |
| `capstone_mcp` | 28 | 0 | 1 | 28 | 0 | 0 | 0 | 8 | 0 |
| `scripts` | 27 | 12 | 9 | 69 | 1 | 1 | 422 | 70 | 19 |
| `experiments` | 130 | 2 | 5 | 70 | 0 | 0 | 43 | 61 | 3 |
| `code/visualization` | 3 | 3 | 5 | 13 | 0 | 0 | 0 | 5 | 0 |
| `data/processed_data/results_v1` | 23 | 1 | 2 | 27 | 0 | 0 | 0 | 10 | 0 |
| `data/processed_data/results_v2` | 52 | 0 | 2 | 22 | 0 | 0 | 38 | 46 | 1 |
| `data/raw_data/benchmark_v1` | 18 | 0 | 1 | 35 | 0 | 0 | 0 | 17 | 0 |
| `data/raw_data/synthetic` | 19 | 0 | 2 | 14 | 0 | 0 | 3 | 8 | 0 |

WEBSITE column dominated by `capstone-website/backend/static_data/`
(an informational copy of the vault used for serving). Live backend
Python refs are much smaller — see "Website coupling" below.

## Website coupling — live (excluding static_data informational copy)

| Source path | Live website refs |
|---|---:|
| `code/data_preprocessing/` | 0 |
| `code/analysis/` | 1 |
| `code/models/` | 1 |
| `code/capstone_mcp/` | 0 |
| `code/scripts/` | 2 |
| `data/processed_data/results_v2/` | 24 |
| `data/raw_data/synthetic/` | 1 |
| **Total** | **29** |

Concrete filesystem reads on the FastAPI backend are limited:
- `capstone-website/backend/v2_routes.py` — reads from
  `data/processed_data/results_v2/` (24 path strings).
- `capstone-website/backend/main.py` — reads `data/raw_data/synthetic/perturbations.json`
  for v1-pert filtering (1 ref).

29 refs is tractable as a real fix during Phase 10.E. **Recommend
option (a)**: update the backend paths in-flight rather than leaving
broken.

---

## Estimated total work

| Phase | Work | Estimate |
|---|---|---|
| 10.A (this) | Scope analysis | done |
| 10.B | Branch + snapshot | 5 min |
| 10.C | Data restructure + sed (~370 refs, isolated to data paths) | 15 min |
| 10.D | Code restructure + sed (~1,900 live refs across .py / .sh / .md / .R / .tex / configs) | 60–90 min |
| 10.E | Downstream fix-ups (CLAUDE.md, bayesian_scope.md, README, website backend, vault links) | 45 min |
| 10.F | E2E verification (pytest + paper compile + submission ZIP) | 20 min |
| 10.G | Merge | 2 min |
| **Total** | | **2.5–3 hrs wall** |

Per-ref cost is ~negligible because sed handles bulk; the long pole is
verifying after each sed pass and handling residuals (regex misses,
overlapping rewrites, false positives in comment/prose contexts).

---

## Surprises / notes

1. **`paper/` 222 hits for "baseline"** — almost all false positives
   from the `IEEEtran` bibliography style commenting and LaTeX
   `baselineskip` typesetting parameter. Slash-suffix check shows only
   **1 real path reference** in paper/ to `code/data_preprocessing/`. Same pattern for
   `code/analysis/` (only 1 real ref in paper). The TEX risk is small;
   most rewriting needed is in prose comments inside `.tex` source
   files referring to canonical code locations.

2. **`scripts` 785 total hits** dominated by 422 in `capstone-website/`
   (most inside `static_data/` informational copies of the vault) and
   422 from word-token false positives. Real live `code/scripts/` refs are
   manageable (~30 in code, ~12 in R, ~9 in shell, plus paper/2 + few
   in CLAUDE.md / README.md / bayesian_scope.md).

3. **`data/processed_data/results_v2/` 163 refs** is the biggest single
   real-path mover — 52 in PY, 38 in website, 46 in vault. Sed handles
   all of them.

4. **`llm_runner` MD count 101** — vast majority in `llm-stats-vault/`
   (44) and the historic `llm-stats-vault/cleanup/` audit docs. Sed pass against MD
   files (with `--exclude-dir=90-archive,cleanup`) will catch the live
   ones.

5. **No surprises that change strategy.** No single source dir exceeds
   ~800 raw hits, and even 800 is mostly false-positive word usage.
   Plan as written is fine.

6. **Website coupling decision:** option (a) — fix in 10.E. Only 29
   live refs, all in two files (`v2_routes.py`, `main.py`). Cheap.

7. **Vault links:** quick pre-count below.

```text
grep -rn -E "(baseline|evaluation|llm_runner|capstone_mcp|scripts)/" \
  llm-stats-vault/ --exclude-dir=90-archive | wc -l
```

(Reported alongside scope output: vault refs per source dir total
60+55+44+8+70 = **237** in live vault.) That's over the 30-ref
threshold — defer to Monday TODO per 10.E.2 fallback.

---

## Rewrite-rule reference (used by 10.C and 10.D sed passes)

### 10.C — data paths

```
data/processed_data/results_v1   →   data/processed_data/results_v1
data/processed_data/results_v2   →   data/processed_data/results_v2
data/raw_data/benchmark_v1        →   data/raw_data/benchmark_v1
data/raw_data/synthetic           →   data/raw_data/synthetic
```

Recovery sed in case of double-substitution:
```
data/raw_data/  →   data/raw_data/
```

### 10.D — code paths + Python imports

```
^from baseline\.         →   ^from data_preprocessing.
^from baseline           →   ^from data_preprocessing
^import baseline\.       →   ^import data_preprocessing.
^import baseline$        →   ^import data_preprocessing

^from evaluation\.       →   ^from analysis.
^from evaluation         →   ^from analysis
^import evaluation\.     →   ^import analysis.
^import evaluation$      →   ^import analysis

^from llm_runner\.       →   ^from models.
^from llm_runner         →   ^from models
^import llm_runner\.     →   ^import models.
^import llm_runner$      →   ^import models

# capstone_mcp keeps its name — only location changes, no import rewrite needed.

code/data_preprocessing/                →   code/data_preprocessing/
code/analysis/              →   code/analysis/
code/models/              →   code/models/
code/capstone_mcp/            →   code/code/capstone_mcp/
code/scripts/                 →   code/scripts/
code/visualization →  code/visualization
code/scripts/run_benchmark      →  code/scripts/run_benchmark
code/scripts/runs_jsonl_adapter →  code/scripts/runs_jsonl_adapter
```

Excludes for sed pass: `.venv`, `.git`, `node_modules`,
`llm-stats-vault/90-archive`, and `./code/*` once 10.D.2 moves
have happened (to avoid rewriting already-relative internal paths
inside moved packages).
