# baseline/bayesian/utils.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple
import math
import numpy as np

def require_positive(x: float, name: str) -> None:
    if x <= 0:
        raise ValueError(f"{name} must be > 0, got {x}")

def require_nonnegative(x: float, name: str) -> None:
    if x < 0:
        raise ValueError(f"{name} must be >= 0, got {x}")

def require_int_nonnegative(x, name: str) -> None:
    if not isinstance(x, (int, np.integer)) or x < 0:
        raise ValueError(f"{name} must be an integer >= 0, got {x}")

def safe_log(x: float) -> float:
    if x <= 0:
        return float("-inf")
    return math.log(x)

@dataclass(frozen=True)
class CredibleInterval:
    level: float  # e.g., 0.95
    lower: float
    upper: float