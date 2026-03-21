from __future__ import annotations

import json
import os
from pathlib import Path

from manim import *

from math_video_factory.config import DEFAULT_FONT


def load_script_data() -> dict:
    script_path = os.environ.get("VIDEO_SCRIPT_PATH")
    if not script_path:
        raise ValueError("VIDEO_SCRIPT_PATH 환경변수가 설정되지 않았습니다.")

    path = Path(script_path)
    if not path.exists():
        raise FileNotFoundError(f"script JSON 파일이 없습니다: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"script JSON 형식이 올바르지 않습니다: {path}")

    scenes = data.get("scenes")
    if not isinstance(scenes, list):
        raise ValueError(f"script JSON에 scenes 리스트가 없습니다: {path}")

    return data


def load_timing_data() -> list[float]:
    timing_path = os.environ.get("VIDEO_TIMING_PATH")
    if not timing_path:
        return []

    path = Path(timing_path)
    if not path.exists():
        return []

    data = json.loads(path.read_text(encoding="utf-8"))
    durations = data.get("durations", [])

    if not isinstance(durations, list):
        return []

    cleaned: list[float] = []
    for value in durations:
        try:
            cleaned.append(float(value))
        except (TypeError, ValueError):
            cleaned.append(0.0)

    return cleaned


class AutoVideoScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE
        self.text_color = BLACK
        self.emphasis_color = DARK_BLUE
        self.warning_color = RED
        self.result_color = GREEN

        script_data = load_script_data()
        self.scenes_data = script_data["scenes"]
        self.scene_durations = load_timing_data()

        for idx, scene in enumerate(self.scenes_data):
            self.current_scene_index = idx

            scene_type = scene["type"]
            payload = scene.get("payload", {})
            tts_text = str(scene.get("tts", "")).strip()

            if scene_type == "title":
                self.render_title(payload, tts_text)
            elif scene_type == "problem":
                self.render_problem(payload, tts_text)
            elif scene_type == "concept":
                self.render_concept(payload, tts_text)
            elif scene_type == "equation":
                self.render_equation(payload, tts_text)
            elif scene_type == "transform":
                self.render_transform(payload, tts_text)
            elif scene_type == "array":
                self.render_array(payload, tts_text)
            elif scene_type == "grouping":
                self.render_grouping(payload, tts_text)
            elif scene_type == "fraction":
                self.render_fraction(payload, tts_text)
            elif scene_type == "compare":
                self.render_compare(payload, tts_text)
            elif scene_type == "pattern":
                self.render_pattern(payload, tts_text)
            elif scene_type == "graph":
                self.render_graph(payload, tts_text)
            elif scene_type == "wrap_up":
                self.render_wrap_up(payload, tts_text)
            else:
                raise ValueError(f"지원하지 않는 scene type: {scene_type}")
            
    def hold_time(self, tts_text: str, minimum: float = 1.2) -> float:
        """
        가능하면 실제 측정된 mp3 길이를 사용하고,
        없으면 문자 수 기반 추정치로 fallback 한다.
        """
        idx = getattr(self, "current_scene_index", -1)

        if 0 <= idx < len(getattr(self, "scene_durations", [])):
            measured = float(self.scene_durations[idx])

            # 음성 끝과 장면 전환이 너무 붙지 않게 소량 여유 추가
            return max(measured + 0.25, minimum)

        estimated = max(len(tts_text) * 0.08, minimum)
        return min(estimated, 5.0)

    def make_text(
        self,
        text: str,
        *,
        font_size: int = 32,
        color=BLACK,
        line_spacing: float = 0.9,
    ) -> Text:
        return Text(
            text,
            font=DEFAULT_FONT,
            font_size=font_size,
            color=color,
            line_spacing=line_spacing,
        )

    def render_title(self, payload: dict, tts_text: str) -> None:
        title_text = str(payload.get("text", "제목"))
        subtitle_text = str(payload.get("subtitle", "")).strip()

        title = self.make_text(
            title_text,
            font_size=40,
            color=self.text_color,
        )

        if subtitle_text:
            subtitle = self.make_text(
                subtitle_text,
                font_size=24,
                color=self.emphasis_color,
            )
            subtitle.next_to(title, DOWN, buff=0.35)
            group = VGroup(title, subtitle).move_to(ORIGIN)

            self.play(Write(title), run_time=0.9)
            self.play(FadeIn(subtitle, shift=UP), run_time=0.5)
            self.wait(self.hold_time(tts_text, 1.4))
            self.play(FadeOut(group), run_time=0.4)
        else:
            title.move_to(ORIGIN)
            self.play(Write(title), run_time=0.9)
            self.wait(self.hold_time(tts_text, 1.4))
            self.play(FadeOut(title), run_time=0.4)

    def render_problem(self, payload: dict, tts_text: str) -> None:
        text = self.make_text(
            str(payload.get("text", "")),
            font_size=30,
            color=self.text_color,
        )
        text.move_to(ORIGIN)

        self.play(FadeIn(text, shift=UP), run_time=0.7)
        self.wait(self.hold_time(tts_text))
        self.play(FadeOut(text), run_time=0.4)

    def render_concept(self, payload: dict, tts_text: str) -> None:
        text_value = str(payload.get("text", ""))
        tone = str(payload.get("tone", "normal"))

        color = self.text_color
        if tone == "warning":
            color = self.warning_color
        elif tone == "emphasis":
            color = self.emphasis_color

        text = self.make_text(
            text_value,
            font_size=28,
            color=color,
        )
        text.move_to(ORIGIN)

        self.play(FadeIn(text), run_time=0.6)
        self.wait(self.hold_time(tts_text))
        self.play(FadeOut(text), run_time=0.4)

    def render_equation(self, payload: dict, tts_text: str) -> None:
        expression = str(payload.get("expression", ""))
        expr = MathTex(expression, color=self.text_color).scale(1.2)

        self.play(Write(expr), run_time=0.8)
        self.wait(self.hold_time(tts_text))
        self.play(FadeOut(expr), run_time=0.4)

    def render_transform(self, payload: dict, tts_text: str) -> None:
        from_expression = str(payload.get("from_expression", ""))
        to_expression = str(payload.get("to_expression", ""))

        from_expr = MathTex(from_expression, color=self.text_color).scale(1.0)
        from_expr.move_to(UP * 1.2)

        to_expr = MathTex(to_expression, color=self.emphasis_color).scale(1.2)
        to_expr.move_to(DOWN * 1.0)

        arrow = Arrow(
            from_expr.get_bottom(),
            to_expr.get_top(),
            buff=0.2,
            color=self.text_color,
        )

        self.play(Write(from_expr), run_time=0.6)
        self.play(GrowArrow(arrow), run_time=0.4)
        self.play(Write(to_expr), run_time=0.6)
        self.wait(self.hold_time(tts_text))
        self.play(FadeOut(from_expr), FadeOut(arrow), FadeOut(to_expr), run_time=0.4)

    def render_array(self, payload: dict, tts_text: str) -> None:
        rows = int(payload.get("rows", 1))
        cols = int(payload.get("cols", 1))
        label_text = str(payload.get("label", "")).strip()

        dots = VGroup()
        spacing = 0.5

        for r in range(rows):
            row_group = VGroup()
            for c in range(cols):
                dot = Dot(radius=0.06, color=BLUE)
                dot.move_to(
                    LEFT * ((cols - 1) * spacing / 2)
                    + RIGHT * c * spacing
                    + UP * ((rows - 1) * spacing / 2)
                    - DOWN * r * spacing
                )
                row_group.add(dot)
            dots.add(row_group)

        label = None
        if label_text:
            label = self.make_text(
                label_text,
                font_size=24,
                color=self.text_color,
            ).to_edge(UP, buff=0.7)

        if label:
            self.play(FadeIn(label), run_time=0.4)

        for row in dots:
            self.play(FadeIn(row, lag_ratio=0.08), run_time=0.25)

        self.wait(self.hold_time(tts_text))
        fade_targets = [dots]
        if label:
            fade_targets.append(label)
        self.play(*[FadeOut(x) for x in fade_targets], run_time=0.4)

    def render_grouping(self, payload: dict, tts_text: str) -> None:
        total = int(payload.get("total", 1))
        group_size = int(payload.get("group_size", 1))
        label_text = str(payload.get("label", "")).strip()

        dots = VGroup()
        spacing = 0.5
        per_row = 6

        for i in range(total):
            dot = Dot(radius=0.055, color=BLUE)
            row = i // per_row
            col = i % per_row
            dot.move_to(
                LEFT * ((per_row - 1) * spacing / 2)
                + RIGHT * col * spacing
                + UP * 1.0
                - DOWN * row * spacing
            )
            dots.add(dot)

        boxes = VGroup()
        if group_size > 0:
            for start in range(0, total, group_size):
                chunk = dots[start:start + group_size]
                if len(chunk) == group_size:
                    box = SurroundingRectangle(VGroup(*chunk), color=GREEN, buff=0.12)
                    boxes.add(box)

        label = None
        if label_text:
            label = self.make_text(
                label_text,
                font_size=24,
                color=self.text_color,
            ).to_edge(UP, buff=0.7)

        if label:
            self.play(FadeIn(label), run_time=0.4)

        self.play(FadeIn(dots), run_time=0.6)

        for box in boxes:
            self.play(Create(box), run_time=0.25)

        self.wait(self.hold_time(tts_text))
        fade_targets = [dots, boxes]
        if label:
            fade_targets.append(label)
        self.play(*[FadeOut(x) for x in fade_targets], run_time=0.4)

    def render_fraction(self, payload: dict, tts_text: str) -> None:
        parts = int(payload.get("parts", 2))
        selected = int(payload.get("selected", 1))
        label_text = str(payload.get("label", "\\frac{1}{2}"))

        if parts <= 0:
            parts = 2
        selected = max(0, min(selected, parts))

        sectors = VGroup()
        circle_radius = 1.5

        for i in range(parts):
            start_angle = i * TAU / parts
            sector = Sector(
                outer_radius=circle_radius,
                start_angle=start_angle,
                angle=TAU / parts,
                fill_color=ORANGE if i < selected else LIGHT_GRAY,
                fill_opacity=0.9,
                stroke_color=BLACK,
                stroke_width=2,
            )
            sectors.add(sector)

        fraction_label = MathTex(label_text, color=self.emphasis_color).scale(1.2)
        fraction_label.next_to(sectors, DOWN, buff=0.6)

        self.play(FadeIn(sectors), run_time=0.8)
        self.play(Write(fraction_label), run_time=0.5)
        self.wait(self.hold_time(tts_text))
        self.play(FadeOut(sectors), FadeOut(fraction_label), run_time=0.4)

    def render_compare(self, payload: dict, tts_text: str) -> None:
        items = payload.get("items", [])
        label_text = str(payload.get("label", "")).strip()

        if not isinstance(items, list):
            items = []

        boxes = VGroup()
        for item in items:
            rect = RoundedRectangle(
                width=2.2,
                height=1.0,
                corner_radius=0.15,
                stroke_color=BLACK,
                stroke_width=2,
                fill_color=WHITE,
                fill_opacity=1,
            )
            txt = self.make_text(
                str(item),
                font_size=24,
                color=self.text_color,
            ).move_to(rect.get_center())
            boxes.add(VGroup(rect, txt))

        boxes.arrange(RIGHT, buff=0.35)
        boxes.move_to(ORIGIN)

        label = None
        if label_text:
            label = self.make_text(
                label_text,
                font_size=24,
                color=self.emphasis_color,
            ).to_edge(UP, buff=0.7)

        if label:
            self.play(FadeIn(label), run_time=0.4)

        self.play(FadeIn(boxes, lag_ratio=0.15), run_time=0.8)
        self.wait(self.hold_time(tts_text))
        fade_targets = [boxes]
        if label:
            fade_targets.append(label)
        self.play(*[FadeOut(x) for x in fade_targets], run_time=0.4)

    def render_pattern(self, payload: dict, tts_text: str) -> None:
        pattern = str(payload.get("pattern", "2, 4, 6, 8"))
        question = str(payload.get("question", "")).strip()

        pattern_text = self.make_text(
            pattern,
            font_size=34,
            color=self.text_color,
        ).move_to(UP * 0.3)

        question_obj = None
        if question:
            question_obj = self.make_text(
                question,
                font_size=24,
                color=self.emphasis_color,
            ).next_to(pattern_text, DOWN, buff=0.45)

        self.play(Write(pattern_text), run_time=0.8)
        if question_obj:
            self.play(FadeIn(question_obj, shift=UP), run_time=0.4)

        self.wait(self.hold_time(tts_text))
        fade_targets = [pattern_text]
        if question_obj:
            fade_targets.append(question_obj)
        self.play(*[FadeOut(x) for x in fade_targets], run_time=0.4)

    def render_graph(self, payload: dict, tts_text: str) -> None:
        points = payload.get("points", [[1, 2], [2, 4], [3, 6]])
        x_label = str(payload.get("x_label", "x"))
        y_label = str(payload.get("y_label", "y"))

        if not isinstance(points, list) or not points:
            points = [[1, 2], [2, 4], [3, 6]]

        axes = Axes(
            x_range=[0, max(p[0] for p in points) + 1, 1],
            y_range=[0, max(p[1] for p in points) + 1, 1],
            x_length=6,
            y_length=4,
            axis_config={"color": BLACK},
        )

        axis_labels = axes.get_axis_labels(
            self.make_text(x_label, font_size=20, color=self.text_color),
            self.make_text(y_label, font_size=20, color=self.text_color),
        )

        dots = VGroup()
        for x, y in points:
            dots.add(Dot(axes.c2p(x, y), radius=0.07, color=BLUE))

        self.play(Create(axes), FadeIn(axis_labels), run_time=0.9)
        self.play(FadeIn(dots, lag_ratio=0.15), run_time=0.8)
        self.wait(self.hold_time(tts_text))
        self.play(FadeOut(axes), FadeOut(axis_labels), FadeOut(dots), run_time=0.4)

    def render_wrap_up(self, payload: dict, tts_text: str) -> None:
        text = self.make_text(
            str(payload.get("text", "")),
            font_size=30,
            color=self.emphasis_color,
        ).move_to(ORIGIN)

        box = SurroundingRectangle(
            text,
            color=self.emphasis_color,
            buff=0.3,
            corner_radius=0.18,
        )

        self.play(FadeIn(text, shift=UP), run_time=0.6)
        self.play(Create(box), run_time=0.4)
        self.wait(self.hold_time(tts_text, 1.5))
        self.play(FadeOut(text), FadeOut(box), run_time=0.4)