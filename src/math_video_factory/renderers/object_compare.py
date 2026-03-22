from __future__ import annotations

from manim import FadeIn, Write, VGroup

from .base import BaseRenderer, SceneContext


class ObjectCompareRenderer(BaseRenderer):
    """
    좌/우 두 대상을 비교해서 보여주는 렌더러.
    left / right 텍스트를 각각 배치하고,
    필요하면 상단 title, 하단 caption을 함께 표시한다.
    """

    def render(self, ctx: SceneContext, scene_data: dict) -> None:
        debug_guides = ctx.maybe_add_debug_guides(scene_data)

        title_text = str(scene_data.get("title") or "").strip()
        left_text = str(scene_data.get("left") or "").strip()
        right_text = str(scene_data.get("right") or "").strip()
        caption_text = str(scene_data.get("caption") or "").strip()

        used = 0.0

        title = None
        left_box = None
        right_box = None
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
            ctx.scene.play(Write(title), run_time=0.5)
            used += 0.5

        # -----------------------------
        # left / right
        # -----------------------------
        left_label = ctx.fit_text(
            left_text or "왼쪽",
            max_width=float(ctx.layout_value(scene_data, "item_max_width", 5.0)),
            font_size=int(ctx.layout_value(scene_data, "item_font_size", 40)),
            color=ctx.text_color,
            line_spacing=float(ctx.layout_value(scene_data, "item_line_spacing", 0.95)),
        )

        right_label = ctx.fit_text(
            right_text or "오른쪽",
            max_width=float(ctx.layout_value(scene_data, "item_max_width", 5.0)),
            font_size=int(ctx.layout_value(scene_data, "item_font_size", 40)),
            color=ctx.text_color,
            line_spacing=float(ctx.layout_value(scene_data, "item_line_spacing", 0.95)),
        )

        left_x = float(ctx.layout_value(scene_data, "left_x", -3.2))
        right_x = float(ctx.layout_value(scene_data, "right_x", 3.2))
        item_y = float(ctx.layout_value(scene_data, "item_y", 0.2))

        left_label.move_to([left_x, item_y, 0])
        right_label.move_to([right_x, item_y, 0])

        left_box = VGroup(left_label)
        right_box = VGroup(right_label)

        ctx.scene.play(FadeIn(left_box, shift=0.2), run_time=0.45)
        used += 0.45

        ctx.scene.play(FadeIn(right_box, shift=0.2), run_time=0.45)
        used += 0.45

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
        ctx.clear(title, left_box, right_box, caption, debug_guides)