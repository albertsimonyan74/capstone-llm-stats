import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from pathlib import Path
from typing import Optional
from collections import defaultdict

try:
    from backend.user_study import router as user_study_router
except ModuleNotFoundError:
    from user_study import router as user_study_router

app = FastAPI(title="LLM Bayesian Benchmark API")

_frontend = os.environ.get("FRONTEND_URL", "")
_ORIGINS = ["http://localhost:5173", "http://localhost:3000"] + (
    [_frontend] if _frontend else ["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_study_router)

BASE_DIR   = Path(os.environ.get("DATA_ROOT", str(Path(__file__).parent.parent.parent)))
TASKS_FILE = BASE_DIR / "data" / "benchmark_v1" / "tasks_all.json"
RUNS_FILE  = BASE_DIR / "experiments" / "results_v1" / "runs.jsonl"


def _load_tasks():
    with open(TASKS_FILE) as f:
        return json.load(f)


def _load_runs():
    runs = []
    if RUNS_FILE.exists():
        with open(RUNS_FILE) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        runs.append(json.loads(line))
                    except Exception:
                        pass
    return runs


def _task_type(task_id: str) -> str:
    parts = task_id.rsplit("_", 1)
    return parts[0] if len(parts) == 2 and parts[1].isdigit() else task_id


def _enrich(t: dict) -> dict:
    task_id = t.get("task_id", "")
    task_type = t.get("task_type") or _task_type(task_id)
    is_conceptual = task_id.startswith("CONCEPTUAL")
    # Phase 2 tasks have category="computational_bayes"; Phase 1 have notes.topic
    raw_category = t.get("category", "")
    if raw_category == "computational_bayes":
        category = "computational_bayes"
    elif is_conceptual:
        category = "conceptual"
    else:
        category = "numeric"

    notes = t.get("notes", {})
    topic = notes.get("topic", "") if isinstance(notes, dict) else str(notes)
    desc = topic.replace("_", " ") if topic else task_type.replace("_", " ")

    raw_targets = t.get("numeric_targets", [])
    if isinstance(raw_targets, list):
        targets = {nt["key"]: nt.get("true_value", 0) for nt in raw_targets if "key" in nt}
    else:
        targets = raw_targets

    # inputs: P1 stores under notes.inputs, P2 stores at top level
    inputs = t.get("inputs") or (notes.get("inputs", {}) if isinstance(notes, dict) else {})

    return {
        "task_id":          task_id,
        "task_type":        task_type,
        "tier":             t.get("tier", 1),
        "difficulty":       t.get("difficulty", "basic"),
        "description":      desc,
        "category":         category,
        "numeric_targets":  targets,
        "rubric_keys":      t.get("rubric_keys", []),
        "reference_answer": t.get("reference_answer", ""),
        "notes_topic":      topic,
        "inputs":           inputs,
        "prompt":           t.get("prompt", ""),
        "required_structure_checks":  t.get("required_structure_checks", []),
        "required_assumption_checks": t.get("required_assumption_checks", []),
    }


@app.get("/api/status")
def status():
    tasks = _load_tasks()
    runs  = _load_runs()
    models = list({r.get("model_name") or r.get("model_family", "") for r in runs if r.get("model_name") or r.get("model_family")})
    tier_counts: dict = {}
    for t in tasks:
        k = str(t.get("tier", "?"))
        tier_counts[k] = tier_counts.get(k, 0) + 1
    return {
        "total_tasks":    len(tasks),
        "total_runs":     len(runs),
        "models_run":     models,
        "benchmark_ready": True,
        "tier_counts":    tier_counts,
    }


@app.get("/api/tasks")
def get_tasks(
    tier:         Optional[str] = None,
    category:     Optional[str] = None,
    task_type:    Optional[str] = None,
    search_id:    Optional[str] = None,
    search_topic: Optional[str] = None,
    limit:        int = 200,
):
    tasks  = _load_tasks()
    result = []

    for t in tasks:
        task_id  = t.get("task_id", "")
        tt       = t.get("task_type") or _task_type(task_id)
        is_conceptual = task_id.startswith("CONCEPTUAL")

        if tier:
            allowed = {int(x) for x in tier.split(",") if x.isdigit()}
            if allowed and t.get("tier") not in allowed:
                continue

        if category:
            raw_cat = t.get("category", "")
            if category == "conceptual" and not is_conceptual:
                continue
            if category == "numeric" and (is_conceptual or raw_cat == "computational_bayes"):
                continue
            if category == "computational_bayes" and raw_cat != "computational_bayes":
                continue

        if task_type and tt.upper() != task_type.upper():
            continue

        if search_id and search_id.upper() not in task_id.upper():
            continue

        if search_topic:
            notes = t.get("notes", {})
            topic = notes.get("topic", "") if isinstance(notes, dict) else str(notes)
            hay   = (task_id + " " + topic + " " + tt).lower()
            if search_topic.lower() not in hay:
                continue

        result.append(_enrich(t))
        if len(result) >= limit:
            break

    return {"tasks": result, "total": len(result), "total_all": len(tasks)}


@app.get("/api/task/{task_id}")
def get_task(task_id: str):
    tasks = _load_tasks()
    t = next((x for x in tasks if x.get("task_id", "").upper() == task_id.upper()), None)
    if not t:
        return {"error": f"Task {task_id} not found"}

    # Try building prompt
    question = ""
    try:
        import sys
        sys.path.insert(0, str(BASE_DIR))
        from llm_runner.prompt_builder import build_prompt
        question = build_prompt(t)
    except Exception as e:
        notes = t.get("notes", {})
        topic = notes.get("topic", "") if isinstance(notes, dict) else str(notes)
        question = f"[{task_id}] {topic}"

    enriched = _enrich(t)
    enriched["question"] = question
    return enriched


@app.get("/api/results/summary")
def results_summary():
    runs = _load_runs()
    if not runs:
        return {"models": {}, "total_runs": 0}

    model_data: dict = defaultdict(lambda: {"scores": [], "latencies": [], "passes": 0, "n": 0})
    for r in runs:
        mf    = r.get("model_name") or r.get("model_family", "unknown")
        score = r.get("final_score", r.get("normalized_score", 0))
        model_data[mf]["scores"].append(score)
        model_data[mf]["latencies"].append(r.get("latency_ms", 0))
        model_data[mf]["n"] += 1
        if r.get("pass", False):
            model_data[mf]["passes"] += 1

    models = {}
    for mf, d in model_data.items():
        n = d["n"]
        models[mf] = {
            "avg_score":      round(sum(d["scores"]) / n, 4) if n else 0,
            "pass_rate":      round(d["passes"] / n, 4) if n else 0,
            "n_tasks":        n,
            "avg_latency_ms": round(sum(d["latencies"]) / n, 1) if n else 0,
        }

    return {"models": models, "total_runs": len(runs)}


@app.get("/api/leaderboard")
def leaderboard():
    summary = results_summary()
    models  = summary.get("models", {})
    ranking = sorted(models.items(), key=lambda x: x[1]["avg_score"], reverse=True)
    return {
        "ranking":    [{"model": m, **d, "rank": i + 1} for i, (m, d) in enumerate(ranking)],
        "total_runs": summary["total_runs"],
    }


@app.get("/api/results/by_type")
def results_by_type():
    runs = _load_runs()
    data: dict = defaultdict(lambda: defaultdict(list))
    for r in runs:
        tid = r.get("task_id", "")
        tt  = _task_type(tid)
        mf  = r.get("model_name") or r.get("model_family", "unknown")
        data[tt][mf].append(r.get("final_score", r.get("normalized_score", 0)))

    return {
        tt: {mf: round(sum(scores) / len(scores), 4) for mf, scores in models.items()}
        for tt, models in data.items()
    }
