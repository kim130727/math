from __future__ import annotations

import json
from pathlib import Path

from manim import *


PROJECT_DIR = Path(__file__).resolve().parent
SCRIPT_FILE = PROJECT_DIR / "script.txt"
TIMINGS_FILE = PROJECT_DIR / "timings.json"

FONT = "Malgun Gothic"


def load_timings() -> list[float]:
    if TIMINGS_FILE.exists():
        data = json.loads(TIMINGS_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "durations" in data:
            return [float(x) for x in data["durations"]]
    return []


def load_script(script_file: Path) -> list[dict]:
    if not script_file.exists():
        raise FileNotFoundError(f"스크립트 파일이 없습니다: {script_file}")

    scenes: list[dict] = []

    lines = script_file.read_text(encoding="utf-8").splitlines()
    for line_no, raw in enumerate(lines, start=1):
        line = raw.strip()

        if not line or line.startswith("#"):
            continue

        parts = [p.strip() for p in line.split("|")]
        scene_type = parts[0].lower()

        scenes.append(
            {
                "line_no": line_no,
                "type": scene_type,
                "parts": parts[1:],
                "raw": raw,
            }
        )

    if not scenes:
        raise ValueError("script.txt에 장면 데이터가 없습니다.")

    return scenes


class WhyMultiplication(Scene):
    def construct(self) -> None:
        self.camera.background_color = WHITE

        self.timings = load_timings()
        self.script = load_script(SCRIPT_FILE)
        self.scene_index = 0

        self.TEXT_COLOR = BLACK
        self.EMPHASIS_COLOR = DARK_BLUE
        self.WARNING_COLOR = RED
        self.HIGHLIGHT_COLOR = ORANGE
        self.RESULT_COLOR = GREEN

        for scene_data in self.script:
            scene_type = scene_data["type"]

            if scene_type == "title":
                self.render_title(scene_data["parts"])
            elif scene_type == "question":
                self.render_question(scene_data["parts"])
            elif scene_type == "explain":
                self.render_explain(scene_data["parts"])
            elif scene_type == "count_add":
                self.render_count_add(scene_data["parts"])
            elif scene_type == "highlight":
                self.render_highlight(scene_data["parts"])
            elif scene_type == "meaning":
                self.render_meaning(scene_data["parts"])
            elif scene_type == "short_expr":
                self.render_short_expr(scene_data["parts"])
            elif scene_type == "grid":
                self.render_grid(scene_data["parts"])
            elif scene_type == "conclusion":
                self.render_conclusion(scene_data["parts"])
            else:
                raise ValueError(
                    f"{scene_data['line_no']}번째 줄: 알 수 없는 장면 종류입니다: {scene_type}"
                )

            self.scene_index += 1

    def sec(self, default: float) -> float:
        if 0 <= self.scene_index < len(self.timings):
            return float(self.timings[self.scene_index])
        return default

    def render_title(self, parts: list[str]) -> None:
        if len(parts) < 2:
            raise ValueError("title 장면은 'title|제목|부제' 형식이어야 합니다.")

        title_text, subtitle_text = parts[0], parts[1]

        title = Text(
            title_text,
            font=FONT,
            font_size=42,
            color=self.TEXT_COLOR,
        )
        subtitle = Text(
            subtitle_text,
            font=FONT,
            font_size=26,
            color=self.TEXT_COLOR,
        )
        subtitle.next_to(title, DOWN, buff=0.35)
        group = VGroup(title, subtitle).move_to(ORIGIN)

        self.play(Write(title), run_time=1.0)
        self.play(FadeIn(subtitle, shift=UP), run_time=0.6)
        self.wait(max(self.sec(2.8) - 1.6, 0.2))
        self.play(FadeOut(group), run_time=0.4)

    def render_question(self, parts: list[str]) -> None:
        if len(parts) < 2:
            raise ValueError("question 장면은 'question|수식|질문문장' 형식이어야 합니다.")

        formula_text, question_text = parts[0], parts[1]

        formula = MathTex(formula_text, color=self.TEXT_COLOR).scale(1.4)
        formula.to_edge(UP, buff=1.1)

        question = Text(
            question_text,
            font=FONT,
            font_size=32,
            color=self.TEXT_COLOR,
        )
        question.next_to(formula, DOWN, buff=0.8)

        self.play(Write(formula), run_time=0.8)
        self.play(FadeIn(question, shift=UP), run_time=0.6)
        self.wait(max(self.sec(5.0) - 1.4, 0.2))
        self.play(FadeOut(formula), FadeOut(question), run_time=0.4)

    def render_explain(self, parts: list[str]) -> None:
        if len(parts) < 3:
            raise ValueError(
                "explain 장면은 'explain|윗문장|아랫문장|반복덧셈수식' 형식이어야 합니다."
            )

        text1 = Text(
            parts[0],
            font=FONT,
            font_size=34,
            color=self.TEXT_COLOR,
        ).to_edge(UP, buff=0.8)

        text2 = Text(
            parts[1],
            font=FONT,
            font_size=34,
            color=self.HIGHLIGHT_COLOR,
        )
        text2.next_to(text1, DOWN, buff=0.35)

        repeated_add = MathTex(parts[2], color=self.TEXT_COLOR).scale(1.05)
        repeated_add.next_to(text2, DOWN, buff=0.75)

        self.play(Write(text1), run_time=0.7)
        self.play(Write(text2), run_time=0.7)
        self.play(Write(repeated_add), run_time=0.8)
        self.wait(max(self.sec(4.5) - 2.2, 0.2))
        self.play(FadeOut(text1), FadeOut(text2), FadeOut(repeated_add), run_time=0.4)

    def render_count_add(self, parts: list[str]) -> None:
        if len(parts) < 2:
            raise ValueError("count_add 장면은 'count_add|더하는수|몇번' 형식이어야 합니다.")

        addend = int(parts[0])
        count = int(parts[1])

        title = Text(
            f"{addend}을 {count}번 더해 볼까요?",
            font=FONT,
            font_size=30,
            color=self.TEXT_COLOR,
        ).to_edge(UP, buff=1.0)

        sums = []
        running = 0
        expr_parts = []
        for _ in range(count):
            running += addend
            expr_parts.append(str(addend))
            if len(expr_parts) == 1:
                sums.append(str(addend))
            else:
                sums.append(f"{'+'.join(expr_parts)}={running}")

        current = MathTex(sums[0], color=self.TEXT_COLOR).scale(1.0).move_to(DOWN * 0.2)

        self.play(FadeIn(title), run_time=0.4)
        self.play(Write(current), run_time=0.4)

        total_time = self.sec(3.2)
        per_step = max((total_time - 0.8) / max(count - 1, 1), 0.2)

        for expr in sums[1:]:
            new_expr = MathTex(expr, color=self.TEXT_COLOR).move_to(current)
            self.play(Transform(current, new_expr), run_time=per_step)

        self.play(FadeOut(title), FadeOut(current), run_time=0.4)

    def render_highlight(self, parts: list[str]) -> None:
        if len(parts) < 2:
            raise ValueError("highlight 장면은 'highlight|강조할수식|강조문장' 형식이어야 합니다.")

        expr = MathTex(parts[0], color=self.TEXT_COLOR).scale(1.05).move_to(UP * 0.2)
        box = SurroundingRectangle(expr, color=self.WARNING_COLOR, buff=0.25)

        warn = Text(
            parts[1],
            font=FONT,
            font_size=26,
            color=self.WARNING_COLOR,
        )
        warn.next_to(box, DOWN, buff=0.35)

        self.play(Write(expr), run_time=0.6)
        self.play(Create(box), run_time=0.5)
        self.play(FadeIn(warn), run_time=0.3)
        self.wait(max(self.sec(3.5) - 1.4, 0.2))
        self.play(FadeOut(expr), FadeOut(box), FadeOut(warn), run_time=0.4)

    def render_meaning(self, parts: list[str]) -> None:
        if len(parts) < 2:
            raise ValueError("meaning 장면은 'meaning|문장1|문장2' 형식이어야 합니다.")

        sentence1 = Text(
            parts[0],
            font=FONT,
            font_size=32,
            color=self.TEXT_COLOR,
        ).to_edge(UP, buff=0.9)

        sentence2 = Text(
            parts[1],
            font=FONT,
            font_size=32,
            color=self.EMPHASIS_COLOR,
        )
        sentence2.next_to(sentence1, DOWN, buff=0.35)

        self.play(Write(sentence1), run_time=0.7)
        self.play(Write(sentence2), run_time=0.7)
        self.wait(max(self.sec(5.0) - 1.4, 0.2))
        self.play(FadeOut(sentence1), FadeOut(sentence2), run_time=0.4)

    def render_short_expr(self, parts: list[str]) -> None:
        if len(parts) < 2:
            raise ValueError(
                "short_expr 장면은 'short_expr|반복덧셈수식|곱셈수식' 형식이어야 합니다."
            )

        add_expr = MathTex(parts[0], color=self.TEXT_COLOR).move_to(UP * 0.4)
        mul_expr = MathTex(parts[1], color=self.HIGHLIGHT_COLOR).scale(1.25)
        mul_expr.next_to(add_expr, DOWN, buff=1.2)
        arrow = Arrow(
            add_expr.get_bottom(),
            mul_expr.get_top(),
            buff=0.18,
            color=self.TEXT_COLOR,
        )

        self.play(Write(add_expr), run_time=0.6)
        self.play(GrowArrow(arrow), run_time=0.4)
        self.play(Write(mul_expr), run_time=0.6)
        self.wait(max(self.sec(3.5) - 1.6, 0.2))
        self.play(FadeOut(add_expr), FadeOut(arrow), FadeOut(mul_expr), run_time=0.4)

    def render_grid(self, parts: list[str]) -> None:
        if len(parts) < 6:
            raise ValueError(
                "grid 장면은 'grid|행수|열수|윗문장|왼쪽라벨|아래라벨|결과수식' 형식이어야 합니다."
            )

        rows = int(parts[0])
        cols = int(parts[1])
        title_text = parts[2]
        left_label_text = parts[3]
        bottom_label_text = parts[4]
        result_text = parts[5]

        title = Text(
            title_text,
            font=FONT,
            font_size=30,
            color=self.TEXT_COLOR,
        ).to_edge(UP, buff=0.7)

        self.play(FadeIn(title), run_time=0.4)

        dots = VGroup()
        spacing = 0.42
        grid_center_shift = DOWN * 1.4

        for r in range(rows):
            row_group = VGroup()
            for c in range(cols):
                dot = Dot(radius=0.048, color=self.EMPHASIS_COLOR)
                dot.move_to(
                    LEFT * ((cols - 1) * spacing / 2)
                    + RIGHT * (c * spacing)
                    + UP * ((rows - 1) * spacing / 2)
                    - DOWN * (r * spacing)
                    + grid_center_shift
                )
                row_group.add(dot)
            dots.add(row_group)

        grid_draw_time = 1.8
        for row in dots:
            self.play(FadeIn(row, lag_ratio=0.08), run_time=grid_draw_time / max(rows, 1))

        brace_left = Brace(dots, LEFT, color=self.TEXT_COLOR)
        brace_bottom = Brace(dots, DOWN, color=self.TEXT_COLOR)

        left_label = Text(
            left_label_text,
            font=FONT,
            font_size=22,
            color=self.TEXT_COLOR,
        ).next_to(brace_left, LEFT, buff=0.18)

        bottom_label = Text(
            bottom_label_text,
            font=FONT,
            font_size=20,
            color=self.TEXT_COLOR,
        ).next_to(brace_bottom, DOWN, buff=0.12)

        self.play(GrowFromCenter(brace_left), FadeIn(left_label), run_time=0.5)
        self.play(GrowFromCenter(brace_bottom), FadeIn(bottom_label), run_time=0.5)

        total = MathTex(result_text, color=self.RESULT_COLOR).scale(0.95)
        total.next_to(bottom_label, DOWN, buff=0.18)
        self.play(Write(total), run_time=0.5)

        used = 0.4 + 1.8 + 0.5 + 0.5 + 0.5
        self.wait(max(self.sec(4.0) - used, 0.2))

        self.play(
            FadeOut(title),
            FadeOut(brace_left),
            FadeOut(brace_bottom),
            FadeOut(left_label),
            FadeOut(bottom_label),
            FadeOut(dots),
            FadeOut(total),
            run_time=0.5,
        )

    def render_conclusion(self, parts: list[str]) -> None:
        if len(parts) < 5:
            raise ValueError(
                "conclusion 장면은 "
                "'conclusion|제목|문장1|문장2|긴수식|짧은수식' 형식이어야 합니다."
            )

        final1 = Text(
            parts[0],
            font=FONT,
            font_size=36,
            color=self.TEXT_COLOR,
        ).to_edge(UP, buff=0.75)

        final2 = Text(
            parts[1],
            font=FONT,
            font_size=30,
            color=self.TEXT_COLOR,
        )
        final2.next_to(final1, DOWN, buff=0.45)

        final3 = Text(
            parts[2],
            font=FONT,
            font_size=30,
            color=self.HIGHLIGHT_COLOR,
        )
        final3.next_to(final2, DOWN, buff=0.28)

        final4 = MathTex(parts[3], color=self.TEXT_COLOR).scale(0.9)
        final4.next_to(final3, DOWN, buff=0.55)

        final5 = MathTex(parts[4], color=self.EMPHASIS_COLOR).scale(1.1)
        final5.next_to(final4, DOWN, buff=0.5)

        self.play(Write(final1), run_time=0.7)
        self.play(FadeIn(final2, shift=UP), run_time=0.5)
        self.play(FadeIn(final3, shift=UP), run_time=0.5)
        self.play(Write(final4), run_time=0.7)
        self.play(TransformFromCopy(final4, final5), run_time=0.7)

        self.wait(max(self.sec(5.0) - 3.1, 0.2))