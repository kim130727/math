from __future__ import annotations

import os
from dataclasses import dataclass, field

from manim import (
    BLACK,
    BLUE_D,
    DARK_BLUE,
    DashedLine,
    FadeOut,
    GREEN,
    GREY_B,
    GREY_D,
    MEDIUM,
    RED,
    SurroundingRectangle,
    Text,
    VGroup,
)


@dataclass
class SceneContext:
    scene: object
    timings: list[float]
    font: str = "Malgun Gothic"
    scene_index: int = 0

    text_color: object = BLACK
    accent_color: object = DARK_BLUE
    warning_color: object = RED
    result_color: object = GREEN
    subtle_color: object = GREY_D

    max_text_width: float = field(init=False)
    max_math_width: float = field(init=False)
    debug_layout: bool = False

    def __post_init__(self) -> None:
        self.max_text_width = self.scene.camera.frame_width - 1.0
        self.max_math_width = self.scene.camera.frame_width - 1.2
        self.debug_layout = os.getenv("MATH_DEBUG_LAYOUT", "").strip().lower() in {
            "1",
            "true",
            "yes",
            "y",
            "on",
        }

    # ------------------------------------------------------------------
    # timing
    # ------------------------------------------------------------------
    def sec(self, default: float) -> float:
        if 0 <= self.scene_index < len(self.timings):
            return max(float(self.timings[self.scene_index]), 0.8)
        return default

    def hold_after(
        self,
        used: float,
        default_total: float,
        scene_data: dict | None = None,
    ) -> None:
        total = default_total
        if scene_data:
            total = float(scene_data.get("duration", default_total))
        total = self.sec(total)
        remain = max(total - used, 0.15)
        self.scene.wait(remain)

    # ------------------------------------------------------------------
    # layout
    # ------------------------------------------------------------------
    def layout_value(self, scene_data: dict, key: str, default):
        layout = scene_data.get("layout", {})
        if isinstance(layout, dict) and key in layout:
            return layout[key]
        return default

    def fit_text(
        self,
        text: str,
        *,
        max_width: float | None = None,
        font_size: int = 40,
        color=None,
        line_spacing: float = 0.9,
        weight: str = MEDIUM,
    ) -> Text:
        obj = Text(
            text,
            font=self.font,
            font_size=font_size,
            color=color if color is not None else self.text_color,
            line_spacing=line_spacing,
            weight=weight,
        )
        width_limit = max_width if max_width is not None else self.max_text_width
        if obj.width > width_limit:
            obj.scale_to_fit_width(width_limit)
        return obj

    def make_top_label(
        self,
        text: str,
        color=None,
        scene_data: dict | None = None,
    ) -> Text:
        y = 3.45
        if scene_data:
            y = float(self.layout_value(scene_data, "top_label_y", 3.45))

        label = self.fit_text(
            text,
            font_size=28,
            color=color if color is not None else self.subtle_color,
            line_spacing=0.9,
            weight=MEDIUM,
        )
        label.move_to([0, y, 0])
        return label

    def make_bottom_caption(
        self,
        text: str,
        color=None,
        scene_data: dict | None = None,
    ) -> Text:
        y = -6.7
        if scene_data:
            y = float(self.layout_value(scene_data, "bottom_caption_y", -6.7))

        caption = self.fit_text(
            text,
            font_size=28,
            color=color if color is not None else self.subtle_color,
            line_spacing=0.9,
            weight=MEDIUM,
        )
        caption.move_to([0, y, 0])
        return caption

    # ------------------------------------------------------------------
    # debug
    # ------------------------------------------------------------------
    def maybe_add_debug_guides(self, scene_data: dict) -> VGroup | None:
        debug_this_scene = self.debug_layout or bool(scene_data.get("debug_layout", False))
        if not debug_this_scene:
            return None

        frame_w = self.scene.camera.frame_width
        frame_h = self.scene.camera.frame_height

        center_h = DashedLine(
            start=[-frame_w / 2, 0, 0],
            end=[frame_w / 2, 0, 0],
            color=GREY_B,
            stroke_width=2,
        )
        center_v = DashedLine(
            start=[0, -frame_h / 2, 0],
            end=[0, frame_h / 2, 0],
            color=GREY_B,
            stroke_width=2,
        )

        title_y = float(self.layout_value(scene_data, "title_y", 2.6))
        body_y = float(self.layout_value(scene_data, "body_y", 0.0))
        bottom_y = float(self.layout_value(scene_data, "bottom_caption_y", -6.7))

        title_guide = DashedLine(
            start=[-frame_w / 2, title_y, 0],
            end=[frame_w / 2, title_y, 0],
            color=BLUE_D,
            stroke_width=2,
        )
        body_guide = DashedLine(
            start=[-frame_w / 2, body_y, 0],
            end=[frame_w / 2, body_y, 0],
            color=BLUE_D,
            stroke_width=2,
        )
        bottom_guide = DashedLine(
            start=[-frame_w / 2, bottom_y, 0],
            end=[frame_w / 2, bottom_y, 0],
            color=BLUE_D,
            stroke_width=2,
        )

        guides = VGroup(center_h, center_v, title_guide, body_guide, bottom_guide)
        self.scene.add(guides)
        return guides

    def debug_box(self, mob, color=RED):
        return SurroundingRectangle(mob, color=color, buff=0.08, stroke_width=2)

    # ------------------------------------------------------------------
    # cleanup
    # ------------------------------------------------------------------
    def clear(self, *mobs, run_time: float = 0.35) -> None:
        existing = [m for m in mobs if m is not None]
        if existing:
            self.scene.play(*[FadeOut(m) for m in existing], run_time=run_time)


class BaseRenderer:
    def render(self, ctx: SceneContext, scene_data: dict) -> None:
        raise NotImplementedError