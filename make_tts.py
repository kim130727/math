from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


PROJECT_DIR = Path(__file__).resolve().parent
SCRIPT_FILE = PROJECT_DIR / "script.txt"
OUTPUT_DIR = PROJECT_DIR / "tts_output"

MODEL = "gpt-4o-mini-tts"
VOICE = "alloy"


def load_script(script_file: Path) -> list[dict]:
    if not script_file.exists():
        raise FileNotFoundError(f"스크립트 파일이 없습니다: {script_file}")

    scenes: list[dict] = []

    lines = script_file.read_text(encoding="utf-8").splitlines()
    for line_no, raw in enumerate(lines, start=1):
        line = raw.strip()

        if not line or line.startswith("#"):
            continue

        parts = [p.strip() for p in line.split("|")]
        scene_type = parts[0].lower()

        scenes.append(
            {
                "line_no": line_no,
                "type": scene_type,
                "parts": parts[1:],
                "raw": raw,
            }
        )

    if not scenes:
        raise ValueError("script.txt에 장면 데이터가 없습니다.")

    return scenes


def tts_text_for_scene(scene: dict) -> str:
    scene_type = scene["type"]
    parts = scene["parts"]

    if scene_type == "title":
        if len(parts) < 2:
            raise ValueError("title 장면은 'title|제목|부제' 형식이어야 합니다.")
        return f"{parts[0]}. {parts[1]}"

    if scene_type == "question":
        if len(parts) < 2:
            raise ValueError("question 장면은 'question|수식|질문문장' 형식이어야 합니다.")
        return parts[1]

    if scene_type == "explain":
        if len(parts) < 3:
            raise ValueError(
                "explain 장면은 'explain|윗문장|아랫문장|반복덧셈수식' 형식이어야 합니다."
            )
        return f"{parts[0]}. {parts[1]}."

    if scene_type == "count_add":
        if len(parts) < 2:
            raise ValueError("count_add 장면은 'count_add|더하는수|몇번' 형식이어야 합니다.")
        addend = parts[0]
        count = parts[1]
        return f"{addend}을 {count}번 더해 볼까요?"

    if scene_type == "highlight":
        if len(parts) < 2:
            raise ValueError("highlight 장면은 'highlight|강조할수식|강조문장' 형식이어야 합니다.")
        return parts[1]

    if scene_type == "meaning":
        if len(parts) < 2:
            raise ValueError("meaning 장면은 'meaning|문장1|문장2' 형식이어야 합니다.")
        return f"{parts[0]}. {parts[1]}"

    if scene_type == "short_expr":
        if len(parts) < 2:
            raise ValueError(
                "short_expr 장면은 'short_expr|반복덧셈수식|곱셈수식' 형식이어야 합니다."
            )
        add_expr = parts[0].replace("+", " 더하기 ")
        mul_expr = parts[1].replace(r"\times", " 곱하기 ")
        return f"{add_expr}. 이것을 {mul_expr} 로 간단히 나타낼 수 있습니다."

    if scene_type == "grid":
        if len(parts) < 6:
            raise ValueError(
                "grid 장면은 'grid|행수|열수|윗문장|왼쪽라벨|아래라벨|결과수식' 형식이어야 합니다."
            )
        title_text = parts[2]
        result_text = parts[5].replace(r"\times", " 곱하기 ")
        return f"{title_text}. 그래서 {result_text} 입니다."

    if scene_type == "conclusion":
        if len(parts) < 5:
            raise ValueError(
                "conclusion 장면은 "
                "'conclusion|제목|문장1|문장2|긴수식|짧은수식' 형식이어야 합니다."
            )
        return f"{parts[0]}. {parts[1]}. {parts[2]}."

    raise ValueError(f"{scene['line_no']}번째 줄: 알 수 없는 장면 종류입니다: {scene_type}")


def make_tts() -> None:
    load_dotenv()
    client = OpenAI()

    scenes = load_script(SCRIPT_FILE)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total = len(scenes)
    print(f"[INFO] 총 {total}개 장면의 TTS를 생성합니다.")

    for idx, scene in enumerate(scenes, start=1):
        output_path = OUTPUT_DIR / f"{idx:02d}.mp3"
        text = tts_text_for_scene(scene)

        print(f"[{idx}/{total}] 생성 중: {output_path.name}")
        print(f"  TTS: {text}")

        with client.audio.speech.with_streaming_response.create(
            model=MODEL,
            voice=VOICE,
            input=text,
        ) as response:
            response.stream_to_file(output_path)

    print("[DONE] TTS 생성 완료")


if __name__ == "__main__":
    try:
        make_tts()
    except Exception as exc:
        print(f"[ERROR] {exc}")
        sys.exit(1)