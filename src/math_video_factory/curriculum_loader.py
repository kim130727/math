from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import ExampleSpec, GradeCurriculum, VideoSpec


def _read_yaml_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"커리큘럼 파일이 없습니다: {path}")

    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(
            f"커리큘럼 파일 인코딩이 올바르지 않습니다. UTF-8로 저장해 주세요: {path}"
        ) from exc

    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise ValueError(f"YAML 파싱 오류가 발생했습니다: {path}") from exc

    if data is None:
        raise ValueError(f"커리큘럼 파일이 비어 있습니다: {path}")

    if not isinstance(data, dict):
        raise ValueError(f"커리큘럼 파일 최상위는 dict여야 합니다: {path}")

    return data


def _ensure_dict(value: Any, *, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} 항목은 dict 형식이어야 합니다.")
    return value


def _ensure_list(value: Any, *, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{label} 항목은 list 형식이어야 합니다.")
    return value


def _to_str(value: Any, *, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def _to_int(value: Any, *, label: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} 값은 정수여야 합니다: {value!r}") from exc


def _normalize_keywords(value: Any) -> list[str]:
    if value is None:
        return []

    if not isinstance(value, list):
        raise ValueError("keywords 항목은 list 형식이어야 합니다.")

    result: list[str] = []
    for i, item in enumerate(value):
        text = _to_str(item)
        if not text:
            raise ValueError(f"keywords[{i}] 값이 비어 있습니다.")
        result.append(text)
    return result


def _normalize_example(raw: Any, *, video_label: str) -> ExampleSpec:
    if raw is None:
        return ExampleSpec()

    example_dict = _ensure_dict(raw, label=f"{video_label}.example")
    example_type = _to_str(example_dict.get("type"))

    if not example_type:
        raise ValueError(f"{video_label}.example.type 값이 필요합니다.")

    data = {k: v for k, v in example_dict.items() if k != "type"}

    # 자주 쓰는 타입은 최소 검증만 추가
    if example_type == "repeated_addition":
        if "addend" not in data or "count" not in data:
            raise ValueError(
                f"{video_label}.example 은 repeated_addition 타입이므로 "
                "addend, count 값이 필요합니다."
            )
        data["addend"] = _to_int(data["addend"], label=f"{video_label}.example.addend")
        data["count"] = _to_int(data["count"], label=f"{video_label}.example.count")

    elif example_type == "division_grouping":
        if "total" not in data or "group_size" not in data:
            raise ValueError(
                f"{video_label}.example 은 division_grouping 타입이므로 "
                "total, group_size 값이 필요합니다."
            )
        data["total"] = _to_int(data["total"], label=f"{video_label}.example.total")
        data["group_size"] = _to_int(
            data["group_size"],
            label=f"{video_label}.example.group_size",
        )

    elif example_type == "counting_objects":
        if "count" in data:
            data["count"] = _to_int(data["count"], label=f"{video_label}.example.count")
        if "item" in data:
            data["item"] = _to_str(data["item"])

    elif example_type == "place_value":
        if "number" not in data:
            raise ValueError(
                f"{video_label}.example 은 place_value 타입이므로 number 값이 필요합니다."
            )
        data["number"] = _to_int(data["number"], label=f"{video_label}.example.number")

    elif example_type == "fraction_half":
        if "item" in data:
            data["item"] = _to_str(data["item"])

    elif example_type == "measurement":
        if "subject" in data:
            data["subject"] = _to_str(data["subject"])

    elif example_type == "pattern_growth":
        if "pattern" in data:
            data["pattern"] = _to_str(data["pattern"])
        if "rule_text" in data:
            data["rule_text"] = _to_str(data["rule_text"])

    elif example_type == "average":
        scores = data.get("scores", [])
        if not isinstance(scores, list):
            raise ValueError(f"{video_label}.example.scores 항목은 list 형식이어야 합니다.")
        data["scores"] = [_to_int(x, label=f"{video_label}.example.scores") for x in scores]

    elif example_type == "ratio":
        if "left" in data:
            data["left"] = _to_int(data["left"], label=f"{video_label}.example.left")
        if "right" in data:
            data["right"] = _to_int(data["right"], label=f"{video_label}.example.right")

    return ExampleSpec(
        type=example_type,
        data=data,
    )


def _normalize_video(raw: Any, *, index: int) -> VideoSpec:
    video = _ensure_dict(raw, label=f"videos[{index}]")
    video_label = f"videos[{index}]"

    video_id = _to_str(video.get("id"))
    if not video_id:
        raise ValueError(f"{video_label}.id 값이 필요합니다.")

    title = _to_str(video.get("title"))
    if not title:
        raise ValueError(f"{video_label}.title 값이 필요합니다.")

    concept = _to_str(video.get("concept"))
    if not concept:
        raise ValueError(f"{video_label}.concept 값이 필요합니다.")

    abstraction_stage = _to_str(video.get("abstraction_stage"))
    if not abstraction_stage:
        raise ValueError(f"{video_label}.abstraction_stage 값이 필요합니다.")

    key_understanding = _to_str(video.get("key_understanding"))
    if not key_understanding:
        raise ValueError(f"{video_label}.key_understanding 값이 필요합니다.")

    keywords = _normalize_keywords(video.get("keywords", []))
    example = _normalize_example(video.get("example"), video_label=video_label)

    return VideoSpec(
        id=video_id,
        title=title,
        concept=concept,
        abstraction_stage=abstraction_stage,
        key_understanding=key_understanding,
        keywords=keywords,
        example=example,
        visual_model=_to_str(video.get("visual_model")),
        narration_style=_to_str(video.get("narration_style"), default="초등 친화적"),
        conclusion=_to_str(video.get("conclusion")),
    )


def load_curriculum(path: Path) -> GradeCurriculum:
    root = _read_yaml_file(path)

    if "grade" not in root:
        raise ValueError(f"grade 값이 없습니다: {path}")
    if "grade_goal" not in root:
        raise ValueError(f"grade_goal 값이 없습니다: {path}")
    if "videos" not in root:
        raise ValueError(f"videos 값이 없습니다: {path}")

    grade = _to_int(root.get("grade"), label="grade")
    grade_goal = _to_str(root.get("grade_goal"))
    if not grade_goal:
        raise ValueError(f"grade_goal 값이 비어 있습니다: {path}")

    videos_raw = _ensure_list(root.get("videos"), label="videos")
    videos = [_normalize_video(item, index=i) for i, item in enumerate(videos_raw)]

    seen_ids: set[str] = set()
    for video in videos:
        if video.id in seen_ids:
            raise ValueError(f"중복된 video id가 있습니다: {video.id}")
        seen_ids.add(video.id)

    return GradeCurriculum(
        grade=grade,
        grade_goal=grade_goal,
        videos=videos,
    )


def load_curriculum_by_grade(curriculum_dir: Path, grade: int) -> GradeCurriculum:
    path = curriculum_dir / f"grade_{grade}.yaml"
    curriculum = load_curriculum(path)

    if curriculum.grade != int(grade):
        raise ValueError(
            f"파일의 grade 값({curriculum.grade})과 요청한 grade 값({grade})이 다릅니다: {path}"
        )

    return curriculum