from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CURRICULUM_DIR = PROJECT_ROOT / "curriculum"
GENERATED_DIR = PROJECT_ROOT / "generated"

SCRIPTS_DIR = GENERATED_DIR / "scripts"
TTS_DIR = GENERATED_DIR / "tts"
TIMINGS_DIR = GENERATED_DIR / "timings"
RENDERS_DIR = GENERATED_DIR / "renders"
VIDEOS_DIR = GENERATED_DIR / "videos"

ASSETS_DIR = PROJECT_ROOT / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"

# -------------------------------------------------------------------
# Manim runtime
# -------------------------------------------------------------------
MANIM_QUALITY = os.getenv("MANIM_QUALITY", "-pqh").strip()
MANIM_ENTRY_FILE = PROJECT_ROOT / "src" / "math_video_factory" / "manim_entry.py"
MANIM_SCENE_NAME = "AutoVideoScene"

# -------------------------------------------------------------------
# TTS runtime
# -------------------------------------------------------------------
TTS_MODEL = os.getenv("TTS_MODEL", "gpt-4o-mini-tts").strip()
TTS_VOICE = os.getenv("TTS_VOICE", "alloy").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

# -------------------------------------------------------------------
# Visual / font
# -------------------------------------------------------------------
DEFAULT_FONT = os.getenv("DEFAULT_FONT", "Malgun Gothic").strip()

# -------------------------------------------------------------------
# Shorts mode
# -------------------------------------------------------------------
SHORTS_MODE = os.getenv("SHORTS_MODE", "true").strip().lower() in {
    "1",
    "true",
    "yes",
    "y",
    "on",
}

VIDEO_WIDTH = int(os.getenv("VIDEO_WIDTH", "1080").strip())
VIDEO_HEIGHT = int(os.getenv("VIDEO_HEIGHT", "1920").strip())
FRAME_WIDTH = float(os.getenv("FRAME_WIDTH", "9").strip())
FRAME_HEIGHT = float(os.getenv("FRAME_HEIGHT", "16").strip())
FRAME_RATE = int(os.getenv("FRAME_RATE", "30").strip())
SHORTS_MAX_DURATION = float(os.getenv("SHORTS_MAX_DURATION", "55").strip())

# -------------------------------------------------------------------
# ffmpeg encoding
# -------------------------------------------------------------------
FFMPEG_CRF = int(os.getenv("FFMPEG_CRF", "23").strip())
FFMPEG_PRESET = os.getenv("FFMPEG_PRESET", "medium").strip()
FFMPEG_AUDIO_BITRATE = os.getenv("FFMPEG_AUDIO_BITRATE", "128k").strip()

# -------------------------------------------------------------------
# 기타 옵션
# -------------------------------------------------------------------
DEBUG = os.getenv("DEBUG", "false").strip().lower() in {
    "1",
    "true",
    "yes",
    "y",
    "on",
}


def ensure_directories() -> None:
    for path in [
        GENERATED_DIR,
        SCRIPTS_DIR,
        TTS_DIR,
        TIMINGS_DIR,
        RENDERS_DIR,
        VIDEOS_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)


def validate_runtime_config(*, require_tts: bool = True) -> None:
    """
    실행 전 필수 설정을 검증한다.
    """
    if require_tts and not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY가 설정되지 않았습니다.\n"
            "프로젝트 루트의 .env 파일에 아래처럼 추가하세요.\n\n"
            "OPENAI_API_KEY=your_api_key_here"
        )

    if VIDEO_WIDTH <= 0 or VIDEO_HEIGHT <= 0:
        raise RuntimeError("VIDEO_WIDTH, VIDEO_HEIGHT는 0보다 커야 합니다.")

    if FRAME_WIDTH <= 0 or FRAME_HEIGHT <= 0:
        raise RuntimeError("FRAME_WIDTH, FRAME_HEIGHT는 0보다 커야 합니다.")

    if FRAME_RATE <= 0:
        raise RuntimeError("FRAME_RATE는 0보다 커야 합니다.")

    if SHORTS_MAX_DURATION <= 0:
        raise RuntimeError("SHORTS_MAX_DURATION은 0보다 커야 합니다.")

    allowed_presets = {
        "ultrafast",
        "superfast",
        "veryfast",
        "faster",
        "fast",
        "medium",
        "slow",
        "slower",
        "veryslow",
    }
    if FFMPEG_PRESET not in allowed_presets:
        raise RuntimeError(
            "FFMPEG_PRESET 값이 올바르지 않습니다. "
            f"현재값: {FFMPEG_PRESET}"
        )