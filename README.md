# Capstone — Reasoning or Pattern Matching? Multi-Metric and External Judge Evaluation of LLMs on Bayesian Statistical Reasoning

DS 299 Capstone, American University of Armenia, Akian College of Science and Engineering.
Author: Albert Simonyan. Advisor: Vahe Movsisyan, PhD.

## Objective

Benchmark five frontier large-language-model APIs (Claude Sonnet 4.5, GPT-4.1, Gemini 2.5 Flash, DeepSeek-Chat, Mistral Large) on 171 Bayesian and inferential statistical-reasoning tasks with 473 perturbations across three axes (rephrase, semantic, numerical). Score each response by a deterministic keyword rubric, a literature-weighted NMACR aggregator, and an external out-of-family Llama 3.3 70B Turbo judge constrained to assumption-compliance. Compute three independent rank orders — accuracy, robustness, and calibration — and characterise the divergences hidden by single-number leaderboards.

## Software Requirements

- Python 3.11
- R 4.3+ (for figure pipeline)
- TeX Live or TinyTeX 2024+ (for paper compile; needs `IEEEtran.cls`, `IEEEtran.bst`, `amsmath`, `graphicx`, `booktabs`, `hyperref` — `IEEEtran` files vendored in `paper/`)
- macOS / Linux. Tested on macOS Darwin 25.3.0.

## Quick Reproduction

```bash
./reproduce.sh
```

This runs the full pipeline: dependency install, benchmark execution, scoring, figure generation, and paper compilation. Takes ~30 minutes on first run (warm cache: ~5 minutes for figure regeneration only).

## Detailed Reproduction Steps

Step-by-step:
1. Clone repo + create `.env` from `.env.example` with valid API keys for all five LLM providers plus `TOGETHER_API_KEY` for the judge.
2. `python -m venv .venv && source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. `Rscript -e 'renv::restore()'` (restores R deps from `renv.lock`)
5. `code/scripts/refresh_pipeline.sh` (canonical analysis entry point — deduplicates runs, scores, aggregates, computes calibration / robustness / agreement / taxonomy)
6. `cd code/visualization && Rscript run_all.R` (regenerates all paper figures into `figures/`)
7. `cp code/visualization/figures/* paper/figures/` (or manually pick the figures referenced in `main.tex`)
8. `cd paper && pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex`

## How Figures and Tables Were Generated

All figures are generated programmatically (per capstone-guideline §8.2):

- **Figure 1** (pipeline) — matplotlib script inline in build (`code/scripts/_phase7_pipeline.py` equivalent, embedded in `paper/figures/pipeline.png`). TikZ source held back pending TeX Live cross-release upgrade.
- **Figure 2** (rank flow across the three metrics) — `poster/scripts/dimension_leaderboard_print.py` (matplotlib + `poster/scripts/print_theme.py` for white background and dark text at 600 DPI). Copied to `paper/figures/rank_flow.png`.
- **Figure 3** (per-NMACR-dimension ECE) — matplotlib bar chart generated from `data/processed_data/results_v2/per_dim_calibration.json` with the same print-theme palette. Source values come from `code/scripts/calibration_analysis.py`.
- **Table I** (per-model performance) — values from `data/processed_data/results_v2/{calibration,robustness_v2}.json` and `data/processed_data/results_v1/results.json`, formatted by hand in LaTeX `booktabs` (acceptable per guideline since the values come from automated outputs, not the formatting).

To regenerate all figures from scratch:
```bash
Rscript code/visualization/run_all.R
```

## Running the 53-Test Suite

```bash
pytest code/data_preprocessing/ code/capstone_mcp/
```

Tests cover Bayesian and frequentist task generators (`code/data_preprocessing/`) plus the FastMCP query interface (`code/capstone_mcp/`).

## Project Files Layout (Working Repo, post Phase 10)

```
code/
  data_preprocessing/           Bayesian + frequentist task generators + ground-truth solvers
  analysis/                     metrics.py (Path B), llm_judge_rubric.py (Together judge), rubrics
  models/                       5 model clients (httpx, no SDKs), runner, prompt builders, parser
  capstone_mcp/                 FastMCP server exposing 7 query tools over the benchmark
  scripts/                      Analysis pipeline entry points + figure generators + run_benchmark.py
  visualization/                R analysis pipeline (run_all.R, 18 R scripts) + figures
data/
  raw_data/benchmark_v1/        tasks_all.json (171)
  raw_data/synthetic/           perturbations_all.json (473) + schema
  processed_data/results_v1/    Path A scores (runs.jsonl, results.json)
  processed_data/results_v2/    judge scores + downstream analyses
paper/                          IEEEtran conference scaffold + 6 section files + main.tex + references.bib
poster/                         AUA poster TeX + figures + scripts (historical artifact)
report_materials/figures/       Paper-side figure outputs
literature/                     textbooks/ + lectures/ subdir (37 lecture PDFs, gitignored)
llm-stats-vault/                Obsidian vault (sessions, knowledge, atlas, 40-literature/)
  └── 90-archive/               Canonical archive root (audit/, scripts_legacy/, data_legacy/, …)
conftest.py                     Puts code/ on sys.path for pytest
```

Detailed inventory + classification: see `cleanup/01_inventory.md`. Project overview: `bayesian_scope.md`. Operating rules: `CLAUDE.md`.

## Data Sources

- **Task suite**: hand-authored by the author, programmatically generated by `code/data_preprocessing/bayesian/build_tasks_*.py` from textbook formulations (Bolstad 2007, Hoff 2009, Bishop 2006).
- **Perturbations**: 75 hand-authored seeds plus 398 LLM-generated (Together AI Llama 3.3 70B Turbo via `code/scripts/generate_perturbations_full.py`), all filtered against the ground-truth solver before inclusion.
- **Model outputs**: API calls to Anthropic, OpenAI, Google, DeepSeek, Mistral, and Together AI between 2026-04-30 and 2026-05-03 (see `data/processed_data/results_v2/*.jsonl` headers for exact per-run timestamps).
- **Bibliography**: curated from `llm-stats-vault/40-literature/citation-map.md`; bibtex stored at `paper/references.bib`.

## Academic Integrity Statement

All code in this repository is original work by the author except where explicitly noted. External libraries are listed in `requirements.txt` and `renv.lock` with their respective licenses preserved. The capstone was developed with the assistance of Anthropic's Claude (Sonnet 4.5 / 4.6 and Opus) for code generation, review, and prose drafting; all final analytical decisions, methodological choices, and substantive claims are the author's own. The benchmark task content draws on standard textbook formulations of Bayesian and inferential statistics (Bolstad 2007, Hoff 2009, Bishop 2006), cited in `paper/references.bib`.

## Citation

If you use this work, please cite as:

```
Simonyan, A. "Reasoning or Pattern Matching? Multi-Metric and External
Judge Evaluation of LLMs on Bayesian Statistical Reasoning."
CODASSCA 2026.
```

## License

MIT (TODO: confirm with advisor before public release).
