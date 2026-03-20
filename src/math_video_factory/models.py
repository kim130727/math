from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExampleSpec:
    """
    영상에서 사용할 대표 예시 데이터
    예:
    - repeated_addition
    - division_grouping
    - fraction_half
    - pattern_growth
    """
    type: str
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class VideoSpec:
    """
    한 편의 영상 기획 데이터
    """
    id: str
    title: str
    concept: str
    abstraction_stage: str
    key_understanding: str
    keywords: list[str] = field(default_factory=list)
    example: ExampleSpec = field(default_factory=lambda: ExampleSpec(type=""))
    visual_model: str = ""
    narration_style: str = "초등 친화적"
    conclusion: str = ""


@dataclass
class GradeCurriculum:
    """
    한 학년 전체 커리큘럼 데이터
    """
    grade: int
    grade_goal: str
    videos: list[VideoSpec] = field(default_factory=list)


@dataclass
class SceneSpec:
    """
    실제 영상 장면 1개에 대한 데이터
    """
    type: str
    payload: dict[str, Any] = field(default_factory=dict)
    tts: str = ""


@dataclass
class ScriptSpec:
    """
    한 편 영상의 전체 장면 스크립트 데이터
    """
    video_id: str
    title: str
    grade: int
    scenes: list[SceneSpec] = field(default_factory=list)