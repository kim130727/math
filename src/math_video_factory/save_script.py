from __future__ import annotations

import json
from pathlib import Path

from .models import ScriptSpec


def script_to_dict(script: ScriptSpec) -> dict:
    """
    ScriptSpec 객체를 JSON 저장용 dict로 변환한다.
    """
    return {
        "video_id": script.video_id,
        "title": script.title,
        "grade": script.grade,
        "scenes": [
            {
                "type": scene.type,
                "payload": scene.payload,
                "tts": scene.tts,
            }
            for scene in script.scenes
        ],
    }


def save_script(script: ScriptSpec, out_path: Path) -> None:
    """
    ScriptSpec 객체를 JSON 파일로 저장한다.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    payload = script_to_dict(script)
    out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def save_scripts(scripts: list[ScriptSpec], out_dir: Path) -> list[Path]:
    """
    여러 ScriptSpec 객체를 JSON 파일들로 저장한다.
    반환값은 저장된 파일 경로 리스트이다.
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    saved_paths: list[Path] = []

    for script in scripts:
        out_path = out_dir / f"{script.video_id}.json"
        save_script(script, out_path)
        saved_paths.append(out_path)

    return saved_paths