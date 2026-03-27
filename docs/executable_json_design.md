# 실행형 수학 문제 JSON 아키텍처 v1

## 1) 시스템 역할 분리 설명

### 1. 입력 데이터
- 문제 텍스트: 원문 문항
- OCR 결과: 이미지/PDF 텍스트 추출값
- 구조 추출 데이터: bbox/polygon, 요소 타입
- 기존 JSON: `document`, `styles`, `semantic`, `render`, `quality_notes`

### 2. ChatGPT API
- 문제 의미 이해(`semantic`)
- 중간 추론(`derived_facts`) 생성
- 풀이 단계(`solution_plan.steps`) 생성
- 장면 오브젝트(`scene_objects`) 생성
- 안전성/신뢰도(`validation`) 생성

### 3. Python 파이프라인
- 시스템/사용자 프롬프트 조합
- API 호출 및 응답 파싱
- 스키마 검증 및 보정 재시도
- 실패 시 `human_review_required=true`
- `json_re/{same_filename}.json` 저장

### 4. Manim
- JSON 로드
- `scene_objects`를 Manim 객체로 생성
- `solution_plan.steps` 순차 실행
- 자막/내레이션 출력
- 최종 영상 렌더링

핵심 원칙:
- ChatGPT API가 생각한다.
- JSON은 사고 결과이자 실행 스크립트다.
- Manim은 실행만 한다.

## 2) 실행형 JSON 설계 원칙
- 문제 의미를 담는다.
- 풀이 과정을 담는다.
- 장면 오브젝트를 담는다.
- 애니메이션 순서를 담는다.
- 입력 불완전성을 담는다.
- 사람 검수 필요성을 담는다.

즉, 설명용 JSON이 아니라 실행형 JSON이다.

## 3) JSON 스키마 v1 제안

```json
{
  "schema_version": "1.0",
  "problem_id": "string",
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

필드 정의:
- `schema_version` (필수, string): 스키마 버전. 예: `"1.0"`
- `problem_id` (필수, string): 문제 식별자. 예: `"[평가문제] ..._q0004"`
- `input_meta` (필수, object): 원본 입력 메타. 예: 파일명, OCR 텍스트, 언어
- `pedagogy` (필수, object): 설명 전략/학습 강조 포인트
- `semantic` (필수, object): 문제 의미 해석
- `derived_facts` (필수, array): 중간 계산/중간 추론
- `scene_objects` (필수, array): 렌더링용 교육 오브젝트 정의
- `layout_template` (필수, object): 화면 영역/배치 템플릿
- `solution_plan` (필수, object): Manim 실행 스크립트
- `animation_prefs` (필수, object): 속도/강조 색상/자막 모드
- `validation` (필수, object): 안전성/검수 필요 여부

## 4) ChatGPT API 프롬프트 설계

### A. System Prompt (엄격)
```text
너는 초등 수학 문제를 실행형 JSON으로 변환하는 엔진이다.
역할:
1) 문제 유형 분류
2) 정답 계산
3) 중간 추론(derived_facts) 생성
4) 장면 오브젝트(scene_objects) 생성
5) Manim 실행용 solution_plan 생성
6) validation 생성

절대 규칙:
- JSON 이외의 텍스트를 출력하지 말 것
- 정답만 출력하지 말고 풀이 단계와 중간 추론을 반드시 포함할 것
- 필수 최상위 키를 모두 포함할 것
- confidence가 0.70 미만이면 human_review_required=true
- render_safe, solve_safe, human_review_required, confidence, warnings를 validation에 반드시 포함할 것
```

### B. User Prompt Template
```json
{
  "problem_id": "...",
  "problem_text": "...",
  "ocr_text": "...",
  "image_description": "...",
  "legacy_semantic": {},
  "legacy_render": {},
  "required_schema": {
    "schema_version": "1.0",
    "problem_id": "string",
    "input_meta": {},
    "pedagogy": {},
    "semantic": {},
    "derived_facts": [],
    "scene_objects": [],
    "layout_template": {},
    "solution_plan": {},
    "animation_prefs": {},
    "validation": {}
  },
  "constraints": [
    "답만 내지 말 것",
    "derived_facts를 반드시 생성할 것",
    "scene_objects를 반드시 생성할 것",
    "solution_plan.steps를 단계적으로 생성할 것",
    "validation을 반드시 생성할 것",
    "JSON 외 텍스트 금지"
  ]
}
```

### 재시도/보정 전략
- JSON 파싱 실패: `retry_reason=json_parse_failed`로 재요청
- 필수 필드 누락: 누락 키 목록을 넣어 보정 요청
- confidence < 0.7: 강제로 `human_review_required=true`
- 최대 재시도 초과: 규칙 기반 fallback + 경고 기록

## 5) 예시 JSON 3개

### 예시 1) 573 + 244 = □
```json
{
  "schema_version": "1.0",
  "problem_id": "example_add_carry_573_244",
  "input_meta": {
    "source_filename": "example1.png",
    "language": "ko",
    "raw_problem_text": "573 + 244 = □",
    "ocr_text": "573 + 244 = □"
  },
  "pedagogy": {
    "grade_band": "elementary",
    "explanation_style": "base10_blocks",
    "focus": ["place_value", "carry"]
  },
  "semantic": {
    "problem_type": "arithmetic_addition",
    "expressions": [{"lhs": 573, "operator": "+", "rhs": 244, "result": 817}],
    "answer": 817,
    "givens": [{"value": 573}, {"value": 244}],
    "unknowns": ["result"],
    "constraints": ["three_digit_addition"],
    "concept_tags": ["addition", "place_value", "carry"]
  },
  "derived_facts": [
    {"id": "f1", "kind": "intermediate_sum", "value": 7, "explanation": "일의 자리: 3+4=7"},
    {"id": "f2", "kind": "intermediate_sum", "value": 11, "explanation": "십의 자리: 7+4=11"},
    {"id": "f3", "kind": "carry", "value": 1, "explanation": "십의 자리 합 11에서 백의 자리로 받아올림 1"},
    {"id": "f4", "kind": "intermediate_sum", "value": 8, "explanation": "백의 자리: 5+2+1=8"}
  ],
  "scene_objects": [
    {"id": "problem_text", "type": "text_block", "text": "573 + 244 = □"},
    {"id": "expr", "type": "math_expression", "latex": "573 + 244 = \\Box"},
    {"id": "lhs_blocks", "type": "base10_blocks", "value": {"hundreds": 5, "tens": 7, "ones": 3}},
    {"id": "rhs_blocks", "type": "base10_blocks", "value": {"hundreds": 2, "tens": 4, "ones": 4}},
    {"id": "answer_box", "type": "answer_box", "placeholder": "□"},
    {"id": "carry_hint", "type": "highlight_box", "target": "tens_column"}
  ],
  "layout_template": {
    "name": "worksheet_default",
    "regions": {
      "problem": [0.05, 0.05, 0.9, 0.2],
      "work": [0.08, 0.25, 0.84, 0.55],
      "answer": [0.68, 0.82, 0.18, 0.1]
    }
  },
  "solution_plan": {
    "strategy": "place_value_first",
    "steps": [
      {"id": "step_01", "action": "display_problem", "target": "problem_text", "inputs": {}, "outputs": {"shown": true}, "narration": "문제를 읽어 봅시다.", "animation": "write", "duration": 1.2, "depends_on": []},
      {"id": "step_02", "action": "show_object", "target": "lhs_blocks", "inputs": {}, "outputs": {"lhs_visible": true}, "narration": "573을 수모형으로 나타냅니다.", "animation": "fade_in", "duration": 1.1, "depends_on": ["step_01"]},
      {"id": "step_03", "action": "show_object", "target": "rhs_blocks", "inputs": {}, "outputs": {"rhs_visible": true}, "narration": "244도 수모형으로 나타냅니다.", "animation": "fade_in", "duration": 1.1, "depends_on": ["step_02"]},
      {"id": "step_04", "action": "combine_place_values", "target": "expr", "inputs": {"place": "ones"}, "outputs": {"ones_result": 7}, "narration": "일의 자리 3과 4를 더해 7입니다.", "animation": "highlight", "duration": 1.0, "depends_on": ["step_03"]},
      {"id": "step_05", "action": "combine_place_values", "target": "expr", "inputs": {"place": "tens"}, "outputs": {"tens_raw": 11}, "narration": "십의 자리 7과 4를 더하면 11입니다.", "animation": "highlight", "duration": 1.0, "depends_on": ["step_04"]},
      {"id": "step_06", "action": "regroup", "target": "carry_hint", "inputs": {"from": "tens", "to": "hundreds", "value": 1}, "outputs": {"carry_done": true}, "narration": "십의 자리 10개는 백의 자리 1개로 받아올림합니다.", "animation": "transform", "duration": 1.2, "depends_on": ["step_05"]},
      {"id": "step_07", "action": "combine_place_values", "target": "expr", "inputs": {"place": "hundreds"}, "outputs": {"hundreds_result": 8}, "narration": "백의 자리 5+2+1=8입니다.", "animation": "highlight", "duration": 1.0, "depends_on": ["step_06"]},
      {"id": "step_08", "action": "fill_answer", "target": "answer_box", "inputs": {"answer": 817}, "outputs": {"answer_filled": true}, "narration": "정답은 817입니다.", "animation": "write", "duration": 0.9, "depends_on": ["step_07"]},
      {"id": "step_09", "action": "conclude", "target": "problem_text", "inputs": {}, "outputs": {"done": true}, "narration": "자리값을 나누어 계산하면 정확합니다.", "animation": "fade_out", "duration": 0.8, "depends_on": ["step_08"]}
    ]
  },
  "animation_prefs": {"theme": "clean_math", "pace": "normal", "caption_mode": "korean_subtitles"},
  "validation": {"render_safe": true, "solve_safe": true, "human_review_required": false, "confidence": 0.97, "warnings": []}
}
```

### 예시 2) 917 - 353 = □
```json
{
  "schema_version": "1.0",
  "problem_id": "example_sub_borrow_917_353",
  "input_meta": {
    "source_filename": "example2.png",
    "language": "ko",
    "raw_problem_text": "917 - 353 = □",
    "ocr_text": "917 - 353 = □"
  },
  "pedagogy": {
    "grade_band": "elementary",
    "explanation_style": "vertical_algorithm",
    "focus": ["place_value", "borrow_check"]
  },
  "semantic": {
    "problem_type": "arithmetic_subtraction",
    "expressions": [{"lhs": 917, "operator": "-", "rhs": 353, "result": 564}],
    "answer": 564,
    "givens": [{"value": 917}, {"value": 353}],
    "unknowns": ["result"],
    "constraints": ["three_digit_subtraction"],
    "concept_tags": ["subtraction", "place_value", "borrow"]
  },
  "derived_facts": [
    {"id": "f1", "kind": "borrow_check", "value": {"ones": false, "tens": true}, "explanation": "일의 자리는 받아내림 불필요, 십의 자리는 필요"},
    {"id": "f2", "kind": "intermediate_diff", "value": 4, "explanation": "일의 자리: 7-3=4"},
    {"id": "f3", "kind": "borrow", "value": 1, "explanation": "백의 자리 9에서 1을 빌려 십의 자리 1을 11로 만든다"},
    {"id": "f4", "kind": "intermediate_diff", "value": 6, "explanation": "십의 자리: 11-5=6"},
    {"id": "f5", "kind": "intermediate_diff", "value": 5, "explanation": "백의 자리: 8-3=5"}
  ],
  "scene_objects": [
    {"id": "problem_text", "type": "text_block", "text": "917 - 353 = □"},
    {"id": "vertical_sub", "type": "vertical_algorithm", "operator": "-", "rows": ["917", "353", "___"]},
    {"id": "answer_box", "type": "answer_box", "placeholder": "□"},
    {"id": "borrow_arrow", "type": "arrow", "from": "hundreds_column", "to": "tens_column"},
    {"id": "borrow_highlight", "type": "highlight_box", "target": "tens_column"}
  ],
  "layout_template": {
    "name": "vertical_default",
    "regions": {
      "problem": [0.05, 0.05, 0.9, 0.2],
      "work": [0.2, 0.28, 0.6, 0.5],
      "answer": [0.66, 0.82, 0.18, 0.1]
    }
  },
  "solution_plan": {
    "strategy": "column_subtraction",
    "steps": [
      {"id": "step_01", "action": "display_problem", "target": "problem_text", "inputs": {}, "outputs": {"shown": true}, "narration": "917에서 353을 빼는 문제입니다.", "animation": "write", "duration": 1.2, "depends_on": []},
      {"id": "step_02", "action": "show_object", "target": "vertical_sub", "inputs": {}, "outputs": {"vertical_ready": true}, "narration": "세로셈으로 정렬해 봅시다.", "animation": "fade_in", "duration": 1.1, "depends_on": ["step_01"]},
      {"id": "step_03", "action": "derive_intermediate_value", "target": "vertical_sub", "inputs": {"place": "ones"}, "outputs": {"ones_result": 4}, "narration": "일의 자리 7-3=4입니다.", "animation": "highlight", "duration": 1.0, "depends_on": ["step_02"]},
      {"id": "step_04", "action": "highlight", "target": "borrow_highlight", "inputs": {"place": "tens"}, "outputs": {"borrow_check": true}, "narration": "십의 자리 1에서 5를 뺄 수 있는지 확인합니다.", "animation": "highlight", "duration": 0.9, "depends_on": ["step_03"]},
      {"id": "step_05", "action": "regroup", "target": "borrow_arrow", "inputs": {"from": "hundreds", "to": "tens", "value": 1}, "outputs": {"tens_after_borrow": 11, "hundreds_after_borrow": 8}, "narration": "백의 자리에서 1을 빌려 십의 자리를 11로 만듭니다.", "animation": "transform", "duration": 1.2, "depends_on": ["step_04"]},
      {"id": "step_06", "action": "derive_intermediate_value", "target": "vertical_sub", "inputs": {"place": "tens"}, "outputs": {"tens_result": 6}, "narration": "십의 자리 11-5=6입니다.", "animation": "highlight", "duration": 1.0, "depends_on": ["step_05"]},
      {"id": "step_07", "action": "derive_intermediate_value", "target": "vertical_sub", "inputs": {"place": "hundreds"}, "outputs": {"hundreds_result": 5}, "narration": "백의 자리 8-3=5입니다.", "animation": "highlight", "duration": 1.0, "depends_on": ["step_06"]},
      {"id": "step_08", "action": "fill_answer", "target": "answer_box", "inputs": {"answer": 564}, "outputs": {"answer_filled": true}, "narration": "정답은 564입니다.", "animation": "write", "duration": 0.9, "depends_on": ["step_07"]},
      {"id": "step_09", "action": "conclude", "target": "problem_text", "inputs": {}, "outputs": {"done": true}, "narration": "받아내림 여부를 먼저 판단하면 정확하게 뺄 수 있습니다.", "animation": "fade_out", "duration": 0.8, "depends_on": ["step_08"]}
    ]
  },
  "animation_prefs": {"theme": "clean_math", "pace": "normal", "caption_mode": "korean_subtitles"},
  "validation": {"render_safe": true, "solve_safe": true, "human_review_required": false, "confidence": 0.96, "warnings": []}
}
```

### 예시 3) 문장제 도토리 문제
```json
{
  "schema_version": "1.0",
  "problem_id": "example_wordproblem_acorn",
  "input_meta": {
    "source_filename": "example3.png",
    "language": "ko",
    "raw_problem_text": "동생은 도토리 412개를 주웠고, 형은 동생보다 133개 더 많이 주웠습니다. 형과 동생이 주운 도토리는 모두 몇 개인가요?",
    "ocr_text": "동생 412, 형은 133 더 많음, 모두 몇 개인가"
  },
  "pedagogy": {
    "grade_band": "elementary",
    "explanation_style": "word_problem_reasoning",
    "focus": ["relation_equation", "intermediate_value", "two_step_addition"]
  },
  "semantic": {
    "problem_type": "word_problem",
    "expressions": [
      {"lhs": 412, "operator": "+", "rhs": 133, "result": 545},
      {"lhs": 412, "operator": "+", "rhs": 545, "result": 957}
    ],
    "answer": 957,
    "givens": [
      {"entity": "동생", "value": 412},
      {"entity": "형", "relation": "동생보다 133개 더 많음"}
    ],
    "unknowns": ["형과 동생의 합"],
    "constraints": ["two_step_reasoning_required"],
    "concept_tags": ["word_problem", "addition", "derived_facts"]
  },
  "derived_facts": [
    {"id": "f1", "kind": "relation_to_equation", "value": "형=동생+133", "explanation": "형은 동생보다 133개 더 많다."},
    {"id": "f2", "kind": "intermediate_value", "value": 545, "equation": "412+133=545", "explanation": "형이 주운 도토리 수"},
    {"id": "f3", "kind": "final_composition", "value": 957, "equation": "412+545=957", "explanation": "동생과 형의 합"}
  ],
  "scene_objects": [
    {"id": "problem_text", "type": "text_block", "text": "동생 412개, 형은 133개 더 많음. 둘이 모두 몇 개인가?"},
    {"id": "relation_text", "type": "text_block", "text": "형 = 동생 + 133"},
    {"id": "eq_1", "type": "math_expression", "latex": "412 + 133 = 545"},
    {"id": "eq_2", "type": "math_expression", "latex": "412 + 545 = 957"},
    {"id": "answer_box", "type": "answer_box", "placeholder": "□"},
    {"id": "guide_arrow", "type": "arrow", "from": "relation_text", "to": "eq_1"},
    {"id": "step_highlight", "type": "highlight_box", "target": "eq_2"}
  ],
  "layout_template": {
    "name": "word_problem_default",
    "regions": {
      "problem": [0.05, 0.05, 0.9, 0.25],
      "reasoning": [0.08, 0.32, 0.84, 0.4],
      "answer": [0.68, 0.82, 0.18, 0.1]
    }
  },
  "solution_plan": {
    "strategy": "derive_then_compose",
    "steps": [
      {"id": "step_01", "action": "display_problem", "target": "problem_text", "inputs": {}, "outputs": {"shown": true}, "narration": "문장을 읽고 누가 얼마를 주웠는지 정리합니다.", "animation": "write", "duration": 1.3, "depends_on": []},
      {"id": "step_02", "action": "write_equation", "target": "relation_text", "inputs": {}, "outputs": {"relation_ready": true}, "narration": "형의 양을 식으로 쓰면 형=동생+133입니다.", "animation": "fade_in", "duration": 1.1, "depends_on": ["step_01"]},
      {"id": "step_03", "action": "derive_intermediate_value", "target": "eq_1", "inputs": {"equation": "412+133"}, "outputs": {"brother_count": 545}, "narration": "먼저 형이 주운 양을 구하면 545개입니다.", "animation": "write", "duration": 1.2, "depends_on": ["step_02"]},
      {"id": "step_04", "action": "derive_intermediate_value", "target": "eq_2", "inputs": {"equation": "412+545"}, "outputs": {"total": 957}, "narration": "이제 동생과 형의 양을 합하면 957개입니다.", "animation": "transform", "duration": 1.3, "depends_on": ["step_03"]},
      {"id": "step_05", "action": "fill_answer", "target": "answer_box", "inputs": {"answer": 957}, "outputs": {"answer_filled": true}, "narration": "정답 칸에 957을 씁니다.", "animation": "write", "duration": 0.9, "depends_on": ["step_04"]},
      {"id": "step_06", "action": "show_feedback", "target": "step_highlight", "inputs": {"message": "중간 계산을 먼저 세우면 문장제를 쉽게 풀 수 있어요."}, "outputs": {"feedback_shown": true}, "narration": "문장제는 관계식과 중간값이 핵심입니다.", "animation": "highlight", "duration": 1.0, "depends_on": ["step_05"]},
      {"id": "step_07", "action": "conclude", "target": "problem_text", "inputs": {}, "outputs": {"done": true}, "narration": "최종 답은 957개입니다.", "animation": "fade_out", "duration": 0.8, "depends_on": ["step_06"]}
    ]
  },
  "animation_prefs": {"theme": "clean_math", "pace": "normal", "caption_mode": "korean_subtitles"},
  "validation": {"render_safe": true, "solve_safe": true, "human_review_required": false, "confidence": 0.98, "warnings": []}
}
```

## 6) Python 구현 골격

추가된 파일:
- `src/math_video_factory/problem_pipeline/prompt_builder.py`
- `src/math_video_factory/problem_pipeline/llm_client.py`
- `src/math_video_factory/problem_pipeline/schema_models.py`
- `src/math_video_factory/problem_pipeline/json_validator.py`
- `src/math_video_factory/problem_pipeline/problem_converter.py`
- `src/math_video_factory/problem_pipeline/save_problem_spec.py`
- `convert_legacy_json.py`

핵심 포인트:
- 시스템/사용자 프롬프트 조합 함수 제공
- ChatGPT API 호출 함수 제공
- 응답에서 JSON 추출 함수 제공
- dataclass 기반 스키마(`ProblemSpecV1`) 제공
- 검증 실패 시 재시도 + fallback
- confidence 낮으면 human_review_required 처리
- `json_re` 저장 지원

실행:
```bash
python convert_legacy_json.py --input-dir json --output-dir json_re
```

LLM 보강:
```bash
python convert_legacy_json.py --input-dir json --output-dir json_re --use-llm
```

## 7) Manim 연결 구조

권장 컴포넌트:
- `ProblemSpecLoader`: JSON 로드/검증
- `SceneObjectFactory`: `scene_objects` -> Manim mobject 생성
- `LayoutEngine`: `layout_template` 반영
- `SolutionDirector`: `solution_plan.steps` 순회
- `AnimationExecutor`: action별 play 실행
- `NarrationBuilder`: `narration`을 자막/음성으로 연결

코드 골격:
```python
class ProblemSpecLoader:
    def load(self, path: str) -> dict:
        import json
        from pathlib import Path
        return json.loads(Path(path).read_text(encoding="utf-8"))

class SolutionDirector:
    def __init__(self, scene, obj_factory, executor):
        self.scene = scene
        self.obj_factory = obj_factory
        self.executor = executor

    def run(self, spec: dict) -> None:
        if not spec["validation"].get("render_safe", False):
            self.executor.run_safe_fallback(scene=self.scene, message="검수 필요 문제")
            return
        objects = self.obj_factory.build(spec["scene_objects"])
        for step in spec["solution_plan"]["steps"]:
            self.executor.execute(step=step, objects=objects, scene=self.scene)
```

`validation.render_safe=false` 처리:
- 정식 렌더 대신 fallback scene 표시
- 로그에 문제 ID/경고를 기록
- human review queue로 전달

## 8) 기존 JSON -> 실행형 JSON 변환 전략

- `semantic` 재사용:
  - `expression`, `answer`, `instruction` 우선 재사용
- `render.elements` 승격:
  - `text` -> `text_block`
  - `base10_group` -> `base10_blocks`
  - `rect/rounded_rect` -> `answer_box` 또는 `highlight_box`
  - `line` -> `arrow`
- bbox/polygon:
  - 기하 정보는 배치 보조 자료로만 사용
- `derived_facts` 생성:
  - 기존 JSON에 없으면 LLM 또는 규칙 엔진이 생성
- `solution_plan` 생성:
  - 대부분 LLM 생성이 우선
  - LLM 실패 시 규칙 기반 기본 플랜으로 fallback
- `quality_notes` -> `validation`:
  - confidence 매핑
  - limitations를 warnings로 이동
- 누락/애매한 데이터 처리:
  - `human_review_required=true`
  - `warnings`에 원인 기록

## 9) 추천 폴더 구조

```text
math/
  json/
  json_re/
  docs/
    executable_json_design.md
  src/
    math_video_factory/
      problem_pipeline/
        __init__.py
        prompt_builder.py
        llm_client.py
        schema_models.py
        json_validator.py
        problem_converter.py
        save_problem_spec.py
  convert_legacy_json.py
```

## 10) 다음 구현 체크리스트

- [ ] LLM 실제 응답 품질 평가셋 구축 (덧셈/뺄셈/문장제)
- [ ] action별 Manim executor 상세 구현
- [ ] `clock_face`, `fraction_model`, `angle_diagram` factory 확장
- [ ] 실패 케이스 human review UI 연동
- [ ] 회귀 테스트(`json` -> `json_re`) 자동화

추가:
- 구현 우선순위:
  1. 변환 안정성(파싱/검증/저장)
  2. solution_plan 액션 표준화
  3. Manim executor 확장
  4. LLM 품질 보정
- 첫 번째 MVP 범위:
  - 연산형(+,-) + 기본 문장제
  - 필수 top-level 키 100% 생성
  - `render_safe/solve_safe/human_review_required/confidence` 자동 산출
  - `json` -> `json_re` 일괄 변환 완료
