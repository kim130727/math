from __future__ import annotations

import subprocess
from pathlib import Path

from pydub import AudioSegment

from . import config as app_config


def _get_setting(name: str, default):
    return getattr(app_config, name, default)


def _ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _collect_scene_mp3_files(tts_audio_dir: Path) -> list[Path]:
    if not tts_audio_dir.exists():
        raise FileNotFoundError(f"TTS 디렉터리가 없습니다: {tts_audio_dir}")

    mp3_files = sorted(
        [
            path
            for path in tts_audio_dir.glob("*.mp3")
            if not path.name.endswith("_merged.mp3")
        ]
    )

    if not mp3_files:
        raise FileNotFoundError(
            f"TTS mp3 파일을 찾지 못했습니다: {tts_audio_dir}"
        )

    return mp3_files


def merge_tts_audio(
    *,
    tts_audio_dir: Path,
    merged_audio_path: Path,
    ) -> Path:

    mp3_files = _collect_scene_mp3_files(tts_audio_dir)
    _ensure_parent_dir(merged_audio_path)

    merged = AudioSegment.empty()

    GAP_MS = int(_get_setting("TTS_GAP_MS", 500))  # ← 추가

    for mp3_file in mp3_files:
        audio = AudioSegment.from_file(mp3_file, format="mp3")
        merged += audio

        # ← 추가
        silence = AudioSegment.silent(duration=GAP_MS)
        merged += silence

    merged.export(merged_audio_path, format="mp3")
    print(f"[DONE] 병합 오디오 생성: {merged_audio_path}")

    return merged_audio_path


def get_audio_duration_seconds(audio_path: Path) -> float:
    if not audio_path.exists():
        raise FileNotFoundError(f"오디오 파일이 없습니다: {audio_path}")

    audio = AudioSegment.from_file(audio_path)
    return float(len(audio) / 1000.0)


def _build_ffmpeg_command(
    *,
    render_video_path: Path,
    merged_audio_path: Path,
    final_video_path: Path,
) -> list[str]:
    shorts_mode = bool(_get_setting("SHORTS_MODE", True))
    video_width = int(_get_setting("VIDEO_WIDTH", 1080))
    video_height = int(_get_setting("VIDEO_HEIGHT", 1920))
    frame_rate = int(_get_setting("FRAME_RATE", 30))
    max_duration = float(_get_setting("SHORTS_MAX_DURATION", 55))
    crf = int(_get_setting("FFMPEG_CRF", 23))
    preset = str(_get_setting("FFMPEG_PRESET", "medium"))
    audio_bitrate = str(_get_setting("FFMPEG_AUDIO_BITRATE", "128k"))

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(render_video_path),
        "-i",
        str(merged_audio_path),
    ]

    if shorts_mode:
        vf = (
            f"scale={video_width}:{video_height}:force_original_aspect_ratio=decrease,"
            f"pad={video_width}:{video_height}:(ow-iw)/2:(oh-ih)/2"
        )
        cmd.extend(["-vf", vf, "-t", str(max_duration)])
    else:
        cmd.extend(["-shortest"])

    cmd.extend(
        [
            "-c:v",
            "libx264",
            "-preset",
            preset,
            "-crf",
            str(crf),
            "-pix_fmt",
            "yuv420p",
            "-r",
            str(frame_rate),
            "-c:a",
            "aac",
            "-b:a",
            audio_bitrate,
            "-ar",
            "48000",
            "-movflags",
            "+faststart",
            str(final_video_path),
        ]
    )

    return cmd


def mux_video_and_audio(
    *,
    render_video_path: Path,
    merged_audio_path: Path,
    final_video_path: Path,
) -> Path:
    """
    렌더된 무음 mp4와 병합된 mp3를 합쳐 최종 mp4를 만든다.
    쇼츠 모드일 때는 9:16 규격과 최대 길이를 강제한다.
    """
    if not render_video_path.exists():
        raise FileNotFoundError(f"렌더 영상이 없습니다: {render_video_path}")

    if not merged_audio_path.exists():
        raise FileNotFoundError(f"병합 오디오가 없습니다: {merged_audio_path}")

    _ensure_parent_dir(final_video_path)

    cmd = _build_ffmpeg_command(
        render_video_path=render_video_path,
        merged_audio_path=merged_audio_path,
        final_video_path=final_video_path,
    )

    print("[FFMPEG CMD]")
    print(" ".join(cmd))

    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "ffmpeg 명령을 찾을 수 없습니다. 시스템 PATH에 ffmpeg가 있어야 합니다."
        ) from exc
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.strip() if exc.stderr else str(exc)
        raise RuntimeError(f"ffmpeg 최종 합성에 실패했습니다.\n{message}") from exc

    print(f"[DONE] 최종 영상 생성: {final_video_path}")
    return final_video_path


def build_final_video(
    *,
    render_video_path: Path,
    tts_audio_dir: Path,
    merged_audio_path: Path,
    final_video_path: Path,
) -> Path:
    """
    1) 장면별 mp3 병합
    2) 렌더 영상 + 병합 오디오 mux
    """
    merge_tts_audio(
        tts_audio_dir=tts_audio_dir,
        merged_audio_path=merged_audio_path,
    )

    return mux_video_and_audio(
        render_video_path=render_video_path,
        merged_audio_path=merged_audio_path,
        final_video_path=final_video_path,
    )