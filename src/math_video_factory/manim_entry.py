from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

from manim import Scene, WHITE


_THIS_FILE = Path(__file__).resolve()
_PROJECT_ROOT = _THIS_FILE.parents[2]

if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.math_video_factory.curriculum_loader import load_curriculum_by_grade
from src.math_video_factory.curriculum_to_script import build_video_script
from src.math_video_factory.models import SceneSpec, VideoSpec
from src.math_video_factory.simple_renderers import (
    SceneContext,
    register_renderers,
    registry,
)


def _project_root() -> Path:
    return _PROJECT_ROOT


def _curriculum_dir() -> Path:
    return _project_root() / "curriculum"


def _find_video_spec(grade: int, video_id: str) -> VideoSpec:
    curriculum = load_curriculum_by_grade(_curriculum_dir(), grade)

    for spec in curriculum.videos:
        if spec.id == video_id:
            return spec

    available = ", ".join(v.id for v in curriculum.videos) or "(없음)"
    raise ValueError(
        f"영상 ID를 찾을 수 없습니다: {video_id} "
        f"(grade={grade}, available={available})"
    )


def _scene_spec_to_render_dict(scene: SceneSpec) -> dict[str, Any]:
    payload = dict(scene.payload or {})
    scene_type = str(scene.type or "fallback").strip()

    if scene_type == "title":
        return {
            "type": "fallback",
            "title": str(payload.get("text", "")).strip(),
            "body": str(payload.get("subtitle", "")).strip(),
            "caption": str(scene.tts or "").strip(),
            "duration": 3.2,
        }

    if scene_type == "problem":
        return {
            "type": "question",
            "question": str(payload.get("text", "")).strip(),
            "body": str(payload.get("body", "")).strip(),
            "caption": str(scene.tts or "").strip(),
            "duration": 3.0,
        }

    if scene_type == "concept":
        return {
            "type": "fallback",
            "title": "핵심 생각",
            "body": str(payload.get("text", "")).strip(),
            "caption": str(scene.tts or "").strip(),
            "duration": 3.0,
        }

    if scene_type == "wrap_up":
        return {
            "type": "fallback",
            "title": "정리",
            "body": str(payload.get("text", "")).strip(),
            "caption": str(scene.tts or "").strip(),
            "duration": 3.2,
        }

    if scene_type == "equation":
        expression = str(payload.get("expression", "")).strip()
        return {
            "type": "fallback",
            "title": "식으로 나타내기",
            "body": expression,
            "caption": str(scene.tts or "").strip(),
            "duration": 3.0,
        }

    if scene_type == "transform":
        from_expr = str(payload.get("from_expression", "")).strip()
        to_expr = str(payload.get("to_expression", "")).strip()
        body = f"{from_expr}\n↓\n{to_expr}".strip()
        return {
            "type": "fallback",
            "title": "더 짧게 표현하기",
            "body": body,
            "caption": str(scene.tts or "").strip(),
            "duration": 3.2,
        }

    if scene_type == "grouping":
        total = payload.get("total", "")
        group_size = payload.get("group_size", "")
        label = str(payload.get("label", "")).strip()
        body_lines = []
        if label:
            body_lines.append(label)
        body_lines.append(f"전체: {total}")
        body_lines.append(f"묶음 크기: {group_size}")
        return {
            "type": "fallback",
            "title": "묶어 보기",
            "body": "\n".join(body_lines).strip(),
            "caption": str(scene.tts or "").strip(),
            "duration": 3.0,
        }

    if scene_type == "pattern":
        pattern = str(payload.get("pattern", "")).strip()
        question = str(payload.get("question", "")).strip()
        return {
            "type": "fallback",
            "title": "규칙 보기",
            "body": f"{pattern}\n{question}".strip(),
            "caption": str(scene.tts or "").strip(),
            "duration": 3.0,
        }

    if scene_type == "fraction":
        label = str(payload.get("label", "")).strip()
        item = str(payload.get("item", "")).strip()
        parts = payload.get("parts", "")
        selected = payload.get("selected", "")
        body_lines = []
        if item:
            body_lines.append(f"대상: {item}")
        if label:
            body_lines.append(f"표현: {label}")
        body_lines.append(f"전체 조각: {parts}")
        body_lines.append(f"선택 조각: {selected}")
        return {
            "type": "fallback",
            "title": "부분을 나타내기",
            "body": "\n".join(body_lines).strip(),
            "caption": str(scene.tts or "").strip(),
            "duration": 3.0,
        }

    if scene_type == "compare":
        items = payload.get("items", [])
        label = str(payload.get("label", "")).strip()
        left = ""
        right = ""

        if isinstance(items, list) and len(items) >= 2:
            left = str(items[0])
            right = str(items[1])
        elif isinstance(items, list) and len(items) == 1:
            left = str(items[0])

        return {
            "type": "compare",
            "title": label or "비교하기",
            "left": left,
            "right": right,
            "caption": str(scene.tts or "").strip(),
            "duration": 3.0,
        }

    body_parts: list[str] = []
    for key, value in payload.items():
        if value in ("", None):
            continue
        body_parts.append(f"{key}: {value}")

    return {
        "type": "fallback",
        "title": scene_type,
        "body": "\n".join(body_parts).strip() or str(scene.tts or "").strip(),
        "caption": str(scene.tts or "").strip(),
        "duration": 3.0,
    }


def _extract_timings(scene_dicts: list[dict[str, Any]]) -> list[float]:
    timings: list[float] = []

    for i, scene in enumerate(scene_dicts):
        raw = scene.get("duration", 3.0)
        try:
            sec = float(raw)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"scene[{i}].duration 값이 올바르지 않습니다: {raw}"
            ) from exc

        timings.append(max(sec, 0.8))

    return timings


def load_curriculum_bundle(grade: int, video_id: str) -> dict[str, Any]:
    spec = _find_video_spec(grade, video_id)
    script = build_video_script(grade, spec)

    render_scenes = [_scene_spec_to_render_dict(scene) for scene in script.scenes]

    return {
        "grade": grade,
        "video_id": video_id,
        "title": script.title,
        "video_spec": spec,
        "script": script,
        "scenes": render_scenes,
        "timings": _extract_timings(render_scenes),
    }


class CurriculumScene(Scene):
    GRADE: int = 0
    VIDEO_ID: str = "g0_v0"

    def construct(self) -> None:
        self.camera.background_color = WHITE

        register_renderers()

        bundle = load_curriculum_bundle(self.GRADE, self.VIDEO_ID)
        scenes = bundle["scenes"]
        timings = bundle["timings"]

        for index, scene_data in enumerate(scenes):
            ctx = SceneContext(
                scene=self,
                timings=timings,
                scene_index=index,
            )
            registry.render(ctx, scene_data)


def _parse_scene_class_name(name: str) -> tuple[int, str]:
    match = re.fullmatch(r"Grade(\d+)Video(\d+)", name)
    if not match:
        raise AttributeError(name)

    grade = int(match.group(1))
    video_no = int(match.group(2))
    return grade, f"g{grade}_v{video_no}"


def __getattr__(name: str):
    grade, video_id = _parse_scene_class_name(name)

    dynamic_cls = type(
        name,
        (CurriculumScene,),
        {
            "GRADE": grade,
            "VIDEO_ID": video_id,
            "__module__": __name__,
        },
    )
    globals()[name] = dynamic_cls
    return dynamic_cls


class Grade0Video0(CurriculumScene):
    GRADE = 0
    VIDEO_ID = "g0_v0"