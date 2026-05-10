# StatEval: Benchmarking LLMs on Statistical Reasoning

## Metadata
- Authors: Yuchen Lu, Run Yang, Yichen Zhang, Shuguang Yu, Runpeng Dai, Ziwei Wang, Jiayi Xiang, Wenxin E, Siran Gao, Xinyao Ruan, Yirui Huang, Chenjing Xi, Haibo Hu, Yueming Fu, Qinglan Yu, Xiaobing Wei, Jiani Gu, Rui Sun, Jiaxuan Jia, Fan Zhou
- Year: 2025
- Venue: arXiv preprint
- arXiv ID: 2510.09517
- URL: https://arxiv.org/abs/2510.09517
- Date added to vault: 2026-05-01
- Source category: ORIGINAL_REFERENCE

## One-line summary
Benchmark evaluating LLM statistical reasoning across descriptive statistics and hypothesis testing using multiple-choice format.

## Key findings
- LLMs show large gaps between descriptive and inferential statistics performance.
- Multiple-choice format underestimates failure modes hidden in free-response.
- Frontier models cluster on accuracy but diverge on reasoning quality.
- Coverage limited to frequentist methods — Bayesian inference not represented.
- Establishes benchmark vocabulary for statistical-reasoning evaluation.

## How it grounds this project
Closest prior work. This benchmark extends StatEval to Bayesian inference (171 tasks across 38 types) and switches scoring from multiple-choice to free-response with a 5-dimensional rubric (N·M·A·C·R). StatEval's gap on inferential reasoning motivates RQ1 (methodology) and the existence of this benchmark. Cite throughout — Abstract, RQ1 panel, literature comparison table.

## Citation in poster
(Lu et al., 2025)

## Citation in paper
Lu et al. (2025) introduce StatEval, the closest prior benchmark for LLM statistical reasoning, covering descriptive and frequentist hypothesis testing.

## Bibtex key
lu2025stateval

## Project artifacts that cite this
- Abstract / poster header
- RQ1 (methodology panel)
- ../../90-archive/audit/literature_comparison.md (when written)
- evaluation/llm_judge_rubric.py (rubric design rationale)

## Tags
#closest-prior-work #statistical-reasoning #benchmark #methodology
