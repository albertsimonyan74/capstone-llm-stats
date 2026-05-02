"""
v2 API routes — serves Day 1-3 analysis results from experiments/results_v2/
and llm-stats-vault/40-literature/.

Mounted at /api/v2/ via the existing FastAPI app in main.py.
v1 routes (/, /api/status, /api/tasks, /api/leaderboard, /api/results/*,
/api/user-study/*) are untouched.
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v2", tags=["v2"])

# ─── Paths ────────────────────────────────────────────────────────
BASE_DIR = Path(os.environ.get("DATA_ROOT", str(Path(__file__).parent.parent.parent)))
RESULTS_V2 = BASE_DIR / "experiments" / "results_v2"
LIT_DIR = BASE_DIR / "llm-stats-vault" / "40-literature"

V2_FILES = {
    "agreement_keyword_judge": RESULTS_V2 / "keyword_vs_judge_agreement.json",
    "krippendorff": RESULTS_V2 / "krippendorff_agreement.json",
    "calibration_verbalized": RESULTS_V2 / "calibration.json",
    "calibration_consistency": RESULTS_V2 / "self_consistency_calibration.json",
    "robustness": RESULTS_V2 / "robustness_v2.json",
    "bootstrap_ci": RESULTS_V2 / "bootstrap_ci.json",
    "error_taxonomy": RESULTS_V2 / "error_taxonomy_v2.json",
    "judge_dimension_means": RESULTS_V2 / "judge_dimension_means.json",
    "tolerance_sensitivity": RESULTS_V2 / "tolerance_sensitivity.json",
    "perturbations_all": BASE_DIR / "data" / "synthetic" / "perturbations_all.json",
    "pass_flip": RESULTS_V2 / "combined_pass_flip_analysis.json",
    "keyword_degradation": RESULTS_V2 / "keyword_degradation_check.json",
}

# Files required for /api/v2/health to report ok
HEALTH_REQUIRED = [
    "agreement_keyword_judge",
    "krippendorff",
    "calibration_verbalized",
    "calibration_consistency",
    "robustness",
    "bootstrap_ci",
    "error_taxonomy",
    "judge_dimension_means",
    "tolerance_sensitivity",
    "pass_flip",
    "keyword_degradation",
]

# ─── mtime-keyed cache ────────────────────────────────────────────
# {path_str: (mtime_ns, parsed_data)}
_cache: Dict[str, tuple] = {}


def _load_json(path: Path) -> Any:
    """Read JSON with mtime-based cache. Re-reads if file changed on disk."""
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Data file missing: {path.name}")
    key = str(path)
    try:
        mtime = path.stat().st_mtime_ns
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"stat failed for {path.name}: {e}")

    cached = _cache.get(key)
    if cached and cached[0] == mtime:
        return cached[1]

    try:
        with open(path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"JSON parse error in {path.name}: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"read failed for {path.name}: {e}")

    _cache[key] = (mtime, data)
    return data


# ─── Krippendorff α interpretation (Park et al., 2025 thresholds) ─
def _alpha_interp(alpha: float) -> str:
    if alpha is None:
        return "undefined"
    if alpha > 0.8:
        return "strong"
    if alpha >= 0.667:
        return "acceptable"
    return "questionable"


# ─── Response models ──────────────────────────────────────────────
class RankingEntry(BaseModel):
    model: str
    score: Optional[float] = None
    delta: Optional[float] = None
    ece: Optional[float] = None
    ci: Optional[List[float]] = None
    rank: Optional[int] = None


class HeadlineRankings(BaseModel):
    accuracy: List[RankingEntry]
    robustness: List[RankingEntry]
    calibration: List[RankingEntry]


class HeadlineNumbers(BaseModel):
    pass_flip_rate: float
    pass_flip_n: int
    pass_flip_total: int
    krippendorff_alpha_assumption: float
    krippendorff_alpha_ci: List[float]
    krippendorff_interpretation: str
    dominant_failure_mode: str
    dominant_failure_pct: float
    dominant_failure_n: int
    dominant_failure_total: int
    n_perturbations: int
    n_runs: int
    n_judge_records: int
    rankings: HeadlineRankings


class HealthEntry(BaseModel):
    file: str
    exists: bool
    parses: bool
    size_bytes: Optional[int] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    ok: bool
    files: List[HealthEntry]


# ─── /api/v2/health ───────────────────────────────────────────────
@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    entries: List[HealthEntry] = []
    all_ok = True
    for key in HEALTH_REQUIRED:
        path = V2_FILES[key]
        exists = path.exists()
        parses = False
        size_bytes: Optional[int] = None
        err: Optional[str] = None
        if exists:
            try:
                size_bytes = path.stat().st_size
                with open(path) as f:
                    json.load(f)
                parses = True
            except Exception as e:
                err = str(e)
        else:
            err = "file not found"
        if not (exists and parses):
            all_ok = False
        entries.append(
            HealthEntry(
                file=path.name,
                exists=exists,
                parses=parses,
                size_bytes=size_bytes,
                error=err,
            )
        )
    return HealthResponse(ok=all_ok, files=entries)


# ─── Headline numbers ─────────────────────────────────────────────
def _build_rankings() -> HeadlineRankings:
    bs = _load_json(V2_FILES["bootstrap_ci"])
    rob = _load_json(V2_FILES["robustness"])
    calib = _load_json(V2_FILES["calibration_verbalized"])

    # Accuracy: sorted by mean desc, with bootstrap CI
    acc_items = []
    for model, d in bs.get("accuracy", {}).items():
        acc_items.append(
            {
                "model": model,
                "score": d.get("mean"),
                "ci": [d.get("ci_lower"), d.get("ci_upper")],
            }
        )
    acc_items.sort(key=lambda x: x["score"] if x["score"] is not None else -1, reverse=True)
    accuracy = [
        RankingEntry(rank=i + 1, model=x["model"], score=x["score"], ci=x["ci"])
        for i, x in enumerate(acc_items)
    ]

    # Robustness: from robustness_v2.ranking (rank 1 = lowest delta = most robust)
    rob_ranking = rob.get("ranking", [])
    rob_ci_block = bs.get("robustness", {})
    robustness: List[RankingEntry] = []
    for entry in rob_ranking:
        m = entry.get("model")
        ci_data = rob_ci_block.get(m, {})
        robustness.append(
            RankingEntry(
                rank=entry.get("rank"),
                model=m,
                delta=entry.get("delta"),
                ci=[ci_data.get("ci_lower"), ci_data.get("ci_upper")]
                if ci_data
                else None,
            )
        )

    # Calibration: ECE asc (lower is better)
    cal_items = [(m, d.get("ece")) for m, d in calib.items()
                 if isinstance(d, dict) and d.get("ece") is not None]
    cal_items.sort(key=lambda x: x[1])
    calibration = [
        RankingEntry(rank=i + 1, model=m, ece=ece) for i, (m, ece) in enumerate(cal_items)
    ]

    return HeadlineRankings(
        accuracy=accuracy, robustness=robustness, calibration=calibration
    )


@router.get("/headline_numbers", response_model=HeadlineNumbers)
def headline_numbers() -> HeadlineNumbers:
    agreement = _load_json(V2_FILES["agreement_keyword_judge"])
    krippendorff = _load_json(V2_FILES["krippendorff"])
    taxonomy = _load_json(V2_FILES["error_taxonomy"])
    rob = _load_json(V2_FILES["robustness"])

    # Pass-flip
    flip = agreement.get("pass_flip_assumption", {})
    flip_n = int(flip.get("keyword_pass_judge_fail", 0))
    flip_total = int(flip.get("n_compared", 0))
    flip_pct = flip.get("kw_pass_judge_fail_pct")
    flip_rate = (flip_pct / 100.0) if flip_pct is not None else (
        flip_n / flip_total if flip_total else 0.0
    )

    # Krippendorff α on assumption_compliance
    alpha_block = krippendorff.get("overall", {}).get("assumption_compliance", {})
    alpha = float(alpha_block.get("alpha", 0.0))
    alpha_ci = [
        float(alpha_block.get("ci_lower", 0.0)),
        float(alpha_block.get("ci_upper", 0.0)),
    ]

    # Dominant failure mode
    l1 = taxonomy.get("l1_totals", {})
    if l1:
        dom_mode, dom_n = max(l1.items(), key=lambda kv: kv[1])
        dom_total = int(taxonomy.get("n_failures_classified", sum(l1.values())))
        dom_pct = dom_n / dom_total if dom_total else 0.0
    else:
        dom_mode, dom_n, dom_total, dom_pct = "UNKNOWN", 0, 0, 0.0

    # robustness_v2.n_perturbations is total perturbation runs (rows).
    # Unique perturbation count lives in data/synthetic/perturbations_all.json.
    n_runs = int(rob.get("n_perturbations", 0))
    n_models = len(rob.get("models", [])) or 5
    perts_path = V2_FILES["perturbations_all"]
    if perts_path.exists():
        try:
            n_perts = len(_load_json(perts_path))
        except Exception:
            n_perts = n_runs // n_models if n_models else 0
    else:
        n_perts = n_runs // n_models if n_models else 0

    return HeadlineNumbers(
        pass_flip_rate=round(flip_rate, 4),
        pass_flip_n=flip_n,
        pass_flip_total=flip_total,
        krippendorff_alpha_assumption=round(alpha, 4),
        krippendorff_alpha_ci=[round(alpha_ci[0], 4), round(alpha_ci[1], 4)],
        krippendorff_interpretation=_alpha_interp(alpha),
        dominant_failure_mode=dom_mode,
        dominant_failure_pct=round(dom_pct, 4),
        dominant_failure_n=int(dom_n),
        dominant_failure_total=dom_total,
        n_perturbations=n_perts,
        n_runs=n_runs,
        n_judge_records=n_runs,
        rankings=_build_rankings(),
    )


# ─── Three rankings ───────────────────────────────────────────────
@router.get("/rankings")
def rankings() -> Dict[str, Any]:
    bs = _load_json(V2_FILES["bootstrap_ci"])
    rob = _load_json(V2_FILES["robustness"])
    sc = _load_json(V2_FILES["calibration_consistency"])

    return {
        "weighting_scheme": bs.get("weighting_scheme"),
        "accuracy": {
            "method": bs.get("method"),
            "B": bs.get("B"),
            "seed": bs.get("seed"),
            "per_model": bs.get("accuracy", {}),
            "separability": bs.get("separability", {}).get("accuracy", []),
        },
        "robustness": {
            "per_model": bs.get("robustness", {}),
            "ranking": rob.get("ranking", []),
            "separability": bs.get("separability", {}).get("robustness", []),
            "per_perturbation_type": {
                m: d.get("per_perturbation_type", {})
                for m, d in rob.get("per_model", {}).items()
            },
        },
        "calibration": {
            "verbalized_ece": bs.get("calibration_ece_points", {}),
            "consistency_ece": sc.get("ece_comparison_full") or sc.get("ece_comparison", {}),
            "note": bs.get("calibration_note"),
        },
        "models": rob.get("models", list(bs.get("accuracy", {}).keys())),
    }


# ─── Error taxonomy ───────────────────────────────────────────────
@router.get("/error_taxonomy")
def error_taxonomy(include_records: bool = False) -> Dict[str, Any]:
    tax = _load_json(V2_FILES["error_taxonomy"])
    out = {
        "generated_at": tax.get("generated_at"),
        "judge_model": tax.get("judge_model"),
        "n_failures_classified": tax.get("n_failures_classified"),
        "l1_to_l2_mapping": tax.get("l1_to_l2_mapping", {}),
        "l2_definitions": tax.get("l2_definitions", {}),
        "l1_totals": tax.get("l1_totals", {}),
        "l2_totals": tax.get("l2_totals", {}),
        "by_model_l1": tax.get("by_model_l1", {}),
        "by_model_l2": tax.get("by_model_l2", {}),
    }
    if include_records:
        out["records"] = tax.get("records", [])
    else:
        out["n_records_available"] = len(tax.get("records", []))
    return out


# ─── Robustness ───────────────────────────────────────────────────
@router.get("/robustness")
def robustness() -> Dict[str, Any]:
    rob = _load_json(V2_FILES["robustness"])
    return {
        "n_perturbations": rob.get("n_perturbations"),
        "n_base_scores": rob.get("n_base_scores"),
        "missing_base": rob.get("missing_base"),
        "models": rob.get("models", []),
        "task_types": rob.get("task_types", []),
        "perturbation_types": rob.get("perturbation_types", []),
        "per_model": rob.get("per_model", {}),
        "ranking": rob.get("ranking", []),
        "per_task_type_heatmap": rob.get("per_task_type_heatmap", {}),
        "notes": rob.get("notes"),
    }


# ─── Agreement (keyword vs judge + Krippendorff) ──────────────────
@router.get("/agreement")
def agreement() -> Dict[str, Any]:
    kj = _load_json(V2_FILES["agreement_keyword_judge"])
    kr = _load_json(V2_FILES["krippendorff"])

    return {
        "n_joined": kj.get("n_joined"),
        "n_with_both_assumption_scores": kj.get("n_with_both_assumption_scores"),
        "spearman_per_dimension": kj.get("overall_per_dimension", {}),
        "spearman_per_model": kj.get("per_model", {}),
        "spearman_per_task_type": kj.get("per_task_type", {}),
        "pass_flip_assumption": kj.get("pass_flip_assumption", {}),
        "judge_completeness_alone": kj.get("judge_completeness_alone", {}),
        "krippendorff": {
            "bootstrap_B": kr.get("bootstrap_B"),
            "bootstrap_seed": kr.get("bootstrap_seed"),
            "level_of_measurement": kr.get("level_of_measurement"),
            "thresholds": kr.get("thresholds", {}),
            "overall": kr.get("overall", {}),
            "per_model": kr.get("per_model", {}),
            "interpretation": kr.get("interpretation", {}),
        },
        "methodology_citation": kj.get(
            "_methodology_citation", kr.get("_methodology_citation")
        ),
    }


# ─── Calibration (verbalized + consistency-based) ─────────────────
@router.get("/calibration")
def calibration() -> Dict[str, Any]:
    verb = _load_json(V2_FILES["calibration_verbalized"])
    cons = _load_json(V2_FILES["calibration_consistency"])
    bs = _load_json(V2_FILES["bootstrap_ci"])

    return {
        "verbalized": {
            "per_model": verb,
            "ece_points": bs.get("calibration_ece_points", {}),
            "note": bs.get("calibration_note"),
        },
        "consistency": {
            "n_tasks": cons.get("n_tasks"),
            "n_models": cons.get("n_models"),
            "n_runs_per_pair": cons.get("n_runs_per_pair"),
            "temperature": cons.get("temperature"),
            "top_p": cons.get("top_p"),
            "stratification": cons.get("stratification", {}),
            "selected_task_ids": cons.get("selected_task_ids", []),
            "per_model": cons.get("per_model", {}),
            "ece_comparison": cons.get("ece_comparison_full") or cons.get("ece_comparison", {}),
            "session_cost_usd": cons.get("session_cost_usd"),
            "aborted_partial": cons.get("aborted_partial"),
            "methodology_citation": cons.get("_methodology_citation"),
        },
    }


# ─── Pass-flip (combined base + perturbation) ─────────────────────
@router.get("/pass_flip")
def pass_flip() -> Dict[str, Any]:
    """Combined base + perturbation pass-flip analysis (Phase 1.5)."""
    pf = _load_json(V2_FILES["pass_flip"])
    deg = _load_json(V2_FILES["keyword_degradation"])
    return {
        "base": pf.get("base", {}),
        "perturbation": pf.get("perturbation", {}),
        "combined": pf.get("combined", {}),
        "comparison": pf.get("comparison", {}),
        "keyword_degradation": {
            "base": deg.get("base", {}),
            "perturbation": deg.get("perturbation", {}),
            "drops": deg.get("drops", {}),
            "per_perturbation_type": deg.get("per_perturbation_type", {}),
            "verdict": deg.get("verdict", ""),
        },
    }


# ─── Literature parser ────────────────────────────────────────────
_META_FIELD = re.compile(r"^- ([A-Za-z][A-Za-z0-9 /]*?):\s*(.+)$")
_HEADER = re.compile(r"^# (.+)$")
_SECTION = re.compile(r"^## (.+)$")


def _parse_lit_md(path: Path) -> Optional[Dict[str, Any]]:
    """Parse a single literature markdown note into a structured record."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return None

    title = ""
    metadata: Dict[str, str] = {}
    one_line = ""
    poster_cite = ""
    paper_cite = ""

    section: Optional[str] = None
    accum: List[str] = []

    def flush():
        nonlocal one_line, poster_cite, paper_cite
        joined = "\n".join(accum).strip()
        if not section or not joined:
            return
        if section.lower().startswith("one-line summary"):
            one_line = joined.splitlines()[0].strip() if joined else ""
        elif section.lower().startswith("citation in poster"):
            poster_cite = joined.splitlines()[0].strip()
        elif section.lower().startswith("citation in paper"):
            paper_cite = joined.splitlines()[0].strip()

    for raw in text.splitlines():
        line = raw.rstrip()
        h = _HEADER.match(line)
        if h and not title:
            title = h.group(1).strip()
            continue
        s = _SECTION.match(line)
        if s:
            flush()
            section = s.group(1).strip()
            accum = []
            continue
        if section and section.lower() == "metadata":
            m = _META_FIELD.match(line)
            if m:
                metadata[m.group(1).strip().lower()] = m.group(2).strip()
        else:
            accum.append(line)
    flush()

    category_raw = metadata.get("source category", "").upper()
    if "ORIGINAL" in category_raw:
        category = "original"
    elif "NEW" in category_raw:
        category = "new"
    elif "TEXTBOOK" in category_raw:
        category = "textbook"
    else:
        category = "unknown"

    return {
        "filename": path.name,
        "title": title,
        "authors": metadata.get("authors", metadata.get("author", "")),
        "year": metadata.get("year", ""),
        "venue": metadata.get("venue", metadata.get("publisher", "")),
        "arxiv_id": metadata.get("arxiv id", ""),
        "isbn": metadata.get("isbn", ""),
        "url": metadata.get("url", ""),
        "edition": metadata.get("edition", ""),
        "publisher": metadata.get("publisher", ""),
        "category": category,
        "source_category_raw": metadata.get("source category", ""),
        "summary": one_line,
        "citation_poster": poster_cite,
        "citation_paper": paper_cite,
    }


@router.get("/literature")
def literature() -> Dict[str, Any]:
    if not LIT_DIR.exists():
        raise HTTPException(
            status_code=404, detail=f"Literature directory missing: {LIT_DIR}"
        )

    papers_dir = LIT_DIR / "papers"
    textbooks_dir = LIT_DIR / "textbooks"

    papers: List[Dict[str, Any]] = []
    if papers_dir.exists():
        for p in sorted(papers_dir.glob("*.md")):
            rec = _parse_lit_md(p)
            if rec:
                papers.append(rec)

    textbooks: List[Dict[str, Any]] = []
    if textbooks_dir.exists():
        for p in sorted(textbooks_dir.glob("*.md")):
            rec = _parse_lit_md(p)
            if rec:
                rec["category"] = "textbook"
                textbooks.append(rec)

    originals = [p for p in papers if p["category"] == "original"]
    new_papers = [p for p in papers if p["category"] == "new"]

    return {
        "totals": {
            "all": len(papers) + len(textbooks),
            "papers": len(papers),
            "originals": len(originals),
            "new": len(new_papers),
            "textbooks": len(textbooks),
        },
        "originals": originals,
        "new": new_papers,
        "textbooks": textbooks,
    }
