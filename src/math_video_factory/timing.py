from __future__ import annotations

import json
from pathlib import Path

from mutagen.mp3 import MP3


def list_scene_mp3_files(tts_dir: Path) -> list[Path]:
    if not tts_dir.exists():
        raise FileNotFoundError(f"TTS 폴더가 없습니다: {tts_dir}")

    files = sorted(
        p for p in tts_dir.glob("*.mp3")
        if not p.name.endswith("_merged.mp3")
    )

    if not files:
        raise FileNotFoundError(f"측정할 mp3 파일이 없습니다: {tts_dir}")

    return files


def measure_mp3_durations(tts_dir: Path) -> list[float]:
    durations: list[float] = []

    for mp3_path in list_scene_mp3_files(tts_dir):
        audio = MP3(mp3_path)
        durations.append(round(float(audio.info.length), 3))

    return durations


def measure_and_save_timings(
    video_id: str,
    tts_dir: Path,
    out_path: Path,
) -> Path:
    durations = measure_mp3_durations(tts_dir)

    payload = {
        "video_id": video_id,
        "durations": durations,
        "scene_count": len(durations),
        "total_duration": round(sum(durations), 3),
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"[DONE] timings 저장 완료: {out_path}")
    return out_path