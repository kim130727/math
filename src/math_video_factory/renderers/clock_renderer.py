from __future__ import annotations

import math

from manim import Circle, Create, FadeIn, Line, Text, VGroup

from .base import BaseRenderer, SceneContext


class ClockRenderer(BaseRenderer):
    """
    아날로그 시계를 그리는 렌더러.

    지원 예시:
    - hour: 3
    - minute: 0

    옵션 예시:
    - title: "몇 시일까요?"
    - label: "3시"
    - caption: "긴 바늘과 짧은 바늘을 보세요"
    """

    def render(self, ctx: SceneContext, scene_data: dict) -> None:
        debug_guides = ctx.maybe_add_debug_guides(scene_data)

        title_text = str(scene_data.get("title") or "").strip()
        label_text = str(scene_data.get("label") or "").strip()
        caption_text = str(scene_data.get("caption") or "").strip()

        hour = self._safe_int(scene_data.get("hour", 3), default=3) % 12
        minute = self._safe_int(scene_data.get("minute", 0), default=0) % 60

        used = 0.0

        title = None
        clock_group = None
        label = None
        caption = None

        # -----------------------------
        # title
        # -----------------------------
        if title_text:
            title = ctx.fit_text(
                title_text,
                font_size=int(ctx.layout_value(scene_data, "title_font_size", 50)),
                color=ctx.accent_color,
                line_spacing=0.9,
            )
            title.move_to(
                [
                    float(ctx.layout_value(scene_data, "title_x", 0.0)),
                    float(ctx.layout_value(scene_data, "title_y", 2.7)),
                    0,
                ]
            )
            ctx.scene.play(FadeIn(title), run_time=0.45)
            used += 0.45

        # -----------------------------
        # clock
        # -----------------------------
        clock_group = self._make_clock(ctx, scene_data, hour=hour, minute=minute)
        clock_group.move_to(
            [
                float(ctx.layout_value(scene_data, "clock_x", 0.0)),
                float(ctx.layout_value(scene_data, "clock_y", 0.1)),
                0,
            ]
        )

        ctx.scene.play(Create(clock_group), run_time=0.9)
        used += 0.9

        # -----------------------------
        # label
        # -----------------------------
        if label_text:
            label = ctx.fit_text(
                label_text,
                font_size=int(ctx.layout_value(scene_data, "label_font_size", 38)),
                color=ctx.text_color,
                line_spacing=0.9,
            )
            label.move_to(
                [
                    float(ctx.layout_value(scene_data, "label_x", 0.0)),
                    float(ctx.layout_value(scene_data, "label_y", -2.2)),
                    0,
                ]
            )
            ctx.scene.play(FadeIn(label), run_time=0.35)
            used += 0.35

        # -----------------------------
        # caption
        # -----------------------------
        if caption_text:
            caption = ctx.make_bottom_caption(caption_text, scene_data=scene_data)
            ctx.scene.play(FadeIn(caption), run_time=0.3)
            used += 0.3

        # -----------------------------
        # hold
        # -----------------------------
        ctx.hold_after(used, 3.2, scene_data)

        # -----------------------------
        # cleanup
        # -----------------------------
        ctx.clear(title, clock_group, label, caption, debug_guides)

    def _make_clock(
        self,
        ctx: SceneContext,
        scene_data: dict,
        *,
        hour: int,
        minute: int,
    ) -> VGroup:
        radius = float(ctx.layout_value(scene_data, "clock_radius", 1.8))

        face = Circle(radius=radius)

        number_group = self._make_numbers(ctx, radius=radius)
        tick_group = self._make_ticks(radius=radius)

        hour_hand = self._make_hour_hand(radius=radius, hour=hour, minute=minute)
        minute_hand = self._make_minute_hand(radius=radius, minute=minute)

        return VGroup(face, tick_group, number_group, hour_hand, minute_hand)

    def _make_numbers(self, ctx: SceneContext, *, radius: float) -> VGroup:
        items = []

        for n in range(1, 13):
            angle = self._clock_angle_for_hour(n)
            x = math.cos(angle) * radius * 0.78
            y = math.sin(angle) * radius * 0.78

            txt = Text(
                str(n),
                font=ctx.font,
                font_size=26,
                color=ctx.text_color,
            )
            txt.move_to([x, y, 0])
            items.append(txt)

        return VGroup(*items)

    def _make_ticks(self, *, radius: float) -> VGroup:
        ticks = []

        for i in range(12):
            angle = math.pi / 2 - (2 * math.pi * i / 12)

            outer_x = math.cos(angle) * radius
            outer_y = math.sin(angle) * radius

            inner_x = math.cos(angle) * radius * 0.90
            inner_y = math.sin(angle) * radius * 0.90

            tick = Line(
                [inner_x, inner_y, 0],
                [outer_x, outer_y, 0],
            )
            ticks.append(tick)

        return VGroup(*ticks)

    def _make_hour_hand(self, *, radius: float, hour: int, minute: int) -> Line:
        total_hour = (hour % 12) + (minute / 60.0)
        angle = math.pi / 2 - (2 * math.pi * total_hour / 12)

        end_x = math.cos(angle) * radius * 0.50
        end_y = math.sin(angle) * radius * 0.50

        return Line([0, 0, 0], [end_x, end_y, 0])

    def _make_minute_hand(self, *, radius: float, minute: int) -> Line:
        angle = math.pi / 2 - (2 * math.pi * minute / 60)

        end_x = math.cos(angle) * radius * 0.78
        end_y = math.sin(angle) * radius * 0.78

        return Line([0, 0, 0], [end_x, end_y, 0])

    def _clock_angle_for_hour(self, hour_num: int) -> float:
        hour_num = 12 if hour_num == 12 else hour_num % 12
        return math.pi / 2 - (2 * math.pi * (hour_num % 12) / 12)

    def _safe_int(self, value, *, default: int) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default