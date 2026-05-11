"""
Simple JSONL logger for runs.

Writes one JSON object per line (append-only). Great for experiments.
"""

from __future__ import annotations
import json
from datetime import datetime
from typing import Any, Dict


def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def log_jsonl(path: str, record: Dict[str, Any]) -> None:
    record = dict(record)
    record["_ts"] = now_iso()
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")