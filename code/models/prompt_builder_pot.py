"""
Program-of-Thoughts prompt builder and executor.
Implements Chen et al. (2022): LLM generates Python code, external interpreter executes.
Provides numerical accuracy upper bound vs zero-shot CoT baseline.
"""
from __future__ import annotations
import os
import re
import subprocess
import tempfile

FORBIDDEN = [
    "import os", "import sys", "import subprocess",
    "open(", "exec(", "eval(", "__import__", "shutil",
]


def build_pot_prompt(task: dict) -> str:
    """Return a prompt instructing the model to write executable Python."""
    from models.prompt_builder import build_prompt
    base = build_prompt(task)
    pot_instruction = (
        "\n\nSolve this problem by writing Python code using numpy/scipy.\n"
        "Your code must print the final answer as:\n"
        "  print('ANSWER:', val1, val2, ...)\n"
        "Write complete, executable Python code between ```python and ``` tags.\n"
        "Do not import os, sys, or subprocess."
    )
    return base + pot_instruction


def _is_float(s: str) -> bool:
    try:
        float(s.replace(",", ""))
        return True
    except ValueError:
        return False


def execute_pot_response(response_text: str, timeout: int = 10) -> list[float]:
    """
    Extract Python code from LLM response, execute it safely, return numeric results.
    Returns [] on timeout, security violation, or parse failure.
    """
    code_match = re.search(r"```python\n(.*?)```", response_text, re.DOTALL)
    if not code_match:
        return []

    code = code_match.group(1)

    for token in FORBIDDEN:
        if token in code:
            return []

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write(code)
            tmp_path = f.name

        result = subprocess.run(
            ["python3", tmp_path],
            capture_output=True, text=True, timeout=timeout,
        )

        for line in result.stdout.splitlines():
            if "ANSWER:" in line.upper():
                parts = line.split(":", 1)[1].strip().split()
                try:
                    return [float(v.replace(",", "")) for v in parts if _is_float(v)]
                except ValueError:
                    return []
        return []

    except subprocess.TimeoutExpired:
        return []
    except Exception:
        return []
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
