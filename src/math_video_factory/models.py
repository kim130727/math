from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ExampleSpec:
    """
    커리큘럼의 example 블록을 정규화한 구조.
    예:
        example:
          type: "pattern_growth"
          pattern: "●, ●●, ●●●"
          rule_text: "하나씩 늘어납니다."
    """
    type: str = ""
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class VideoSpec:
    """
    커리큘럼 YAML의 videos 항목 하나.
    """
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


@dataclass(slots=True)
class GradeCurriculum:
    """
    학년 단위 커리큘럼 묶음.
    """
    grade: int
    grade_goal: str
    videos: list[VideoSpec] = field(default_factory=list)


@dataclass(slots=True)
class SceneSpec:
    """
    실제 렌더 가능한 장면 단위 스펙.
    type:
        title, problem, concept, wrap_up, equation, transform,
        grouping, pattern, fraction, compare ...
    payload:
        각 장면 타입별 렌더 데이터
    tts:
        장면용 내레이션 텍스트
    """
    type: str
    payload: dict[str, Any] = field(default_factory=dict)
    tts: str = ""


@dataclass(slots=True)
class ScriptSpec:
    """
    하나의 비디오를 장면 리스트로 변환한 최종 스크립트.
    """
    grade: int
    video_id: str
    title: str
    scenes: list[SceneSpec] = field(default_factory=list)