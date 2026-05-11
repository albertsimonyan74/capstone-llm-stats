# Phase 5 — canonical data pull

Generated 2026-05-10. All values pulled from canonical sources only. No `audit/` numbers.

---

## Per-model accuracy (171 base tasks, NMACR-weighted normalized score)

Source: `data/processed_data/results_v1/results.json` → `model_aggregates[*].normalized_score`.

| Rank | Model | Accuracy |
|---:|---|---:|
| 1 | claude | 0.6833 |
| 2 | mistral | 0.6441 |
| 3 | gemini | 0.6420 |
| 4 | deepseek | 0.6252 |
| 5 | **chatgpt** | **0.6212** |

---

## Per-model calibration (binary-pass ECE, lower = better)

Source: `data/processed_data/results_v2/calibration.json` → `<model>.ece`.

| Rank | Model | ECE |
|---:|---|---:|
| 1 | claude | 0.0334 |
| 2 | chatgpt | 0.0339 |
| 3 | gemini | 0.0765 |
| 4 | mistral | 0.0811 |
| 5 | deepseek | 0.1977 |

> Claude vs ChatGPT gap is 0.0005 — within bootstrap CI per `bootstrap_ci.json`. Phase 5 framing: lead the headline with the **ChatGPT inversion** + **Claude 1/1/4 pattern**, not the binary-pass ECE micro-margin.

---

## Per-model robustness (1 − Δ between base and perturbation pass rate)

Source: `data/processed_data/results_v2/robustness_v2.json` → `ranking`. n = 398 perturbations per model (v2 set).

| Rank | Model | Robustness | Δ (base − pert) |
|---:|---|---:|---:|
| 1 | **chatgpt** | **0.9996** | 0.0003 |
| 2 | mistral | 0.9981 | 0.0013 |
| 3 | gemini | 0.9824 | 0.0129 |
| 4 | **claude** | 0.9565 | 0.0305 |
| 5 | deepseek | 0.9422 | 0.0388 |

Headline divergences:
- **ChatGPT**: rank 5 accuracy → rank 1 robustness. Per-base means: `base_mean=0.6661`, `pert_mean=0.6658` (essentially identical).
- **Claude**: rank 1 accuracy + rank 1 ECE → rank 4 robustness. `base_mean=0.7011`, `pert_mean=0.6706` (drops 3 percentage points under perturbation).

---

## Keyword-rubric vs external-judge agreement (Spearman ρ)

Source: `data/processed_data/results_v2/keyword_vs_judge_agreement.json` → `overall_per_dimension`. n = 750 paired runs.

| Dimension | Spearman ρ | Pearson r | Cohen κ (pass/fail) | Keyword pass rate | Judge pass rate |
|---|---:|---:|---:|---:|---:|
| `method_structure` | 0.004 | -0.016 | -0.022 | 0.968 | 0.984 |
| `assumption_compliance` | **0.602** | 0.591 | 0.442 | 0.711 | **0.557** |
| `reasoning_quality` | 0.180 | n/a | n/a | 0.835 | 1.000 |

Headline: **assumption-compliance** is the only dimension where keyword rubric and external judge agree non-trivially (ρ = 0.602). The other two dimensions diverge.

**Assumption-compliance gap (judge view)**: judge pass rate = 0.557 → **44.3% of responses fail to explicitly state required assumptions**.

---

## Krippendorff α (3 dimensions, n=750)

Source: `data/processed_data/results_v2/krippendorff_agreement.json` → `overall`.

| Dimension | α | 95% CI |
|---|---:|---|
| `method_structure` | -0.009 | [-0.072, 0.062] |
| `assumption_compliance` | 0.573 | [0.516, 0.622] |
| `reasoning_quality` | -0.125 | [-0.197, -0.059] |

All three labeled `"questionable"` per `interpretation` field. Use carefully in §VII threats-to-validity, not abstract.

---

## Failure taxonomy (n = 143 judge-classified failures)

Source: `data/processed_data/results_v2/error_taxonomy_v2.json` → `l1_totals`. Judge: `meta-llama/Llama-3.3-70B-Instruct-Turbo`.

| L1 category | Count | Share |
|---|---:|---:|
| `ASSUMPTION_VIOLATION` | 67 | **46.9%** |
| `MATHEMATICAL_ERROR` | 48 | 33.6% |
| `FORMATTING_FAILURE` | 18 | 12.6% |
| `CONCEPTUAL_ERROR` | 10 | 7.0% |

---

## Models — exact configuration strings

Source: `llm_runner/model_clients.py` (httpx, no vendor SDKs). All 5 share `_MAX_TOKENS=1024`, `_TIMEOUT=60s`.

| Family | Model string | Endpoint | Env var |
|---|---|---|---|
| `claude` | `claude-sonnet-4-5` | `api.anthropic.com/v1/messages` | `ANTHROPIC_API_KEY` |
| `chatgpt` | `gpt-4.1` | `api.openai.com/v1/chat/completions` | `OPENAI_API_KEY` |
| `gemini` | `gemini-2.5-flash` | Google Generative Language API | `GEMINI_API_KEY` |
| `deepseek` | `deepseek-chat` | `api.deepseek.com/v1/chat/completions` | `DEEPSEEK_API_KEY` |
| `mistral` | `mistral-large-latest` | `api.mistral.ai/v1/chat/completions` | `MISTRAL_API_KEY` |

---

## Judge protocol

Source: `evaluation/llm_judge_rubric.py`.

- **Judge model**: `meta-llama/Llama-3.3-70B-Instruct-Turbo` (out-of-family — not one of the 5 benchmarked models).
- **Provider**: Together AI, OpenAI-compatible REST endpoint `api.together.xyz/v1/chat/completions`.
- **Env var**: `TOGETHER_API_KEY` (declared in `.env.example` 2026-05-10).
- **Inference settings**: T=0.0, max_tokens=1024, retry on 429/5xx with 30s backoff.
- **Rubric**: 4 dimensions (`method_structure`, `assumption_compliance`, `reasoning_quality`, `reasoning_completeness`), 0.0–1.0 with one-sentence justification per dimension.
- **Cost**: ≈ $8 for ~3,800 calls at $0.88/M tokens (full project). Migrated from Groq's free tier (100K tokens/day cap).

---

## Task suite + perturbation taxonomy

Source: `data/raw_data/benchmark_v1/`, `data/raw_data/synthetic/perturbations_all.json`.

- **171 base tasks** = 136 Phase 1 (31 task types) + 35 Phase 2 (7 advanced types: GIBBS / MH / HMC / RJMCMC / HIERARCHICAL / VB / ABC) = **38 task types**.
- **473 perturbations** = 75 v1 hand-authored + 398 v2 LLM-generated (Together AI Llama 3.3 70B). Disjoint partition: v1 covers 25 baselines × 3 axes; v2 covers the remaining 146 baselines.
- **Perturbation axis distribution**: rephrase 171, semantic 171, numerical 131. All 171 baselines covered (40 with 2 perturbations, 131 with 3).
- **Mean perturbations per base**: 2.77.

---

## NMACR weights (literature-derived)

Source: `evaluation/metrics.py` docstring + `llm_runner/response_parser.py:29`.

| Symbol | Component | Weight | Citations |
|---|---|---:|---|
| A | Assumption Compliance | 0.30 | Du 2025, Boye & Moell 2025, Yamauchi 2025 |
| R | Reasoning Quality | 0.25 | Yamauchi 2025, Boye & Moell 2025, ReasonBench 2025 |
| M | Method Structure | 0.20 | Wei 2022, Chen 2022, Bishop 2006 |
| C | Confidence Calibration | 0.15 | Nagarkar 2026, FermiEval 2025, Multi-Answer 2026 |
| N | Numerical Accuracy | 0.10 | Liu 2025, Boye & Moell 2025 |

Sum = 1.00. Sole canonical scheme since Approach A, 2026-05-03.

---

## Bibkey selection from vault

Source: `llm-stats-vault/40-literature/bibtex.bib` + `paper/bib/refs.bib`.

For abstract / intro use:
- `lu2025stateval`, `nagarkar2026canllm`, `liu2025matheval` — statistical-reasoning benchmarks
- `longjohn2025bayesian` — Bayesian-specific eval
- `wei2022cot`, `chen2022pot` — reasoning prompting baselines
- `reasonbench2025`, `brittlebench2026`, `fragility2025` — robustness / instability
- `park2025judge`, `judgment2025noise` — LLM-as-judge methodology
- `du2025icecream` — assumption-compliance parallel finding
- Stubs (Phase 4 added, fill in later): `guo2017calibration`, `zheng2023judge`, `llama3`

---

## Summary of confirmed values for abstract / intro

| Variable | Value | Source |
|---|---|---|
| Models | 5 (claude, chatgpt, gemini, deepseek, mistral) | `llm_runner/model_clients.py` |
| Base tasks | 171 (= 136 Phase 1 + 35 Phase 2) | `data/raw_data/benchmark_v1/tasks_all.json` |
| Task types | 38 | derived |
| Perturbations | 473 | `data/raw_data/synthetic/perturbations_all.json` |
| Perturbation axes | 3 (rephrase, semantic, numerical) | derived |
| Judge model | Llama 3.3 70B Turbo (Together AI) | `evaluation/llm_judge_rubric.py` |
| ChatGPT accuracy rank → robustness rank | **5 → 1** | results_v1 + results_v2 |
| ChatGPT accuracy | 0.6212 | results_v1 |
| ChatGPT robustness | 0.9996 | results_v2 |
| Claude (acc, ECE, robustness) ranks | (1, 1, 4) | results_v1 + results_v2 |
| Assumption-compliance Spearman ρ (kw vs judge) | **0.602** | keyword_vs_judge_agreement.json |
| % responses missing required assumptions (judge view) | **44.3%** | judge_pass_rate=0.557 |
| ASSUMPTION_VIOLATION share of failures | **46.9%** (67/143) | error_taxonomy_v2.json |

No `[TODO: confirm]` blockers. All numbers traced to canonical files.
