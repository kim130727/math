from __future__ import annotations

import argparse
import sys

from math_video_factory.build_pipeline import BuildPipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Math Video Factory 빌드 도구"
    )
    parser.add_argument(
        "--grade",
        type=int,
        required=True,
        help="빌드할 학년 번호 (예: 1)",
    )
    parser.add_argument(
        "--video",
        type=str,
        default=None,
        help="특정 video_id만 빌드할 때 사용 (예: g1_v1)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    pipeline = BuildPipeline()
    outputs = pipeline.build_grade(
        grade=args.grade,
        video_id=args.video,
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