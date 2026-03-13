from pathlib import Path
import os
from dotenv import load_dotenv
from openai import OpenAI

# .env 로드
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

OUT_DIR = Path("tts_output")
OUT_DIR.mkdir(exist_ok=True)

MODEL = "gpt-4o-mini-tts"
VOICE = "alloy"

INSTRUCTIONS = (
    "초등학생 대상 수학 강의 내레이션입니다. "
    "친절하고 또렷하게, 너무 빠르지 않게 읽어주세요. "
    "문장 사이에는 자연스러운 짧은 쉬는 구간을 넣고, "
    "숫자와 수식은 분명하게 발음해주세요."
)

SEGMENTS = [
    ("01_title", "왜 곱하기를 배워야 할까요?"),
    ("02_question", "여러분, 8 곱하기 8은 얼마일까요? 맞아요. 64입니다. 그런데 왜 우리는 곱하기를 배워야 할까요?"),
    ("03_no_multiply", "곱하기를 배우지 않았다면, 8 곱하기 8을 바로 계산할 수 없어요. 대신 8을 8번 더해야 합니다."),
    ("04_repeat_add_intro", "즉, 8을 8번 더해야 하지요."),
    ("05_repeat_add_count", "8, 16, 24, 32, 40, 48, 56, 64."),
    ("06_inconvenient", "이 방법도 틀리지는 않아요. 하지만 수가 커질수록 너무 길고 불편해집니다."),
    ("07_multiplication_meaning", "그래서 수학에서는 같은 수를 반복해서 더하는 것을 더 간단하게 나타내는 방법을 만들었습니다. 그것이 바로 곱하기입니다."),
    ("08_short_expression", "8을 8번 더하는 것을 8 곱하기 8이라고 짧고 효율적으로 쓰는 것입니다."),
    ("09_grid_intro", "8개씩 있는 줄이 8줄 있다고 생각해 볼까요?"),
    ("10_grid_explain", "한 줄에 8개, 그런 줄이 8개 있으면 모두 64개가 됩니다."),
    ("11_grid_concept", "이처럼 곱하기는 반복되는 더하기를 한눈에 보이게 해 주는 약속입니다."),
    ("12_conclusion", "정리해 볼게요. 곱하기를 배우는 이유는 같은 수를 여러 번 더해야 할 때 더 빠르고, 더 짧고, 더 정확하게 계산하기 위해서입니다."),
    ("13_formula_wrapup", "그래서 8 더하기 8 더하기 8 더하기 8 더하기 8 더하기 8 더하기 8 더하기 8은 64를, 8 곱하기 8은 64로 간단하게 표현하는 것입니다."),
    ("14_final", "즉, 곱하기는 반복되는 더하기를 효율적으로 바꿔 주는 수학의 도구입니다."),
]

for name, text in SEGMENTS:
    out_path = OUT_DIR / f"{name}.mp3"

    with client.audio.speech.with_streaming_response.create(
        model=MODEL,
        voice=VOICE,
        input=text,
        instructions=INSTRUCTIONS,
    ) as response:
        response.stream_to_file(out_path)

    print(f"saved: {out_path}")