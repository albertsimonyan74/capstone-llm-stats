# Research Questions

## Project: Benchmarking Large Language Models on Inferential and Bayesian Statistical Reasoning

---

## RQ1 — Numerical and Statistical Accuracy

For a benchmark of 171 inferential and Bayesian tasks (136 Phase 1 + 35 Phase 2), what is the numerical accuracy of each evaluated LLM under a standardized prompting protocol, measured using absolute and relative error within predefined tolerance thresholds?

**Implementation:** `numeric_score` (N weight 0.20) in `llm_runner/response_parser.py`.  
**Results (2026-04-26):** Claude 88.9% pass · Gemini 86.0% · Mistral 84.8% · DeepSeek 78.9% · ChatGPT 77.8%

---

## RQ2 — Method Selection Accuracy

What proportion of benchmark tasks involve incorrect statistical method selection by each LLM (e.g., inappropriate model choice, incorrect prior specification, misuse of frequentist vs Bayesian methods) when compared to a closed-form ground-truth baseline?

**Implementation:** `structure_score` (M weight 0.20) in `llm_runner/response_parser.py`.  
**Results:** Claude avg structure 0.95 · Gemini 0.93 · Mistral 0.90 · DeepSeek 0.88 · ChatGPT 0.87

---

## RQ3 — Assumption Compliance

To what extent do LLMs explicitly identify, verify, and respect required statistical assumptions (e.g., prior specification, conjugacy conditions, exchangeability), and how frequently do they proceed despite assumption violations?

**Implementation:** `assumption_score` (A weight 0.20) in `llm_runner/response_parser.py`.  
**Results:** Claude avg assumption 0.73 · Gemini 0.70 · DeepSeek 0.66 · Mistral 0.61 · ChatGPT 0.60

---

## RQ4 — Robustness to Prompt Variations

How stable are LLM outputs under three controlled perturbation types — rephrase (same math, different wording), numerical (changed values), and semantic (same math, new real-world context) — and how does score sensitivity vary across models and perturbation types?

**Implementation:** `data/synthetic/perturbations.json` (75 tasks = 25 base × 3 types); `scripts/analyze_perturbations.py` → `experiments/results_v1/rq4_analysis.json`.  
**Results (2026-04-26, 375 runs, all 5 models):**  
- ChatGPT most robust (0.931) · Mistral 0.925 · Claude 0.915 · DeepSeek 0.901 · Gemini 0.896  
- Rephrase easiest (0.923) · Semantic 0.909 · Numerical hardest (0.908)

---

## RQ5 — Confidence and Trust Calibration

Is there a measurable relationship between model-reported confidence and actual correctness in statistical reasoning tasks? Do models that express higher confidence achieve higher numeric scores?

**Implementation:** `extract_confidence()` + `confidence_calibration_score()` in `llm_runner/response_parser.py` (C weight 0.20). Explicit %, hedging language, and definitive phrasing extracted; overconfident-on-wrong penalized 1.5×.  
**Status:** Active in all 855 benchmark runs. Full calibration analysis pending.

---

# Scope Freeze Note

These five research questions define the full analytical scope of the project.
No additional research questions will be introduced unless formally justified
and approved through scope revision.