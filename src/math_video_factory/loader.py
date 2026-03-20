from __future__ import annotations

from pathlib import Path

import yaml

from .models import ExampleSpec, GradeCurriculum, VideoSpec


def _validate_required_keys(raw: dict, required_keys: list[str], context: str) -> None:
    missing = [key for key in required_keys if key not in raw]
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"{context} 에 필수 키가 없습니다: {joined}")


def load_curriculum(path: Path) -> GradeCurriculum:
    """
    YAML 커리큘럼 파일을 읽어서 GradeCurriculum 객체로 변환한다.
    """
    if not path.exists():
        raise FileNotFoundError(f"커리큘럼 파일이 없습니다: {path}")

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))

    if not isinstance(raw, dict):
        raise ValueError(f"커리큘럼 파일 형식이 올바르지 않습니다: {path}")

    _validate_required_keys(
        raw,
        ["grade", "grade_goal", "videos"],
        f"커리큘럼 파일 {path.name}",
    )

    grade = raw["grade"]
    grade_goal = raw["grade_goal"]
    videos_raw = raw["videos"]

    if not isinstance(videos_raw, list):
        raise ValueError(f"{path.name} 의 videos 는 리스트여야 합니다.")

    videos: list[VideoSpec] = []

    for idx, item in enumerate(videos_raw, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"{path.name} 의 videos[{idx}] 는 객체여야 합니다.")

        _validate_required_keys(
            item,
            [
                "id",
                "title",
                "concept",
                "abstraction_stage",
                "key_understanding",
                "example",
                "visual_model",
                "conclusion",
            ],
            f"{path.name} 의 videos[{idx}]",
        )

        example_raw = item["example"]
        if not isinstance(example_raw, dict):
            raise ValueError(f"{path.name} 의 videos[{idx}].example 은 객체여야 합니다.")

        if "type" not in example_raw:
            raise ValueError(f"{path.name} 의 videos[{idx}].example 에 type 이 필요합니다.")

        keywords = item.get("keywords", [])
        if keywords is None:
            keywords = []
        if not isinstance(keywords, list):
            raise ValueError(f"{path.name} 의 videos[{idx}].keywords 는 리스트여야 합니다.")

        narration_style = item.get("narration_style", "초등 친화적")

        videos.append(
            VideoSpec(
                id=str(item["id"]),
                title=str(item["title"]),
                concept=str(item["concept"]),
                abstraction_stage=str(item["abstraction_stage"]),
                key_understanding=str(item["key_understanding"]),
                keywords=[str(x) for x in keywords],
                example=ExampleSpec(
                    type=str(example_raw["type"]),
                    data={
                        str(k): v
                        for k, v in example_raw.items()
                        if k != "type"
                    },
                ),
                visual_model=str(item["visual_model"]),
                narration_style=str(narration_style),
                conclusion=str(item["conclusion"]),
            )
        )

    return GradeCurriculum(
        grade=int(grade),
        grade_goal=str(grade_goal),
        videos=videos,
    )


def load_curriculum_by_grade(curriculum_dir: Path, grade: int) -> GradeCurriculum:
    """
    학년 번호로 curriculum/grade_{n}.yaml 파일을 읽는다.
    """
    path = curriculum_dir / f"grade_{grade}.yaml"
    return load_curriculum(path)