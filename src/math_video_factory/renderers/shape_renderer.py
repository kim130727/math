from __future__ import annotations

from manim import Circle, Create, FadeIn, Rectangle, RegularPolygon, Text, VGroup

from .base import BaseRenderer, SceneContext


class ShapeRenderer(BaseRenderer):
    """
    기본 도형을 화면에 보여주는 렌더러.

    지원 예시:
    - shape: circle
    - shape: square
    - shape: triangle

    옵션 예시:
    - count: 3
    - label: "동그라미"
    - title: "이것은 원입니다"
    - caption: "모양을 살펴보세요"
    """

    def render(self, ctx: SceneContext, scene_data: dict) -> None:
        debug_guides = ctx.maybe_add_debug_guides(scene_data)

        title_text = str(scene_data.get("title") or "").strip()
        shape_name = str(scene_data.get("shape") or "circle").strip().lower()
        label_text = str(scene_data.get("label") or "").strip()
        caption_text = str(scene_data.get("caption") or "").strip()

        try:
            count = int(scene_data.get("count", 1))
        except (TypeError, ValueError):
            count = 1
        count = max(1, count)

        used = 0.0

        title = None
        shapes_group = None
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
        # shape objects
        # -----------------------------
        shapes = []
        shape_size = float(ctx.layout_value(scene_data, "shape_size", 1.0))
        spacing = float(ctx.layout_value(scene_data, "shape_spacing", 2.3))
        shape_y = float(ctx.layout_value(scene_data, "shape_y", 0.2))

        for _ in range(count):
            shape_obj = self._make_shape(shape_name, shape_size)
            shapes.append(shape_obj)

        shapes_group = VGroup(*shapes)

        if count == 1:
            shapes_group.move_to(
                [
                    float(ctx.layout_value(scene_data, "shape_x", 0.0)),
                    shape_y,
                    0,
                ]
            )
        else:
            shapes_group.arrange(buff=spacing)
            shapes_group.move_to(
                [
                    float(ctx.layout_value(scene_data, "shape_x", 0.0)),
                    shape_y,
                    0,
                ]
            )

        ctx.scene.play(Create(shapes_group), run_time=0.7)
        used += 0.7

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
                    float(ctx.layout_value(scene_data, "label_y", -2.0)),
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
        ctx.hold_after(used, 3.0, scene_data)

        # -----------------------------
        # cleanup
        # -----------------------------
        ctx.clear(title, shapes_group, label, caption, debug_guides)

    def _make_shape(self, shape_name: str, size: float):
        if shape_name == "circle":
            return Circle(radius=size)
        if shape_name == "square":
            side = size * 2
            return Rectangle(width=side, height=side)
        if shape_name == "triangle":
            return RegularPolygon(n=3, radius=size)

        # fallback
        return Circle(radius=size)