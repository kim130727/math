from __future__ import annotations

import numpy as np
from manim import *


FONT = "Malgun Gothic"


class Character(VGroup):
    def __init__(
        self,
        name: str,
        body_color=BLUE,
        scale_factor: float = 1.0,
        **kwargs,
    ):
        super().__init__(**kwargs)

        head = Circle(
            radius=0.45,
            stroke_color=BLACK,
            stroke_width=2,
            fill_color=body_color,
            fill_opacity=1,
        )
        eye_l = Dot(
            point=head.get_center() + LEFT * 0.15 + UP * 0.08,
            radius=0.03,
            color=BLACK,
        )
        eye_r = Dot(
            point=head.get_center() + RIGHT * 0.15 + UP * 0.08,
            radius=0.03,
            color=BLACK,
        )

        mouth = Arc(
            radius=0.16,
            start_angle=210 * DEGREES,
            angle=120 * DEGREES,
            color=BLACK,
            stroke_width=2,
        ).move_to(head.get_center() + DOWN * 0.08)

        body = RoundedRectangle(
            width=0.9,
            height=1.1,
            corner_radius=0.18,
            stroke_color=BLACK,
            stroke_width=2,
            fill_color=body_color,
            fill_opacity=1,
        ).next_to(head, DOWN, buff=0.02)

        arm_l = Line(
            body.get_left() + UP * 0.25,
            body.get_left() + LEFT * 0.35,
            color=BLACK,
            stroke_width=2,
        )
        arm_r = Line(
            body.get_right() + UP * 0.25,
            body.get_right() + RIGHT * 0.35,
            color=BLACK,
            stroke_width=2,
        )

        leg_l = Line(
            body.get_bottom() + LEFT * 0.18,
            body.get_bottom() + DOWN * 0.35 + LEFT * 0.12,
            color=BLACK,
            stroke_width=2,
        )
        leg_r = Line(
            body.get_bottom() + RIGHT * 0.18,
            body.get_bottom() + DOWN * 0.35 + RIGHT * 0.12,
            color=BLACK,
            stroke_width=2,
        )

        label = Text(
            name,
            font=FONT,
            font_size=24,
            color=BLACK,
        ).next_to(body, DOWN, buff=0.15)

        self.head = head
        self.body = body
        self.eye_l = eye_l
        self.eye_r = eye_r
        self.mouth = mouth
        self.arm_l = arm_l
        self.arm_r = arm_r
        self.leg_l = leg_l
        self.leg_r = leg_r
        self.label = label

        self.add(
            head,
            eye_l,
            eye_r,
            mouth,
            body,
            arm_l,
            arm_r,
            leg_l,
            leg_r,
            label,
        )
        self.scale(scale_factor)

    def look_happy(self):
        happy_mouth = Arc(
            radius=0.18,
            start_angle=200 * DEGREES,
            angle=140 * DEGREES,
            color=BLACK,
            stroke_width=2,
        ).move_to(self.head.get_center() + DOWN * 0.06)
        return Transform(self.mouth, happy_mouth)

    def look_surprised(self):
        surprise = Circle(
            radius=0.06,
            color=BLACK,
            stroke_width=2,
        ).move_to(self.head.get_center() + DOWN * 0.08)
        return Transform(self.mouth, surprise)


def make_speech_bubble(
    text: str,
    speaker: Mobject,
    *,
    side=UP,
    buff: float = 0.35,
    shift_vec=ORIGIN,
    width: float = 4.6,
    height: float = 2.0,
    font_size: int = 26,
):
    bubble = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.2,
        stroke_color=BLACK,
        stroke_width=2,
        fill_color=WHITE,
        fill_opacity=1,
    )

    content = Text(
        text,
        font=FONT,
        font_size=font_size,
        color=BLACK,
        line_spacing=0.9,
    ).move_to(bubble.get_center())

    bubble_group = VGroup(bubble, content)
    bubble_group.next_to(speaker, side, buff=buff)
    bubble_group.shift(shift_vec)

    direction = speaker.get_center() - bubble.get_center()
    norm = np.linalg.norm(direction)
    if norm == 0:
        direction = DOWN
    else:
        direction = direction / norm

    tail_base = bubble.get_boundary_point(direction)

    perp = np.array([-direction[1], direction[0], 0.0])
    perp_norm = np.linalg.norm(perp)
    if perp_norm == 0:
        perp = RIGHT
    else:
        perp = perp / perp_norm

    tip = tail_base + direction * 0.55
    tail = Polygon(
        tail_base + perp * 0.16,
        tip,
        tail_base - perp * 0.16,
        color=BLACK,
        fill_color=WHITE,
        fill_opacity=1,
        stroke_width=2,
    )

    return VGroup(bubble, tail, content)


class JibbungNabbungDialogue(Scene):
    def construct(self):
        self.camera.background_color = "#F7F7F7"

        title = Text(
            "지뽕이 · 나뽕이\n곱하기 이야기",
            font=FONT,
            font_size=34,
            color=BLACK,
            line_spacing=0.9,
        ).to_edge(UP, buff=0.4)

        jibbung = Character(
            "지뽕이",
            body_color=ORANGE,
            scale_factor=0.95,
        ).to_edge(LEFT, buff=1.2).shift(DOWN * 0.8)

        nabbung = Character(
            "나뽕이",
            body_color=BLUE,
            scale_factor=0.95,
        ).to_edge(RIGHT, buff=1.2).shift(DOWN * 0.8)

        self.play(FadeIn(title, shift=DOWN), run_time=0.8)
        self.play(
            FadeIn(jibbung, shift=RIGHT * 0.4),
            FadeIn(nabbung, shift=LEFT * 0.4),
            run_time=0.8,
        )
        self.wait(0.3)

        # 1. 질문
        bubble_j1 = make_speech_bubble(
            "사탕이 8개씩 들어 있는\n봉지가 8개래!\n모두 몇 개일까?",
            jibbung,
            side=UP,
            shift_vec=RIGHT * 0.7,
            width=4.8,
            height=2.3,
        )

        self.play(jibbung.look_surprised(), run_time=0.3)
        self.play(FadeIn(bubble_j1, shift=UP * 0.2), run_time=0.5)
        self.wait(1.6)
        self.play(FadeOut(bubble_j1), run_time=0.3)

        # 2. 설명
        bubble_n1 = make_speech_bubble(
            "곱하기를 모르면\n8을 8번 더하면 돼!",
            nabbung,
            side=UP,
            shift_vec=LEFT * 0.7,
            width=4.5,
            height=2.0,
        )

        self.play(nabbung.look_happy(), run_time=0.3)
        self.play(FadeIn(bubble_n1, shift=UP * 0.2), run_time=0.5)

        expr = MathTex(
            "8+8+8+8+8+8+8+8=64",
            color=BLACK,
        ).scale(1.0).move_to(DOWN * 0.1)

        self.play(Write(expr), run_time=0.8)
        self.wait(1.2)
        self.play(FadeOut(bubble_n1), run_time=0.3)

        # 3. 카운트
        count_title = Text(
            "하나씩 더해 볼까?",
            font=FONT,
            font_size=28,
            color=BLACK,
        ).move_to(UP * 1.1)

        self.play(FadeIn(count_title), run_time=0.4)

        sums = [
            "8",
            "8+8=16",
            "8+8+8=24",
            "8+8+8+8=32",
            "8+8+8+8+8=40",
            "8+8+8+8+8+8=48",
            "8+8+8+8+8+8+8=56",
            "8+8+8+8+8+8+8+8=64",
        ]
        current = MathTex(sums[0], color=BLACK).scale(1.0).move_to(DOWN * 0.15)
        self.play(Transform(expr, current), run_time=0.3)

        for s in sums[1:]:
            new_expr = MathTex(s, color=BLACK).move_to(expr)
            self.play(Transform(expr, new_expr), run_time=0.45)

        self.wait(0.4)

        # 4. 지뽕이 반응
        bubble_j2 = make_speech_bubble(
            "으악!\n너무 길어!\n헷갈려!",
            jibbung,
            side=UP,
            shift_vec=RIGHT * 0.7,
            width=3.8,
            height=2.1,
        )

        box = SurroundingRectangle(expr, color=RED, buff=0.2)

        self.play(
            jibbung.look_surprised(),
            Create(box),
            FadeIn(bubble_j2, shift=UP * 0.2),
            run_time=0.6,
        )
        self.wait(1.3)
        self.play(FadeOut(bubble_j2), FadeOut(box), run_time=0.3)

        # 5. 곱하기 소개
        bubble_n2 = make_speech_bubble(
            "그래서 곱하기를 써!\n8이 8번 있으니까\n8 × 8 이야!",
            nabbung,
            side=UP,
            shift_vec=LEFT * 0.7,
            width=4.7,
            height=2.3,
        )

        short_expr = MathTex(
            "8\\times 8 = 64",
            color=DARK_BLUE,
        ).scale(1.2).move_to(expr)

        self.play(FadeIn(bubble_n2, shift=UP * 0.2), run_time=0.5)
        self.play(Transform(expr, short_expr), run_time=0.8)
        self.wait(1.4)
        self.play(FadeOut(bubble_n2), FadeOut(count_title), run_time=0.3)

        # 6. 배열 장면
        grid_title = Text(
            "사탕 8개짜리 봉지가 8개!",
            font=FONT,
            font_size=28,
            color=BLACK,
        ).move_to(UP * 1.25)

        self.play(FadeIn(grid_title), run_time=0.4)

        dots = VGroup()
        rows, cols = 8, 8
        spacing = 0.38
        center_shift = DOWN * 0.7

        for r in range(rows):
            row_group = VGroup()
            for c in range(cols):
                d = Dot(radius=0.045, color=BLUE)
                d.move_to(
                    LEFT * ((cols - 1) * spacing / 2)
                    + RIGHT * (c * spacing)
                    + UP * ((rows - 1) * spacing / 2)
                    - DOWN * (r * spacing)
                    + center_shift
                )
                row_group.add(d)
            dots.add(row_group)

        self.play(FadeOut(expr), run_time=0.2)
        for row in dots:
            self.play(FadeIn(row, lag_ratio=0.08), run_time=0.2)

        brace_left = Brace(dots, LEFT, color=BLACK)
        brace_bottom = Brace(dots, DOWN, color=BLACK)

        left_label = Text(
            "8봉지",
            font=FONT,
            font_size=22,
            color=BLACK,
        ).next_to(brace_left, LEFT, buff=0.15)

        bottom_label = Text(
            "한 봉지에 8개",
            font=FONT,
            font_size=20,
            color=BLACK,
        ).next_to(brace_bottom, DOWN, buff=0.12)

        result = MathTex(
            "8\\times 8 = 64",
            color=GREEN,
        ).scale(1.0).next_to(bottom_label, DOWN, buff=0.2)

        self.play(GrowFromCenter(brace_left), FadeIn(left_label), run_time=0.4)
        self.play(GrowFromCenter(brace_bottom), FadeIn(bottom_label), run_time=0.4)
        self.play(Write(result), run_time=0.5)

        bubble_n3 = make_speech_bubble(
            "이렇게 같은 묶음이\n여러 개 있을 때\n곱하기를 쓰는 거야!",
            nabbung,
            side=UP,
            shift_vec=LEFT * 0.7,
            width=4.7,
            height=2.3,
        )

        self.play(FadeIn(bubble_n3, shift=UP * 0.2), run_time=0.5)
        self.wait(1.8)
        self.play(FadeOut(bubble_n3), run_time=0.3)

        # 7. 마무리
        bubble_j3 = make_speech_bubble(
            "아하!\n같은 묶음이 많을 때는\n곱하기가 빠르구나!",
            jibbung,
            side=UP,
            shift_vec=RIGHT * 0.7,
            width=4.5,
            height=2.3,
        )

        self.play(jibbung.look_happy(), run_time=0.3)
        self.play(FadeIn(bubble_j3, shift=UP * 0.2), run_time=0.5)
        self.wait(1.8)

        final_title = Text(
            "곱하기 = 같은 묶음을 빠르게 세는 방법",
            font=FONT,
            font_size=30,
            color=DARK_BLUE,
        ).to_edge(DOWN, buff=0.4)

        self.play(FadeIn(final_title, shift=UP * 0.2), run_time=0.5)
        self.wait(1.5)