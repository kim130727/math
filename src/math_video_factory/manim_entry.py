from __future__ import annotations

import json
import os
from pathlib import Path

from manim import *


def _env_str(name: str, default: str) -> str:
    return os.getenv(name, default).strip()


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    return int(raw)


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    return float(raw)


# -------------------------------------------------------------------
# Shorts / render configuration
# -------------------------------------------------------------------
config.pixel_width = _env_int("VIDEO_WIDTH", 1080)
config.pixel_height = _env_int("VIDEO_HEIGHT", 1920)
config.frame_rate = _env_int("FRAME_RATE", 30)
config.frame_width = _env_float("FRAME_WIDTH", 9.0)
config.frame_height = _env_float("FRAME_HEIGHT", 16.0)
config.background_color = "#F7F7F7"

FONT = _env_str("DEFAULT_FONT", "Malgun Gothic")

SCRIPT_JSON_PATH = Path(_env_str("MATH_SCRIPT_JSON", ""))
TIMING_JSON_PATH = Path(_env_str("MATH_TIMING_JSON", ""))


def load_script() -> dict:
    if not SCRIPT_JSON_PATH.exists():
        raise FileNotFoundError(
            f"MATH_SCRIPT_JSON 파일을 찾을 수 없습니다: {SCRIPT_JSON_PATH}"
        )

    data = json.loads(SCRIPT_JSON_PATH.read_text(encoding="utf-8"))
    if "scenes" not in data or not isinstance(data["scenes"], list):
        raise ValueError("script JSON 형식이 올바르지 않습니다. scenes 배열이 필요합니다.")
    return data


def load_timings() -> list[float]:
    """
    timing JSON 두 형식을 모두 허용:
    1) {"durations": [2.1, 3.4, ...]}
    2) {"items": [{"duration_sec": 2.1}, ...]}
    """
    if not TIMING_JSON_PATH.exists():
        return []

    data = json.loads(TIMING_JSON_PATH.read_text(encoding="utf-8"))

    durations = data.get("durations")
    if isinstance(durations, list):
        result: list[float] = []
        for x in durations:
            try:
                result.append(float(x))
            except Exception:
                result.append(3.0)
        return result

    items = data.get("items")
    if isinstance(items, list):
        result = []
        for item in items:
            try:
                result.append(float(item.get("duration_sec", 3.0)))
            except Exception:
                result.append(3.0)
        return result

    return []


def fit_text_box(
    text: str,
    *,
    max_width: float,
    font_size: int = 40,
    color=BLACK,
    line_spacing: float = 0.9,
    weight: str = NORMAL,
) -> Text:
    obj = Text(
        text,
        font=FONT,
        font_size=font_size,
        color=color,
        line_spacing=line_spacing,
        weight=weight,
    )
    if obj.width > max_width:
        obj.scale_to_fit_width(max_width)
    return obj


def fit_math_box(
    expression: str,
    *,
    max_width: float,
    font_size: int = 72,
    color=BLACK,
) -> Mobject:
    try:
        obj = MathTex(expression, color=color, font_size=font_size)
    except Exception:
        obj = fit_text_box(
            expression,
            max_width=max_width,
            font_size=int(font_size * 0.6),
            color=color,
            line_spacing=0.9,
            weight=BOLD,
        )

    if obj.width > max_width:
        obj.scale_to_fit_width(max_width)
    return obj


class AutoVideoScene(Scene):
    def construct(self) -> None:
        self.script = load_script()
        self.timings = load_timings()
        self.scene_idx = 0

        self.max_text_width = config.frame_width - 1.0
        self.max_math_width = config.frame_width - 1.2

        self.text_color = BLACK
        self.accent_color = DARK_BLUE
        self.warning_color = RED
        self.result_color = GREEN
        self.subtle_color = GREY_D

        for scene in self.script["scenes"]:
            scene_type = str(scene.get("type", "")).strip().lower()

            # 기존 payload 구조도 허용하고,
            # 새 구조(장면 필드가 바로 아래 있음)도 허용
            payload = self._normalize_payload(scene)

            if scene_type == "title":
                self.render_title(payload)
            elif scene_type == "hook":
                self.render_hook(payload)
            elif scene_type == "problem":
                self.render_problem(payload)
            elif scene_type == "equation":
                self.render_equation(payload)
            elif scene_type in {"observation", "abstraction", "concept", "realization", "example"}:
                self.render_concept(payload)
            elif scene_type in {"transform", "transformation"}:
                self.render_transform(payload)
            elif scene_type == "grouping":
                self.render_grouping(payload)
            elif scene_type == "wrap_up":
                self.render_wrap_up(payload)
            else:
                self.render_unknown(scene_type, payload)

            self.scene_idx += 1

    # ---------------------------------------------------------------
    # normalization helpers
    # ---------------------------------------------------------------
    def _normalize_payload(self, scene: dict) -> dict:
        """
        scene 안의 payload가 있으면 그것을 우선 사용하고,
        없으면 scene의 주요 필드를 payload처럼 정리한다.
        """
        payload = scene.get("payload")
        if isinstance(payload, dict) and payload:
            return payload

        normalized: dict = {}

        # 자주 쓰는 공통 필드
        for key in [
            "text",
            "subtitle",
            "visual",
            "tts",
            "focus_word",
            "tone",
            "label",
        ]:
            if key in scene:
                normalized[key] = scene[key]

        # transform 관련
        sequence = scene.get("sequence")
        if isinstance(sequence, list) and sequence:
            normalized["sequence"] = sequence
            if len(sequence) >= 2:
                normalized["from_expression"] = str(sequence[0])
                normalized["to_expression"] = str(sequence[-1])

        if "from_expression" in scene:
            normalized["from_expression"] = scene["from_expression"]
        if "to_expression" in scene:
            normalized["to_expression"] = scene["to_expression"]

        # problem 관련
        items = scene.get("items")
        if isinstance(items, list):
            normalized["items"] = items

        # grouping 관련
        for key in ["total", "group_size"]:
            if key in scene:
                normalized[key] = scene[key]

        # fallback
        if "text" not in normalized:
            normalized["text"] = ""

        return normalized

    # ---------------------------------------------------------------
    # timing helpers
    # ---------------------------------------------------------------
    def sec(self, default: float) -> float:
        if 0 <= self.scene_idx < len(self.timings):
            return max(float(self.timings[self.scene_idx]), 0.8)
        return default

    def hold_after(self, used: float, default_total: float) -> None:
        total = self.sec(default_total)
        remain = max(total - used, 0.15)
        self.wait(remain)

    # ---------------------------------------------------------------
    # common layout helpers
    # ---------------------------------------------------------------
    def make_top_label(self, text: str, color=GREY_D) -> Text:
        obj = fit_text_box(
            text,
            max_width=self.max_text_width,
            font_size=28,
            color=color,
            line_spacing=0.9,
            weight=MEDIUM,
        )
        obj.to_edge(UP, buff=0.45)
        return obj

    def clear_scene(self, *mobs: Mobject, run_time: float = 0.35) -> None:
        existing = [m for m in mobs if m is not None]
        if existing:
            self.play(*[FadeOut(m) for m in existing], run_time=run_time)

    # ---------------------------------------------------------------
    # scene renderers
    # ---------------------------------------------------------------
    def render_title(self, payload: dict) -> None:
        main_text = str(payload.get("text", "")).strip() or "수학"
        subtitle = str(payload.get("subtitle", "")).strip()

        eyebrow = self.make_top_label("오늘의 질문", color=self.subtle_color)

        title = fit_text_box(
            main_text,
            max_width=self.max_text_width,
            font_size=58,
            color=self.text_color,
            line_spacing=0.92,
            weight=BOLD,
        ).move_to(UP * 1.7)

        subtitle_obj = None
        if subtitle:
            subtitle_obj = fit_text_box(
                subtitle,
                max_width=self.max_text_width - 0.2,
                font_size=34,
                color=self.accent_color,
                line_spacing=0.95,
                weight=MEDIUM,
            )
            subtitle_obj.next_to(title, DOWN, buff=0.45)

        underline = Line(
            LEFT * 2.2,
            RIGHT * 2.2,
            color=self.accent_color,
            stroke_width=6,
        ).next_to(subtitle_obj or title, DOWN, buff=0.5)

        used = 0.0
        self.play(FadeIn(eyebrow, shift=DOWN * 0.2), run_time=0.35)
        used += 0.35
        self.play(Write(title), run_time=0.7)
        used += 0.7

        if subtitle_obj is not None:
            self.play(FadeIn(subtitle_obj, shift=UP * 0.2), run_time=0.45)
            used += 0.45

        self.play(Create(underline), run_time=0.35)
        used += 0.35

        self.hold_after(used, 2.8)
        self.clear_scene(eyebrow, title, subtitle_obj, underline)

    def render_hook(self, payload: dict) -> None:
        text = str(payload.get("text", "")).strip() or "생각의 문을 열어 봅시다."

        eyebrow = self.make_top_label("생각 열기", color=self.subtle_color)

        question_box = RoundedRectangle(
            width=config.frame_width - 0.8,
            height=4.0,
            corner_radius=0.35,
            stroke_color=self.accent_color,
            stroke_width=5,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(UP * 0.4)

        question = fit_text_box(
            text,
            max_width=question_box.width - 0.8,
            font_size=46,
            color=self.accent_color,
            line_spacing=0.96,
            weight=BOLD,
        ).move_to(question_box.get_center())

        mark = Text(
            "?",
            font=FONT,
            font_size=96,
            color=self.accent_color,
            weight=BOLD,
        ).next_to(question_box, DOWN, buff=0.35)

        used = 0.0
        self.play(FadeIn(eyebrow, shift=DOWN * 0.2), run_time=0.25)
        used += 0.25
        self.play(Create(question_box), run_time=0.4)
        used += 0.4
        self.play(FadeIn(question, shift=UP * 0.15), run_time=0.45)
        used += 0.45
        self.play(FadeIn(mark, scale=0.9), run_time=0.25)
        used += 0.25

        self.hold_after(used, 3.2)
        self.clear_scene(eyebrow, question_box, question, mark)

    def render_problem(self, payload: dict) -> None:
        text = str(payload.get("text", "")).strip() or "문제를 생각해 봅시다."
        items = payload.get("items", [])
        items = items if isinstance(items, list) else []

        eyebrow = self.make_top_label("문제", color=self.subtle_color)

        q_box = RoundedRectangle(
            width=config.frame_width - 0.8,
            height=4.2,
            corner_radius=0.3,
            stroke_color=self.accent_color,
            stroke_width=4,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(UP * 0.6)

        question = fit_text_box(
            text,
            max_width=q_box.width - 0.7,
            font_size=40,
            color=self.text_color,
            line_spacing=0.95,
            weight=MEDIUM,
        ).move_to(q_box.get_center())

        items_obj = None
        if items:
            items_text = " · ".join(str(x) for x in items)
            items_obj = fit_text_box(
                items_text,
                max_width=self.max_text_width,
                font_size=28,
                color=self.accent_color,
                line_spacing=0.9,
                weight=MEDIUM,
            ).next_to(q_box, DOWN, buff=0.35)

        hint = fit_text_box(
            "천천히 보면 공통점이 보여요",
            max_width=self.max_text_width,
            font_size=26,
            color=self.subtle_color,
            line_spacing=0.9,
            weight=MEDIUM,
        )
        hint.next_to(items_obj or q_box, DOWN, buff=0.28)

        used = 0.0
        self.play(FadeIn(eyebrow, shift=DOWN * 0.2), run_time=0.3)
        used += 0.3
        self.play(Create(q_box), run_time=0.45)
        used += 0.45
        self.play(FadeIn(question, shift=UP * 0.2), run_time=0.45)
        used += 0.45

        if items_obj is not None:
            self.play(FadeIn(items_obj), run_time=0.25)
            used += 0.25

        self.play(FadeIn(hint), run_time=0.25)
        used += 0.25

        self.hold_after(used, 4.0)
        self.clear_scene(eyebrow, q_box, question, items_obj, hint)

    def render_equation(self, payload: dict) -> None:
        expression = str(payload.get("expression", "")).strip() or "1+1=2"

        eyebrow = self.make_top_label("생각을 식으로 나타내기", color=self.subtle_color)

        expr = fit_math_box(
            expression,
            max_width=self.max_math_width,
            font_size=88,
            color=self.text_color,
        ).move_to(UP * 0.3)

        desc = fit_text_box(
            "하나씩 세면 이렇게 길어질 수 있어요",
            max_width=self.max_text_width,
            font_size=32,
            color=self.warning_color,
            line_spacing=0.9,
            weight=MEDIUM,
        ).next_to(expr, DOWN, buff=0.7)

        used = 0.0
        self.play(FadeIn(eyebrow, shift=DOWN * 0.2), run_time=0.3)
        used += 0.3
        self.play(Write(expr), run_time=0.7)
        used += 0.7
        self.play(FadeIn(desc, shift=UP * 0.2), run_time=0.35)
        used += 0.35

        self.hold_after(used, 3.8)
        self.clear_scene(eyebrow, expr, desc)

    def render_concept(self, payload: dict) -> None:
        text = str(payload.get("text", "")).strip() or "중요한 생각"
        tone = str(payload.get("tone", "normal")).strip().lower()

        eyebrow_text = "핵심 생각"
        box_color = self.accent_color
        text_color = self.text_color

        if tone == "warning":
            eyebrow_text = "왜 새 방법이 필요할까요?"
            box_color = self.warning_color
            text_color = self.warning_color

        eyebrow = self.make_top_label(eyebrow_text, color=self.subtle_color)

        box = RoundedRectangle(
            width=config.frame_width - 0.8,
            height=3.8,
            corner_radius=0.35,
            stroke_color=box_color,
            stroke_width=4,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(UP * 0.2)

        concept = fit_text_box(
            text,
            max_width=box.width - 0.8,
            font_size=40,
            color=text_color,
            line_spacing=0.96,
            weight=MEDIUM,
        ).move_to(box.get_center())

        focus_word = str(payload.get("focus_word", "")).strip()
        focus_obj = None
        if focus_word:
            focus_obj = fit_text_box(
                focus_word,
                max_width=self.max_text_width,
                font_size=28,
                color=box_color,
                line_spacing=0.9,
                weight=BOLD,
            ).next_to(box, DOWN, buff=0.4)

        used = 0.0
        self.play(FadeIn(eyebrow, shift=DOWN * 0.2), run_time=0.3)
        used += 0.3
        self.play(Create(box), run_time=0.45)
        used += 0.45
        self.play(FadeIn(concept, shift=UP * 0.15), run_time=0.4)
        used += 0.4

        if focus_obj is not None:
            self.play(FadeIn(focus_obj), run_time=0.25)
            used += 0.25

        self.hold_after(used, 3.5)
        self.clear_scene(eyebrow, box, concept, focus_obj)

    def render_transform(self, payload: dict) -> None:
        sequence = payload.get("sequence", [])
        sequence = sequence if isinstance(sequence, list) else []

        if len(sequence) >= 2:
            from_expr = str(sequence[0]).strip()
            to_expr = str(sequence[-1]).strip()
        else:
            from_expr = str(payload.get("from_expression", "")).strip() or "1+1+1"
            to_expr = str(payload.get("to_expression", "")).strip() or "3"

        eyebrow = self.make_top_label("바뀌어도 남는 것", color=self.subtle_color)

        from_obj = fit_text_box(
            from_expr,
            max_width=self.max_text_width,
            font_size=42,
            color=self.text_color,
            line_spacing=0.92,
            weight=MEDIUM,
        ).move_to(UP * 2.3)

        arrow = Arrow(
            start=UP * 1.0,
            end=DOWN * 0.1,
            buff=0.0,
            color=self.accent_color,
            stroke_width=8,
            max_tip_length_to_length_ratio=0.16,
        )

        to_obj = fit_text_box(
            to_expr,
            max_width=self.max_text_width,
            font_size=72,
            color=self.accent_color,
            line_spacing=0.92,
            weight=BOLD,
        ).move_to(DOWN * 1.9)

        mid_steps = None
        if len(sequence) > 2:
            mids = "   →   ".join(str(x) for x in sequence[1:-1])
            mid_steps = fit_text_box(
                mids,
                max_width=self.max_text_width,
                font_size=24,
                color=self.subtle_color,
                line_spacing=0.9,
                weight=MEDIUM,
            ).move_to(DOWN * 0.55)

        tip = fit_text_box(
            "겉모습은 달라도 공통 구조는 남아요",
            max_width=self.max_text_width,
            font_size=28,
            color=self.accent_color,
            line_spacing=0.9,
            weight=MEDIUM,
        ).to_edge(DOWN, buff=0.8)

        used = 0.0
        self.play(FadeIn(eyebrow, shift=DOWN * 0.2), run_time=0.25)
        used += 0.25
        self.play(Write(from_obj), run_time=0.45)
        used += 0.45
        self.play(GrowArrow(arrow), run_time=0.35)
        used += 0.35

        if mid_steps is not None:
            self.play(FadeIn(mid_steps), run_time=0.25)
            used += 0.25

        self.play(TransformFromCopy(from_obj, to_obj), run_time=0.6)
        used += 0.6
        self.play(FadeIn(tip, shift=UP * 0.15), run_time=0.3)
        used += 0.3

        self.hold_after(used, 3.8)
        self.clear_scene(eyebrow, from_obj, arrow, mid_steps, to_obj, tip)

    def render_grouping(self, payload: dict) -> None:
        total = int(payload.get("total", 9))
        group_size = int(payload.get("group_size", 3))
        label = str(payload.get("label", f"{total}개를 {group_size}개씩 묶기")).strip()

        eyebrow = self.make_top_label("하나하나 묶어 보기", color=self.subtle_color)
        label_obj = fit_text_box(
            label,
            max_width=self.max_text_width,
            font_size=34,
            color=self.text_color,
            line_spacing=0.9,
            weight=MEDIUM,
        ).move_to(UP * 2.5)

        dots = VGroup()
        cols = min(total, 5)
        rows = (total + cols - 1) // cols
        spacing_x = 1.1
        spacing_y = 0.95
        start_x = -((cols - 1) * spacing_x) / 2
        start_y = 1.2

        for idx in range(total):
            r = idx // cols
            c = idx % cols
            dot = Dot(
                point=np.array(
                    [
                        start_x + c * spacing_x,
                        start_y - r * spacing_y,
                        0,
                    ]
                ),
                radius=0.12,
                color=self.accent_color,
            )
            dots.add(dot)

        groups = VGroup()
        for start in range(0, total, group_size):
            chunk = dots[start : start + group_size]
            if len(chunk) == 0:
                continue
            box = SurroundingRectangle(
                VGroup(*chunk),
                color=self.result_color,
                buff=0.18,
                corner_radius=0.15,
                stroke_width=4,
            )
            groups.add(box)

        summary = fit_text_box(
            f"{group_size}개씩 묶으면 몇 묶음인지 볼 수 있어요",
            max_width=self.max_text_width,
            font_size=30,
            color=self.result_color,
            line_spacing=0.9,
            weight=MEDIUM,
        ).to_edge(DOWN, buff=0.9)

        used = 0.0
        self.play(FadeIn(eyebrow, shift=DOWN * 0.2), run_time=0.25)
        used += 0.25
        self.play(FadeIn(label_obj, shift=UP * 0.15), run_time=0.35)
        used += 0.35
        self.play(FadeIn(dots, lag_ratio=0.08), run_time=0.65)
        used += 0.65

        for g in groups:
            self.play(Create(g), run_time=0.25)
            used += 0.25

        self.play(FadeIn(summary, shift=UP * 0.15), run_time=0.3)
        used += 0.3

        self.hold_after(used, 4.4)
        self.clear_scene(eyebrow, label_obj, dots, groups, summary)

    def render_wrap_up(self, payload: dict) -> None:
        text = str(payload.get("text", "")).strip() or "오늘의 정리"

        badge = self.make_top_label("한 줄 정리", color=self.result_color)

        box = RoundedRectangle(
            width=config.frame_width - 0.7,
            height=4.4,
            corner_radius=0.4,
            stroke_color=self.result_color,
            stroke_width=5,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(UP * 0.2)

        summary = fit_text_box(
            text,
            max_width=box.width - 0.8,
            font_size=44,
            color=self.text_color,
            line_spacing=0.97,
            weight=BOLD,
        ).move_to(box.get_center())

        sparkle_left = Star(
            n=5,
            outer_radius=0.18,
            color=self.result_color,
            fill_opacity=1,
        ).next_to(box, LEFT, buff=0.25)

        sparkle_right = Star(
            n=5,
            outer_radius=0.18,
            color=self.result_color,
            fill_opacity=1,
        ).next_to(box, RIGHT, buff=0.25)

        used = 0.0
        self.play(FadeIn(badge, shift=DOWN * 0.2), run_time=0.25)
        used += 0.25
        self.play(Create(box), run_time=0.45)
        used += 0.45
        self.play(FadeIn(summary, shift=UP * 0.15), run_time=0.5)
        used += 0.5
        self.play(FadeIn(sparkle_left), FadeIn(sparkle_right), run_time=0.25)
        used += 0.25

        self.hold_after(used, 3.6)
        self.clear_scene(badge, box, summary, sparkle_left, sparkle_right)

    def render_unknown(self, scene_type: str, payload: dict) -> None:
        eyebrow = self.make_top_label("지원되지 않는 장면", color=self.warning_color)
        title = fit_text_box(
            f"scene type: {scene_type or 'unknown'}",
            max_width=self.max_text_width,
            font_size=34,
            color=self.warning_color,
            line_spacing=0.9,
            weight=BOLD,
        ).move_to(UP * 0.8)

        body = fit_text_box(
            json.dumps(payload, ensure_ascii=False, indent=2),
            max_width=self.max_text_width,
            font_size=22,
            color=self.text_color,
            line_spacing=0.9,
        ).next_to(title, DOWN, buff=0.45)

        used = 0.0
        self.play(FadeIn(eyebrow), run_time=0.2)
        used += 0.2
        self.play(FadeIn(title), run_time=0.3)
        used += 0.3
        self.play(FadeIn(body), run_time=0.35)
        used += 0.35

        self.hold_after(used, 2.5)
        self.clear_scene(eyebrow, title, body)