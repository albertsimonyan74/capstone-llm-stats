# Investigation 2 — judge audit

**Verdict: (a) Together AI Llama 3.3 70B Turbo. Code matches CLAUDE.md.** No contradiction.

The earlier inventory flag was a false positive: my Phase 1 grep regex `api[-_]?key` matched the function-argument name `api_key: str` at [code/analysis/llm_judge_rubric.py:151](code/analysis/llm_judge_rubric.py#L151) — not `OPENAI_API_KEY`. The judge file does NOT reference OpenAI.

## Evidence

### Client construction in `llm_judge_rubric.py`
- [code/analysis/llm_judge_rubric.py:37](code/analysis/llm_judge_rubric.py#L37): `TOGETHER_URL = "https://api.together.xyz/v1/chat/completions"`
- [code/analysis/llm_judge_rubric.py:38](code/analysis/llm_judge_rubric.py#L38): `JUDGE_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"`
- [code/analysis/llm_judge_rubric.py:172](code/analysis/llm_judge_rubric.py#L172): `await client.post(TOGETHER_URL, json=payload, headers=headers, timeout=TIMEOUT_S)` — direct httpx, no SDK
- [code/analysis/llm_judge_rubric.py:318](code/analysis/llm_judge_rubric.py#L318): `api_key = os.environ.get("TOGETHER_API_KEY")`
- Module docstring lines 1–16: explicit "Together AI (`meta-llama/Llama-3.3-70B-Instruct-Turbo`)" + "External to all 5 benchmarked models" + "Migrated from Groq's free tier" history.

### Caller chain
- [code/scripts/score_perturbations.py:1-15](code/scripts/score_perturbations.py): the perturbation pipeline explicitly invokes `python -m evaluation.llm_judge_rubric` with the Together-AI judge for the 473×5 perturbation runs.
- [code/scripts/error_taxonomy.py:44, 379-381](code/scripts/error_taxonomy.py): also Together AI (separate task-error-classification judge), uses `TOGETHER_API_KEY`.

### Result JSONL headers
All v2 judge JSONLs carry `"judge_model": "meta-llama/Llama-3.3-70B-Instruct-Turbo"`:
- `data/processed_data/results_v2/llm_judge_scores_full.jsonl`
- `data/processed_data/results_v2/llm_judge_scores_sample.jsonl`
- `data/processed_data/results_v2/perturbation_judge_scores.jsonl`
- `data/processed_data/results_v2/error_taxonomy_v2_judge.jsonl`

### `.env.example`
[/.env.example](.env.example) declares 5 model keys: `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `MISTRAL_API_KEY`.

**Gap**: `TOGETHER_API_KEY` is NOT declared in `.env.example` despite being required by the judge and the perturbation/taxonomy/error-classification pipelines. Working `.env` presumably has it.

### Where `OPENAI_API_KEY` is actually used (legitimately, for the GPT-4.1 *benchmark target*, not judge)
- [code/models/model_clients.py:264, 269, 288](code/models/model_clients.py) — ChatGPT client (one of the 5 benchmarked models)
- [code/scripts/self_consistency_full.py:141, 151](code/scripts/self_consistency_full.py) — RQ5 self-consistency runs against gpt-4.1
- [capstone-website/backend/user_study.py:435, 438, 450](capstone-website/backend/user_study.py) — frontend user-study live query against gpt-4.1
- [code/capstone_mcp/server.py:127](code/capstone_mcp/server.py), [code/capstone_mcp/tools/scoring.py:35](code/capstone_mcp/tools/scoring.py) — docstrings only

All `OPENAI_API_KEY` callers point at ChatGPT-the-target, not judge. Consistent with CLAUDE.md.

## Conclusion

**(a) — Together AI via direct httpx, env var correct (`TOGETHER_API_KEY`), code matches CLAUDE.md.** Judge is `meta-llama/Llama-3.3-70B-Instruct-Turbo`. No code path is dead. No contradiction with documentation.

## Action items (out of scope for Phase 2 reorg, surfacing for paper write-up)
1. Add `TOGETHER_API_KEY=` line to `.env.example` (1-line edit). Currently undeclared despite being a hard requirement for judge + perturbation generation + error taxonomy.
2. Module docstring still references "Groq Llama 3.3 70B" in the argparse description at [code/analysis/llm_judge_rubric.py:416](code/analysis/llm_judge_rubric.py#L416) — minor doc-string lag from the Groq→Together migration noted at lines 11–12. Cosmetic.
