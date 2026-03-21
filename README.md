실행 방법
이제 이렇게 단계별로 갈 수 있습니다.

uv run main.py --grade 0 --video g0_v0 --step script
uv run main.py --grade 0 --video g0_v0 --step review
uv run main.py --grade 0 --video g0_v0 --step tts --limit-scenes 2
uv run main.py --grade 0 --video g0_v0 --step timing
uv run main.py --grade 0 --video g0_v0 --step render
uv run main.py --grade 0 --video g0_v0 --step final
전체 한 번에는:

uv run main.py --grade 0 --video g0_v0 --step all

# Math Video Factory

초등 1학년부터 6학년까지의 수학 핵심 개념을  
**커리큘럼 데이터(YAML)** 기반으로 자동 영상화하는 프로젝트입니다.

이 프로젝트의 목표는 다음과 같습니다.

- 학년별 핵심 주제를 데이터로 관리한다.
- 데이터에서 자동으로 장면 스크립트(JSON)를 생성한다.
- 장면 스크립트로 Manim 영상을 자동 렌더링한다.
- 장면별 TTS 음성을 자동 생성한다.
- 최종적으로 영상과 음성을 합쳐 하나의 교육 영상을 만든다.

---

## 핵심 철학

수학은 단순 계산 훈련이 아니라  
**세상을 더 높은 수준에서 이해하게 해 주는 추상의 도구**입니다.

이 프로젝트는 초등 수학을 다음 흐름으로 해석합니다.

- 1학년: 개수
- 2학년: 묶음
- 3학년: 반복 구조
- 4학년: 관계와 표현
- 5학년: 보이지 않는 개념
- 6학년: 일반화와 규칙

각 학년은 5개의 핵심 영상으로 구성합니다.

---

## 전체 자동화 흐름

```text
curriculum YAML
→ script JSON 생성
→ 장면별 TTS 생성
→ TTS 길이 측정
→ Manim 장면 렌더링
→ ffmpeg로 음성/영상 합성
→ 최종 mp4 생성


프로젝트 구조

math_video_factory/
├─ README.md
├─ pyproject.toml
├─ .env
├─ main.py
├─ curriculum/
│  ├─ grade_1.yaml
│  ├─ grade_2.yaml
│  ├─ grade_3.yaml
│  ├─ grade_4.yaml
│  ├─ grade_5.yaml
│  └─ grade_6.yaml
├─ generated/
│  ├─ scripts/
│  ├─ tts/
│  ├─ timings/
│  ├─ renders/
│  └─ videos/
├─ src/
│  └─ math_video_factory/
│     ├─ __init__.py
│     ├─ config.py
│     ├─ models.py
│     ├─ loader.py
│     ├─ curriculum_to_script.py
│     ├─ save_script.py
│     ├─ tts_engine.py
│     ├─ timing.py
│     ├─ manim_runner.py
│     ├─ ffmpeg_utils.py
│     ├─ build_pipeline.py
│     └─ manim_entry.py
└─ assets/
   ├─ fonts/
   ├─ images/
   └─ icons/


   주요 개념
1. Curriculum YAML

사람이 직접 작성하는 교육 설계 데이터입니다.

예:

학년

영상 제목

핵심 개념

추상화 단계

대표 예시

시각 모델

결론 문장

2. Script JSON

YAML을 바탕으로 자동 생성되는 장면 데이터입니다.

예:

title

problem

equation

transform

array

grouping

wrap_up

3. Manim Renderer

Script JSON을 읽어서 공통 장면 엔진으로 렌더링합니다.

4. TTS Engine

각 장면의 내레이션을 mp3 파일로 생성합니다.

5. Build Pipeline

전체 과정을 자동 실행합니다.

지원하는 기본 장면 타입

초기 버전에서는 아래 장면 타입만 지원합니다.

title

problem

concept

equation

transform

array

grouping

wrap_up

이후 확장 가능한 장면 타입:

number_line

fraction

compare

pattern

graph

실행 준비
1. Python 버전

Python 3.12 이상 권장

2. 시스템 의존성

ffmpeg 설치 필요

LaTeX/Manim 실행 환경 필요

3. 환경 변수

.env 파일에 OpenAI API 키 설정

OPENAI_API_KEY=your_api_key_here
설치
pip install -e .

또는

pip install -r requirements.txt

프로젝트는 pyproject.toml 기반으로 관리합니다.

실행 예시
3학년 전체 빌드
python main.py --grade 3
특정 영상 하나만 빌드
python main.py --grade 3 --video g3_v1
출력 결과

빌드가 완료되면 다음 파일들이 생성됩니다.

자동 생성 스크립트
generated/scripts/g3_v1.json
장면별 TTS
generated/tts/g3_v1/01.mp3
generated/tts/g3_v1/02.mp3
...
타이밍 정보
generated/timings/g3_v1.json
Manim 렌더 결과
generated/renders/g3_v1.mp4
최종 합성 영상
generated/videos/g3_v1_final.mp4
개발 순서

이 프로젝트는 아래 순서로 구현합니다.

README.md

pyproject.toml

src/math_video_factory/__init__.py

src/math_video_factory/config.py

src/math_video_factory/models.py

src/math_video_factory/loader.py

src/math_video_factory/curriculum_to_script.py

src/math_video_factory/save_script.py

src/math_video_factory/tts_engine.py

src/math_video_factory/timing.py

src/math_video_factory/manim_runner.py

src/math_video_factory/ffmpeg_utils.py

src/math_video_factory/build_pipeline.py

src/math_video_factory/manim_entry.py

main.py

curriculum/grade_1.yaml 샘플

1차 구현 범위

우선은 아래 범위까지만 구현합니다.

학년별 YAML 로드

Script JSON 자동 생성

TTS 생성

TTS 길이 측정

공통 Manim 엔트리로 렌더

영상 + 음성 합성

고급 기능은 2차로 확장합니다.

2차 확장 예정

분수 원형 시각화

수직선

그래프 장면

각도 장면

장면 길이 자동 동기화

자막 자동 삽입

썸네일 자동 생성

예시 목표

예를 들어 3학년 1번 영상은 이렇게 생성됩니다.

입력

제목: 왜 곱하기를 배울까요

개념: 곱셈

예시: 4개씩 있는 묶음이 3개

시각 모델: 배열

출력

문제 장면

반복 더하기 장면

불편함 장면

곱셈 변환 장면

배열 시각화 장면

정리 장면

주의 사항

폰트는 환경마다 다를 수 있으므로 config.py에서 관리합니다.

OpenAI TTS를 사용하려면 API 키가 필요합니다.

Manim 렌더는 환경 설정에 따라 시간이 걸릴 수 있습니다.

ffmpeg가 PATH에 잡혀 있어야 최종 합성이 가능합니다.

라이선스

교육용/연구용 내부 프로젝트 기준으로 시작하며,
필요 시 별도 라이선스를 추가합니다.