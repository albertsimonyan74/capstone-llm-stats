# Audit Notes

Frozen-at-submission design-decision logs referenced from §III.F of
the paper "Reasoning or Pattern Matching? Multi-Metric and External
Judge Evaluation of LLMs on Bayesian Statistical Reasoning". Not
maintained beyond submission.

| File | Documents |
|---|---|
| `aggregation_locus.md` | NMACR aggregation source-of-truth: which file computes which dimension, the dual-write contract between live runner and post-hoc evaluator, and the literature trail behind each weight. |
| `methodology_continuity.md` | Evolution log of the evaluation pipeline from single-prompt to multi-dimensional: Approach A weighting, dual-scoring path, v1 → v2 perturbation migration, and the locked decisions at each cut. |
| `limitations_disclosures.md` | Explicit limitations and bias disclosures complementing §VI Threats to Validity: judge self-consistency, train-time contamination risk, Phase 2 ground-truth tolerance, and known scope omissions. |
