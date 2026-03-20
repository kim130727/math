from __future__ import annotations

import argparse
from pathlib import Path

from src.math_video_factory.build_pipeline import BuildPipeline
from src.math_video_factory.config import CURRICULUM_DIR
from src.math_video_factory.loader import load_curriculum_by_grade


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="초등 수학 커리큘럼 기반 자동 영상 생성기"
    )

    parser.add_argument(
        "--grade",
        type=int,
        help="빌드할 학년 번호 (예: 1, 2, 3, 4, 5, 6)",
    )

    parser.add_argument(
        "--video",
        type=str,
        default=None,
        help="특정 video_id 하나만 빌드 (예: g1_v1)",
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="학년별 등록된 영상 목록만 출력",
    )

    return parser.parse_args()


def list_grade_videos(grade: int) -> None:
    curriculum = load_curriculum_by_grade(CURRICULUM_DIR, grade)

    print(f"\n[{grade}학년] 목표: {curriculum.grade_goal}")
    print("-" * 60)

    for video in curriculum.videos:
        print(f"{video.id} | {video.title} | {video.concept}")

    print("-" * 60)


def main() -> None:
    args = parse_args()

    if args.grade is None:
        raise SystemExit("`--grade` 값을 입력해주세요. 예: uv run main.py --grade 1")

    if args.grade not in {1, 2, 3, 4, 5, 6}:
        raise SystemExit("학년은 1부터 6까지만 입력할 수 있습니다.")

    if args.list:
        list_grade_videos(args.grade)
        return

    project_root = Path(__file__).resolve().parent
    pipeline = BuildPipeline(project_root=project_root)

    built_videos = pipeline.build_grade(
        grade=args.grade,
        video_id=args.video,
    )

    print("\n" + "=" * 60)
    print("[최종 결과]")
    for path in built_videos:
        print(path)
    print("=" * 60)


if __name__ == "__main__":
    main()