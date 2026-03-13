from __future__ import annotations

import json
from pathlib import Path
from mutagen.mp3 import MP3

AUDIO_DIR = Path("tts_output")
OUTPUT_JSON = Path("timings.json")

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


def get_mp3_duration_seconds(path: Path) -> float:
    audio = MP3(path)
    return float(audio.info.length)


def main() -> None:
    if not AUDIO_DIR.exists():
        raise FileNotFoundError(f"오디오 폴더가 없습니다: {AUDIO_DIR.resolve()}")

    timings: dict[str, float] = {}
    missing_files: list[str] = []

    print(f"오디오 폴더: {AUDIO_DIR.resolve()}")
    print("-" * 50)

    total_duration = 0.0

    for name in ORDER:
        mp3_path = AUDIO_DIR / f"{name}.mp3"

        if not mp3_path.exists():
            missing_files.append(mp3_path.name)
            print(f"[누락] {mp3_path.name}")
            continue

        duration = round(get_mp3_duration_seconds(mp3_path), 2)
        timings[name] = duration
        total_duration += duration

        print(f"{mp3_path.name:<32} {duration:>6.2f} sec")

    print("-" * 50)
    print(f"총 길이: {total_duration:.2f} sec")

    OUTPUT_JSON.write_text(
        json.dumps(timings, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"저장 완료: {OUTPUT_JSON.resolve()}")

    if missing_files:
        print("\n누락된 파일:")
        for filename in missing_files:
            print(f" - {filename}")


if __name__ == "__main__":
    main()