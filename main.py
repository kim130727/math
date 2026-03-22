from __future__ import annotations

import argparse

from src.math_video_factory.manim_runner import render_video


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Math video factory runner")
    parser.add_argument("--grade", type=int, required=True, help="학년 번호")
    parser.add_argument("--video", type=str, required=True, help="영상 ID 예: g0_v0")
    parser.add_argument(
        "--quality",
        type=str,
        default="l",
        choices=["l", "m", "h", "p", "k"],
        help="Manim 품질 (l/m/h/p/k)",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="렌더 후 자동 미리보기",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return render_video(
        grade=args.grade,
        video_id=args.video,
        quality=args.quality,
        preview=args.preview,
    )


if __name__ == "__main__":
    raise SystemExit(main())