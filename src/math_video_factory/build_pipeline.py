from __future__ import annotations

import argparse
from pathlib import Path

from .manim_runner import render_video


PROJECT_ROOT = Path(__file__).resolve().parents[2]


# --------------------------------------------------
# (선택) TTS 생성 훅
# --------------------------------------------------
def run_tts_if_needed(grade: int, video_id: str, enable: bool) -> None:
    if not enable:
        return

    print(f"[INFO] TTS 생성 시작: grade={grade}, video={video_id}")

    # 👉 나중에 연결 (예: make_tts.py)
    # subprocess.run([...])

    print("[INFO] (현재는 TTS 비활성 상태 - TODO)")


# --------------------------------------------------
# (선택) 후처리 훅
# --------------------------------------------------
def post_process_if_needed(grade: int, video_id: str, enable: bool) -> None:
    if not enable:
        return

    print(f"[INFO] 후처리 시작: {video_id}")

    # 👉 나중에 ffmpeg 연결
    # 예: 음성 합치기, 자막, 쇼츠 리사이즈 등

    print("[INFO] (현재는 후처리 비활성 상태 - TODO)")


# --------------------------------------------------
# 메인 파이프라인
# --------------------------------------------------
def build_pipeline(
    *,
    grade: int,
    video_id: str,
    quality: str = "l",
    preview: bool = False,
    tts: bool = False,
    post: bool = False,
) -> int:
    print("=" * 60)
    print("[PIPELINE] START")
    print(f"grade={grade} video={video_id}")
    print("=" * 60)

    # 1. TTS (선택)
    run_tts_if_needed(grade, video_id, tts)

    # 2. Manim 렌더
    print("\n[STEP] Manim 렌더링 시작")
    code = render_video(
        grade=grade,
        video_id=video_id,
        quality=quality,
        preview=preview,
    )

    if code != 0:
        print(f"[ERROR] Manim 렌더 실패 (code={code})")
        return code

    print("[STEP] Manim 렌더 완료")

    # 3. 후처리 (선택)
    post_process_if_needed(grade, video_id, post)

    print("=" * 60)
    print("[PIPELINE] DONE")
    print("=" * 60)

    return 0


# --------------------------------------------------
# CLI
# --------------------------------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build pipeline")

    parser.add_argument("--grade", type=int, required=True)
    parser.add_argument("--video", type=str, required=True)

    parser.add_argument(
        "--quality",
        type=str,
        default="l",
        choices=["l", "m", "h", "p", "k"],
    )

    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--tts", action="store_true")
    parser.add_argument("--post", action="store_true")

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    return build_pipeline(
        grade=args.grade,
        video_id=args.video,
        quality=args.quality,
        preview=args.preview,
        tts=args.tts,
        post=args.post,
    )


if __name__ == "__main__":
    raise SystemExit(main())