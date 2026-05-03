"""Strictness verification for the external LLM-as-judge.

Loads judge results + matches them to original responses + task specs.
Prints low-score `assumption_compliance` cases for manual inspection,
then computes auto-flag heuristics (template justifications, length-
independence, keyword count) and emits an auto-verdict.

Run from project root:
    python scripts/inspect_judge_strictness.py
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

JUDGE_PATH = Path("experiments/results_v2/llm_judge_scores_sample.jsonl")
RUNS_PATH = Path("experiments/results_v1/runs.jsonl")
TASKS_PATH = Path("data/benchmark_v1/tasks_all.json")
PERT_PATH = Path("data/synthetic/perturbations_all.json")

KEYWORDS = ["assume", "assumption", "iid", "i.i.d.", "independent",
            "identically", "prior", "likelihood"]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def load_tasks() -> dict[str, dict]:
    out = {t["task_id"]: t for t in json.loads(TASKS_PATH.read_text())}
    if PERT_PATH.exists():
        out.update({t["task_id"]: t for t in json.loads(PERT_PATH.read_text())})
    return out


def excerpt(text: str, head: int = 800, tail: int = 400) -> str:
    text = text or ""
    if len(text) <= head + tail:
        return text
    return f"{text[:head]}\n...\n{text[-tail:]}"


def keyword_count(text: str) -> int:
    t = (text or "").lower()
    return sum(t.count(kw) for kw in KEYWORDS)


def main() -> int:
    judge_records = load_jsonl(JUDGE_PATH)
    runs_by_id = {r["run_id"]: r for r in load_jsonl(RUNS_PATH)}
    tasks = load_tasks()

    low_score: list[dict] = []
    for jr in judge_records:
        ac = jr.get("assumption_compliance") or {}
        score = ac.get("score")
        if score is None:
            continue
        if score < 0.5:
            low_score.append(jr)

    print(f"Loaded {len(judge_records)} judge records.")
    print(f"Low-score (assumption_compliance < 0.5): {len(low_score)}\n")

    lengths: list[int] = []
    keyword_counts: list[int] = []
    justifications: list[str] = []

    for jr in low_score:
        run = runs_by_id.get(jr["run_id"])
        task = tasks.get(jr["task_id"])
        if not run or not task:
            print(f"  [skip] missing run or task for {jr['run_id']}")
            continue

        raw = run.get("raw_response") or ""
        lengths.append(len(raw))
        keyword_counts.append(keyword_count(raw))
        justifications.append((jr["assumption_compliance"].get("justification") or "").strip())

        required = task.get("required_assumption_checks", [])
        score = jr["assumption_compliance"]["score"]
        just = jr["assumption_compliance"].get("justification", "")

        print("=" * 80)
        print(f"RUN: {jr['run_id']}  |  TASK: {jr['task_id']}  |  MODEL: {jr['model_family']}")
        print("=" * 80)
        print("REQUIRED ASSUMPTIONS (from task spec):")
        if required:
            for c in required:
                print(f"  - {c}")
        else:
            print("  (none)")
        print()
        print(f"JUDGE VERDICT: assumption_compliance = {score}")
        print(f'JUDGE JUSTIFICATION: "{just}"')
        print()
        print(f"MODEL'S RESPONSE (length={len(raw)} chars, keyword hits={keyword_count(raw)}):")
        print("-" * 3)
        print(excerpt(raw))
        print("-" * 3)
        print()
        print("YOUR JUDGMENT: [judge correct / judge too strict / borderline]")
        print("NOTES: ____________________________________________________________________")
        print("=" * 80)
        print()

    # ── Auto-flag signals ────────────────────────────────────────────────────
    print("\n" + "#" * 80)
    print("# AUTO-FLAG SUMMARY")
    print("#" * 80)

    print(f"\nTotal low-score cases: {len(low_score)}\n")

    # Signal 1: Template justifications
    norm = [j.lower() for j in justifications]
    counter = Counter(norm)
    most_common, freq = counter.most_common(1)[0] if counter else ("", 0)
    template_signal = freq >= max(8, int(0.8 * len(low_score))) and len(low_score) >= 8
    print("SIGNAL 1 — Justification pattern:")
    print(f"  Top justification appears {freq}/{len(low_score)} times.")
    print(f"  Top text: \"{most_common[:160]}\"")
    print(f"  Pattern-matching detected: {template_signal}")

    # Signal 1b: shared phrase ("iid" or "independ" or "explicitly state")
    shared_phrase = sum(1 for j in norm if "explicitly state" in j or "iid" in j or "independent" in j)
    print(f"  Justifications mentioning iid/independence/explicit-stating: {shared_phrase}/{len(low_score)}")

    # Signal 2: Length-independent zeros
    print("\nSIGNAL 2 — Response length distribution among low-score cases:")
    if lengths:
        lengths_sorted = sorted(lengths)
        print(f"  min={lengths_sorted[0]}  median={lengths_sorted[len(lengths_sorted)//2]}  max={lengths_sorted[-1]}")
        long_low = sum(1 for L in lengths if L > 2000)
        short_low = sum(1 for L in lengths if L < 500)
        print(f"  long responses (>2000 chars) with low score:  {long_low}/{len(lengths)}")
        print(f"  short responses (<500 chars) with low score:  {short_low}/{len(lengths)}")
        length_independent = long_low > 0 and short_low >= 0  # long zeros = length not the cue
        print(f"  Length-independent zeros (long responses still zero): {length_independent}")
    else:
        length_independent = False

    # Signal 3: Keyword count
    print("\nSIGNAL 3 — Keyword counts in low-score responses:")
    print(f"  Keywords tracked: {KEYWORDS}")
    if keyword_counts:
        kw_sorted = sorted(keyword_counts)
        print(f"  min={kw_sorted[0]}  median={kw_sorted[len(kw_sorted)//2]}  max={kw_sorted[-1]}")
        high_kw = sum(1 for k in keyword_counts if k >= 5)
        print(f"  responses with >=5 keyword hits getting zero score: {high_kw}/{len(keyword_counts)}")
        keyword_signal = high_kw >= max(1, int(0.6 * len(keyword_counts)))
        print(f"  High-keyword zeros suggest possible over-strictness: {keyword_signal}")
    else:
        keyword_signal = False

    # Final verdict
    signals = [template_signal, length_independent, keyword_signal]
    n_true = sum(signals)
    print("\n" + "#" * 80)
    print("# AUTO-VERDICT")
    print("#" * 80)
    print(f"\n  Signals true: {n_true}/3")
    print(f"    template_justifications:    {template_signal}")
    print(f"    length_independent_zeros:   {length_independent}")
    print(f"    high_keyword_count_zeros:   {keyword_signal}")
    print()
    if n_true == 3:
        verdict = "PROBABLY OVER-STRICT"
    elif n_true == 0:
        verdict = "LIKELY CORRECT"
    else:
        verdict = "MIXED"
    print(f"  ==> {verdict}")
    print()
    print("  Final call is yours after reading the printed cases above.")
    print("#" * 80)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
