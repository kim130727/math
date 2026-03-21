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

MANIM_QUALITY = os.getenv("MANIM_QUALITY", "-pqh")

MANIM_ENTRY_FILE = PROJECT_ROOT / "src" / "math_video_factory" / "manim_entry.py"
MANIM_SCENE_NAME = "AutoVideoScene"

TTS_MODEL = os.getenv("TTS_MODEL", "gpt-4o-mini-tts")
TTS_VOICE = os.getenv("TTS_VOICE", "alloy")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

DEFAULT_FONT = os.getenv("DEFAULT_FONT", "Malgun Gothic")


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
    실행 전 필수 환경변수를 검증한다.
    """
    if require_tts and not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY가 설정되지 않았습니다.\n"
            "프로젝트 루트의 .env 파일에 아래처럼 추가하세요.\n\n"
            "OPENAI_API_KEY=your_api_key_here"
        )