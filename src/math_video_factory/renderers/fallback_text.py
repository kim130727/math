from __future__ import annotations

from manim import FadeIn, Write

from .base import BaseRenderer, SceneContext


class FallbackTextRenderer(BaseRenderer):
    """
    전용 렌더러가 없는 장면을 위한 기본 렌더러.
    title / body / caption 정도만 안전하게 배치해서 출력한다.
    """

    def render(self, ctx: SceneContext, scene_data: dict) -> None:
        debug_guides = ctx.maybe_add_debug_guides(scene_data)

        title_text = str(scene_data.get("title", "")).strip()
        body_text = str(
            scene_data.get("body")
            or scene_data.get("text")
            or scene_data.get("script")
            or ""
        ).strip()
        caption_text = str(scene_data.get("caption", "")).strip()

        title = None
        body = None
        caption = None

        used = 0.0

        # -----------------------------
        # title
        # -----------------------------
        if title_text:
            title = ctx.fit_text(
                title_text,
                font_size=int(ctx.layout_value(scene_data, "title_font_size", 52)),
                color=ctx.accent_color,
                line_spacing=0.9,
            )
            title.move_to(
                [
                    float(ctx.layout_value(scene_data, "title_x", 0.0)),
                    float(ctx.layout_value(scene_data, "title_y", 2.6)),
                    0,
                ]
            )
            ctx.scene.play(Write(title), run_time=0.6)
            used += 0.6

        # -----------------------------
        # body
        # -----------------------------
        if body_text:
            body = ctx.fit_text(
                body_text,
                max_width=float(
                    ctx.layout_value(scene_data, "body_max_width", ctx.max_text_width - 0.4)
                ),
                font_size=int(ctx.layout_value(scene_data, "body_font_size", 42)),
                color=ctx.text_color,
                line_spacing=float(ctx.layout_value(scene_data, "body_line_spacing", 0.95)),
            )
            body.move_to(
                [
                    float(ctx.layout_value(scene_data, "body_x", 0.0)),
                    float(ctx.layout_value(scene_data, "body_y", 0.0)),
                    0,
                ]
            )
            ctx.scene.play(FadeIn(body, shift=0.15), run_time=0.6)
            used += 0.6

        # -----------------------------
        # caption
        # -----------------------------
        if caption_text:
            caption = ctx.make_bottom_caption(caption_text, scene_data=scene_data)
            ctx.scene.play(FadeIn(caption), run_time=0.35)
            used += 0.35

        # -----------------------------
        # hold
        # -----------------------------
        ctx.hold_after(used, 3.0, scene_data)

        # -----------------------------
        # cleanup
        # -----------------------------
        ctx.clear(title, body, caption, debug_guides)