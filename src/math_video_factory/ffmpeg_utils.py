from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from pydub import AudioSegment

from .config import PROJECT_ROOT


def check_ffmpeg_available() -> None:
    """
    ffmpeg 실행 가능 여부 확인
    """
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "ffmpeg를 찾을 수 없습니다. 시스템 PATH에 ffmpeg가 있어야 합니다."
        )


def list_mp3_files(audio_dir: Path) -> list[Path]:
    if not audio_dir.exists():
        raise FileNotFoundError(f"오디오 폴더가 없습니다: {audio_dir}")

    mp3_files = sorted(
        p for p in audio_dir.glob("*.mp3")
        if not p.name.endswith("_merged.mp3")
    )

    if not mp3_files:
        raise FileNotFoundError(f"mp3 파일이 없습니다: {audio_dir}")

    return mp3_files


def merge_mp3_files(audio_dir: Path, merged_output_path: Path) -> Path:
    """
    장면별 mp3 파일을 하나의 mp3 파일로 병합한다.
    """
    check_ffmpeg_available()

    mp3_files = list_mp3_files(audio_dir)

    merged = AudioSegment.empty()
    for mp3_path in mp3_files:
        merged += AudioSegment.from_mp3(mp3_path)

    merged_output_path.parent.mkdir(parents=True, exist_ok=True)
    merged.export(merged_output_path, format="mp3")

    print(f"[DONE] 병합 오디오 생성: {merged_output_path}")
    return merged_output_path


def mux_video_and_audio(
    video_path: Path,
    audio_path: Path,
    output_path: Path,
) -> Path:
    """
    영상(mp4)과 오디오(mp3)를 합쳐 최종 mp4를 생성한다.
    """
    check_ffmpeg_available()

    if not video_path.exists():
        raise FileNotFoundError(f"영상 파일이 없습니다: {video_path}")

    if not audio_path.exists():
        raise FileNotFoundError(f"오디오 파일이 없습니다: {audio_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

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

    print("\n=== 영상 + 음성 합치기 ===")
    print(" ".join(cmd))

    subprocess.run(
        cmd,
        check=True,
        cwd=PROJECT_ROOT,
    )

    print(f"[DONE] 최종 영상 생성: {output_path}")
    return output_path


def build_final_video(
    render_video_path: Path,
    tts_audio_dir: Path,
    merged_audio_path: Path,
    final_video_path: Path,
) -> Path:
    """
    장면별 TTS 병합 + 렌더 영상 합성까지 한 번에 수행
    """
    merged_audio = merge_mp3_files(tts_audio_dir, merged_audio_path)
    return mux_video_and_audio(render_video_path, merged_audio, final_video_path)