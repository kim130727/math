from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExampleSpec:
    type: str = ""
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class VideoSpec:
    id: str
    title: str
    concept: str
    abstraction_stage: str
    key_understanding: str
    keywords: list[str] = field(default_factory=list)
    example: ExampleSpec = field(default_factory=ExampleSpec)
    visual_model: str = ""
    narration_style: str = "초등 친화적"
    conclusion: str = ""


@dataclass
class SceneSpec:
    type: str
    payload: dict[str, Any] = field(default_factory=dict)
    tts: str = ""


@dataclass
class ScriptSpec:
    video_id: str
    title: str
    grade: int
    scenes: list[SceneSpec] = field(default_factory=list)


@dataclass
class GradeCurriculum:
    grade: int
    grade_goal: str
    videos: list[VideoSpec] = field(default_factory=list)