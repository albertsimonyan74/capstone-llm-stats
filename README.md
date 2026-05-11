# Capstone — Reasoning or Pattern Matching? Multi-Metric and External Judge Evaluation of LLMs on Bayesian Statistical Reasoning

DS 299 Capstone, American University of Armenia, Akian College of Science & Engineering.
Author: Albert Simonyan. Advisor: Vahe Movsisyan, PhD.

## Project Objective

Benchmark five frontier large-language-model APIs (Claude Sonnet 4.5, GPT-4.1, Gemini 2.5 Flash, DeepSeek-Chat, Mistral Large) on 171 Bayesian and inferential statistical-reasoning tasks with 473 perturbations across three axes (rephrase, semantic, numerical). Score each response by a deterministic keyword rubric, a literature-weighted NMACR aggregator, and an external out-of-family Llama 3.3 70B Turbo judge constrained to assumption-compliance and reasoning quality. Compute three independent rank orders — accuracy, robustness, calibration — and characterize the divergences hidden by single-number leaderboards.

The headline contribution is the three-ranking framework and empirical evidence that the rank order of the same five models depends on which axis you measure.

## Research Questions

- **RQ1.** How accurately do frontier LLMs solve closed-form Bayesian problems (Phase 1 conjugate models)?
- **RQ2.** How accurately do they solve computational Bayesian methods (Phase 2: Gibbs / MH / HMC / RJMCMC / VB / ABC / hierarchical)?
- **RQ3.** Where does each model fail — what is the dominant L1 failure category (assumption violation, mathematical error, formatting, conceptual)?
- **RQ4.** How robust are model accuracies under three perturbation axes (rephrase / numerical / semantic)? Canonical scope: 473 perturbations covering all 171 base tasks.
- **RQ5.** How well-calibrated is each model's stated confidence vs its empirical accuracy (binary-pass ECE)?

## Repository Map

```
code/
  data_preprocessing/           Bayesian + frequentist task generators + ground-truth solvers
  analysis/                     metrics.py (Path B), llm_judge_rubric.py (Together judge), rubrics
  models/                       5 model clients (httpx, no SDKs), runner, prompt builders, parser
  capstone_mcp/                 FastMCP server exposing 7 query tools over the benchmark
  scripts/                      Analysis pipeline entry points + figure generators + run_benchmark.py
  visualization/                R analysis pipeline (run_all.R, 18 R scripts) + figures
data/
  raw_data/benchmark_v1/        tasks.json + tasks_advanced.json + tasks_all.json (171)
  raw_data/synthetic/           perturbations_all.json (473) + schema
  processed_data/results_v1/    Path A scores (runs.jsonl, results.json)
  processed_data/results_v2/    judge scores + downstream analyses
paper/                          IEEEtran conference scaffold + 6 section files + main.tex + references.bib + figures/
poster/                         AUA poster TeX + figures + scripts (historical artifact)
literature/                     textbooks/ + lectures/ subdir (37 lecture PDFs, gitignored)
llm-stats-vault/                Obsidian vault (sessions, knowledge, atlas, 40-literature/, cleanup/, logs/)
  └── 90-archive/               Canonical archive root (audit/, scripts_legacy/, data_legacy/, …)
conftest.py                     Puts code/ on sys.path for pytest
```

Phase 10 (2026-05-11) restructured the repo to capstone-guideline §5 layout. Pre-Phase-10 directories `baseline/`, `evaluation/`, `llm_runner/`, `experiments/`, `report_materials/r_analysis/` no longer exist at the working-repo root. Phase 12 (2026-05-11) moved `cleanup/` and `logs/` under `llm-stats-vault/`. Phase 14 (2026-05-11) merged `report_materials/figures/` into `paper/figures/`. Archival convention: all under `llm-stats-vault/90-archive/<category>_legacy/`.

Operating rules: [CLAUDE.md](CLAUDE.md). Methodology rationale: `llm-stats-vault/90-archive/audit/{aggregation_locus.md, methodology_continuity.md, limitations_disclosures.md}`.

## Software Requirements

- Python 3.11
- R 4.3+ (for figure pipeline)
- TeX Live or TinyTeX 2024+ for paper compile. Needs `IEEEtran.cls`, `IEEEtran.bst`, `amsmath`, `graphicx`, `booktabs`, `float`, `hyperref`. `IEEEtran` files vendored in `paper/`.
- macOS or Linux. Tested on macOS Darwin 25.3.0.

## Required API Keys

Copy `.env.example` → `.env` and fill in:

| Variable | Used by |
|---|---|
| `ANTHROPIC_API_KEY` | Claude Sonnet 4.5 |
| `OPENAI_API_KEY` | GPT-4.1 |
| `GEMINI_API_KEY` | Gemini 2.5 Flash |
| `DEEPSEEK_API_KEY` | DeepSeek-Chat |
| `MISTRAL_API_KEY` | Mistral Large |
| `TOGETHER_API_KEY` | Llama 3.3 70B Turbo (external judge) |

Missing keys produce error records rather than aborting; runs are skipped per missing key.

## Quick Start

```bash
./reproduce.sh
```

Runs the full pipeline: dependency install, benchmark execution, scoring, figure generation, paper compilation. About 30 minutes on first run; ~5 minutes for figure-only regeneration with warm cache.

## Detailed Reproduction Steps

1. Clone the repo and create `.env` from `.env.example` with valid API keys for all five LLM providers plus `TOGETHER_API_KEY`.
2. `python -m venv .venv && source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. `Rscript -e 'renv::restore()'` (restores R deps from `renv.lock`)
5. `export PYTHONPATH="$(pwd)/code"`
6. `bash code/scripts/refresh_pipeline.sh` — canonical analysis entry point. Deduplicates runs, scores, aggregates, computes calibration, robustness, agreement, taxonomy.
7. `cd code/visualization && Rscript run_all.R` — regenerates all paper figures into `figures/`.
8. `cp code/visualization/figures/* paper/figures/` (or pick the figures referenced by `main.tex`).
9. `cd paper && pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex`

## Benchmark Design

### Task suite

171 base tasks across 38 task types in two phases. Generators are deterministic; task JSON files are never edited manually, only regenerated.

**Phase 1 — closed-form conjugate models (136 tasks, 31 types).** Generated by `code/data_preprocessing/bayesian/build_tasks_bayesian.py` → `data/raw_data/benchmark_v1/tasks.json`. Covers Beta-Binomial, Gamma-Poisson, Normal mean (known/unknown σ²), Normal-Inverse-Gamma, Dirichlet-Multinomial, Bayesian linear regression, decision theory (Bayes risk under squared, absolute, 0-1 loss), prior sensitivity / improper priors, and Box-Muller / inverse-transform stress tests.

**Phase 2 — computational Bayesian methods (35 tasks, 7 types, 5 tasks each).** Generated by `build_tasks_advanced.py` → `tasks_advanced.json`. Uses `np.random.seed(42)` for ground-truth MC estimates.

| Type | Method | Tolerance |
|---|---|---|
| GIBBS | Gibbs Sampling | 0.05 |
| MH | Metropolis-Hastings | 0.05 |
| HMC | Hamiltonian Monte Carlo | 0.05 |
| RJMCMC | Reversible Jump MCMC | 0.05 |
| HIERARCHICAL | Hierarchical Bayes | 0.05 |
| VB | Variational Bayes | 0.10 |
| ABC | Approximate Bayesian Computation | 0.10 |

Combined task set: `data/raw_data/benchmark_v1/tasks_all.json` (171 records).

### Perturbations — three axes, 473 records

Canonical superset: `data/raw_data/synthetic/perturbations_all.json` (473 records covering all 171 base tasks; mean 2.77 per base). 75 hand-authored seeds (25 bases) plus 398 LLM-generated v2 (146 bases) partition the space disjointly.

| Axis | Records | Description |
|---|---:|---|
| `rephrase` | 171 | Same math + answer, prompt reworded |
| `semantic` | 171 | Same math, new real-world framing |
| `numerical` | 131 | Numbers changed, ground truth recomputed |

v2 generator: `code/scripts/generate_perturbations_full.py` (Together AI Llama 3.3 70B Turbo). Every generated perturbation was checked against the ground-truth solver before inclusion.

### Models evaluated

Queried via direct `httpx`, no vendor SDKs. Configured in `code/models/model_clients.py`.

| Family | Model string | Provider endpoint |
|---|---|---|
| `claude` | `claude-sonnet-4-5` | Anthropic Messages |
| `chatgpt` | `gpt-4.1` | OpenAI Chat Completions |
| `gemini` | `gemini-2.5-flash` | Google Generative Language |
| `deepseek` | `deepseek-chat` | DeepSeek Chat Completions |
| `mistral` | `mistral-large-latest` | Mistral Chat Completions |

Shared run config: `_MAX_TOKENS=1024`, `_TIMEOUT=60s`, retries 3× with provider-specific backoff. Gemini uses 30/60/120s waits to handle RPM limits; daily RPD exhaustion is non-recoverable (quota resets midnight Pacific). System prompt is identical across all 5 models.

## Evaluation Methodology

Three independent scoring paths. The keyword-rubric paths (A and B) must remain weight-aligned; the external judge is independent.

### NMACR per-task components

Five dimensions in [0, 1] with literature-derived weights (sole canonical scheme since Approach A, 2026-05-03):

| Symbol | Component | Weight |
|---|---|---:|
| N | Numerical Accuracy | 0.10 |
| M | Method / Structure | 0.20 |
| A | Assumption Compliance | 0.30 |
| C | Confidence Calibration | 0.15 |
| R | Reasoning Quality | 0.25 |

Weights defended in `code/analysis/metrics.py` docstring; full literature trail in `llm-stats-vault/90-archive/audit/methodology_continuity.md` (Du 2025, Boye & Moell 2025, Yamauchi 2025, ReasonBench 2025, Wei 2022, Chen 2022, Bishop 2006, Nagarkar 2026, FermiEval 2025, Liu 2025).

### Path A — live runner (deterministic keyword rubric)

`code/models/response_parser.py`: `full_score(raw_response, task) -> dict`. Used by `code/models/run_all_tasks.py` to score each model response as it streams in. CONCEPTUAL tasks scored as `1.0 × rubric_score`; tasks with both numeric targets and rubric structure scored as `0.6 × numeric + 0.4 × rubric`. Pass threshold `final_score ≥ 0.5`.

### Path B — post-hoc (TaskRun dataclass aggregation)

`code/analysis/metrics.py`: `score_all_models(tasks, runs)` operates on `TaskRun` dataclasses parsed from `runs.jsonl`. Same NMACR weights, same numeric/rubric blend. Tier-5 stress-test multiplier 1.50 (no Tier-5 tasks currently exist).

### External judge — Llama 3.3 70B Turbo via Together AI

`code/analysis/llm_judge_rubric.py`: independent re-scoring of each `(task, response)` pair on four dimensions: `METHOD_STRUCTURE`, `ASSUMPTION_COMPLIANCE`, `REASONING_QUALITY`, `REASONING_COMPLETENESS`. Model is `meta-llama/Llama-3.3-70B-Instruct-Turbo`, T=0.0, max_tokens=1024. Out-of-family by design (none of the 5 benchmarked models). Cost ≈ $8 for ~3,800 judge calls at $0.88/M tokens.

Outputs: `data/processed_data/results_v2/llm_judge_scores_full.jsonl` (base runs), `perturbation_judge_scores.jsonl` (perturbation runs), `error_taxonomy_v2_judge.jsonl` (failure classification).

### Aggregation locus

Single-path aggregation: each task contributes one normalized score; models are averaged across all tasks completed. Avoids the two-stage averaging bias earlier v1 analyses exhibited. Rationale: `llm-stats-vault/90-archive/audit/aggregation_locus.md`.

## Three-Ranking Framework — Headline Finding

The same five models reorder when scored on different axes. Central empirical claim of the paper.

**Ranking by accuracy** (Path A normalized score):

1. Claude 0.683
2. Mistral 0.644
3. Gemini 0.642
4. DeepSeek 0.625
5. GPT-4.1 0.621

**Ranking by robustness** (1 − Δ between base and perturbation pass rate):

1. GPT-4.1 0.9996 (Δ = 0.0003)
2. Mistral 0.9981 (Δ = 0.0013)
3. Gemini 0.9824 (Δ = 0.0129)
4. Claude 0.9565 (Δ = 0.0305)
5. DeepSeek 0.9422 (Δ = 0.0388)

**Ranking by calibration** (binary-pass ECE, lower = better):

1. Claude 0.0334
2. GPT-4.1 0.0339
3. Gemini 0.0765
4. Mistral 0.0811
5. DeepSeek 0.1977

Two headline patterns: Claude leads accuracy and calibration but drops to 4th on robustness; GPT-4.1 is last on accuracy but first on robustness. The Claude-vs-GPT-4.1 calibration gap (0.0005) is within bootstrap CI; the accuracy-robustness inversion for GPT-4.1 is the clearer story.

**Supporting findings.** Assumption violation is the dominant failure mode at 47% of judge-classified failures (`ASSUMPTION_VIOLATION` 67, `MATHEMATICAL_ERROR` 48, `FORMATTING_FAILURE` 18, `CONCEPTUAL_ERROR` 10; n=143). Keyword-vs-judge agreement on assumption-compliance: Spearman ρ = 0.602 (n=750 paired runs). Keyword rubric passes 71.1% on the assumption dimension; judge passes 55.7%. Surface-form scoring systematically overcounts substantive assumption articulation.

## How Figures and Tables Were Generated

All figures are generated programmatically per capstone-guideline §8.2:

- **Figure 1** (pipeline) — matplotlib via `code/scripts/_phase7_pipeline.py` equivalent. Output at `paper/figures/pipeline.png`. TikZ source held back pending TeX Live cross-release upgrade.
- **Figure 2** (rank flow across the three metrics) — `poster/scripts/dimension_leaderboard_print.py` (matplotlib + `poster/scripts/print_theme.py` for white background, dark text, 600 DPI). Copied to `paper/figures/rank_flow.png`.
- **Figure 3** (Krippendorff strip across judged dimensions) — `poster/scripts/krippendorff_strip_print.py`. Output `paper/figures/krippendorff_strip.png`.
- **Figure 4** (calibration ECE paired, verbalized vs self-consistency) — `poster/scripts/calibration_ece_paired_print.py`. Output `paper/figures/calibration_ece_paired.png`.
- **Table I** (per-model performance) — values from `data/processed_data/results_v2/{calibration,robustness_v2}.json` and `data/processed_data/results_v1/results.json`, formatted in LaTeX `booktabs`.

To regenerate all figures from scratch:

```bash
Rscript code/visualization/run_all.R
```

## Running the Test Suite

```bash
pytest code/data_preprocessing/frequentist/test_frequentist.py code/capstone_mcp/test_server.py -v
```

53 tests cover Bayesian and frequentist task generators (`code/data_preprocessing/`) plus the FastMCP query interface (`code/capstone_mcp/`).

Lint:

```bash
ruff check .
```

## Data Sources

- **Task suite**: hand-authored by the author, programmatically generated by `code/data_preprocessing/bayesian/build_tasks_*.py` from textbook formulations (Bolstad 2007, Hoff 2009, Bishop 2006).
- **Perturbations**: 75 hand-authored seeds plus 398 LLM-generated via `code/scripts/generate_perturbations_full.py` (Together AI Llama 3.3 70B Turbo). All filtered against the ground-truth solver before inclusion.
- **Model outputs**: API calls to Anthropic, OpenAI, Google, DeepSeek, Mistral, and Together AI between 2026-04-30 and 2026-05-03. Per-run timestamps in `data/processed_data/results_v2/*.jsonl` headers.
- **Bibliography**: curated from `llm-stats-vault/40-literature/citation-map.md`; bibtex stored at `paper/references.bib`.

## Academic Integrity Statement

All code in this repository is original work by the author except where explicitly noted. External libraries are listed in `requirements.txt` and `renv.lock` with their respective licenses preserved. The capstone was developed with the assistance of Anthropic's Claude (Sonnet 4.5 / 4.6 and Opus) for code generation, review, and prose drafting; all final analytical decisions, methodological choices, and substantive claims are the author's own. The benchmark task content draws on standard textbook formulations of Bayesian and inferential statistics (Bolstad 2007, Hoff 2009, Bishop 2006), cited in `paper/references.bib`.

## Citation

```
Simonyan, A. "Reasoning or Pattern Matching? Multi-Metric and External
Judge Evaluation of LLMs on Bayesian Statistical Reasoning."
CODASSCA 2026.
```

## License

MIT (TODO: confirm with advisor before public release).
