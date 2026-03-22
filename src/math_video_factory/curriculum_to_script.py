from __future__ import annotations

from .models import ExampleSpec, SceneSpec, ScriptSpec, VideoSpec


def _safe_text(value: object, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def _safe_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _keyword_text(video: VideoSpec) -> str:
    if not video.keywords:
        return ""
    return ", ".join(video.keywords)


def _build_title_scene(video: VideoSpec) -> SceneSpec:
    subtitle = f"{video.concept} | {video.abstraction_stage}"
    return SceneSpec(
        type="title",
        payload={
            "text": video.title,
            "subtitle": subtitle,
        },
        tts=f"{video.title}. {video.concept}에 대해 함께 생각해 봅시다.",
    )


def _build_problem_scene(video: VideoSpec) -> SceneSpec:
    question = (
        f"{video.title}에서 가장 중요한 생각은 무엇일까요?"
    )
    body = video.key_understanding
    return SceneSpec(
        type="problem",
        payload={
            "text": question,
            "body": body,
        },
        tts=f"질문입니다. {video.key_understanding}",
    )


def _build_concept_scene(video: VideoSpec) -> SceneSpec:
    keyword_text = _keyword_text(video)
    body = video.key_understanding
    if keyword_text:
        body = f"{body}\n핵심 낱말: {keyword_text}"

    return SceneSpec(
        type="concept",
        payload={
            "text": body,
        },
        tts=video.key_understanding,
    )


def _build_wrap_up_scene(video: VideoSpec) -> SceneSpec:
    closing = video.conclusion or video.key_understanding
    return SceneSpec(
        type="wrap_up",
        payload={
            "text": closing,
        },
        tts=closing,
    )


def _build_example_scenes(video: VideoSpec) -> list[SceneSpec]:
    example = video.example
    if not example or not example.type:
        return []

    builders = {
        "pattern_growth": _build_pattern_growth_scenes,
        "repeated_addition": _build_repeated_addition_scenes,
        "counting_objects": _build_counting_objects_scenes,
        "division_grouping": _build_division_grouping_scenes,
        "place_value": _build_place_value_scenes,
        "fraction_half": _build_fraction_half_scenes,
        "measurement": _build_measurement_scenes,
        "average": _build_average_scenes,
        "ratio": _build_ratio_scenes,
    }

    builder = builders.get(example.type)
    if builder is None:
        return [_build_unknown_example_scene(video, example)]

    return builder(video, example)


def _build_unknown_example_scene(video: VideoSpec, example: ExampleSpec) -> SceneSpec:
    parts = []
    for key, value in (example.data or {}).items():
        if value in ("", None):
            continue
        parts.append(f"{key}: {value}")

    body = "\n".join(parts) if parts else "예시 정보를 확인해 주세요."

    return SceneSpec(
        type="concept",
        payload={
            "text": f"예시 타입: {example.type}\n{body}".strip(),
        },
        tts=f"{video.title}의 예시는 {example.type} 유형입니다.",
    )


def _build_pattern_growth_scenes(video: VideoSpec, example: ExampleSpec) -> list[SceneSpec]:
    pattern = _safe_text(example.data.get("pattern"))
    rule_text = _safe_text(example.data.get("rule_text"))

    scenes: list[SceneSpec] = [
        SceneSpec(
            type="pattern",
            payload={
                "pattern": pattern,
                "question": "어떤 규칙이 보이나요?",
            },
            tts=f"이 패턴을 보세요. {pattern}",
        )
    ]

    if rule_text:
        scenes.append(
            SceneSpec(
                type="concept",
                payload={
                    "text": rule_text,
                },
                tts=rule_text,
            )
        )

    return scenes


def _build_repeated_addition_scenes(video: VideoSpec, example: ExampleSpec) -> list[SceneSpec]:
    addend = _safe_int(example.data.get("addend"), 0)
    count = _safe_int(example.data.get("count"), 0)

    if addend <= 0 or count <= 0:
        return [
            SceneSpec(
                type="concept",
                payload={
                    "text": "반복 덧셈 예시 값이 올바르지 않습니다.",
                },
                tts="반복 덧셈 예시 값을 확인해 주세요.",
            )
        ]

    expression = " + ".join([str(addend)] * count)
    result = addend * count

    return [
        SceneSpec(
            type="grouping",
            payload={
                "label": f"{addend}이 {count}번 반복됩니다.",
                "total": addend * count,
                "group_size": addend,
            },
            tts=f"{addend}이 {count}번 반복됩니다.",
        ),
        SceneSpec(
            type="equation",
            payload={
                "expression": f"{expression} = {result}",
            },
            tts=f"{addend}를 {count}번 더하면 {result}입니다.",
        ),
        SceneSpec(
            type="transform",
            payload={
                "from_expression": expression,
                "to_expression": f"{addend} × {count} = {result}",
            },
            tts=f"이것을 더 짧게 {addend} 곱하기 {count}는 {result}라고 쓸 수 있습니다.",
        ),
    ]


def _build_counting_objects_scenes(video: VideoSpec, example: ExampleSpec) -> list[SceneSpec]:
    count = _safe_int(example.data.get("count"), 0)
    item = _safe_text(example.data.get("item"), "물건")

    if count <= 0:
        return [
            SceneSpec(
                type="concept",
                payload={
                    "text": "세기 예시의 count 값이 올바르지 않습니다.",
                },
                tts="세기 예시 값을 확인해 주세요.",
            )
        ]

    return [
        SceneSpec(
            type="concept",
            payload={
                "text": f"{item}을 하나씩 세어 보면 모두 {count}개입니다.",
            },
            tts=f"{item}을 하나씩 세어 보면 모두 {count}개입니다.",
        ),
        SceneSpec(
            type="equation",
            payload={
                "expression": f"{item} {count}개",
            },
            tts=f"{count}라는 수는 {item}의 개수를 나타냅니다.",
        ),
    ]


def _build_division_grouping_scenes(video: VideoSpec, example: ExampleSpec) -> list[SceneSpec]:
    total = _safe_int(example.data.get("total"), 0)
    group_size = _safe_int(example.data.get("group_size"), 0)

    if total <= 0 or group_size <= 0:
        return [
            SceneSpec(
                type="concept",
                payload={
                    "text": "나눗셈 묶기 예시 값이 올바르지 않습니다.",
                },
                tts="나눗셈 묶기 예시 값을 확인해 주세요.",
            )
        ]

    groups = total // group_size
    remainder = total % group_size

    scenes = [
        SceneSpec(
            type="grouping",
            payload={
                "label": f"{total}개를 {group_size}개씩 묶어 봅시다.",
                "total": total,
                "group_size": group_size,
            },
            tts=f"{total}개를 {group_size}개씩 묶어 봅시다.",
        ),
        SceneSpec(
            type="equation",
            payload={
                "expression": f"{total} ÷ {group_size} = {groups}",
            },
            tts=f"{total} 나누기 {group_size}는 {groups}입니다.",
        ),
    ]

    if remainder:
        scenes.append(
            SceneSpec(
                type="concept",
                payload={
                    "text": f"그리고 {remainder}개가 남습니다.",
                },
                tts=f"그리고 {remainder}개가 남습니다.",
            )
        )

    return scenes


def _build_place_value_scenes(video: VideoSpec, example: ExampleSpec) -> list[SceneSpec]:
    number = _safe_int(example.data.get("number"), 0)

    tens = number // 10
    ones = number % 10

    return [
        SceneSpec(
            type="concept",
            payload={
                "text": f"{number}은(는) 십이 {tens}개, 일이 {ones}개입니다.",
            },
            tts=f"{number}은 십이 {tens}개, 일이 {ones}개입니다.",
        ),
        SceneSpec(
            type="equation",
            payload={
                "expression": f"{number} = {tens}×10 + {ones}",
            },
            tts=f"{number}은 {tens} 곱하기 10 더하기 {ones}로 볼 수 있습니다.",
        ),
    ]


def _build_fraction_half_scenes(video: VideoSpec, example: ExampleSpec) -> list[SceneSpec]:
    item = _safe_text(example.data.get("item"), "하나의 대상")

    return [
        SceneSpec(
            type="fraction",
            payload={
                "item": item,
                "label": "1/2",
                "parts": 2,
                "selected": 1,
            },
            tts=f"{item}을 두 부분으로 똑같이 나누면 그중 한 부분은 이분의 일입니다.",
        ),
        SceneSpec(
            type="concept",
            payload={
                "text": "분수는 전체를 같은 크기로 나눈 뒤, 그중 얼마를 보는지 나타냅니다.",
            },
            tts="분수는 전체를 같은 크기로 나눈 뒤, 그중 얼마를 보는지 나타냅니다.",
        ),
    ]


def _build_measurement_scenes(video: VideoSpec, example: ExampleSpec) -> list[SceneSpec]:
    subject = _safe_text(example.data.get("subject"), "대상")

    return [
        SceneSpec(
            type="concept",
            payload={
                "text": f"{subject}의 길이나 크기를 재면 눈대중보다 더 정확하게 알 수 있습니다.",
            },
            tts=f"{subject}의 길이나 크기를 재면 눈대중보다 더 정확하게 알 수 있습니다.",
        ),
        SceneSpec(
            type="concept",
            payload={
                "text": "측정은 비교를 더 분명하게 만들어 줍니다.",
            },
            tts="측정은 비교를 더 분명하게 만들어 줍니다.",
        ),
    ]


def _build_average_scenes(video: VideoSpec, example: ExampleSpec) -> list[SceneSpec]:
    raw_scores = example.data.get("scores", [])
    scores = [int(x) for x in raw_scores] if isinstance(raw_scores, list) else []

    if not scores:
        return [
            SceneSpec(
                type="concept",
                payload={
                    "text": "평균 예시의 scores 값이 비어 있습니다.",
                },
                tts="평균 예시 값을 확인해 주세요.",
            )
        ]

    total = sum(scores)
    count = len(scores)
    average = total / count

    if average.is_integer():
        average_text = str(int(average))
    else:
        average_text = f"{average:.1f}"

    return [
        SceneSpec(
            type="concept",
            payload={
                "text": f"점수 {scores}의 합은 {total}입니다.",
            },
            tts=f"점수의 합은 {total}입니다.",
        ),
        SceneSpec(
            type="equation",
            payload={
                "expression": f"{total} ÷ {count} = {average_text}",
            },
            tts=f"합을 {count}로 나누면 평균은 {average_text}입니다.",
        ),
    ]


def _build_ratio_scenes(video: VideoSpec, example: ExampleSpec) -> list[SceneSpec]:
    left = _safe_int(example.data.get("left"), 0)
    right = _safe_int(example.data.get("right"), 0)

    if left <= 0 or right <= 0:
        return [
            SceneSpec(
                type="concept",
                payload={
                    "text": "비 예시 값이 올바르지 않습니다.",
                },
                tts="비 예시 값을 확인해 주세요.",
            )
        ]

    return [
        SceneSpec(
            type="compare",
            payload={
                "label": "두 양의 관계",
                "items": [left, right],
            },
            tts=f"{left} 대 {right}처럼 두 양의 관계를 비교할 수 있습니다.",
        ),
        SceneSpec(
            type="equation",
            payload={
                "expression": f"{left}:{right}",
            },
            tts=f"이 비는 {left} 대 {right}라고 읽습니다.",
        ),
    ]


def build_video_script(grade: int, video: VideoSpec) -> ScriptSpec:
    scenes: list[SceneSpec] = []
    scenes.append(_build_title_scene(video))
    scenes.append(_build_problem_scene(video))
    scenes.extend(_build_example_scenes(video))
    scenes.append(_build_concept_scene(video))
    scenes.append(_build_wrap_up_scene(video))

    return ScriptSpec(
        grade=grade,
        video_id=video.id,
        title=video.title,
        scenes=scenes,
    )