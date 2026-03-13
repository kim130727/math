from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
SCENE_FILE = PROJECT_DIR / "why_multiplication.py"
SCENE_NAME = "WhyMultiplication"

MAKE_TTS_FILE = PROJECT_DIR / "make_tts.py"
MEASURE_TTS_FILE = PROJECT_DIR / "measure_tts.py"

TTS_DIR = PROJECT_DIR / "tts_output"
TIMINGS_JSON = PROJECT_DIR / "timings.json"
MERGED_AUDIO = PROJECT_DIR / "narration_full.mp3"
FINAL_VIDEO = PROJECT_DIR / "why_multiplication_final.mp4"

QUALITY = "qh"   # ql / qm / qh / qk


ORDER = [
    "01_title",
    "02_question",
    "03_no_multiply",
    "04_repeat_add_intro",
    "05_repeat_add_count",
    "06_inconvenient",
    "07_multiplication_meaning",
    "08_short_expression",
    "09_grid_intro",
    "10_grid_explain",
    "11_grid_concept",
    "12_conclusion",
    "13_formula_wrapup",
    "14_final",
]


def run_cmd(cmd: list[str], title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)
    print(" ".join(cmd))
    result = subprocess.run(cmd, cwd=PROJECT_DIR)
    if result.returncode != 0:
        raise SystemExit(f"\n실패: {title}")


def ensure_file(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"{label} 파일이 없습니다: {path}")


def check_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        raise SystemExit(
            "ffmpeg가 설치되어 있지 않습니다.\n"
            "Windows라면 예: winget install ffmpeg"
        )


def merge_mp3_with_pydub() -> None:
    try:
        from pydub import AudioSegment
    except ImportError as exc:
        raise SystemExit(
            "pydub가 설치되어 있지 않습니다.\n"
            "설치: uv add pydub"
        ) from exc

    if not TTS_DIR.exists():
        raise FileNotFoundError(f"tts_output 폴더가 없습니다: {TTS_DIR}")

    audio = AudioSegment.silent(duration=0)

    for name in ORDER:
        mp3_path = TTS_DIR / f"{name}.mp3"
        if not mp3_path.exists():
            raise FileNotFoundError(f"누락된 mp3: {mp3_path.name}")
        audio += AudioSegment.from_mp3(mp3_path)

    audio.export(MERGED_AUDIO, format="mp3")
    print(f"\n오디오 병합 완료: {MERGED_AUDIO}")


def find_rendered_video() -> Path:
    media_dir = PROJECT_DIR / "media"
    if not media_dir.exists():
        raise FileNotFoundError("media 폴더가 없습니다. Manim 렌더가 실패했을 수 있습니다.")

    candidates = sorted(
        media_dir.rglob(f"{SCENE_NAME}.mp4"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not candidates:
        raise FileNotFoundError(f"{SCENE_NAME}.mp4 를 media 폴더에서 찾지 못했습니다.")

    return candidates[0]


def mux_video_and_audio(video_path: Path, audio_path: Path, output_path: Path) -> None:
    check_ffmpeg()

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        str(output_path),
    ]
    run_cmd(cmd, "5단계: 영상 + 음성 합치기")


def main() -> None:
    ensure_file(SCENE_FILE, "Manim")
    ensure_file(MAKE_TTS_FILE, "make_tts.py")
    ensure_file(MEASURE_TTS_FILE, "measure_tts.py")

    # 1. TTS 생성
    run_cmd([sys.executable, str(MAKE_TTS_FILE)], "1단계: TTS 생성")

    # 2. 음성 길이 측정 → timings.json
    run_cmd([sys.executable, str(MEASURE_TTS_FILE)], "2단계: 음성 길이 측정")

    ensure_file(TIMINGS_JSON, "timings.json")

    # 3. timings.json 반영된 Manim 렌더
    run_cmd(
        [sys.executable, "-m", "manim", "render", f"-{QUALITY}", str(SCENE_FILE), SCENE_NAME],
        "3단계: Manim 영상 렌더",
    )

    rendered_video = find_rendered_video()
    print(f"\n렌더 영상 발견: {rendered_video}")

    # 4. mp3 병합
    print("\n" + "=" * 70)
    print("4단계: mp3 병합")
    print("=" * 70)
    merge_mp3_with_pydub()

    ensure_file(MERGED_AUDIO, "병합 음성")

    # 5. 영상 + 음성 합치기
    mux_video_and_audio(rendered_video, MERGED_AUDIO, FINAL_VIDEO)

    print("\n" + "=" * 70)
    print("완료")
    print("=" * 70)
    print(f"최종 영상: {FINAL_VIDEO}")


if __name__ == "__main__":
    main()