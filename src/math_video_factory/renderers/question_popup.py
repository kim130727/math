from __future__ import annotations

from manim import FadeIn, FadeOut, PopInFromScale, Write, VGroup

from .base import BaseRenderer, SceneContext


class QuestionPopupRenderer(BaseRenderer):
    """
    질문을 강조해서 팝업처럼 띄우는 렌더러
    """

    def render(self, ctx: SceneContext, scene_data: dict) -> None:
        debug_guides = ctx.maybe_add_debug_guides(scene_data)

        question_text = str(
            scene_data.get("question")
            or scene_data.get("title")
            or ""
        ).strip()

        sub_text = str(scene_data.get("body") or "").strip()
        caption_text = str(scene_data.get("caption") or "").strip()

        used = 0.0

        question = None
        sub = None
        caption = None

        # -----------------------------
        # QUESTION (핵심)
        # -----------------------------
        if question_text:
            question = ctx.fit_text(
                question_text,
                font_size=int(ctx.layout_value(scene_data, "question_font_size", 60)),
                color=ctx.accent_color,
                line_spacing=0.9,
            )

            question.move_to(
                [
                    float(ctx.layout_value(scene_data, "question_x", 0.0)),
                    float(ctx.layout_value(scene_data, "question_y", 0.8)),
                    0,
                ]
            )

            ctx.scene.play(PopInFromScale(question, scale=0.6), run_time=0.6)
            used += 0.6

        # -----------------------------
        # SUB TEXT (설명)
        # -----------------------------
        if sub_text:
            sub = ctx.fit_text(
                sub_text,
                font_size=int(ctx.layout_value(scene_data, "body_font_size", 40)),
                color=ctx.text_color,
                line_spacing=0.95,
            )

            sub.next_to(question, direction=ctx.scene.DOWN, buff=0.5)

            ctx.scene.play(FadeIn(sub), run_time=0.4)
            used += 0.4

        # -----------------------------
        # CAPTION (하단)
        # -----------------------------
        if caption_text:
            caption = ctx.make_bottom_caption(caption_text, scene_data=scene_data)
            ctx.scene.play(FadeIn(caption), run_time=0.3)
            used += 0.3

        # -----------------------------
        # HOLD
        # -----------------------------
        ctx.hold_after(used, 3.0, scene_data)

        # -----------------------------
        # CLEANUP
        # -----------------------------
        ctx.clear(question, sub, caption, debug_guides)