from __future__ import annotations

from .models import SceneSpec, ScriptSpec, VideoSpec


def build_video_script(grade: int, spec: VideoSpec) -> ScriptSpec:
    """
    VideoSpec 1개를 받아서 자동으로 장면 스크립트(ScriptSpec)로 변환한다.
    """

    scenes: list[SceneSpec] = []

    scenes.append(
        SceneSpec(
            type="title",
            payload={
                "text": spec.title,
                "subtitle": spec.key_understanding,
            },
            tts=spec.title,
        )
    )

    problem_text = build_problem_text(spec)
    scenes.append(
        SceneSpec(
            type="problem",
            payload={"text": problem_text},
            tts=problem_text,
        )
    )

    old_method_scene = build_old_method_scene(spec)
    if old_method_scene is not None:
        scenes.append(old_method_scene)

    difficulty_text = build_difficulty_text(spec)
    scenes.append(
        SceneSpec(
            type="concept",
            payload={
                "text": difficulty_text,
                "tone": "warning",
            },
            tts=difficulty_text,
        )
    )

    new_concept_scene = build_new_concept_scene(spec)
    scenes.append(new_concept_scene)

    visual_scene = build_visual_scene(spec)
    scenes.append(visual_scene)

    scenes.append(
        SceneSpec(
            type="wrap_up",
            payload={"text": spec.conclusion},
            tts=spec.conclusion,
        )
    )

    return ScriptSpec(
        video_id=spec.id,
        title=spec.title,
        grade=grade,
        scenes=scenes,
    )


def build_problem_text(spec: VideoSpec) -> str:
    """
    대표 예시를 바탕으로 문제 상황 문장을 만든다.
    """
    ex_type = spec.example.type
    data = spec.example.data

    if ex_type == "repeated_addition":
        addend = int(data["addend"])
        count = int(data["count"])
        return f"{addend}개씩 있는 묶음이 {count}개 있습니다. 모두 몇 개일까요?"

    if ex_type == "division_grouping":
        total = int(data["total"])
        group_size = int(data["group_size"])
        return f"{total}개를 {group_size}개씩 묶으면 몇 묶음이 될까요?"

    if ex_type == "fraction_half":
        item = str(data.get("item", "피자"))
        return f"{item}를 반으로 나누면 한 조각은 어떻게 나타낼까요?"

    if ex_type == "place_value":
        number = int(data["number"])
        return f"{number}는 한 자리 수처럼 보지 않고 어떻게 묶어서 생각할 수 있을까요?"

    if ex_type == "measurement":
        subject = str(data.get("subject", "시간과 길이"))
        return f"{subject}는 눈에 잡히지 않는데, 왜 숫자로 나타낼 수 있을까요?"

    if ex_type == "pattern_growth":
        pattern = str(data.get("pattern", "2, 4, 6, 8"))
        return f"{pattern} 같은 규칙은 어떻게 찾을 수 있을까요?"

    if ex_type == "average":
        scores = data.get("scores", [70, 80, 90])
        joined = ", ".join(str(x) for x in scores)
        return f"{joined}점처럼 여러 값이 있을 때, 전체를 대표하는 값은 어떻게 찾을까요?"

    if ex_type == "ratio":
        left = data.get("left", 2)
        right = data.get("right", 3)
        return f"{left}와 {right}를 비교할 때, 단순한 차이 말고 관계 자체를 나타낼 수 있을까요?"

    if ex_type == "graph":
        return "값이 변하는 모습을 표나 그림으로 한눈에 볼 수 있을까요?"

    if ex_type == "equation_generalization":
        return "숫자가 계속 바뀌면 매번 새 식을 써야 할까요?"
    
    if ex_type == "counting_objects":
        count = int(data.get("count", 5))
        item = str(data.get("item", "사과"))
        return f"{item}가 {count}개 있습니다. 우리는 물건 이름이 아니라 무엇을 보고 셀까요?"

    return f"{spec.concept}은 왜 필요할까요?"


def build_old_method_scene(spec: VideoSpec) -> SceneSpec | None:
    """
    새 개념이 등장하기 전의 기존 방법 장면을 만든다.
    """
    ex_type = spec.example.type
    data = spec.example.data

    if ex_type == "repeated_addition":
        addend = int(data["addend"])
        count = int(data["count"])
        expr = "+".join([str(addend)] * count)
        total = addend * count
        return SceneSpec(
            type="equation",
            payload={"expression": f"{expr}={total}"},
            tts=f"하나씩 더하면 {addend}를 {count}번 더해서 {total}가 됩니다.",
        )

    if ex_type == "division_grouping":
        total = int(data["total"])
        group_size = int(data["group_size"])
        return SceneSpec(
            type="grouping",
            payload={
                "total": total,
                "group_size": group_size,
                "label": f"{total}개를 {group_size}개씩 묶기",
            },
            tts=f"{total}개를 {group_size}개씩 하나하나 묶어 보겠습니다.",
        )

    if ex_type == "fraction_half":
        item = str(data.get("item", "피자"))
        return SceneSpec(
            type="concept",
            payload={
                "text": f"{item} 한 개를 그대로 세는 것은 쉽지만, 절반은 정수로 나타내기 어렵습니다.",
                "tone": "normal",
            },
            tts=f"{item} 한 개는 쉽게 셀 수 있지만, 절반은 정수로 나타내기 어렵습니다.",
        )

    if ex_type == "place_value":
        number = int(data["number"])
        digits = list(str(number))
        joined = ", ".join(digits)
        return SceneSpec(
            type="concept",
            payload={
                "text": f"{number}를 숫자 하나하나로만 보면 {joined}처럼 따로 보게 됩니다.",
                "tone": "normal",
            },
            tts=f"{number}를 숫자 하나하나로만 보면 구조를 놓치기 쉽습니다.",
        )

    if ex_type == "measurement":
        subject = str(data.get("subject", "시간과 길이"))
        return SceneSpec(
            type="concept",
            payload={
                "text": f"{subject}는 손으로 잡히지 않아서, 그냥 눈으로만 비교하면 정확하지 않습니다.",
                "tone": "normal",
            },
            tts=f"{subject}는 그냥 느낌으로만 비교하면 정확하지 않습니다.",
        )

    if ex_type == "pattern_growth":
        pattern = str(data.get("pattern", "2, 4, 6, 8"))
        return SceneSpec(
            type="pattern",
            payload={
                "pattern": pattern,
                "question": "어떻게 늘어나고 있을까요?",
            },
            tts=f"{pattern}를 보면 일정한 규칙이 숨어 있습니다.",
        )

    if ex_type == "average":
        scores = data.get("scores", [70, 80, 90])
        return SceneSpec(
            type="compare",
            payload={
                "items": [str(x) for x in scores],
                "label": "점수들",
            },
            tts="값이 여러 개 있을 때는 전체를 한 번에 이해하기가 어렵습니다.",
        )

    if ex_type == "ratio":
        left = data.get("left", 2)
        right = data.get("right", 3)
        return SceneSpec(
            type="compare",
            payload={
                "items": [str(left), str(right)],
                "label": "두 양의 비교",
            },
            tts=f"{left}와 {right}를 단순히 빼기만 하면 관계 전체를 보기 어렵습니다.",
        )

    if ex_type == "graph":
        table_data = data.get("table", [[1, 2], [2, 4], [3, 6]])
        return SceneSpec(
            type="compare",
            payload={
                "items": [f"{x}→{y}" for x, y in table_data],
                "label": "표의 값",
            },
            tts="값을 줄마다 읽으면 흐름을 한눈에 보기 어렵습니다.",
        )

    if ex_type == "equation_generalization":
        examples = data.get("examples", ["3+5", "4+5", "10+5"])
        return SceneSpec(
            type="compare",
            payload={
                "items": examples,
                "label": "비슷한 식들",
            },
            tts="숫자가 바뀔 때마다 식을 새로 쓰면 길고 번거롭습니다.",
        )
    
    if ex_type == "counting_objects":
        count = int(data.get("count", 5))
        item = str(data.get("item", "사과"))
        return SceneSpec(
            type="concept",
            payload={
                "text": f"{item}를 하나씩 보아도 되지만, 수학에서는 전체 개수 {count}를 한 번에 생각할 수 있습니다.",
                "tone": "normal",
            },
            tts=f"{item}를 하나씩 보아도 되지만, 수학에서는 전체 개수를 한 번에 생각할 수 있습니다.",
        )

    return None


def build_difficulty_text(spec: VideoSpec) -> str:
    """
    기존 방식의 한계 문장을 만든다.
    """
    concept_map = {
        "곱셈": "같은 더하기가 계속되면 길고 헷갈립니다.",
        "나눗셈": "전체를 공평하게 나누거나 묶음 수를 찾으려면 기준이 필요합니다.",
        "분수 기초": "정수만으로는 전체의 일부를 나타내기 어렵습니다.",
        "자릿값": "큰 수를 한 자리씩만 보면 묶음의 구조를 이해하기 어렵습니다.",
        "측정": "보이지 않는 양은 공통 기준이 없으면 정확하게 비교하기 어렵습니다.",
        "규칙": "숫자가 늘어나는 모습을 하나씩만 보면 전체 규칙을 보기 어렵습니다.",
        "평균": "값이 많아지면 전체를 대표하는 생각이 필요합니다.",
        "비율": "두 양의 관계는 차이만으로 설명되지 않을 때가 많습니다.",
        "그래프": "변화는 숫자만 나열해서는 한눈에 파악하기 어렵습니다.",
        "식의 일반화": "많은 경우를 하나하나 쓰는 대신 한 번에 나타내는 방법이 필요합니다.",
    }

    return concept_map.get(
        spec.concept,
        "기존 방법만으로는 생각을 짧고 정확하게 나타내기 어렵습니다.",
    )


def build_new_concept_scene(spec: VideoSpec) -> SceneSpec:
    """
    새 개념이 등장하는 핵심 장면을 만든다.
    """
    ex_type = spec.example.type
    data = spec.example.data

    if ex_type == "repeated_addition":
        addend = int(data["addend"])
        count = int(data["count"])
        repeated = "+".join([str(addend)] * count)
        return SceneSpec(
            type="transform",
            payload={
                "from_expression": repeated,
                "to_expression": f"{count}\\times{addend}",
            },
            tts=f"그래서 {count} 곱하기 {addend}로 짧게 나타냅니다.",
        )

    if ex_type == "division_grouping":
        total = int(data["total"])
        group_size = int(data["group_size"])
        return SceneSpec(
            type="equation",
            payload={
                "expression": f"{total}\\div{group_size}",
            },
            tts=f"이렇게 묶음을 찾는 것을 {total} 나누기 {group_size}로 나타냅니다.",
        )

    if ex_type == "fraction_half":
        item = str(data.get("item", "피자"))
        return SceneSpec(
            type="fraction",
            payload={
                "shape": "circle",
                "parts": 2,
                "selected": 1,
                "label": "\\frac{1}{2}",
                "item": item,
            },
            tts=f"이럴 때는 전체를 두 부분으로 나눈 하나, 즉 이분의 일로 나타냅니다.",
        )

    if ex_type == "place_value":
        number = int(data["number"])
        tens = number // 10
        ones = number % 10
        return SceneSpec(
            type="transform",
            payload={
                "from_expression": str(number),
                "to_expression": f"{tens}\\times10+{ones}",
            },
            tts=f"{number}는 {tens}개의 십과 {ones}개의 일로 볼 수 있습니다.",
        )

    if ex_type == "measurement":
        return SceneSpec(
            type="concept",
            payload={
                "text": spec.key_understanding,
                "tone": "emphasis",
            },
            tts=spec.key_understanding,
        )

    if ex_type == "pattern_growth":
        rule_text = str(data.get("rule_text", "일정한 규칙으로 늘어납니다."))
        return SceneSpec(
            type="concept",
            payload={
                "text": rule_text,
                "tone": "emphasis",
            },
            tts=rule_text,
        )

    if ex_type == "average":
        scores = [int(x) for x in data.get("scores", [70, 80, 90])]
        average_value = sum(scores) / len(scores)
        if float(average_value).is_integer():
            average_label = str(int(average_value))
        else:
            average_label = str(round(average_value, 2))
        return SceneSpec(
            type="equation",
            payload={
                "expression": f"\\frac{{{'+'.join(str(x) for x in scores)}}}{{{len(scores)}}}={average_label}",
            },
            tts=f"여러 값을 하나로 대표할 때는 평균을 사용합니다. 여기서는 평균이 {average_label}입니다.",
        )

    if ex_type == "ratio":
        left = data.get("left", 2)
        right = data.get("right", 3)
        return SceneSpec(
            type="equation",
            payload={
                "expression": f"{left}:{right}",
            },
            tts=f"두 양의 관계를 {left} 대 {right}처럼 비로 나타낼 수 있습니다.",
        )

    if ex_type == "graph":
        return SceneSpec(
            type="concept",
            payload={
                "text": "값의 변화를 한눈에 보려면 그래프로 나타내는 것이 좋습니다.",
                "tone": "emphasis",
            },
            tts="값의 변화를 한눈에 보려면 그래프로 나타내는 것이 좋습니다.",
        )

    if ex_type == "equation_generalization":
        variable_expression = str(data.get("variable_expression", "x+5"))
        return SceneSpec(
            type="equation",
            payload={
                "expression": variable_expression,
            },
            tts=f"숫자가 바뀌는 많은 경우를 한 번에 나타내기 위해 식을 사용합니다. 예를 들어 {variable_expression}처럼 쓸 수 있습니다.",
        )

    return SceneSpec(
        type="concept",
        payload={
            "text": spec.key_understanding,
            "tone": "emphasis",
        },
        tts=spec.key_understanding,
    )


def build_visual_scene(spec: VideoSpec) -> SceneSpec:
    """
    시각 모델 장면을 만든다.
    """
    visual_model = spec.visual_model
    ex_type = spec.example.type
    data = spec.example.data

    if visual_model == "array" and ex_type == "repeated_addition":
        addend = int(data["addend"])
        count = int(data["count"])
        return SceneSpec(
            type="array",
            payload={
                "rows": count,
                "cols": addend,
                "label": f"{count}줄에 {addend}개씩",
            },
            tts=f"{count}줄에 {addend}개씩 놓아 보면 반복되는 구조를 한눈에 볼 수 있습니다.",
        )

    if visual_model == "grouping" and ex_type == "division_grouping":
        total = int(data["total"])
        group_size = int(data["group_size"])
        return SceneSpec(
            type="grouping",
            payload={
                "total": total,
                "group_size": group_size,
                "label": f"{group_size}개씩 묶기",
            },
            tts=f"{total}개를 {group_size}개씩 묶어 보면 몇 묶음인지 알 수 있습니다.",
        )

    if visual_model == "fraction_circle":
        parts = int(data.get("parts", 2))
        selected = int(data.get("selected", 1))
        return SceneSpec(
            type="fraction",
            payload={
                "shape": "circle",
                "parts": parts,
                "selected": selected,
                "label": f"\\frac{{{selected}}}{{{parts}}}",
            },
            tts="전체와 부분의 관계를 그림으로 보면 분수를 더 쉽게 이해할 수 있습니다.",
        )

    if visual_model == "place_value_blocks":
        number = int(data["number"])
        tens = number // 10
        ones = number % 10
        return SceneSpec(
            type="compare",
            payload={
                "items": [f"십이 {tens}개", f"일이 {ones}개"],
                "label": f"{number}의 묶음",
            },
            tts=f"{number}를 십의 묶음과 일의 낱개로 나누어 보면 자릿값을 이해할 수 있습니다.",
        )

    if visual_model == "measurement_compare":
        return SceneSpec(
            type="compare",
            payload={
                "items": ["짧다", "길다", "빠르다", "느리다"],
                "label": "비교만으로는 부족한 상태",
            },
            tts="느낌으로만 비교하던 것을 숫자로 바꾸면 더 정확해집니다.",
        )

    if visual_model == "pattern":
        pattern = str(data.get("pattern", "2, 4, 6, 8"))
        return SceneSpec(
            type="pattern",
            payload={
                "pattern": pattern,
                "question": "무엇이 반복될까요?",
            },
            tts="패턴을 보면 다음 수와 규칙을 예측할 수 있습니다.",
        )

    if visual_model == "graph":
        table_data = data.get("table", [[1, 2], [2, 4], [3, 6]])
        return SceneSpec(
            type="graph",
            payload={
                "points": table_data,
                "x_label": str(data.get("x_label", "입력")),
                "y_label": str(data.get("y_label", "출력")),
            },
            tts="그래프는 변화하는 관계를 눈으로 보이게 해 줍니다.",
        )

    if visual_model == "expression_compare":
        examples = data.get("examples", ["3+5", "4+5", "10+5"])
        variable_expression = str(data.get("variable_expression", "x+5"))
        return SceneSpec(
            type="transform",
            payload={
                "from_expression": ",\\ ".join(examples),
                "to_expression": variable_expression,
            },
            tts="비슷한 많은 식을 하나의 일반적인 식으로 나타낼 수 있습니다.",
        )

    return SceneSpec(
        type="concept",
        payload={
            "text": spec.key_understanding,
            "tone": "normal",
        },
        tts=spec.key_understanding,
    )


def build_scripts_for_grade(grade: int, videos: list[VideoSpec]) -> list[ScriptSpec]:
    """
    한 학년의 여러 VideoSpec을 ScriptSpec 리스트로 변환한다.
    """
    return [build_video_script(grade, video) for video in videos]