# Math Problem Executable JSON Converter

초등 수학 문제 JSON(`json/*.json`)를
Manim 실행 가능한 실행형 스키마 JSON(`json_re/*.json`)로 변환하는 프로젝트입니다.

## 핵심 개념
- ChatGPT API: 문제를 이해하고, 풀이 단계/중간 추론/scene_objects/solution_plan을 생성하는 사고 엔진
- 실행형 JSON: 사고 결과이자 Manim 실행 스크립트
- Manim: JSON을 읽어 실행만 하는 렌더러

## 현재 포함 범위
- 기존 JSON(`document`, `semantic`, `render`, `quality_notes`) 입력
- 실행형 스키마 v1 출력
- `validation.render_safe`, `validation.solve_safe`, `validation.human_review_required`, `validation.confidence` 자동 생성
- 파일명 유지 저장: `json/<name>.json` -> `json_re/<name>.json`

## 요구 환경
- Python 3.12+
- uv (권장)
- 선택: OpenAI API 키 (`--use-llm` 사용 시)

## 설치
```bash
uv sync
```

## 실행
기본(규칙 기반 변환):
```bash
uv run python convert_legacy_json.py --input-dir json --output-dir json_re
```

LLM 보강 포함:
```bash
uv run python convert_legacy_json.py --input-dir json --output-dir json_re --use-llm
```

## 출력 스키마(최상위)
```json
{
  "schema_version": "1.0",
  "problem_id": "...",
  "input_meta": {},
  "pedagogy": {},
  "semantic": {},
  "derived_facts": [],
  "scene_objects": [],
  "layout_template": {},
  "solution_plan": {},
  "animation_prefs": {},
  "validation": {}
}
```

## 주요 파일
- `convert_legacy_json.py`: 일괄 변환 엔트리 포인트
- `src/math_video_factory/problem_pipeline/prompt_builder.py`
- `src/math_video_factory/problem_pipeline/llm_client.py`
- `src/math_video_factory/problem_pipeline/schema_models.py`
- `src/math_video_factory/problem_pipeline/json_validator.py`
- `src/math_video_factory/problem_pipeline/problem_converter.py`
- `src/math_video_factory/problem_pipeline/save_problem_spec.py`
- `docs/executable_json_design.md`: 상세 설계 문서 및 예시 JSON

## 폴더 구조
```text
.
├─ json/
├─ json_re/
├─ docs/
│  └─ executable_json_design.md
├─ src/
│  └─ math_video_factory/
│     ├─ __init__.py
│     └─ problem_pipeline/
│        ├─ __init__.py
│        ├─ prompt_builder.py
│        ├─ llm_client.py
│        ├─ schema_models.py
│        ├─ json_validator.py
│        ├─ problem_converter.py
│        └─ save_problem_spec.py
├─ convert_legacy_json.py
├─ pyproject.toml
└─ uv.lock
```

## 주의 사항
- OCR/인코딩 손상으로 연산자 해석이 불명확하면 `human_review_required=true`로 내려갑니다.
- `confidence`가 낮은 결과는 검수 큐로 보내는 것을 권장합니다.

## 다음 단계 권장
1. action별 Manim 실행기(`SolutionDirector`, `AnimationExecutor`) 구현
2. 문장제 전용 `derived_facts` 강화
3. 자동 회귀 테스트 추가 (`json` -> `json_re`)