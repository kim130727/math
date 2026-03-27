from __future__ import annotations

import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .json_validator import validate_problem_spec
from .llm_client import LLMClient
from .prompt_builder import SYSTEM_PROMPT, build_retry_prompt, build_user_prompt
from .schema_models import NarrationSpec, ProblemSpecV1, SolutionStep


def _to_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _extract_ints(text: str) -> list[int]:
    return [int(m) for m in re.findall(r"\d+", text or "")]


def _numbers_from_expression(expression: dict[str, Any]) -> tuple[int | None, str, int | None, int | None]:
    lhs = _to_int(expression.get("lhs"))
    rhs = _to_int(expression.get("rhs"))
    op = str(expression.get("operator") or "")
    result = _to_int(expression.get("result"))
    return lhs, op, rhs, result


def _detect_problem_type(task_type: str, instruction: str, operator: str) -> str:
    text = f"{task_type} {instruction}".lower()
    if any(k in instruction for k in ["모두", "더 많이", "몇 개인가", "몇 개", "문장"]) or "word" in text:
        return "word_problem"
    if "수모형" in instruction or "base" in text:
        return "addition_with_base10" if operator == "+" else "subtraction_with_base10"
    if operator == "+":
        return "arithmetic_addition"
    if operator == "-":
        return "arithmetic_subtraction"
    return "unknown"


def _narration(primary: str, short: str) -> dict[str, str]:
    return asdict(NarrationSpec(primary=primary, alternate_short=short))


def _step(
    *,
    step_id: str,
    phase: str,
    action: str,
    title: str,
    purpose: str,
    target: str,
    inputs: dict[str, Any],
    outputs: dict[str, Any],
    primary: str,
    short: str,
    caption: str,
    emphasis: list[str],
    animation_name: str,
    duration: float,
    checks: list[dict[str, Any]],
    depends_on: list[str],
    teacher_note: str,
) -> dict[str, Any]:
    step = SolutionStep(
        id=step_id,
        phase=phase,
        action=action,
        title=title,
        pedagogical_purpose=purpose,
        target=target,
        inputs=inputs,
        outputs=outputs,
        narration=NarrationSpec(primary=primary, alternate_short=short),
        caption=caption,
        emphasis=emphasis,
        animation={"name": animation_name, "duration": duration},
        checks=checks,
        depends_on=depends_on,
        teacher_note=teacher_note,
    )
    return asdict(step)


def _build_derived_facts(
    *,
    problem_type: str,
    lhs: int | None,
    operator: str,
    rhs: int | None,
    instruction: str,
) -> list[dict[str, Any]]:
    facts: list[dict[str, Any]] = []

    if problem_type == "word_problem":
        nums = _extract_ints(instruction)
        if len(nums) >= 2:
            base = nums[0]
            diff = nums[1]
            first = base + diff
            second = base + first
            facts.extend(
                [
                    {
                        "id": "fact_relation_equation",
                        "kind": "relation_to_equation",
                        "value": f"형=동생+{diff}",
                        "explanation": "문장 조건을 식으로 변환",
                    },
                    {
                        "id": "fact_intermediate_1",
                        "kind": "intermediate_value",
                        "value": first,
                        "equation": f"{base}+{diff}={first}",
                        "explanation": "형이 주운 개수",
                    },
                    {
                        "id": "fact_final_compose",
                        "kind": "final_composition",
                        "value": second,
                        "equation": f"{base}+{first}={second}",
                        "explanation": "둘이 주운 총개수",
                    },
                ]
            )
            return facts

    if lhs is None or rhs is None:
        return facts

    if operator == "+":
        ones = (lhs % 10) + (rhs % 10)
        carry1 = ones // 10
        tens = ((lhs // 10) % 10) + ((rhs // 10) % 10) + carry1
        carry2 = tens // 10
        facts.extend(
            [
                {
                    "id": "fact_place_values",
                    "kind": "place_value_split",
                    "value": {
                        "lhs": {"hundreds": lhs // 100, "tens": (lhs // 10) % 10, "ones": lhs % 10},
                        "rhs": {"hundreds": rhs // 100, "tens": (rhs // 10) % 10, "ones": rhs % 10},
                    },
                    "explanation": "자리값 분해",
                },
                {
                    "id": "fact_ones_sum",
                    "kind": "intermediate_sum",
                    "value": ones,
                    "explanation": f"일의 자리 {lhs%10}+{rhs%10}={ones}",
                },
            ]
        )
        if carry1:
            facts.append({"id": "fact_carry_tens", "kind": "carry", "value": carry1, "explanation": "일의 자리 받아올림"})
        facts.append({"id": "fact_tens_sum", "kind": "intermediate_sum", "value": tens, "explanation": "십의 자리 합"})
        if carry2:
            facts.append({"id": "fact_carry_hundreds", "kind": "carry", "value": carry2, "explanation": "십의 자리 받아올림"})

    if operator == "-":
        borrow_ones = (lhs % 10) < (rhs % 10)
        borrow_tens = ((lhs // 10) % 10) < ((rhs // 10) % 10)
        facts.extend(
            [
                {
                    "id": "fact_place_values",
                    "kind": "place_value_split",
                    "value": {
                        "lhs": {"hundreds": lhs // 100, "tens": (lhs // 10) % 10, "ones": lhs % 10},
                        "rhs": {"hundreds": rhs // 100, "tens": (rhs // 10) % 10, "ones": rhs % 10},
                    },
                    "explanation": "자리값 분해",
                },
                {
                    "id": "fact_borrow_check",
                    "kind": "borrow_check",
                    "value": {"ones": borrow_ones, "tens": borrow_tens},
                    "explanation": "받아내림 필요 여부 판단",
                },
            ]
        )

    return facts


def _build_scene_objects(render: dict[str, Any], expression: dict[str, Any], instruction: str) -> list[dict[str, Any]]:
    objects: list[dict[str, Any]] = [
        {"id": "problem_text", "type": "text_block", "text": instruction},
        {
            "id": "main_expression",
            "type": "math_expression",
            "latex": f"{expression.get('lhs')} {expression.get('operator')} {expression.get('rhs')} = \\Box",
            "value": expression,
        },
        {"id": "answer_box", "type": "answer_box", "placeholder": "□"},
    ]

    for idx, element in enumerate(render.get("elements", []), start=1):
        etype = element.get("type")
        sid = f"legacy_{etype}_{idx}"
        if etype == "base10_group":
            objects.append(
                {
                    "id": sid,
                    "type": "base10_blocks",
                    "label": element.get("label"),
                    "components": element.get("components", {}),
                    "bbox": element.get("bbox", {}),
                }
            )
        elif etype == "text":
            objects.append({"id": sid, "type": "text_block", "text": element.get("text", ""), "bbox": element.get("bbox", {})})
        elif etype in {"rect", "rounded_rect"}:
            objects.append({"id": sid, "type": "highlight_box", "bbox": element.get("bbox", {})})
        elif etype == "line":
            objects.append(
                {
                    "id": sid,
                    "type": "arrow",
                    "from": {"x": element.get("x1"), "y": element.get("y1")},
                    "to": {"x": element.get("x2"), "y": element.get("y2")},
                }
            )

    has_vertical = any(o.get("type") == "text_block" and "-" in str(o.get("text", "")) for o in objects)
    if has_vertical:
        objects.append({"id": "vertical_algo", "type": "vertical_algorithm", "operator": expression.get("operator", "-")})

    return objects


def _build_solution_plan(
    *,
    problem_type: str,
    lhs: int | None,
    rhs: int | None,
    operator: str,
    answer: int | None,
    instruction: str,
) -> dict[str, Any]:
    steps: list[dict[str, Any]] = []

    steps.append(
        _step(
            step_id="step_01",
            phase="intro",
            action="display_problem",
            title="문제 확인",
            purpose="무엇을 구하는지 파악",
            target="problem_text",
            inputs={},
            outputs={"problem_understood": True},
            primary="문제를 읽고 무엇을 구해야 하는지 확인해요.",
            short="문제를 먼저 확인해요.",
            caption="무엇을 구할지 확인",
            emphasis=["goal"],
            animation_name="write",
            duration=1.3,
            checks=[{"type": "target_exists", "target": "problem_text"}],
            depends_on=[],
            teacher_note="학생이 문제 요구를 먼저 말하게 유도",
        )
    )

    steps.append(
        _step(
            step_id="step_02",
            phase="modeling",
            action="show_object",
            title="식 제시",
            purpose="문제 정보를 수식 형태로 시각화",
            target="main_expression",
            inputs={},
            outputs={"expression_shown": True},
            primary="식을 화면에 보여주고 자리값 순서로 계산할 준비를 합니다.",
            short="식을 보여줄게요.",
            caption="식과 계산 순서 준비",
            emphasis=["expression"],
            animation_name="fade_in",
            duration=1.0,
            checks=[{"type": "target_exists", "target": "main_expression"}],
            depends_on=["step_01"],
            teacher_note="연산 기호와 피연산자를 정확히 읽게 지도",
        )
    )

    if problem_type == "word_problem":
        nums = _extract_ints(instruction)
        if len(nums) >= 2:
            a, b = nums[0], nums[1]
            first = a + b
            total = a + first
            steps.extend(
                [
                    _step(
                        step_id="step_03",
                        phase="reasoning",
                        action="derive_intermediate_value",
                        title="관계식으로 변환",
                        purpose="문장 조건을 수식으로 번역",
                        target="main_expression",
                        inputs={"relation": f"형=동생+{b}"},
                        outputs={"relation_built": True},
                        primary=f"형은 동생보다 {b}개 더 많으므로 형=동생+{b}로 나타낼 수 있어요.",
                        short="문장을 식으로 바꿔요.",
                        caption="형=동생+차이",
                        emphasis=["relation"],
                        animation_name="write",
                        duration=1.3,
                        checks=[{"type": "relation_valid"}],
                        depends_on=["step_02"],
                        teacher_note="문장제 핵심은 관계식을 먼저 세우는 것",
                    ),
                    _step(
                        step_id="step_04",
                        phase="compute",
                        action="write_equation",
                        title="중간값 계산",
                        purpose="형의 개수를 먼저 계산",
                        target="main_expression",
                        inputs={"equation": f"{a}+{b}"},
                        outputs={"older_count": first},
                        primary=f"먼저 형의 개수를 계산하면 {a}+{b}={first}이에요.",
                        short="중간값을 구해요.",
                        caption=f"{a}+{b}={first}",
                        emphasis=["intermediate"],
                        animation_name="transform",
                        duration=1.2,
                        checks=[{"type": "numeric", "key": "older_count"}],
                        depends_on=["step_03"],
                        teacher_note="중간 결과를 꼭 기록하게 지도",
                    ),
                    _step(
                        step_id="step_05",
                        phase="compute",
                        action="derive_intermediate_value",
                        title="최종 합 계산",
                        purpose="중간값과 기존 값을 합쳐 최종 정답 도출",
                        target="main_expression",
                        inputs={"equation": f"{a}+{first}"},
                        outputs={"final_answer": total},
                        primary=f"이제 둘의 합은 {a}+{first}={total}입니다.",
                        short="최종 합을 구해요.",
                        caption=f"{a}+{first}={total}",
                        emphasis=["final_sum"],
                        animation_name="write",
                        duration=1.2,
                        checks=[{"type": "numeric", "key": "final_answer"}],
                        depends_on=["step_04"],
                        teacher_note="문장제는 1차 계산 후 2차 계산으로 이어짐",
                    ),
                ]
            )
            answer = total
    elif operator == "+" and lhs is not None and rhs is not None:
        ones = (lhs % 10) + (rhs % 10)
        carry = ones // 10
        steps.extend(
            [
                _step(
                    step_id="step_03",
                    phase="compute",
                    action="show_place_value",
                    title="자리값 분해",
                    purpose="백/십/일 자리 단위로 계산 준비",
                    target="main_expression",
                    inputs={"lhs": lhs, "rhs": rhs},
                    outputs={"place_value_ready": True},
                    primary="두 수를 백, 십, 일 자리로 나누어 봅시다.",
                    short="자리값으로 나눠요.",
                    caption="자리값 분해",
                    emphasis=["place_value"],
                    animation_name="highlight",
                    duration=1.0,
                    checks=[{"type": "place_value_valid"}],
                    depends_on=["step_02"],
                    teacher_note="자리값을 분해하면 오류가 줄어듦",
                ),
                _step(
                    step_id="step_04",
                    phase="compute",
                    action="combine_place_values",
                    title="일의 자리 계산",
                    purpose="첫 계산 단계를 명확히 제시",
                    target="main_expression",
                    inputs={"place": "ones"},
                    outputs={"ones_sum": ones},
                    primary=f"일의 자리 {lhs%10}+{rhs%10}={ones}입니다.",
                    short="일의 자리 계산",
                    caption=f"일의 자리 합: {ones}",
                    emphasis=["ones"],
                    animation_name="highlight",
                    duration=1.0,
                    checks=[{"type": "numeric", "key": "ones_sum"}],
                    depends_on=["step_03"],
                    teacher_note="항상 일의 자리부터 계산",
                ),
                _step(
                    step_id="step_05",
                    phase="compute",
                    action="regroup" if carry else "derive_intermediate_value",
                    title="받아올림 처리" if carry else "받아올림 없음",
                    purpose="자리값 재구성 이해",
                    target="main_expression",
                    inputs={"from": "ones", "to": "tens", "value": carry},
                    outputs={"carry": carry},
                    primary="일의 자리 합이 10 이상이므로 십의 자리로 1을 받아올림합니다." if carry else "받아올림 없이 다음 자리로 넘어갑니다.",
                    short="받아올림 확인",
                    caption="받아올림 처리",
                    emphasis=["carry"],
                    animation_name="transform",
                    duration=1.1,
                    checks=[{"type": "carry_consistent"}],
                    depends_on=["step_04"],
                    teacher_note="받아올림은 10개를 한 묶음으로 바꾸는 개념",
                ),
            ]
        )
    elif operator == "-" and lhs is not None and rhs is not None:
        borrow = (lhs % 10) < (rhs % 10)
        steps.extend(
            [
                _step(
                    step_id="step_03",
                    phase="compute",
                    action="show_place_value",
                    title="자리값 분해",
                    purpose="받아내림 판단 준비",
                    target="main_expression",
                    inputs={"lhs": lhs, "rhs": rhs},
                    outputs={"place_value_ready": True},
                    primary="자리값을 분해해 어느 자리에서 뺄셈이 어려운지 확인해요.",
                    short="자리값 확인",
                    caption="자리값 분해",
                    emphasis=["place_value"],
                    animation_name="highlight",
                    duration=1.0,
                    checks=[{"type": "place_value_valid"}],
                    depends_on=["step_02"],
                    teacher_note="받아내림 판단이 먼저",
                ),
                _step(
                    step_id="step_04",
                    phase="compute",
                    action="highlight",
                    title="받아내림 판단",
                    purpose="계산 가능 여부를 먼저 진단",
                    target="main_expression",
                    inputs={"place": "ones"},
                    outputs={"borrow_needed": borrow},
                    primary="일의 자리에서 받아내림이 필요한지 확인합니다.",
                    short="받아내림 확인",
                    caption="받아내림 필요 여부",
                    emphasis=["borrow_check"],
                    animation_name="highlight",
                    duration=1.0,
                    checks=[{"type": "boolean", "key": "borrow_needed"}],
                    depends_on=["step_03"],
                    teacher_note="먼저 판단 후 계산",
                ),
                _step(
                    step_id="step_05",
                    phase="compute",
                    action="regroup" if borrow else "derive_intermediate_value",
                    title="받아내림 처리" if borrow else "직접 계산",
                    purpose="자릿수 재구성으로 뺄셈 가능 상태 확보",
                    target="main_expression",
                    inputs={"from": "tens", "to": "ones", "value": 1 if borrow else 0},
                    outputs={"borrow_applied": borrow},
                    primary="십의 자리에서 1을 받아와 일의 자리를 10 늘려 계산합니다." if borrow else "받아내림 없이 계산합니다.",
                    short="받아내림 처리",
                    caption="받아내림 적용",
                    emphasis=["borrow"],
                    animation_name="transform",
                    duration=1.1,
                    checks=[{"type": "borrow_consistent"}],
                    depends_on=["step_04"],
                    teacher_note="받아내림의 의미를 블록/화살표로 시각화",
                ),
            ]
        )

    last = steps[-1]["id"]
    steps.append(
        _step(
            step_id="step_06",
            phase="answer",
            action="fill_answer",
            title="정답 기입",
            purpose="최종 결과를 정답 칸에 연결",
            target="answer_box",
            inputs={"answer": answer},
            outputs={"answer_written": True},
            primary=f"계산 결과를 정답 칸에 쓰면 {answer}입니다.",
            short="정답 쓰기",
            caption=f"정답: {answer}",
            emphasis=["answer"],
            animation_name="write",
            duration=0.9,
            checks=[{"type": "answer_not_null"}],
            depends_on=[last],
            teacher_note="결과와 문제 요구가 일치하는지 확인",
        )
    )
    steps.append(
        _step(
            step_id="step_07",
            phase="close",
            action="conclude",
            title="마무리",
            purpose="핵심 풀이 전략 재강조",
            target="problem_text",
            inputs={},
            outputs={"lesson_complete": True},
            primary="자리값과 중간 계산을 차근차근 확인하면 실수를 줄일 수 있어요.",
            short="풀이 마무리",
            caption="핵심: 자리값 + 중간계산",
            emphasis=["summary"],
            animation_name="fade_out",
            duration=0.8,
            checks=[{"type": "flow_complete"}],
            depends_on=["step_06"],
            teacher_note="학생이 스스로 풀이 전략을 말해보게 하기",
        )
    )

    return {
        "strategy": "explain_then_compute",
        "step_policy": "all_steps_need_narration_and_caption",
        "steps": steps,
    }


def convert_legacy_problem(legacy: dict[str, Any], *, problem_id: str) -> dict[str, Any]:
    semantic = legacy.get("semantic", {})
    render = legacy.get("render", {})
    quality = legacy.get("quality_notes", {})
    document = legacy.get("document", {})

    instruction = str(semantic.get("instruction") or "")
    expression = semantic.get("expression") if isinstance(semantic.get("expression"), dict) else {}
    lhs, operator, rhs, expr_result = _numbers_from_expression(expression)
    problem_type = _detect_problem_type(str(document.get("task_type", "")), instruction, operator)

    derived_facts = _build_derived_facts(
        problem_type=problem_type,
        lhs=lhs,
        operator=operator,
        rhs=rhs,
        instruction=instruction,
    )

    default_answer = _to_int(semantic.get("answer"))
    if default_answer is None:
        default_answer = expr_result
    if default_answer is None and derived_facts:
        for fact in reversed(derived_facts):
            val = fact.get("value")
            if isinstance(val, int):
                default_answer = val
                break

    scene_objects = _build_scene_objects(render, expression, instruction)
    solution_plan = _build_solution_plan(
        problem_type=problem_type,
        lhs=lhs,
        rhs=rhs,
        operator=operator,
        answer=default_answer,
        instruction=instruction,
    )

    warnings = list(quality.get("limitations", []))
    confidence = float(quality.get("confidence", 0.65))
    human_review_required = confidence < 0.75

    if operator not in {"+", "-", "*", "/"}:
        warnings.append("연산자 인식이 불명확합니다.")
        human_review_required = True

    if not instruction.strip() or "?" in instruction:
        warnings.append("문제 지문 인코딩 또는 OCR 품질이 낮을 수 있습니다.")
        human_review_required = True

    spec = ProblemSpecV1(
        problem_id=problem_id,
        input_meta={
            "source_filename": legacy.get("source_image", {}).get("filename"),
            "source_size": {
                "width": legacy.get("source_image", {}).get("width"),
                "height": legacy.get("source_image", {}).get("height"),
            },
            "language": document.get("language", "ko"),
            "raw_problem_text": instruction,
            "ocr_text": instruction,
            "legacy_keys": ["source_image", "document", "styles", "semantic", "render", "quality_notes"],
        },
        pedagogy={
            "grade_band": "elementary",
            "goal": "정답뿐 아니라 풀이 설명까지 생성",
            "explanation_style": "teacher_like_step_by_step",
            "must_include": ["narration", "caption", "derived_facts", "checks"],
        },
        semantic={
            "problem_type": problem_type,
            "expressions": [expression] if expression else [],
            "answer": default_answer,
            "givens": [{"lhs": lhs}, {"rhs": rhs}] if lhs is not None and rhs is not None else [],
            "unknowns": ["result"],
            "constraints": ["elementary_math", "explanation_required"],
            "concept_tags": [problem_type, "place_value", "animation_script"],
        },
        derived_facts=derived_facts,
        scene_objects=scene_objects,
        layout_template={
            "name": "worksheet_default",
            "canvas": render.get("canvas", {}),
            "regions": {
                "problem": [0.05, 0.05, 0.9, 0.2],
                "work": [0.08, 0.22, 0.84, 0.58],
                "answer": [0.66, 0.82, 0.2, 0.12],
            },
        },
        solution_plan=solution_plan,
        animation_prefs={
            "theme": "clean_math",
            "pace": "normal",
            "caption_mode": "korean_subtitles",
            "voice_mode": "tts_ready",
        },
        validation={
            "render_safe": bool(scene_objects),
            "solve_safe": default_answer is not None,
            "human_review_required": human_review_required,
            "confidence": confidence,
            "warnings": warnings,
        },
    )

    data = asdict(spec)
    if data["validation"]["confidence"] < 0.7:
        data["validation"]["human_review_required"] = True

    return data


class ProblemConverter:
    def __init__(self, *, llm_client: LLMClient | None = None, max_retries: int = 2) -> None:
        self.llm_client = llm_client
        self.max_retries = max_retries

    def convert(self, *, legacy: dict[str, Any], problem_id: str, use_llm: bool = False) -> dict[str, Any]:
        rule_based = convert_legacy_problem(legacy, problem_id=problem_id)
        if not use_llm or self.llm_client is None:
            return rule_based

        problem_text = str(legacy.get("semantic", {}).get("instruction") or "")
        user_prompt = build_user_prompt(
            problem_text=problem_text,
            ocr_text=problem_text,
            legacy_semantic=legacy.get("semantic", {}),
            legacy_render=legacy.get("render", {}),
            image_description="",
            problem_id=problem_id,
        )

        for _ in range(self.max_retries + 1):
            try:
                candidate = self.llm_client.generate_json(system_prompt=SYSTEM_PROMPT, user_prompt=user_prompt)
            except Exception as exc:
                user_prompt = build_retry_prompt(f"llm_call_failed: {exc}", user_prompt)
                continue

            result = validate_problem_spec(candidate)
            if result.is_valid:
                val = candidate.get("validation", {})
                if isinstance(val.get("confidence"), (float, int)) and val["confidence"] < 0.7:
                    val["human_review_required"] = True
                return candidate

            user_prompt = build_retry_prompt("; ".join(result.errors), str(candidate))

        rule_based["validation"]["warnings"].append("LLM 보강 실패: 규칙 기반 결과를 사용합니다.")
        rule_based["validation"]["human_review_required"] = True
        return rule_based

    def convert_file(self, path: Path, *, use_llm: bool = False) -> dict[str, Any]:
        legacy = json.loads(path.read_text(encoding="utf-8"))
        return self.convert(legacy=legacy, problem_id=path.stem, use_llm=use_llm)
