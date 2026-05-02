"""
Flask backend for the LLM Bayesian Benchmark website.
Reads from the project's data and results directories.
"""
from __future__ import annotations

import json
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

BASE_DIR    = Path(__file__).parent.parent
DATA_DIR    = BASE_DIR / "data" / "benchmark_v1"
RESULTS_DIR = BASE_DIR / "experiments" / "results_v1"
TASKS_FILE  = DATA_DIR / "tasks.json"
RESULTS_FILE = RESULTS_DIR / "results.json"
RUNS_FILE   = RESULTS_DIR / "runs.jsonl"


# ── Data loaders ─────────────────────────────────────────────────────────────

def _load_tasks() -> List[Dict[str, Any]]:
    with open(TASKS_FILE) as f:
        return json.load(f)


def _load_results() -> Dict[str, Any]:
    if not RESULTS_FILE.exists():
        return {"model_aggregates": [], "task_scores": []}
    with open(RESULTS_FILE) as f:
        return json.load(f)


def _load_runs() -> List[Dict[str, Any]]:
    runs: List[Dict[str, Any]] = []
    if not RUNS_FILE.exists():
        return runs
    with open(RUNS_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    runs.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return runs


def _task_prefix(task_id: str) -> str:
    parts = task_id.rsplit("_", 1)
    return parts[0] if len(parts) == 2 and parts[1].isdigit() else task_id


# ── Task type descriptions ────────────────────────────────────────────────────

TASK_TYPE_DESCRIPTIONS = {
    "BETA_BINOM":     "Beta-Binomial conjugate model · posterior, credible interval, predictive PMF",
    "GAMMA_POISSON":  "Gamma-Poisson conjugate model · posterior, credible interval, predictive PMF",
    "NORMAL_GAMMA":   "Normal-Gamma (unknown variance) · posterior parameters, credible interval",
    "DIRICHLET":      "Dirichlet-Multinomial · posterior means, predictive probabilities",
    "DISC_MEDIAN":    "Discrete posterior median via cumulative probability rule",
    "UNIFORM_MLE":    "MLE for Uniform(0,θ) · maximum order statistic derivation",
    "BINOM_FLAT":     "Binomial with flat (Beta(1,1)) prior · posterior update",
    "MINIMAX":        "Minimax estimation · max risk minimization over estimators",
    "BAYES_RISK":     "Bayes risk computation · prior-weighted expected loss",
    "BIAS_VAR":       "Bias-variance decomposition · MSE = Bias² + Var",
    "FISHER_INFO":    "Fisher information computation for standard distributions",
    "RC_BOUND":       "Rao-Cramér lower bound on estimator variance",
    "OPT_SCALED":     "Optimal scaled estimator · c* = (n+2)/(n+1)",
    "MSE_COMPARE":    "MSE comparison of three Uniform(0,θ) estimators",
    "MARKOV":         "Markov chain · stationary distribution, n-step transitions",
    "ORDER_STAT":     "Order statistics · PDF, CDF, range distribution",
    "REGRESSION":     "OLS regression · slope, intercept, residual variance, CI",
    "BOX_MULLER":     "Box-Muller transform · Normal samples from Uniform",
    "GAMBLER":        "Gambler's Ruin · ruin/win probabilities",
    "STATIONARY":     "Markov chain stationary distribution via linear system",
    "RANGE_DIST":     "Sample range as Beta distribution (Beta(n-1, 2))",
    "MLE_EFFICIENCY": "MLE efficiency ratio against Rao-Cramér bound",
    "HPD":            "Highest Posterior Density (HPD) credible interval",
    "JEFFREYS":       "Jeffreys prior (Beta(0.5,0.5)) Binomial update",
    "PPC":            "Posterior predictive check · Bayesian p-value",
    "MLE_MAP":        "MLE vs MAP vs posterior mean · shrinkage",
    "CI_CREDIBLE":    "Frequentist CI vs Bayesian credible interval comparison",
    "LOG_ML":         "Log marginal likelihood via Beta/Gamma function",
    "BAYES_FACTOR":   "Bayes factor BF₁₂ between two conjugate models",
    "BAYES_REG":      "Bayesian linear regression · Normal-Inverse-Gamma conjugate",
    "CONCEPTUAL":     "Conceptual questions · rubric-scored open-ended explanations",
}


# ── Helper: build prompt for a task ──────────────────────────────────────────

def _build_prompt_safe(task: Dict[str, Any]) -> str:
    try:
        import sys
        sys.path.insert(0, str(BASE_DIR))
        from llm_runner.prompt_builder import build_prompt
        return build_prompt(task)
    except Exception as e:
        return f"[Prompt generation error: {e}]"


# ── API routes ────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("templates", "index.html")


@app.route("/api/status")
def api_status():
    tasks = _load_tasks()
    runs  = _load_runs()

    tasks_by_type: Dict[str, int] = defaultdict(int)
    tasks_by_tier: Dict[str, int] = defaultdict(int)
    for t in tasks:
        tasks_by_type[_task_prefix(t["task_id"])] += 1
        tasks_by_tier[str(t["tier"])] += 1

    models_run = list({r.get("model_name") or r.get("model", "") for r in runs if r.get("model_name") or r.get("model")})

    return jsonify({
        "total_tasks":     len(tasks),
        "tasks_by_type":   dict(tasks_by_type),
        "tasks_by_tier":   dict(tasks_by_tier),
        "total_runs":      len(runs),
        "models_run":      models_run,
        "benchmark_ready": True,
    })


@app.route("/api/tasks")
def api_tasks():
    tasks = _load_tasks()

    type_filter   = request.args.get("type", "").upper()
    search_id     = request.args.get("search_id", "").upper().strip()
    search_topic  = request.args.get("search_topic", "").lower().strip()
    search        = request.args.get("search", "").lower().strip()   # legacy combined
    tier_param    = request.args.get("tier", "")
    category      = request.args.get("category", "").lower()
    limit         = int(request.args.get("limit", 50))

    # Parse tier filter (single value or comma-separated)
    allowed_tiers: Optional[set] = None
    if tier_param:
        allowed_tiers = {int(x) for x in tier_param.split(",") if x.strip().isdigit()}

    result = []
    for t in tasks:
        tid    = t["task_id"]
        prefix = _task_prefix(tid)
        notes  = t.get("notes", {})
        topic  = notes.get("topic", "") if isinstance(notes, dict) else str(notes)

        if type_filter and prefix != type_filter:
            continue
        if allowed_tiers and t.get("tier") not in allowed_tiers:
            continue
        if category == "conceptual" and not tid.startswith("CONCEPTUAL"):
            continue
        if category == "numeric" and tid.startswith("CONCEPTUAL"):
            continue
        if search_id and search_id not in tid:
            continue
        if search_topic and search_topic not in topic.lower() and search_topic not in tid.lower():
            continue
        # legacy `search` param: match anywhere in the JSON blob
        if search and search not in json.dumps(t).lower():
            continue

        is_conceptual = tid.startswith("CONCEPTUAL")
        result.append({
            "task_id":    tid,
            "task_type":  prefix,
            "tier":       t.get("tier"),
            "difficulty": t.get("difficulty"),
            "category":   "conceptual" if is_conceptual else "numeric",
            "n_numeric":  len(t.get("numeric_targets", [])),
            "n_rubric":   len(t.get("rubric_keys", [])),
            "question":   t.get("question", ""),
            "notes":      notes,
            "description": topic,
        })
        if len(result) >= limit:
            break

    return jsonify({
        "tasks":     result,
        "total":     len(result),
        "total_all": len(tasks),
    })


@app.route("/api/task/<task_id>")
def api_task(task_id: str):
    tasks = _load_tasks()
    for t in tasks:
        if t["task_id"].upper() == task_id.upper():
            prompt = _build_prompt_safe(t)
            tid    = t["task_id"]
            notes  = t.get("notes", {})
            topic  = notes.get("topic", "") if isinstance(notes, dict) else str(notes)
            return jsonify({
                "task_id":          tid,
                "task_type":        _task_prefix(tid),
                "tier":             t.get("tier"),
                "difficulty":       t.get("difficulty"),
                "category":         "conceptual" if tid.startswith("CONCEPTUAL") else "numeric",
                "question":         prompt or t.get("question", ""),
                "description":      topic,
                "numeric_targets":  t.get("numeric_targets", []),
                "rubric_keys":      t.get("rubric_keys", []),
                "reference_answer": t.get("reference_answer", ""),
                "required_structure_checks":   t.get("required_structure_checks", []),
                "required_assumption_checks":  t.get("required_assumption_checks", []),
                "notes":            notes,
                "prompt":           prompt,
            })
    return jsonify({"error": f"Task '{task_id}' not found"}), 404


@app.route("/api/results/summary")
def api_results_summary():
    runs = _load_runs()
    if not runs:
        return jsonify({"models": {}, "total_runs": 0})

    by_model: Dict[str, List[Dict]] = defaultdict(list)
    for r in runs:
        model = r.get("model_name") or r.get("model_family") or r.get("model", "unknown")
        by_model[model].append(r)

    models_out: Dict[str, Any] = {}
    for model, recs in by_model.items():
        scores    = [r.get("final_score", r.get("normalized_score", 0)) for r in recs]
        passed    = [r.get("pass", False) for r in recs]
        latencies = [r.get("latency_ms", 0) for r in recs if r.get("latency_ms")]
        models_out[model] = {
            "avg_score":     round(sum(scores) / len(scores), 4) if scores else 0,
            "pass_rate":     round(sum(1 for p in passed if p) / len(passed), 4) if passed else 0,
            "n_tasks":       len(recs),
            "avg_latency_ms": round(sum(latencies) / len(latencies), 1) if latencies else 0,
        }

    # Also pull from results.json model_aggregates
    results = _load_results()
    for agg in results.get("model_aggregates", []):
        mn = agg.get("model_name", "")
        if mn and mn not in models_out:
            models_out[mn] = {
                "avg_score":     round(agg.get("normalized_score", 0), 4),
                "pass_rate":     0,
                "n_tasks":       len(results.get("task_scores", [])),
                "avg_latency_ms": 0,
            }
        elif mn in models_out:
            # Trust the aggregate normalized score if available
            models_out[mn]["avg_score"] = round(agg.get("normalized_score", models_out[mn]["avg_score"]), 4)

    return jsonify({"models": models_out, "total_runs": len(runs)})


@app.route("/api/results/by_type")
def api_results_by_type():
    results = _load_results()
    task_scores = results.get("task_scores", [])

    # group by (model, task_type)
    by_model_type: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
    for ts in task_scores:
        model = ts.get("model_name", "unknown")
        tid   = ts.get("task_id", "")
        ttype = _task_prefix(tid)
        score = ts.get("final_weighted_score", 0.0)
        by_model_type[model][ttype].append(score)

    out: Dict[str, Dict[str, float]] = {}
    for model, by_type in by_model_type.items():
        out[model] = {tt: round(sum(ss)/len(ss), 4) for tt, ss in by_type.items()}
    return jsonify(out)


@app.route("/api/results/by_tier")
def api_results_by_tier():
    results = _load_results()
    task_scores = results.get("task_scores", [])

    by_model_tier: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
    for ts in task_scores:
        model = ts.get("model_name", "unknown")
        tier  = str(ts.get("tier", "?"))
        score = ts.get("final_weighted_score", 0.0)
        by_model_tier[model][tier].append(score)

    out: Dict[str, Dict[str, float]] = {}
    for model, by_tier in by_model_tier.items():
        out[model] = {t: round(sum(ss)/len(ss), 4) for t, ss in by_tier.items()}
    return jsonify(out)


@app.route("/api/results/runs")
def api_results_runs():
    runs = _load_runs()
    model_filter = request.args.get("model", "").lower()
    type_filter  = request.args.get("task_type", "").upper()
    limit        = int(request.args.get("limit", 50))

    result = []
    for r in runs:
        model = (r.get("model_name") or r.get("model_family") or r.get("model", "")).lower()
        tid   = r.get("task_id", "")
        ttype = _task_prefix(tid)
        if model_filter and model_filter not in model:
            continue
        if type_filter and ttype != type_filter:
            continue
        result.append(r)
        if len(result) >= limit:
            break
    return jsonify(result)


@app.route("/api/leaderboard")
def api_leaderboard():
    results = _load_results()
    runs    = _load_runs()

    # Collect from model_aggregates
    aggs = {a["model_name"]: a for a in results.get("model_aggregates", [])}

    # Collect from runs
    by_model: Dict[str, List[Dict]] = defaultdict(list)
    for r in runs:
        model = r.get("model_name") or r.get("model_family") or r.get("model", "unknown")
        by_model[model].append(r)

    all_models = set(aggs.keys()) | set(by_model.keys())
    leaderboard = []
    for model in all_models:
        recs   = by_model.get(model, [])
        scores = [r.get("final_score", 0) for r in recs]
        agg    = aggs.get(model, {})
        avg    = agg.get("normalized_score") or (sum(scores)/len(scores) if scores else 0)
        leaderboard.append({
            "model":         model,
            "avg_score":     round(avg, 4),
            "n_tasks":       len(recs) or len(results.get("task_scores", [])),
            "pass_rate":     round(sum(1 for r in recs if r.get("pass", False)) / max(len(recs),1), 4),
            "avg_latency_ms": round(sum(r.get("latency_ms",0) for r in recs) / max(len(recs),1), 1),
            "by_tier":       agg.get("by_tier", {}),
            "by_difficulty": agg.get("by_difficulty", {}),
        })

    leaderboard.sort(key=lambda x: x["avg_score"], reverse=True)
    for i, entry in enumerate(leaderboard):
        entry["rank"] = i + 1

    return jsonify(leaderboard)


@app.route("/api/task_types")
def api_task_types():
    tasks = _load_tasks()
    counts: Dict[str, int] = defaultdict(int)
    for t in tasks:
        counts[_task_prefix(t["task_id"])] += 1

    result = []
    for tt, desc in TASK_TYPE_DESCRIPTIONS.items():
        result.append({
            "type":        tt,
            "description": desc,
            "count":       counts.get(tt, 0),
        })
    result.sort(key=lambda x: x["type"])
    return jsonify(result)


if __name__ == "__main__":
    print("=" * 60)
    print("  LLM Bayesian Benchmark Website")
    print("  http://localhost:5001")
    print("=" * 60)
    app.run(debug=False, port=5001, host="0.0.0.0")
