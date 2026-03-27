from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

REQUIRED_TOP_LEVEL_KEYS = [
    "schema_version",
    "problem_id",
    "input_meta",
    "pedagogy",
    "semantic",
    "derived_facts",
    "scene_objects",
    "layout_template",
    "solution_plan",
    "animation_prefs",
    "validation",
]

REQUIRED_VALIDATION_KEYS = [
    "render_safe",
    "solve_safe",
    "human_review_required",
    "confidence",
    "warnings",
]

REQUIRED_STEP_KEYS = [
    "id",
    "phase",
    "action",
    "title",
    "pedagogical_purpose",
    "target",
    "inputs",
    "outputs",
    "narration",
    "caption",
    "emphasis",
    "animation",
    "checks",
    "depends_on",
    "teacher_note",
]


@dataclass(slots=True)
class ValidationResult:
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_problem_spec(data: dict[str, Any]) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in data:
            errors.append(f"missing top-level key: {key}")

    validation = data.get("validation", {})
    if not isinstance(validation, dict):
        errors.append("validation must be an object")
    else:
        for key in REQUIRED_VALIDATION_KEYS:
            if key not in validation:
                errors.append(f"missing validation key: {key}")

        confidence = validation.get("confidence")
        if isinstance(confidence, (int, float)):
            if confidence < 0 or confidence > 1:
                errors.append("validation.confidence must be between 0 and 1")
            if confidence < 0.7 and not validation.get("human_review_required", False):
                warnings.append("confidence < 0.7: human_review_required should be true")
        else:
            errors.append("validation.confidence must be numeric")

    solution_plan = data.get("solution_plan", {})
    steps = solution_plan.get("steps") if isinstance(solution_plan, dict) else None
    if not isinstance(steps, list) or not steps:
        errors.append("solution_plan.steps must be a non-empty list")
    else:
        for idx, step in enumerate(steps, start=1):
            if not isinstance(step, dict):
                errors.append(f"step[{idx}] must be object")
                continue
            for key in REQUIRED_STEP_KEYS:
                if key not in step:
                    errors.append(f"step[{idx}] missing key: {key}")
            narration = step.get("narration", {})
            if not isinstance(narration, dict) or "primary" not in narration or "alternate_short" not in narration:
                errors.append(f"step[{idx}].narration must include primary/alternate_short")

    if not isinstance(data.get("derived_facts"), list):
        errors.append("derived_facts must be a list")
    if not isinstance(data.get("scene_objects"), list):
        errors.append("scene_objects must be a list")

    return ValidationResult(is_valid=not errors, errors=errors, warnings=warnings)
