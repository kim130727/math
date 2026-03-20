from __future__ import annotations

import json
import sys
from pathlib import Path

from mutagen.mp3 import MP3


PROJECT_DIR = Path(__file__).resolve().parent
SCRIPT_FILE = PROJECT_DIR / "script.txt"
TTS_DIR = PROJECT_DIR / "tts_output"
TIMINGS_FILE = PROJECT_DIR / "timings.json"


def load_scene_count(script_file: Path) -> int:
    if not script_file.exists():
        raise FileNotFoundError(f"스크립트 파일이 없습니다: {script_file}")

    count = 0
    lines = script_file.read_text(encoding="utf-8").splitlines()

    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        count += 1

    if count == 0:
        raise ValueError("script.txt에 장면 데이터가 없습니다.")

    return count


def measure_tts() -> None:
    scene_count = load_scene_count(SCRIPT_FILE)

    durations: list[float] = []
    missing: list[str] = []

    for idx in range(1, scene_count + 1):
        mp3_path = TTS_DIR / f"{idx:02d}.mp3"

        if not mp3_path.exists():
            missing.append(mp3_path.name)
            continue

        audio = MP3(mp3_path)
        durations.append(round(float(audio.info.length), 3))

    if missing:
        raise FileNotFoundError("다음 mp3 파일이 없습니다: " + ", ".join(missing))

    payload = {"durations": durations}

    TIMINGS_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("[DONE] timings.json 생성 완료")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        measure_tts()
    except Exception as exc:
        print(f"[ERROR] {exc}")
        sys.exit(1)