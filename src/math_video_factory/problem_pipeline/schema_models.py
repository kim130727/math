from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class NarrationSpec:
    primary: str
    alternate_short: str


@dataclass(slots=True)
class SolutionStep:
    id: str
    phase: str
    action: str
    title: str
    pedagogical_purpose: str
    target: str
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    narration: NarrationSpec = field(default_factory=lambda: NarrationSpec(primary="", alternate_short=""))
    caption: str = ""
    emphasis: list[str] = field(default_factory=list)
    animation: dict[str, Any] = field(default_factory=dict)
    checks: list[dict[str, Any]] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    teacher_note: str = ""


@dataclass(slots=True)
class ProblemSpecV1:
    schema_version: str = "1.0"
    problem_id: str = ""
    input_meta: dict[str, Any] = field(default_factory=dict)
    pedagogy: dict[str, Any] = field(default_factory=dict)
    semantic: dict[str, Any] = field(default_factory=dict)
    derived_facts: list[dict[str, Any]] = field(default_factory=list)
    scene_objects: list[dict[str, Any]] = field(default_factory=list)
    layout_template: dict[str, Any] = field(default_factory=dict)
    solution_plan: dict[str, Any] = field(default_factory=dict)
    animation_prefs: dict[str, Any] = field(default_factory=dict)
    validation: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
