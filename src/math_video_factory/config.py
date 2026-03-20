from __future__ import annotations

from pathlib import Path


# =========================================
# 기본 경로 설정
# =========================================

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


# =========================================
# Manim 설정
# =========================================

MANIM_QUALITY = "-pqh"  # preview + high quality

MANIM_ENTRY_FILE = (
    PROJECT_ROOT
    / "src"
    / "math_video_factory"
    / "manim_entry.py"
)

MANIM_SCENE_NAME = "AutoVideoScene"


# =========================================
# TTS 설정
# =========================================

TTS_MODEL = "gpt-4o-mini-tts"
TTS_VOICE = "alloy"


# =========================================
# 기본 폰트 설정
# =========================================

DEFAULT_FONT = "Malgun Gothic"


# =========================================
# 디렉토리 생성
# =========================================

def ensure_directories() -> None:
    """
    필요한 폴더 자동 생성
    """
    for path in [
        GENERATED_DIR,
        SCRIPTS_DIR,
        TTS_DIR,
        TIMINGS_DIR,
        RENDERS_DIR,
        VIDEOS_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)