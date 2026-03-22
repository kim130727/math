from __future__ import annotations

import argparse
from pathlib import Path

from src.math_video_factory.manim_runner import render_video


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="커리큘럼 기반 수학 영상 렌더러"
    )
    parser.add_argument(
        "--grade",
        type=int,
        required=True,
        help="학년 번호 (예: 0, 1, 2)",
    )
    parser.add_argument(
        "--video",
        type=str,
        required=True,
        help="비디오 ID (예: g0_v0, g1_v2)",
    )
    parser.add_argument(
        "--quality",
        type=str,
        default=None,
        help="렌더 품질 (l, m, h, p, k 또는 low, medium, high, production, 4k)",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="렌더 후 미리보기 실행",
    )
    return parser.parse_args()


def validate_video_id(grade: int, video_id: str) -> None:
    expected_prefix = f"g{grade}_v"
    if not video_id.startswith(expected_prefix):
        raise ValueError(
            f"video_id 형식이 grade와 맞지 않습니다: "
            f"grade={grade}, video_id={video_id!r}, expected_prefix={expected_prefix!r}"
        )


def main() -> None:
    args = parse_args()
    validate_video_id(args.grade, args.video)

    output_path: Path = render_video(
        grade=args.grade,
        video_id=args.video,
        quality=args.quality,
        preview=args.preview,
    )

    print(f"[OK] 렌더링 완료: {output_path}")


if __name__ == "__main__":
    main()