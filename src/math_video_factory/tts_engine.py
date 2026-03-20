from __future__ import annotations

import json
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from .config import TTS_MODEL, TTS_VOICE


def load_script_json(script_path: Path) -> dict:
    """
    저장된 script JSON 파일을 읽는다.
    """
    if not script_path.exists():
        raise FileNotFoundError(f"스크립트 JSON 파일이 없습니다: {script_path}")

    data = json.loads(script_path.read_text(encoding="utf-8"))

    if not isinstance(data, dict):
        raise ValueError(f"스크립트 JSON 형식이 올바르지 않습니다: {script_path}")

    if "scenes" not in data or not isinstance(data["scenes"], list):
        raise ValueError(f"스크립트 JSON에 scenes 리스트가 없습니다: {script_path}")

    return data


def extract_tts_items(script_data: dict) -> list[str]:
    """
    script JSON에서 장면별 TTS 문장을 추출한다.
    비어 있는 문장은 제외한다.
    """
    items: list[str] = []

    for idx, scene in enumerate(script_data["scenes"], start=1):
        if not isinstance(scene, dict):
            raise ValueError(f"scenes[{idx}] 형식이 올바르지 않습니다.")

        tts_text = str(scene.get("tts", "")).strip()
        if tts_text:
            items.append(tts_text)

    if not items:
        raise ValueError("TTS로 생성할 문장이 없습니다.")

    return items


def generate_tts_files(
    script_path: Path,
    output_dir: Path,
    *,
    model: str = TTS_MODEL,
    voice: str = TTS_VOICE,
) -> list[Path]:
    """
    script JSON을 읽어 장면별 mp3 파일을 생성한다.
    반환값은 생성된 mp3 파일 경로 리스트이다.
    """
    load_dotenv()
    client = OpenAI()

    script_data = load_script_json(script_path)
    tts_items = extract_tts_items(script_data)

    output_dir.mkdir(parents=True, exist_ok=True)

    created_files: list[Path] = []

    total = len(tts_items)
    print(f"[INFO] 총 {total}개 장면의 TTS를 생성합니다.")

    for idx, text in enumerate(tts_items, start=1):
        out_path = output_dir / f"{idx:02d}.mp3"

        print(f"[{idx}/{total}] 생성 중: {out_path.name}")
        print(f"  TTS: {text}")

        with client.audio.speech.with_streaming_response.create(
            model=model,
            voice=voice,
            input=text,
        ) as response:
            response.stream_to_file(out_path)

        created_files.append(out_path)

    print(f"[DONE] TTS 생성 완료: {output_dir}")
    return created_files


def remove_old_tts_files(output_dir: Path) -> None:
    """
    기존 mp3 파일을 삭제한다.
    재빌드 시 이전 파일이 섞이지 않게 하기 위함.
    """
    if not output_dir.exists():
        return

    for mp3_file in output_dir.glob("*.mp3"):
        mp3_file.unlink()


def rebuild_tts_files(
    script_path: Path,
    output_dir: Path,
    *,
    model: str = TTS_MODEL,
    voice: str = TTS_VOICE,
) -> list[Path]:
    """
    기존 mp3를 정리하고 새로 TTS를 생성한다.
    """
    remove_old_tts_files(output_dir)
    return generate_tts_files(
        script_path=script_path,
        output_dir=output_dir,
        model=model,
        voice=voice,
    )