from __future__ import annotations

import json
from typing import Any

STEP_SCHEMA = {
    "id": "step_01",
    "phase": "intro",
    "action": "display_problem",
    "title": "문제 확인",
    "pedagogical_purpose": "무엇을 구하는지 명확히 한다",
    "target": "problem_text",
    "inputs": {},
    "outputs": {},
    "narration": {
        "primary": "문제를 읽어 봅시다.",
        "alternate_short": "문제를 확인해요."
    },
    "caption": "문제를 확인해요.",
    "emphasis": ["problem_goal"],
    "animation": {"name": "write", "duration": 1.2},
    "checks": [{"type": "target_exists", "target": "problem_text"}],
    "depends_on": [],
    "teacher_note": "학생에게 무엇을 구하는지 먼저 말하게 유도"
}

SCHEMA_SNIPPET = {
    "schema_version": "1.0",
    "problem_id": "string",
    "input_meta": {},
    "pedagogy": {},
    "semantic": {},
    "derived_facts": [],
    "scene_objects": [],
    "layout_template": {},
    "solution_plan": {
        "strategy": "string",
        "steps": [STEP_SCHEMA],
    },
    "animation_prefs": {},
    "validation": {},
}

SYSTEM_PROMPT = """
너는 초등 수학 문제를 실행형 JSON으로 변환하는 전용 엔진이다.

절대 규칙:
- JSON 외 텍스트를 절대 출력하지 말 것
- 정답만 쓰지 말고 설명 중심 solution_plan.steps를 생성할 것
- 모든 step에 narration(primary, alternate_short), caption, pedagogical_purpose를 포함할 것
- 문장제는 derived_facts(중간 추론)를 반드시 포함할 것
- validation에는 render_safe, solve_safe, human_review_required, confidence, warnings를 반드시 포함할 것
- confidence < 0.70이면 human_review_required=true로 설정할 것
""".strip()


def build_user_prompt(
    *,
    problem_text: str,
    ocr_text: str | None,
    legacy_semantic: dict[str, Any] | None,
    legacy_render: dict[str, Any] | None,
    image_description: str | None,
    problem_id: str,
    extra_hint: str | None = None,
) -> str:
    payload = {
        "problem_id": problem_id,
        "problem_text": problem_text,
        "ocr_text": ocr_text or "",
        "image_description": image_description or "",
        "legacy_semantic": legacy_semantic or {},
        "legacy_render": legacy_render or {},
        "extra_hint": extra_hint or "",
        "required_schema": SCHEMA_SNIPPET,
        "constraints": [
            "답만 출력 금지",
            "중간 추론(derived_facts) 포함",
            "모든 step에 narration/caption 포함",
            "scene_objects와 solution_plan을 함께 생성",
            "validation 포함",
            "JSON 외 텍스트 금지",
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def build_retry_prompt(reason: str, previous_output: str) -> str:
    payload = {
        "retry_reason": reason,
        "instruction": "기존 출력을 보정하여 스키마에 맞는 JSON만 다시 출력하라.",
        "must_fix": [
            "누락 필드 보완",
            "step 구조 보완",
            "narration.primary/alternate_short 보완",
            "confidence 규칙 준수",
        ],
        "previous_output": previous_output,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)
