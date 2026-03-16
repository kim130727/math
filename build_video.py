from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from pydub import AudioSegment


PROJECT_DIR = Path(__file__).resolve().parent

SCRIPT_FILE = PROJECT_DIR / "script.txt"
SCENE_FILE = PROJECT_DIR / "why_multiplication.py"
SCENE_NAME = "WhyMultiplication"

MAKE_TTS_FILE = PROJECT_DIR / "make_tts.py"
MEASURE_TTS_FILE = PROJECT_DIR / "measure_tts.py"

TTS_DIR = PROJECT_DIR / "tts_output"
MERGED_AUDIO = PROJECT_DIR / "narration_full.mp3"
FINAL_VIDEO = PROJECT_DIR / "why_multiplication_final.mp4"


def ensure_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"필수 파일이 없습니다: {path}")


def check_ffmpeg() -> None:
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as exc:
        raise RuntimeError(
            "ffmpeg를 찾을 수 없습니다. 시스템 PATH에 ffmpeg가 있어야 합니다."
        ) from exc


def run_step(title: str, cmd: list[str]) -> None:
    print(f"\n=== {title} ===")
    print(" ".join(cmd))
    subprocess.run(cmd, check=True, cwd=PROJECT_DIR)


def load_scene_count(script_file: Path) -> int:
    lines = script_file.read_text(encoding="utf-8").splitlines()

    count = 0
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        count += 1

    if count == 0:
        raise ValueError("script.txt에 장면 데이터가 없습니다.")

    return count


def find_rendered_video(scene_name: str) -> Path:
    candidates = sorted(PROJECT_DIR.glob(f"media/videos/**/{scene_name}.mp4"))
    if not candidates:
        raise FileNotFoundError(
            "Manim 렌더 결과를 찾지 못했습니다. media/videos 아래를 확인하세요."
        )
    return candidates[-1]


def merge_audio(scene_count: int) -> None:
    merged = AudioSegment.empty()

    for idx in range(1, scene_count + 1):
        mp3_path = TTS_DIR / f"{idx:02d}.mp3"
        if not mp3_path.exists():
            raise FileNotFoundError(f"오디오 파일이 없습니다: {mp3_path}")

        audio = AudioSegment.from_mp3(mp3_path)
        merged += audio

    merged.export(MERGED_AUDIO, format="mp3")
    print(f"[DONE] 병합 오디오 생성: {MERGED_AUDIO.name}")


def mux_video_and_audio(video_path: Path, audio_path: Path, output_path: Path) -> None:
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-i",
        str(audio_path),
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-shortest",
        str(output_path),
    ]
    run_step("영상 + 음성 합치기", cmd)


def main() -> None:
    ensure_file(SCRIPT_FILE)
    ensure_file(SCENE_FILE)
    ensure_file(MAKE_TTS_FILE)
    ensure_file(MEASURE_TTS_FILE)
    check_ffmpeg()

    scene_count = load_scene_count(SCRIPT_FILE)

    run_step("TTS 생성", [sys.executable, str(MAKE_TTS_FILE)])
    run_step("TTS 길이 측정", [sys.executable, str(MEASURE_TTS_FILE)])

    run_step(
        "Manim 렌더",
        [
            sys.executable,
            "-m",
            "manim",
            "-pqh",
            str(SCENE_FILE),
            SCENE_NAME,
        ],
    )

    rendered_video = find_rendered_video(SCENE_NAME)
    merge_audio(scene_count)
    mux_video_and_audio(rendered_video, MERGED_AUDIO, FINAL_VIDEO)

    print(f"\n[SUCCESS] 최종 영상 생성 완료: {FINAL_VIDEO}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[ERROR] {exc}")
        sys.exit(1)