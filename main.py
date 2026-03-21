from __future__ import annotations

import argparse
import sys

from math_video_factory.build_pipeline import BuildPipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Math Video Factory 단계별 빌드 도구"
    )
    parser.add_argument(
        "--grade",
        type=int,
        required=True,
        help="빌드할 학년 번호 (예: 0, 1)",
    )
    parser.add_argument(
        "--video",
        type=str,
        default=None,
        help="특정 video_id만 빌드할 때 사용 (예: g0_v0, g1_v1)",
    )
    parser.add_argument(
        "--step",
        type=str,
        default="all",
        choices=[
            "script",
            "review",
            "tts",
            "timing",
            "render",
            "final",
            "all",
        ],
        help="실행할 단계 선택",
    )
    parser.add_argument(
        "--limit-scenes",
        type=int,
        default=None,
        help="TTS 생성 시 앞에서부터 일부 장면만 생성할 때 사용",
    )
    parser.add_argument(
        "--scene",
        type=str,
        default=None,
        help="부분 렌더용 장면 ID (렌더러가 지원할 경우 사용)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    pipeline = BuildPipeline()
    outputs = pipeline.build_grade(
        grade=args.grade,
        video_id=args.video,
        step=args.step,
        limit_scenes=args.limit_scenes,
        scene=args.scene,
    )

    print("\n=== BUILD RESULT ===")
    for path in outputs:
        print(path)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[ERROR] {exc}")
        sys.exit(1)