# Reference Papers Bibliography

Five papers directly informing the DS 299 Capstone benchmark design.

---

## 1. StatEval (Lu et al., 2025)

**Citation:** Lu, Y., Yang, R., Zhang, Y., et al. (2025). StatEval: A Comprehensive Benchmark for Large Language Models in Statistics. *arXiv:2510.09517*

**URL:** https://arxiv.org/abs/2510.09517

**Abstract summary:** Largest statistics benchmark to date (13,817 problems across undergraduate–graduate levels), spanning descriptive stats, probability, inference, and regression. Includes human-in-the-loop validation of task quality and multi-difficulty-tier structure.

**Relevance to this project:** This project addresses the same gap but focuses specifically on Bayesian/inferential reasoning with deterministic ground-truth baselines — complementary scope. We adopt StatEval's multi-difficulty-tier structure and extend to computational Bayesian methods (Phase 2) not covered by StatEval.

**Our response:** `code/analysis/task_validator.py` implements an automated proxy for StatEval's human-in-the-loop task quality validation. Multi-tier structure (Tiers 1–4) mirrors StatEval's difficulty stratification.

---

## 2. Can LLM Reasoning Be Trusted? (Nagarkar et al., 2026)

**Citation:** Nagarkar, C., et al. (2026). Can LLM Reasoning Be Trusted? A Comparative Study: Using Human Benchmarking on Statistical Tasks. *arXiv:2601.14479*

**URL:** https://arxiv.org/abs/2601.14479

**Abstract summary:** Demonstrates that LLM-as-Judge evaluation outperforms BLEU and BERTScore for statistical reasoning tasks. Shows that automated LLM evaluation correlates well with human expert judgement on mathematical content. Benchmarks multiple LLMs on statistical problem types similar to this project.

**Relevance to this project:** Directly motivates the `code/analysis/llm_judge.py` implementation. When primary `ANSWER:` extraction fails (yielding `parsed_values=[]`) or structure scoring is low (<0.3), Claude is invoked as evaluator — consistent with Nagarkar et al.'s finding that LLMs outperform surface-string metrics on reasoning quality.

**Our response:** Judge-assisted runs flagged via `judge_assisted=True` in `runs.jsonl`. Two judge functions: `judge_extract_answer()` (N-score recovery) and `judge_score_structure()` (M/A-score recovery).

---

## 3. MathEval (Liu et al., 2025)

**Citation:** Liu, T., Chen, Z., Fang, Z., et al. (2025). MathEval: A Comprehensive Benchmark for Evaluating Large Language Models on Mathematical Reasoning Capabilities. *Frontiers of Digital Education, 2*, 16. https://doi.org/10.1007/s44366-025-0053-z

**URL:** https://journal.hep.com.cn/fde/EN/10.1007/s44366-025-0053-z

**Abstract summary:** Consolidates 22 mathematical datasets into a unified benchmark covering arithmetic through advanced mathematics. Uses GPT-4 for automated answer extraction and scoring. Finds systematic accuracy gaps across difficulty levels and task types.

**Relevance to this project:** Motivates our multi-task-type approach (38 task types vs 22 datasets) and our LLM-based extraction fallback. Our tolerance-based numeric matching (relative tolerance per target) addresses limitations of exact-match scoring used in MathEval.

**Our response:** We implement domain-specific tolerance thresholds (`full_credit_tol`, `zero_credit_scale` per target) rather than exact match. LLM-as-Judge fallback parallels GPT-4 extraction used by MathEval but is triggered only on failed primary extraction.

---

## 4. Program of Thoughts (Chen et al., 2022)

**Citation:** Chen, W., Ma, X., Wang, X., & Cohen, W. W. (2022). Program of Thoughts Prompting: Disentangling Computation from Reasoning for Numerical Reasoning Tasks. *arXiv:2211.12588*

**URL:** https://arxiv.org/abs/2211.12588

**Abstract summary:** PoT prompting instructs LLMs to generate Python code rather than prose reasoning, delegating computation to an external interpreter. Achieves ~12% accuracy gain over Chain-of-Thought (CoT) on numerical reasoning benchmarks by separating reasoning (LLM) from computation (interpreter).

**Relevance to this project:** Directly motivates `code/models/prompt_builder_pot.py`. PoT provides a numerical accuracy upper bound — if an LLM can write correct Python for a statistical task, it demonstrates reasoning without arithmetic errors. Comparison between zero-shot CoT and PoT isolates arithmetic vs. conceptual failures.

**Our response:** `build_pot_prompt()` appends Python code instruction to the standard prompt. `execute_pot_response()` sandboxes execution (10s timeout, forbidden imports list) and extracts `ANSWER:` from stdout. PoT is an optional prompting mode; results comparable to zero-shot baseline.

---

## 5. Chain-of-Thought Prompting (Wei et al., 2022)

**Citation:** Wei, J., Wang, X., Schuurmans, D., et al. (2022). Chain-of-Thought Prompting Elicits Reasoning in Large Language Models. *arXiv:2201.11903*

**URL:** https://arxiv.org/abs/2201.11903

**Abstract summary:** Foundational paper establishing that prompting LLMs to produce intermediate reasoning steps (chain-of-thought) substantially improves performance on arithmetic, symbolic, and commonsense reasoning benchmarks. Few-shot exemplars with reasoning traces elicit emergent CoT behavior in large models.

**Relevance to this project:** All benchmark prompts require step-by-step reasoning before `ANSWER:` output (zero-shot CoT). The R-component (Reasoning Quality, weight=0.20) scores the quality of these reasoning traces across four criteria. `prompt_builder_fewshot.py` implements the exemplar-based few-shot variant for comparison.

**Our response:** Our system prompt instructs: "Show your step-by-step reasoning before giving the final answer." The R-score rubric (4 × 0.25: shows work, identifies model, states formula, interprets result) operationalises CoT quality measurement. Few-shot exemplars defined for BINOM_FLAT, MARKOV, FISHER_INFO, BETA_BINOM, GIBBS.
