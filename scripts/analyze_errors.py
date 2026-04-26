"""
Error Taxonomy Analysis Pipeline

Addresses proposal abstract deliverable: "systematic error taxonomy for LLM
statistical reasoning". Auto-tags each failed run with error categories,
generates summary statistics.

Run from project root:
    python scripts/analyze_errors.py
    python scripts/analyze_errors.py --no-llm          # rule-based only
    python scripts/analyze_errors.py --max-llm 50      # limit LLM calls
"""
from __future__ import annotations
import json
import re
import argparse
from collections import defaultdict
from pathlib import Path

RUNS_PATH  = "experiments/results_v1/runs.jsonl"
TASKS_PATH = "data/benchmark_v1/tasks_all.json"
OUTPUT_PATH = "data/error_taxonomy_results.json"

SYNTH_SUFFIX = ("_rephrase", "_numerical", "_semantic")
MAX_TOKENS = 1024   # model hard cap; output_tokens >= this → truncation

# ── Error taxonomy ────────────────────────────────────────────────────────────
ERROR_TAXONOMY = {
    "E1_NUMERICAL_COMPUTATION": {
        "description": "Correct method, wrong arithmetic or calculation",
        "indicators": ["arithmetic error", "rounding", "calculation mistake"],
    },
    "E2_METHOD_SELECTION": {
        "description": "Wrong statistical method chosen for the problem",
        "indicators": ["wrong distribution", "wrong prior", "wrong estimator"],
    },
    "E3_ASSUMPTION_VIOLATION": {
        "description": "Correct method but required assumptions ignored",
        "indicators": ["ignored assumption", "missing conjugacy check", "violated condition"],
    },
    "E4_FORMAT_FAILURE": {
        "description": "Answer present in prose but ANSWER: line not parseable",
        "indicators": ["no answer line", "wrong format", "missing values"],
    },
    "E5_OVERCONFIDENCE": {
        "description": "High expressed confidence despite low numerical accuracy",
        "indicators": ["certainly", "definitely", "clearly", "obviously"],
    },
    "E6_CONCEPTUAL_CONFUSION": {
        "description": "Fundamental misunderstanding of statistical concept",
        "indicators": ["misidentified model", "wrong interpretation", "confused formula"],
    },
    "E7_TRUNCATION": {
        "description": "Response cut off at token limit before ANSWER: line",
        "indicators": ["output_tokens at max cap", "response mid-sentence"],
    },
    "E8_HALLUCINATION": {
        "description": "Invented values, formulas, or references not in problem",
        "indicators": ["invented parameter", "fabricated formula", "wrong data used"],
    },
    "E9_UNCLASSIFIED": {
        "description": "Failed run not matching any rule heuristic",
        "indicators": [],
    },
}


def rule_based_tag(run: dict) -> list[str]:
    """Rule-based tagging using score fields + token count."""
    tags: list[str] = []
    def _f(val, default=1.0):
        return float(val) if val is not None else default

    ns   = _f(run.get("numeric_score",    run.get("numerical_score")), 1.0)
    ms   = _f(run.get("structure_score"),  1.0)
    as_  = _f(run.get("assumption_score"), 1.0)
    cs   = _f(run.get("confidence_score"), 1.0)
    rs   = _f(run.get("reasoning_score"),  1.0)
    pv   = run.get("parsed_values") or []
    raw  = run.get("raw_response",  "") or ""
    otok = int(run.get("output_tokens", 0) or 0)

    no_answer = (not pv or len(pv) == 0)

    # E7: truncated at hard token cap
    if no_answer and otok >= MAX_TOKENS:
        tags.append("E7_TRUNCATION")

    # E4: short response, no answer extracted
    if no_answer and otok < MAX_TOKENS and len(raw) > 50:
        tags.append("E4_FORMAT_FAILURE")

    # E2: method selection failure
    if ms < 0.3:
        tags.append("E2_METHOD_SELECTION")

    # E3: assumption score zero (dominant pattern — 119 cases)
    if as_ == 0.0:
        tags.append("E3_ASSUMPTION_VIOLATION")

    # E1: numeric wrong but method correct (rule-based says got the method right)
    if ns < 0.3 and ms > 0.6 and not no_answer:
        tags.append("E1_NUMERICAL_COMPUTATION")

    # E5: overconfident on wrong
    if cs < 0.3 and ns < 0.5:
        tags.append("E5_OVERCONFIDENCE")

    # E6: low reasoning score
    if rs < 0.3:
        tags.append("E6_CONCEPTUAL_CONFUSION")

    # E8: default for remaining unclassified non-truncated failures
    if not tags:
        tags.append("E8_HALLUCINATION")

    return tags


def llm_tag(run: dict, task: dict, client, model: str) -> dict:
    """LLM-as-Judge classification for ambiguous cases."""
    taxonomy_lines = "\n".join(
        f"- {k}: {v['description']}" for k, v in ERROR_TAXONOMY.items()
        if k != "E9_UNCLASSIFIED"
    )
    raw_snippet = (run.get("raw_response") or "")[:500]
    ns = run.get("numeric_score", "?")
    ms = run.get("structure_score", "?")
    as_ = run.get("assumption_score", "?")

    prompt = f"""You are classifying a failed LLM response to a statistical reasoning task.

Task type: {task.get('task_type') or run.get('task_type', 'unknown')}
Task difficulty: {task.get('difficulty', 'unknown')}
Expected answer keys: {[t['key'] for t in task.get('numeric_targets', [])]}

Model response (first 500 chars):
{raw_snippet}

Scores: numeric={ns}, method={ms}, assumption={as_}

Error taxonomy:
{taxonomy_lines}

Classify this failure. Return ONLY valid JSON (no markdown):
{{
  "primary_error": "E1_NUMERICAL_COMPUTATION",
  "secondary_errors": ["E4_FORMAT_FAILURE"],
  "evidence": "specific text from response showing the error",
  "confidence": 0.85,
  "correctable_by_reprompting": true
}}"""

    try:
        response = client.messages.create(
            model=model,
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
        text = re.sub(r"```json|```", "", response.content[0].text).strip()
        return json.loads(text)
    except Exception as e:
        return {
            "primary_error": "E9_UNCLASSIFIED",
            "secondary_errors": [],
            "evidence": f"parse_error: {e}",
            "confidence": 0.0,
            "correctable_by_reprompting": False,
        }


def analyze_all_errors(
    runs_path: str = RUNS_PATH,
    tasks_path: str = TASKS_PATH,
    output_path: str = OUTPUT_PATH,
    use_llm: bool = True,
    max_llm_calls: int = 100,
) -> dict:
    """Full error taxonomy pipeline."""
    from dotenv import load_dotenv
    load_dotenv()

    client = None
    _MODEL = "claude-sonnet-4-6"
    if use_llm:
        try:
            import anthropic
            client = anthropic.Anthropic()
        except Exception as e:
            print(f"  anthropic unavailable ({e}) — rule-based only")
            use_llm = False

    # Load tasks index (task_type may be null in tasks_all.json for Phase 1)
    with open(tasks_path) as f:
        tasks = json.load(f)
    tasks_by_id: dict[str, dict] = {t["task_id"]: t for t in tasks}

    # Load benchmark runs (exclude synthetic)
    all_runs: list[dict] = []
    failed_runs: list[dict] = []
    with open(runs_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                run = json.loads(line)
            except json.JSONDecodeError:
                continue
            tid = run.get("task_id", "")
            if any(tid.endswith(s) for s in SYNTH_SUFFIX):
                continue
            if not run.get("task_type"):
                continue  # skip malformed/old placeholder records
            all_runs.append(run)
            score = run.get("final_score")
            if score is not None and float(score) < 0.5 and not run.get("error"):
                failed_runs.append(run)

    n_all = len(all_runs)
    n_fail = len(failed_runs)
    print(f"Benchmark runs: {n_all}  |  Failed (score<0.5): {n_fail}")

    tagged: list[dict] = []
    llm_calls = 0

    for run in failed_runs:
        tid      = run.get("task_id", "")
        task     = tasks_by_id.get(tid, {})
        rule_tags = rule_based_tag(run)

        result: dict = {
            "run_id":           run.get("run_id", ""),
            "task_id":          tid,
            "task_type":        run.get("task_type", ""),
            "model":            run.get("model_family", run.get("model", "")),
            "final_score":      run.get("final_score", 0.0),
            "numeric_score":    run.get("numeric_score", 0.0),
            "structure_score":  run.get("structure_score", 0.0),
            "assumption_score": run.get("assumption_score", 0.0),
            "output_tokens":    run.get("output_tokens", 0),
            "rule_tags":        rule_tags,
            "primary_error":    rule_tags[0] if rule_tags else "E9_UNCLASSIFIED",
            "all_errors":       rule_tags,
            "llm_classification": None,
        }

        # LLM for ambiguous: E8/E9 or pure assumption with no other tags
        needs_llm = (
            use_llm
            and client is not None
            and llm_calls < max_llm_calls
            and (
                "E8_HALLUCINATION" in rule_tags
                or "E9_UNCLASSIFIED" in rule_tags
                or (rule_tags == ["E3_ASSUMPTION_VIOLATION"] and task)
            )
        )
        if needs_llm:
            llm_result = llm_tag(run, task, client, _MODEL)
            primary = llm_result.get("primary_error", rule_tags[0])
            secondary = llm_result.get("secondary_errors") or []
            result["llm_classification"] = llm_result
            result["primary_error"] = primary
            result["all_errors"] = list(
                dict.fromkeys(rule_tags + [primary] + secondary)
            )
            llm_calls += 1
            if llm_calls % 10 == 0:
                print(f"  LLM calls: {llm_calls}/{max_llm_calls}")

    tagged.append(result)  # noqa — moved inside loop below

    # Rebuild correctly (loop above has indentation issue — redo cleanly)
    tagged = []
    llm_calls = 0
    for run in failed_runs:
        tid      = run.get("task_id", "")
        task     = tasks_by_id.get(tid, {})
        rule_tags = rule_based_tag(run)

        result = {
            "run_id":           run.get("run_id", ""),
            "task_id":          tid,
            "task_type":        run.get("task_type", ""),
            "model":            run.get("model_family", run.get("model", "")),
            "final_score":      run.get("final_score", 0.0),
            "numeric_score":    run.get("numeric_score", 0.0),
            "structure_score":  run.get("structure_score", 0.0),
            "assumption_score": run.get("assumption_score", 0.0),
            "output_tokens":    run.get("output_tokens", 0),
            "rule_tags":        rule_tags,
            "primary_error":    rule_tags[0] if rule_tags else "E9_UNCLASSIFIED",
            "all_errors":       rule_tags,
            "llm_classification": None,
        }

        needs_llm = (
            use_llm
            and client is not None
            and llm_calls < max_llm_calls
            and (
                "E8_HALLUCINATION" in rule_tags
                or "E9_UNCLASSIFIED" in rule_tags
                or (rule_tags == ["E3_ASSUMPTION_VIOLATION"] and task)
            )
        )
        if needs_llm:
            llm_result = llm_tag(run, task, client, _MODEL)
            primary   = llm_result.get("primary_error", rule_tags[0])
            secondary = llm_result.get("secondary_errors") or []
            result["llm_classification"]  = llm_result
            result["primary_error"] = primary
            result["all_errors"] = list(
                dict.fromkeys(rule_tags + [primary] + secondary)
            )
            llm_calls += 1
            if llm_calls % 10 == 0:
                print(f"  LLM calls: {llm_calls}/{max_llm_calls}")

        tagged.append(result)

    print(f"  LLM calls used: {llm_calls}")

    # ── Summary statistics ────────────────────────────────────────────────────
    error_counts:       dict[str, int]            = defaultdict(int)
    error_by_model:     dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    error_by_task_type: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    model_primary:      dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    correctable = 0

    for t in tagged:
        for err in t["all_errors"]:
            error_counts[err] += 1
            error_by_model[t["model"]][err] += 1
            error_by_task_type[t["task_type"]][err] += 1
        model_primary[t["model"]][t["primary_error"]] += 1
        llm_c = t.get("llm_classification") or {}
        if llm_c.get("correctable_by_reprompting"):
            correctable += 1

    summary = {
        "total_benchmark_runs": n_all,
        "total_failures": n_fail,
        "failure_rate": round(n_fail / max(n_all, 1), 4),
        "llm_calls_used": llm_calls,
        "correctable_by_reprompting": correctable,
        "error_distribution": dict(
            sorted(error_counts.items(), key=lambda x: -x[1])
        ),
        "error_by_model": {m: dict(v) for m, v in error_by_model.items()},
        "error_by_task_type": {
            tt: dict(v) for tt, v in error_by_task_type.items()
        },
        "model_primary_errors": {m: dict(v) for m, v in model_primary.items()},
        "taxonomy_definitions": {
            k: v["description"] for k, v in ERROR_TAXONOMY.items()
        },
        "tagged_runs": tagged,
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nError taxonomy → {output_path}")
    top5 = list(sorted(error_counts.items(), key=lambda x: -x[1]))[:5]
    print(f"Top errors: {dict(top5)}")
    print(f"By model (primary):")
    for m, errs in sorted(model_primary.items()):
        top = sorted(errs.items(), key=lambda x: -x[1])[:2]
        print(f"  {m}: {dict(top)}")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Error taxonomy analysis for failed benchmark runs"
    )
    parser.add_argument("--no-llm", action="store_true",
                        help="Skip LLM-as-Judge; rule-based tags only")
    parser.add_argument("--max-llm", type=int, default=100,
                        help="Max LLM calls for ambiguous cases (default 100)")
    parser.add_argument("--output", default=OUTPUT_PATH,
                        help="Output JSON path")
    args = parser.parse_args()

    analyze_all_errors(
        use_llm=not args.no_llm,
        max_llm_calls=args.max_llm,
        output_path=args.output,
    )
