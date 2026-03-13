import json
from pathlib import Path
from manim import *

FONT = "Malgun Gothic"

def load_timings():
    path = Path("timings.json")
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}

class WhyMultiplication(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        T = load_timings()

        TEXT_COLOR = BLACK
        EMPHASIS_COLOR = DARK_BLUE
        WARNING_COLOR = RED
        HIGHLIGHT_COLOR = ORANGE
        RESULT_COLOR = GREEN

        def sec(name, default):
            return T.get(name, default)

        # 1. 제목
        title = Text("왜 곱하기를 배워야 할까요?", font=FONT, font_size=42, color=TEXT_COLOR)
        subtitle = Text("곱하기는 반복되는 더하기를 빠르게 표현하는 방법", font=FONT, font_size=26, color=TEXT_COLOR)
        subtitle.next_to(title, DOWN, buff=0.35)
        title_group = VGroup(title, subtitle).move_to(ORIGIN)

        self.play(Write(title), run_time=1.0)
        self.play(FadeIn(subtitle, shift=UP), run_time=0.6)
        self.wait(max(sec("01_title", 2.8) - 1.6, 0.2))
        self.play(FadeOut(title_group), run_time=0.4)

        # 2. 질문 장면
        q = MathTex("8 \\times 8 = 64", color=TEXT_COLOR).scale(1.4)
        q.to_edge(UP, buff=1.1)
        q2 = Text("그런데 왜 곱하기를 배워야 할까요?", font=FONT, font_size=32, color=TEXT_COLOR)
        q2.next_to(q, DOWN, buff=0.8)

        self.play(Write(q), run_time=0.8)
        self.play(FadeIn(q2, shift=UP), run_time=0.6)
        self.wait(max(sec("02_question", 5.0) - 1.4, 0.2))
        self.play(FadeOut(q), FadeOut(q2), run_time=0.4)

        # 3. 곱하기를 모르면
        text1 = Text("곱하기를 배우지 않았다면", font=FONT, font_size=34, color=TEXT_COLOR).to_edge(UP, buff=0.8)
        text2 = Text("8을 8번 더해야 합니다.", font=FONT, font_size=34, color=HIGHLIGHT_COLOR)
        text2.next_to(text1, DOWN, buff=0.35)
        repeated_add = MathTex("8+8+8+8+8+8+8+8=64", color=TEXT_COLOR).scale(1.15)
        repeated_add.next_to(text2, DOWN, buff=0.9)

        self.play(Write(text1), run_time=0.7)
        self.play(Write(text2), run_time=0.7)
        self.wait(max(sec("03_no_multiply", 4.5) - 1.4, 0.2))
        self.play(Write(repeated_add), run_time=0.8)
        self.wait(max(sec("04_repeat_add_intro", 1.5) - 0.8, 0.2))

        # 4. 반복 덧셈 숫자 카운트
        running_title = Text("8을 8번 더해 볼까요?", font=FONT, font_size=32, color=TEXT_COLOR)
        running_title.next_to(repeated_add, DOWN, buff=0.6)
        self.play(FadeIn(running_title), run_time=0.4)

        sums = ["8","8+8=16","8+8+8=24","8+8+8+8=32","8+8+8+8+8=40","8+8+8+8+8+8=48","8+8+8+8+8+8+8=56","8+8+8+8+8+8+8+8=64"]
        current = MathTex(sums[0], color=TEXT_COLOR).move_to(DOWN * 0.4)
        self.play(Write(current), run_time=0.4)

        count_total = sec("05_repeat_add_count", 3.2)
        per_step = max((count_total - 0.4) / 7, 0.2)

        for expr in sums[1:]:
            new_expr = MathTex(expr, color=TEXT_COLOR).move_to(current)
            self.play(Transform(current, new_expr), run_time=per_step)

        self.play(FadeOut(running_title), FadeOut(current), run_time=0.4)

        # 5. 불편함 강조
        box = SurroundingRectangle(repeated_add, color=WARNING_COLOR, buff=0.25)
        warn = Text("길고 불편합니다", font=FONT, font_size=26, color=WARNING_COLOR)
        warn.next_to(box, DOWN, buff=0.35)

        self.play(Create(box), run_time=0.5)
        self.play(FadeIn(warn), run_time=0.3)
        self.wait(max(sec("06_inconvenient", 3.5) - 0.8, 0.2))
        self.play(
            FadeOut(box),
            FadeOut(warn),
            FadeOut(repeated_add),
            run_time=0.4
        )

        # 6. 곱하기 의미
        sentence1 = Text("같은 수를 여러 번 더하는 것을", font=FONT, font_size=32, color=TEXT_COLOR).to_edge(UP, buff=0.9)
        sentence2 = Text("짧고 쉽게 나타낸 것이 곱하기입니다.", font=FONT, font_size=32, color=EMPHASIS_COLOR)
        sentence2.next_to(sentence1, DOWN, buff=0.35)

        self.play(Write(sentence1), run_time=0.7)
        self.play(Write(sentence2), run_time=0.7)
        self.wait(max(sec("07_multiplication_meaning", 5.0) - 1.4, 0.2))

        add_expr = MathTex("8+8+8+8+8+8+8+8", color=TEXT_COLOR).move_to(UP * 0.1)
        mul_expr = MathTex("8\\times 8", color=HIGHLIGHT_COLOR).scale(1.25)
        mul_expr.next_to(add_expr, DOWN, buff=1.2)
        arrow = Arrow(add_expr.get_bottom(), mul_expr.get_top(), buff=0.18, color=TEXT_COLOR)

        self.play(Write(add_expr), run_time=0.6)
        self.play(GrowArrow(arrow), run_time=0.4)
        self.play(Write(mul_expr), run_time=0.6)
        self.wait(max(sec("08_short_expression", 3.5) - 1.6, 0.2))

        self.play(
            FadeOut(sentence1),
            FadeOut(sentence2),
            FadeOut(add_expr),
            FadeOut(arrow),
            mul_expr.animate.to_edge(UP, buff=0.7),
            run_time=0.5
        )

        # 7. 8x8 배열
        grid_title = Text("8개씩 있는 줄이 8줄", font=FONT, font_size=32, color=TEXT_COLOR)
        grid_title.next_to(mul_expr, DOWN, buff=0.45)
        self.play(FadeIn(grid_title), run_time=0.4)
        self.wait(max(sec("09_grid_intro", 2.0) - 0.4, 0.2))

        dots = VGroup()
        rows, cols = 8, 8
        spacing = 0.42
        grid_center_shift = DOWN * 3

        for r in range(rows):
            row_group = VGroup()
            for c in range(cols):
                d = Dot(radius=0.055, color=EMPHASIS_COLOR)
                d.move_to(
                    LEFT * ((cols - 1) * spacing / 2)
                    + RIGHT * (c * spacing)
                    + UP * ((rows - 1) * spacing / 2)
                    - DOWN * (r * spacing)
                    + grid_center_shift
                )
                row_group.add(d)
            dots.add(row_group)

        grid_draw_time = 1.8
        for row in dots:
            self.play(FadeIn(row, lag_ratio=0.08), run_time=grid_draw_time / 8)

        brace_left = Brace(dots, LEFT, color=TEXT_COLOR)
        brace_bottom = Brace(dots, DOWN, color=TEXT_COLOR)

        left_label = Text("8줄", font=FONT, font_size=24, color=TEXT_COLOR).next_to(brace_left, LEFT, buff=0.25)
        bottom_label = Text("한 줄에 8개", font=FONT, font_size=24, color=TEXT_COLOR).next_to(brace_bottom, DOWN, buff=0.25)

        self.play(GrowFromCenter(brace_left), FadeIn(left_label), run_time=0.5)
        self.play(GrowFromCenter(brace_bottom), FadeIn(bottom_label), run_time=0.5)

        total = MathTex("8\\times 8 = 64", color=RESULT_COLOR).scale(1.2)
        total.to_edge(DOWN, buff=0.4)
        self.play(Write(total), run_time=0.5)

        used = 1.8 + 0.5 + 0.5 + 0.5
        self.wait(max(sec("10_grid_explain", 4.0) - used, 0.2))
        self.wait(max(sec("11_grid_concept", 2.5), 0.2))

        self.play(
            FadeOut(grid_title),
            FadeOut(brace_left),
            FadeOut(brace_bottom),
            FadeOut(left_label),
            FadeOut(bottom_label),
            FadeOut(dots),
            FadeOut(mul_expr),
            FadeOut(total),
            run_time=0.5
        )

        # 8. 결론
        final1 = Text("곱하기를 배우는 이유", font=FONT, font_size=38, color=TEXT_COLOR).to_edge(UP, buff=0.9)
        final2 = Text("반복되는 더하기를", font=FONT, font_size=32, color=TEXT_COLOR)
        final2.next_to(final1, DOWN, buff=0.55)
        final3 = Text("더 빠르고 쉽게 계산하기 위해서", font=FONT, font_size=32, color=HIGHLIGHT_COLOR)
        final3.next_to(final2, DOWN, buff=0.35)
        final4 = MathTex("8+8+8+8+8+8+8+8=64", color=TEXT_COLOR).scale(1.0)
        final4.next_to(final3, DOWN, buff=0.8)
        final5 = MathTex("8\\times 8 = 64", color=EMPHASIS_COLOR).scale(1.25)
        final5.next_to(final4, DOWN, buff=0.7)

        self.play(Write(final1), run_time=0.7)
        self.play(FadeIn(final2, shift=UP), run_time=0.5)
        self.play(FadeIn(final3, shift=UP), run_time=0.5)
        self.wait(max(sec("12_conclusion", 5.0) - 1.7, 0.2))

        self.play(Write(final4), run_time=0.7)
        self.play(TransformFromCopy(final4, final5), run_time=0.7)
        self.wait(max(sec("13_formula_wrapup", 5.0) - 1.4, 0.2))
        self.wait(max(sec("14_final", 2.5), 0.2))