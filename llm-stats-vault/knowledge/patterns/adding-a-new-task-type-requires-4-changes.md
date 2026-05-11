---
tags: [pattern, tasks, contribution, benchmark]
date: 2026-04-26
---

# Adding a New Task Type Requires 4 Changes

## The Pattern
Whenever a new statistical task type is introduced, exactly 4 files must be updated in order:

### Step 1: Task Generator
Add `gen_<type>_tasks()` in `code/data_preprocessing/bayesian/build_tasks_bayesian.py`  
(or `build_tasks_advanced.py` for computational methods)  
- This function produces task specs with ground-truth numeric_targets
- Uses baseline computation modules (`conjugate_models.py`, `ground_truth.py`, etc.)

### Step 2: Ground Truth (if needed)
Add `gt_<type>()` in `code/data_preprocessing/bayesian/ground_truth.py`  
- Only needed if the computation is novel and not already in a baseline module
- Returns a dict with computed values that become `numeric_targets`

### Step 3: Prompt Builder
Add `_prompt_<type>(task)` in `code/models/prompt_builder.py`  
- Formats the task spec into a natural-language problem statement
- Returns a string prompt presented to the LLM

### Step 4: Register in Dispatch
Add to `_DISPATCH` dict in `code/models/prompt_builder.py`:
```python
_DISPATCH = {
    ...
    "NEW_TYPE": _prompt_new_type,
}
```

### After Changes
```bash
# Regenerate task files
python -m baseline.bayesian.build_tasks_bayesian
# Or for advanced tasks:
python -m baseline.bayesian.build_tasks_advanced

# Validate generated tasks
python -m evaluation.task_validator  # optional

# Run benchmark on new tasks
python -m llm_runner.run_all_tasks --models claude chatgpt deepseek mistral
```

## Task Spec Schema (what gen_ functions must produce)
```json
{
  "task_id": "NEW_TYPE_01",
  "task_type": "NEW_TYPE",
  "tier": 2,
  "difficulty": "basic",
  "inputs": {"param1": 0.5, "param2": 10},
  "numeric_targets": [
    {"key": "result", "value": 0.583,
     "full_credit_tol": 0.01, "zero_credit_scale": 0.10}
  ],
  "required_structure_checks": ["shows_formula", "identifies_model"],
  "required_assumption_checks": ["states_distribution"],
  "prompt_template": "..."
}
```

## Rules
- Task IDs: `TYPE_NN` format, zero-padded 2 digits (e.g., `NEW_TYPE_01`)
- Never edit generated JSON files — always regenerate
- See [[tasks-json-is-generated-never-edited-manually]]
