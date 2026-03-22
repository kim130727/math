from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from manim import Scene, WHITE

from .renderers import SceneContext, register_renderers, registry


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _curriculum_dir() -> Path:
    return _project_root() / "curriculum"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"커리큘럼 파일이 없습니다: {path}")

    raw = path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw)

    if not isinstance(data, dict):
        raise ValueError(f"커리큘럼 파일 형식이 올바르지 않습니다: {path}")

    return data


def _normalize_scenes(data: dict[str, Any]) -> list[dict[str, Any]]:
    scenes = data.get("scenes")

    if not isinstance(scenes, list) or not scenes:
        raise ValueError("YAML에 scenes 리스트가 없거나 비어 있습니다.")

    normalized: list[dict[str, Any]] = []
    for idx, item in enumerate(scenes):
        if not isinstance(item, dict):
            raise ValueError(f"scenes[{idx}] 항목은 dict여야 합니다.")

        scene_item = dict(item)
        scene_item.setdefault("type", "fallback")
        scene_item.setdefault("duration", 3.0)
        normalized.append(scene_item)

    return normalized


def _extract_timings(scenes: list[dict[str, Any]]) -> list[float]:
    timings: list[float] = []

    for i, scene in enumerate(scenes):
        duration = scene.get("duration", 3.0)
        try:
            sec = float(duration)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"scenes[{i}].duration 값이 올바르지 않습니다: {duration}") from exc

        timings.append(max(sec, 0.8))

    return timings


def load_curriculum_bundle(grade: int, video_id: str) -> dict[str, Any]:
    yaml_path = _curriculum_dir() / f"grade_{grade}.yaml"
    root = _load_yaml(yaml_path)

    videos = root.get("videos")
    if not isinstance(videos, dict):
        raise ValueError(f"커리큘럼 파일 형식이 올바르지 않습니다: {yaml_path}")

    video_data = videos.get(video_id)
    if not isinstance(video_data, dict):
        raise ValueError(f"영상 ID를 찾을 수 없습니다: {video_id}")

    scenes = _normalize_scenes(video_data)

    return {
        "grade": grade,
        "video_id": video_id,
        "yaml_path": yaml_path,
        "meta": root.get("meta", {}),
        "video": video_data,
        "scenes": scenes,
        "timings": _extract_timings(scenes),
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


class Grade0Video0(CurriculumScene):
    GRADE = 0
    VIDEO_ID = "g0_v0"