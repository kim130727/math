from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

CURRICULUM_DIR = BASE_DIR / "curriculum"
GENERATED_DIR = BASE_DIR / "generated"
SCRIPTS_DIR = GENERATED_DIR / "scripts"
TIMINGS_DIR = GENERATED_DIR / "timings"
VIDEOS_DIR = GENERATED_DIR / "videos"
MANIM_MEDIA_DIR = GENERATED_DIR / "manim_media"


def _get_env_str(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None:
        return default
    return str(value).strip()


def _get_env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or str(raw).strip() == "":
        return default
    try:
        return int(str(raw).strip())
    except ValueError as exc:
        raise ValueError(f"환경변수 {name} 값이 정수가 아닙니다: {raw!r}") from exc


def _get_env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or str(raw).strip() == "":
        return default
    try:
        return float(str(raw).strip())
    except ValueError as exc:
        raise ValueError(f"환경변수 {name} 값이 숫자가 아닙니다: {raw!r}") from exc


def _get_env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default

    value = str(raw).strip().lower()
    if value in {"1", "true", "yes", "y", "on"}:
        return True
    if value in {"0", "false", "no", "n", "off"}:
        return False

    raise ValueError(
        f"환경변수 {name} 값이 bool 형식이 아닙니다: {raw!r} "
        "(allowed: 1/0, true/false, yes/no, on/off)"
    )


# -------------------------------------------------------------------
# 기본 렌더 설정
# -------------------------------------------------------------------
SHORTS_MODE = _get_env_bool("SHORTS_MODE", True)

VIDEO_WIDTH = _get_env_int("VIDEO_WIDTH", 1080)
VIDEO_HEIGHT = _get_env_int("VIDEO_HEIGHT", 1920)

# Manim 내부 좌표계 프레임
FRAME_WIDTH = _get_env_float("FRAME_WIDTH", 9.0)
FRAME_HEIGHT = _get_env_float("FRAME_HEIGHT", 16.0)

# l / m / h / p / k 혹은 -pql / -pqm / -pqh 등도 runner 쪽에서 처리
MANIM_QUALITY = _get_env_str("MANIM_QUALITY", "m")

# manim에서 기본으로 사용할 엔트리 파일/씬 이름
# 현재 구조에서는 runner가 동적으로 처리하므로 기본값만 둠
MANIM_ENTRY_FILE = _get_env_str(
    "MANIM_ENTRY_FILE",
    "src/math_video_factory/manim_entry.py",
)
MANIM_SCENE_NAME = _get_env_str("MANIM_SCENE_NAME", "Grade0Video0")


# -------------------------------------------------------------------
# TTS / 후처리용 확장 설정
# 지금 당장은 필수는 아니지만 이후 파이프라인 확장을 위해 유지
# -------------------------------------------------------------------
OPENAI_API_KEY = _get_env_str("OPENAI_API_KEY", "")
OPENAI_TTS_MODEL = _get_env_str("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
OPENAI_TTS_VOICE = _get_env_str("OPENAI_TTS_VOICE", "alloy")
OPENAI_TTS_FORMAT = _get_env_str("OPENAI_TTS_FORMAT", "mp3")

FFMPEG_VIDEO_CODEC = _get_env_str("FFMPEG_VIDEO_CODEC", "libx264")
FFMPEG_AUDIO_CODEC = _get_env_str("FFMPEG_AUDIO_CODEC", "aac")
FFMPEG_CRF = _get_env_int("FFMPEG_CRF", 23)
FFMPEG_PRESET = _get_env_str("FFMPEG_PRESET", "medium")
FFMPEG_AUDIO_BITRATE = _get_env_str("FFMPEG_AUDIO_BITRATE", "192k")


def ensure_directories() -> None:
    CURRICULUM_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    TIMINGS_DIR.mkdir(parents=True, exist_ok=True)
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    MANIM_MEDIA_DIR.mkdir(parents=True, exist_ok=True)


ensure_directories()