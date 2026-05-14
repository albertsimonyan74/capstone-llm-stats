# Scope grep — `results_v1` / `results_v2` references

Generated 2026-05-10. Run from repo root.

Excludes: `.venv/`, `node_modules/`, `.git/`, `llm-stats-vault/90-archive/`, `llm-stats-vault/cleanup/`.

## Summary

| Category | Files | Refs |
|---|---:|---:|
| DOCS | 9 | 27 |
| LIVE_CODE | 28 | 111 |
| PAPER_DOCS | 5 | 13 |
| POSTER_DOCS | 10 | 31 |
| VAULT_DOCS | 19 | 56 |
| WEBSITE_BUNDLE | 7 | 14 |
| WEBSITE_CODE | 4 | 26 |
| **TOTAL** | **82** | **278** |

**Verdict: 278 refs >> 80-ref threshold. DESCOPE REQUIRED.**

## Per-file breakdown by category

### DOCS

- `CLAUDE.md` (2 refs)
    - L134: `- `data/processed_data/results_v1/runs.jsonl` — append-only, never truncate`
    - L135: `- `data/processed_data/results_v1/results.json` — dict: `model_aggregates` + `task_scores``
- `bayesian_scope.md` (1 refs)
    - L122: `Analysis: `scripts/analyze_perturbations.py` → `data/processed_data/results_v1/rq4_analysis.json``
- `planning/ROADMAP.md` (1 refs)
    - L32: `- Output: `data/processed_data/results_v1/perturbation_analysis.json` + summary table`
- `planning/STATE.md` (2 refs)
    - L44: `- runs: data/processed_data/results_v1/runs.jsonl (~620+ records)`
    - L45: `- results: data/processed_data/results_v1/results.json (EMPTY)`
- `planning/codebase/ARCHITECTURE.md` (6 refs)
    - L86: `- Location: `data/raw_data/benchmark_v1/`, `data/raw_data/synthetic/`, `data/processed_data/results_v1/``
    - L96: `- Used by: Run from CLI; produces `data/processed_data/results_v1/runs.jsonl``
    - L130: `10. **Append to JSONL** — `log_jsonl(output_path, record)` appends one JSON object per run to `data/processed_data/results_v1/ru`
    - ... +3 more
- `planning/codebase/CONCERNS.md` (7 refs)
    - L12: `- **Files:** `data/processed_data/results_v1/runs.jsonl`, `code/models/model_clients.py``
    - L19: `- **Files:** `data/processed_data/results_v1/runs.jsonl``
    - L26: `- **Files:** `data/processed_data/results_v1/runs.jsonl`, `data/raw_data/synthetic/perturbations.json``
    - ... +4 more
- `planning/codebase/CONVENTIONS.md` (1 refs)
    - L92: `- `data/processed_data/results_v1/runs.jsonl` — append-only, never truncate`
- `planning/codebase/INTEGRATIONS.md` (3 refs)
    - L107: `- `data/processed_data/results_v1/runs.jsonl` — one JSON object per LLM run, written by `code/models/logger.py``
    - L108: `- `data/processed_data/results_v1/results.json` — scoring output from `code/scripts/run_benchmark.py``
    - L144: `**Logging:** Run logs written to `data/processed_data/results_v1/runs.jsonl` via `code/models/logger.py` (`log_jsonl()` — append-`
- `planning/codebase/STRUCTURE.md` (4 refs)
    - L63: `│   └── results_v1/`
    - L168: `**`data/processed_data/results_v1/`:**`
    - L222: `- `data/processed_data/results_v1/runs.jsonl` — append-only run log (source of truth for all actual LLM outputs)`
    - ... +1 more

### LIVE_CODE

- `capstone_mcp/tools/results.py` (2 refs)
    - L9: `_RESULTS_FILE = Path(__file__).parent.parent.parent / "experiments" / "results_v1" / "results.json"`
    - L10: `_RUNS_FILE    = Path(__file__).parent.parent.parent / "experiments" / "results_v1" / "runs.jsonl"`
- `code/scripts/run_benchmark.py` (3 refs)
    - L6: `- writes results to data/processed_data/results_v1/results.json`
    - L122: `runs_path  = "data/processed_data/results_v1/runs.jsonl"`
    - L123: `out_path   = "data/processed_data/results_v1/results.json"`
- `code/models/run_all_tasks.py` (3 refs)
    - L7: `logs results to data/processed_data/results_v1/runs.jsonl.`
    - L337: `"--output", default="data/processed_data/results_v1/runs.jsonl",`
    - L338: `help="Output JSONL path (default: data/processed_data/results_v1/runs.jsonl)",`
- `code/visualization/00_load_data.R` (2 refs)
    - L20: `"experiments", "results_v1", "runs.jsonl")`
    - L23: `RUNS_PATH <- "../../data/processed_data/results_v1/runs.jsonl"`
- `scripts/analyze_errors.py` (1 refs)
    - L20: `RUNS_PATH  = "data/processed_data/results_v1/runs.jsonl"`
- `scripts/analyze_perturbations.py` (3 refs)
    - L6: `Outputs data/processed_data/results_v1/rq4_analysis.json`
    - L27: `RUNS_PATH     = os.path.join(ROOT, "experiments", "results_v1", "runs.jsonl")`
    - L29: `OUTPUT_PATH   = os.path.join(ROOT, "experiments", "results_v1", "rq4_analysis.json")`
- `scripts/bootstrap_ci.py` (7 refs)
    - L8: `- data/processed_data/results_v1/runs.jsonl`
    - L9: `- data/processed_data/results_v2/perturbation_runs.jsonl`
    - L12: `- data/processed_data/results_v2/bootstrap_ci.json`
    - ... +4 more
- `scripts/calibration_analysis.py` (4 refs)
    - L15: `- data/processed_data/results_v2/calibration.json`
    - L45: `RUNS_PATH = Path("data/processed_data/results_v1/runs.jsonl")`
    - L48: `JUDGE_PATH = Path("data/processed_data/results_v2/llm_judge_scores_full.jsonl")`
    - ... +1 more
- `scripts/combined_pass_flip_analysis.py` (6 refs)
    - L29: `- data/processed_data/results_v2/combined_pass_flip_analysis.json`
    - L63: `BASE_RUNS = Path("data/processed_data/results_v1/runs.jsonl")`
    - L64: `BASE_JUDGE = Path("data/processed_data/results_v2/llm_judge_scores_full.jsonl")`
    - ... +3 more
- `scripts/dedup_runs.py` (1 refs)
    - L15: `RUNS_PATH  = os.path.join(ROOT, "experiments", "results_v1", "runs.jsonl")`
- `scripts/dimension_leaderboard.py` (3 refs)
    - L35: `BOOTSTRAP = ROOT / "experiments" / "results_v2" / "bootstrap_ci.json"`
    - L36: `ROBUST = ROOT / "experiments" / "results_v2" / "robustness_v2.json"`
    - L37: `CALIB = ROOT / "experiments" / "results_v2" / "calibration.json"`
- `scripts/disagreement_by_perttype.py` (2 refs)
    - L8: `data/processed_data/results_v2/combined_pass_flip_analysis.json`
    - L35: `SRC = ROOT / "experiments" / "results_v2" / "combined_pass_flip_analysis.json"`
- `scripts/error_taxonomy.py` (4 refs)
    - L8: `data/processed_data/results_v2/error_taxonomy_v2.json`
    - L38: `RUNS_PATH = ROOT / "data/processed_data/results_v1/runs.jsonl"`
    - L40: `OUT_JSON = ROOT / "data/processed_data/results_v2/error_taxonomy_v2.json"`
    - ... +1 more
- `scripts/generate_group_a_figures.py` (9 refs)
    - L43: `RUNS_V1 = ROOT / "experiments" / "results_v1" / "runs.jsonl"`
    - L44: `PERT_RUNS = ROOT / "experiments" / "results_v2" / "perturbation_runs.jsonl"`
    - L45: `TAXONOMY = ROOT / "experiments" / "results_v2" / "error_taxonomy_v2.json"`
    - ... +6 more
- `scripts/keyword_degradation_check.py` (2 refs)
    - L8: `Output: data/processed_data/results_v2/keyword_degradation_check.json`
    - L35: `OUT_JSON = Path("data/processed_data/results_v2/keyword_degradation_check.json")`
- `scripts/keyword_vs_judge_agreement.py` (6 refs)
    - L3: `Reads keyword scores from data/processed_data/results_v1/runs.jsonl and judge scores`
    - L4: `from data/processed_data/results_v2/llm_judge_scores_full.jsonl. Joins by run_id.`
    - L36: `RUNS_PATH = Path("data/processed_data/results_v1/runs.jsonl")`
    - ... +3 more
- `scripts/krippendorff_agreement.py` (12 refs)
    - L12: `- data/processed_data/results_v1/runs.jsonl`
    - L13: `- data/processed_data/results_v2/llm_judge_scores_full.jsonl`
    - L17: `- data/processed_data/results_v2/krippendorff_agreement.json`
    - ... +9 more
- `scripts/plot_self_consistency_calibration.py` (2 refs)
    - L27: `VERB_CAL = ROOT / "experiments" / "results_v2" / "calibration.json"`
    - L28: `SC_CAL = ROOT / "experiments" / "results_v2" / "self_consistency_calibration.json"`
- `scripts/rank_shift.py` (3 refs)
    - L28: `BOOTSTRAP_PATH = ROOT / "experiments" / "results_v2" / "bootstrap_ci.json"`
    - L29: `ROBUST_PATH = ROOT / "experiments" / "results_v2" / "robustness_v2.json"`
    - L30: `CALIB_PATH = ROOT / "experiments" / "results_v2" / "calibration.json"`
- `scripts/recompute_downstream.py` (11 refs)
    - L4: `Reads data/processed_data/results_v2/nmacr_scores_v2.jsonl (produced by recompute_scores.py)`
    - L7: `3a. data/processed_data/results_v2/bootstrap_ci.json`
    - L8: `3b. data/processed_data/results_v2/robustness_v2.json (Layer 1 + Layer 2 per-dim deltas)`
    - ... +8 more
- `scripts/recompute_scores.py` (2 refs)
    - L2: `Recompute all scores in data/processed_data/results_v1/runs.jsonl using the`
    - L22: `RUNS_PATH  = Path("data/processed_data/results_v1/runs.jsonl")`
- `scripts/refresh_pipeline.sh` (2 refs)
    - L38: `echo "  data/processed_data/results_v1/results.json"`
    - L39: `echo "  data/processed_data/results_v1/rq4_analysis.json"`
- `scripts/robustness_analysis.py` (2 refs)
    - L3: `Reads canonical data/processed_data/results_v2/robustness_v2.json (written by`
    - L37: `CANONICAL_JSON = ROOT / "experiments" / "results_v2" / "robustness_v2.json"`
- `scripts/score_perturbations.py` (4 refs)
    - L8: ``data/processed_data/results_v2/perturbation_runs.jsonl`. Resume-safe: skips any`
    - L13: `--runs data/processed_data/results_v2/perturbation_runs.jsonl \\`
    - L15: `--output data/processed_data/results_v2/perturbation_judge_scores.jsonl`
    - ... +1 more
- `scripts/self_consistency_full.py` (6 refs)
    - L26: `- data/processed_data/results_v2/self_consistency_runs_full.jsonl       (append-only)`
    - L27: `- data/processed_data/results_v2/self_consistency_calibration_full.json`
    - L52: `CALIB_VERBALIZED = ROOT / "data/processed_data/results_v2/calibration.json"`
    - ... +3 more
- `scripts/summarize_results.py` (2 refs)
    - L4: `Reads data/processed_data/results_v1/runs.jsonl → generates`
    - L17: `RUNS_PATH   = os.path.join(ROOT, 'experiments', 'results_v1', 'runs.jsonl')`
- `scripts/three_rankings_figure.py` (3 refs)
    - L25: `CALIB_PATH = ROOT / "experiments" / "results_v2" / "calibration.json"`
    - L26: `ROBUST_PATH = ROOT / "experiments" / "results_v2" / "robustness_v2.json"`
    - L27: `BOOTSTRAP_PATH = ROOT / "experiments" / "results_v2" / "bootstrap_ci.json"`
- `scripts/tolerance_sensitivity.py` (4 refs)
    - L15: `data/processed_data/results_v1/runs.jsonl`
    - L18: `data/processed_data/results_v2/tolerance_sensitivity.json`
    - L40: `RUNS_PATH = ROOT / "experiments" / "results_v1" / "runs.jsonl"`
    - ... +1 more

### PAPER_DOCS

- `paper/sections/00_abstract.tex` (1 refs)
    - L15: `%     Spearman rho = 0.59. Source: data/processed_data/results_v2/.`
- `paper/sections/01_introduction.tex` (2 refs)
    - L14: `%     data/processed_data/results_v2/calibration.json,`
    - L15: `%     data/processed_data/results_v2/robustness_v2.json.`
- `paper/sections/04_experimental_setup.tex` (2 refs)
    - L25: `%       data/processed_data/results_v2/calibration.json (per-model bins,`
    - L34: `%       data/processed_data/results_v2/{robustness_v2,calibration,`
- `paper/sections/05_results.tex` (5 refs)
    - L6: `%     - Accuracy ranking from data/processed_data/results_v1/results.json`
    - L9: `%       data/processed_data/results_v2/robustness_v2.json + bootstrap_ci.json.`
    - L11: `%       data/processed_data/results_v2/calibration.json + per_dim_calibration.json.`
    - ... +2 more
- `paper/sections/07_threats_to_validity.tex` (3 refs)
    - L23: `%       Bootstrap CIs (data/processed_data/results_v2/bootstrap_ci.json) report`
    - L25: `%       data/processed_data/results_v2/tolerance_sensitivity.json.`
    - L29: `%       in data/processed_data/results_v2/nmacr_scores_v2.jsonl and`

### POSTER_DOCS

- `poster/README.md` (1 refs)
    - L12: `| 2 | Krippendorff α gradient strip       | krippendorff_strip_print.py                            | code/scripts/results`
- `poster/SCRAPE_PLAN.md` (1 refs)
    - L111: ``data/processed_data/results_v2/*` (live JSON), `CLAUDE.md`, and`
- `poster/WEBSITE_SCRAPE.md` (7 refs)
    - L1459: ``data/processed_data/results_v2/bootstrap_ci.json` (B=10,000, seed=42).`
    - L1473: ``data/processed_data/results_v2/robustness_v2.json`.`
    - L1486: ``data/processed_data/results_v2/calibration.json`.`
    - ... +4 more
- `poster/scripts/calibration_ece_paired_print.py` (4 refs)
    - L7: `data/processed_data/results_v2/calibration.json:[model].ece`
    - L9: `data/processed_data/results_v2/self_consistency_calibration.json`
    - L31: `VERB_FILE = ROOT / "experiments" / "results_v2" / "calibration.json"`
    - ... +1 more
- `poster/scripts/derive_disagreement_matrix_2x2.py` (4 refs)
    - L32: `BASE_RUNS  = ROOT / "experiments" / "results_v1" / "runs.jsonl"`
    - L33: `BASE_JUDGE = ROOT / "experiments" / "results_v2" / "llm_judge_scores_full.jsonl"`
    - L34: `PERT_RUNS  = ROOT / "experiments" / "results_v2" / "perturbation_runs.jsonl"`
    - ... +1 more
- `poster/scripts/derive_failure_taxonomy_per_task.py` (4 refs)
    - L8: `data/processed_data/results_v2/error_taxonomy_v2.json:records, broken down by L1`
    - L17: `Denominator (per task_type): total runs in data/processed_data/results_v1/runs.jsonl`
    - L44: `TAX_FILE  = ROOT / "experiments" / "results_v2" / "error_taxonomy_v2.json"`
    - ... +1 more
- `poster/scripts/derive_keyword_judge_heatmap_4panel.py` (3 refs)
    - L4: `data/processed_data/results_v1/runs.jsonl × data/processed_data/results_v2/llm_judge_scores_full.jsonl`
    - L34: `BASE_RUNS  = ROOT / "experiments" / "results_v1" / "runs.jsonl"`
    - L35: `BASE_JUDGE = ROOT / "experiments" / "results_v2" / "llm_judge_scores_full.jsonl"`
- `poster/scripts/derive_robustness_heatmap.py` (2 refs)
    - L3: `Source: data/processed_data/results_v2/robustness_v2.json, field`
    - L26: `ROBUST = ROOT / "experiments" / "results_v2" / "robustness_v2.json"`
- `poster/scripts/dimension_leaderboard_print.py` (3 refs)
    - L30: `BOOTSTRAP = ROOT / "experiments" / "results_v2" / "bootstrap_ci.json"`
    - L31: `ROBUST = ROOT / "experiments" / "results_v2" / "robustness_v2.json"`
    - L32: `CALIB = ROOT / "experiments" / "results_v2" / "calibration.json"`
- `poster/scripts/krippendorff_strip_print.py` (2 refs)
    - L3: `Reads data/processed_data/results_v2/krippendorff_agreement.json and renders a`
    - L31: `KRIPP   = ROOT / "experiments" / "results_v2" / "krippendorff_agreement.json"`

### VAULT_DOCS

- `llm-stats-vault/00-home/research-narrative.md` (1 refs)
    - L258: `Surfaced in `data/processed_data/results_v2/calibration.json` →`
- `llm-stats-vault/40-literature/citation-map.md` (10 refs)
    - L104: `- `data/processed_data/results_v2/bootstrap_ci.json`: Papers 06, 15`
    - L105: `- `data/processed_data/results_v2/robustness_v2.json`: Paper 08`
    - L106: `- `data/processed_data/results_v2/error_taxonomy_v2.json`: Papers 09, 13`
    - ... +7 more
- `llm-stats-vault/40-literature/papers/02-original-can-llm-reasoning-2026.md` (2 refs)
    - L22: `Motivates RQ5 (confidence calibration). Findings parallel our keyword-confidence extraction limitations and the empty hi`
    - L36: `- data/processed_data/results_v2/calibration.json`
- `llm-stats-vault/40-literature/papers/06-new-longjohn-bayesian-eval-2025.md` (2 refs)
    - L22: `Direct motivation for our bootstrap CI workstream (Window 4). Maps to scripts/bootstrap_ci.py and data/processed_data/results_v2`
    - L35: `- data/processed_data/results_v2/bootstrap_ci.json`
- `llm-stats-vault/40-literature/papers/08-new-brittlebench-2026.md` (2 refs)
    - L22: `Our perturbation methodology (rephrase / numerical / semantic — 398 perturbations × 5 models) is a domain-specific insta`
    - L38: `- data/processed_data/results_v2/robustness_v2.json`
- `llm-stats-vault/40-literature/papers/09-new-ice-cream-causal-2025.md` (2 refs)
    - L22: `Independent confirmation of our finding that ASSUMPTION_VIOLATION is the dominant failure mode (matches our 46.9%). Thei`
    - L35: `- data/processed_data/results_v2/error_taxonomy_v2.json`
- `llm-stats-vault/40-literature/papers/10-new-llm-judge-empirical-2025.md` (2 refs)
    - L22: `Validates our judge-validation methodology (Llama 3.3 70B Instruct via Together AI). Their α-over-ρ recommendation maps `
    - L36: `- data/processed_data/results_v2/keyword_vs_judge_agreement.json`
- `llm-stats-vault/40-literature/papers/11-new-fermieval-2025.md` (2 refs)
    - L22: `Contrast finding. FermiEval reports overconfidence on estimation; we observe the opposite — zero high-confidence records`
    - L35: `- data/processed_data/results_v2/calibration.json`
- `llm-stats-vault/40-literature/papers/15-new-statistical-fragility-2025.md` (2 refs)
    - L23: `Direct motivation for the bootstrap-CI separability analysis (P-2 audit finding). Their result that ChatGPT vs DeepSeek `
    - L36: `- data/processed_data/results_v2/bootstrap_ci.json`
- `llm-stats-vault/atlas/architecture.md` (2 refs)
    - L73: `| `data/processed_data/results_v1/runs.jsonl` | run_all_tasks.py | run_benchmark.py | append-only |`
    - L74: `| `data/processed_data/results_v1/results.json` | run_benchmark.py | website, scripts | currently empty |`
- `llm-stats-vault/atlas/data-flow.md` (2 refs)
    - L55: `| Run log | `data/processed_data/results_v1/runs.jsonl` | ⚠️ ~620+ (Gemini incomplete) |`
    - L56: `| Results | `data/processed_data/results_v1/results.json` | ❌ EMPTY |`
- `llm-stats-vault/atlas/scoring-pipeline.md` (1 refs)
    - L39: `- Output: `data/processed_data/results_v1/results.json``
- `llm-stats-vault/knowledge/business/proposal-gap-error-taxonomy-analysis-missing.md` (2 refs)
    - L36: `Output: `data/processed_data/results_v1/error_taxonomy.json``
    - L54: `- `data/processed_data/results_v1/runs.jsonl` — source data (1230 records, 375 synthetic flagged by suffix)`
- `llm-stats-vault/knowledge/decisions/runs-jsonl-is-append-only.md` (1 refs)
    - L9: ``data/processed_data/results_v1/runs.jsonl` is **never truncated, overwritten, or edited**.`
- `llm-stats-vault/knowledge/integrations/fastapi-backend-serves-runs-data.md` (1 refs)
    - L15: `- Reads `data/processed_data/results_v1/runs.jsonl` directly`
- `llm-stats-vault/knowledge/patterns/perturbation-types-test-three-robustness-axes.md` (1 refs)
    - L69: `Output: `data/processed_data/results_v1/perturbation_analysis.json` + summary table`
- `llm-stats-vault/sessions/2026-05-05-day5-tier2a5.md` (2 refs)
    - L6: ``data/processed_data/results_v2/calibration.json` from per-bucket ECE/accuracy ONLY.`
    - L55: `Two scripts can overwrite `data/processed_data/results_v2/calibration.json`:`
- `llm-stats-vault/sessions/2026-05-06-poster-rebuild.md` (2 refs)
    - L13: ``CLAUDE.md`, `data/processed_data/results_v2/*`, `../90-archive/audit/recompute_log.md`.`
    - L14: `- Verified live numerics from `data/processed_data/results_v2/*` and`
- `llm-stats-vault/sessions/2026-05-07-poster-defense-prep.md` (17 refs)
    - L7: `- data/processed_data/results_v2/bootstrap_ci.json`
    - L8: `- data/processed_data/results_v2/robustness_v2.json`
    - L9: `- data/processed_data/results_v2/calibration.json`
    - ... +14 more

### WEBSITE_BUNDLE

- `capstone-website/backend/static_data/llm-stats-vault/40-literature/papers/02-original-can-llm-reasoning-2026.md` (2 refs)
    - L22: `Motivates RQ5 (confidence calibration). Findings parallel our keyword-confidence extraction limitations and the empty hi`
    - L36: `- data/processed_data/results_v2/calibration.json`
- `capstone-website/backend/static_data/llm-stats-vault/40-literature/papers/06-new-longjohn-bayesian-eval-2025.md` (2 refs)
    - L22: `Direct motivation for our bootstrap CI workstream (Window 4). Maps to scripts/bootstrap_ci.py and data/processed_data/results_v2`
    - L35: `- data/processed_data/results_v2/bootstrap_ci.json`
- `capstone-website/backend/static_data/llm-stats-vault/40-literature/papers/08-new-brittlebench-2026.md` (2 refs)
    - L22: `Our perturbation methodology (rephrase / numerical / semantic — 398 perturbations × 5 models) is a domain-specific insta`
    - L38: `- data/processed_data/results_v2/robustness_v2.json`
- `capstone-website/backend/static_data/llm-stats-vault/40-literature/papers/09-new-ice-cream-causal-2025.md` (2 refs)
    - L22: `Independent confirmation of our finding that ASSUMPTION_VIOLATION is the dominant failure mode (matches our 46.9%). Thei`
    - L35: `- data/processed_data/results_v2/error_taxonomy_v2.json`
- `capstone-website/backend/static_data/llm-stats-vault/40-literature/papers/10-new-llm-judge-empirical-2025.md` (2 refs)
    - L22: `Validates our judge-validation methodology (Llama 3.3 70B Instruct via Together AI). Their α-over-ρ recommendation maps `
    - L36: `- data/processed_data/results_v2/keyword_vs_judge_agreement.json`
- `capstone-website/backend/static_data/llm-stats-vault/40-literature/papers/11-new-fermieval-2025.md` (2 refs)
    - L22: `Contrast finding. FermiEval reports overconfidence on estimation; we observe the opposite — zero high-confidence records`
    - L35: `- data/processed_data/results_v2/calibration.json`
- `capstone-website/backend/static_data/llm-stats-vault/40-literature/papers/15-new-statistical-fragility-2025.md` (2 refs)
    - L23: `Direct motivation for the bootstrap-CI separability analysis (P-2 audit finding). Their result that ChatGPT vs DeepSeek `
    - L36: `- data/processed_data/results_v2/bootstrap_ci.json`

### WEBSITE_CODE

- `capstone-website/backend/main.py` (1 refs)
    - L35: `RUNS_FILE  = BASE_DIR / "experiments" / "results_v1" / "runs.jsonl"`
- `capstone-website/backend/v2_routes.py` (2 refs)
    - L2: `v2 API routes — serves Day 1-3 analysis results from data/processed_data/results_v2/`
    - L23: `RESULTS_V2 = BASE_DIR / "experiments" / "results_v2"`
- `capstone-website/frontend/src/components/MethodologyPanels.jsx` (1 refs)
    - L902: `// Canonical from data/processed_data/results_v2/tolerance_sensitivity.json`
- `capstone-website/frontend/src/data/visualizations.js` (22 refs)
    - L3: `// Source files referenced relative to repo root (data/processed_data/results_v2/*).`
    - L25: `source: 'data/processed_data/results_v2/bootstrap_ci.json + robustness_v2.json + calibration.json',`
    - L34: `source: 'data/processed_data/results_v2/bootstrap_ci.json',`
    - ... +19 more

