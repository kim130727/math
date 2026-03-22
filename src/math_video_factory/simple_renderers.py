from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from manim import (
    BLACK,
    DOWN,
    UP,
    FadeIn,
    FadeOut,
    Paragraph,
    Scene,
    Text,
    VGroup,
)


@dataclass(slots=True)
class SceneContext:
    scene: Scene
    timings: list[float]
    scene_index: int

    @property
    def duration(self) -> float:
        if 0 <= self.scene_index < len(self.timings):
            return max(float(self.timings[self.scene_index]), 0.8)
        return 3.0


RendererFn = Callable[[SceneContext, dict[str, Any]], None]


class RendererRegistry:
    def __init__(self) -> None:
        self._renderers: dict[str, RendererFn] = {}

    def register(self, name: str, fn: RendererFn) -> None:
        key = str(name).strip().lower()
        if not key:
            raise ValueError("renderer name이 비어 있습니다.")
        self._renderers[key] = fn

    def get(self, name: str) -> RendererFn:
        key = str(name).strip().lower()
        if key in self._renderers:
            return self._renderers[key]

        if "fallback" in self._renderers:
            return self._renderers["fallback"]

        raise KeyError(f"등록되지 않은 renderer 타입입니다: {name}")

    def render(self, ctx: SceneContext, scene_data: dict[str, Any]) -> None:
        if not isinstance(scene_data, dict):
            raise ValueError("scene_data 는 dict 형식이어야 합니다.")

        scene_type = str(scene_data.get("type", "fallback")).strip().lower()
        renderer = self.get(scene_type)
        renderer(ctx, scene_data)


registry = RendererRegistry()


def _safe_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def _make_title(text: str) -> Text:
    return Text(
        text,
        font_size=52,
        color=BLACK,
    )


def _make_body(text: str) -> Paragraph:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        lines = [""]

    return Paragraph(
        *lines,
        line_spacing=0.8,
        font_size=34,
        alignment="center",
        color=BLACK,
    )


def _make_caption(text: str) -> Text | None:
    text = _safe_text(text)
    if not text:
        return None
    return Text(
        text,
        font_size=24,
        color=BLACK,
    )


def _compose_vertical(
    *,
    title: str = "",
    body: str = "",
    caption: str = "",
) -> VGroup:
    parts: list[Any] = []

    if _safe_text(title):
        parts.append(_make_title(_safe_text(title)))

    if _safe_text(body):
        parts.append(_make_body(_safe_text(body)))

    group = VGroup(*parts) if parts else VGroup(Text("", font_size=32, color=BLACK))
    group.arrange(DOWN, buff=0.55)
    group.move_to([0, 0.6, 0])

    caption_obj = _make_caption(caption)
    if caption_obj is not None:
        caption_obj.scale(0.92)
        caption_obj.to_edge(DOWN, buff=0.5)
        group = VGroup(group, caption_obj)

    return group


def _show_and_wait(ctx: SceneContext, mobj) -> None:
    scene = ctx.scene
    scene.play(FadeIn(mobj), run_time=0.35)

    hold = max(ctx.duration - 0.7, 0.6)
    scene.wait(hold)

    scene.play(FadeOut(mobj), run_time=0.35)


def render_fallback(ctx: SceneContext, scene_data: dict[str, Any]) -> None:
    title = _safe_text(scene_data.get("title"))
    body = _safe_text(scene_data.get("body"))
    caption = _safe_text(scene_data.get("caption"))

    group = _compose_vertical(
        title=title,
        body=body,
        caption=caption,
    )
    _show_and_wait(ctx, group)


def render_question(ctx: SceneContext, scene_data: dict[str, Any]) -> None:
    question = _safe_text(scene_data.get("question"))
    body = _safe_text(scene_data.get("body"))
    caption = _safe_text(scene_data.get("caption"))

    if not question:
        question = "질문을 확인해 주세요."

    title_obj = Text(
        question,
        font_size=50,
        color=BLACK,
    )
    title_obj.to_edge(UP, buff=1.2)

    body_obj = _make_body(body if body else "생각해 봅시다.")
    body_obj.next_to(title_obj, DOWN, buff=0.9)

    items = [title_obj, body_obj]

    caption_obj = _make_caption(caption)
    if caption_obj is not None:
        caption_obj.to_edge(DOWN, buff=0.5)
        items.append(caption_obj)

    group = VGroup(*items)
    _show_and_wait(ctx, group)


def render_compare(ctx: SceneContext, scene_data: dict[str, Any]) -> None:
    title = _safe_text(scene_data.get("title"), "비교하기")
    left = _safe_text(scene_data.get("left"))
    right = _safe_text(scene_data.get("right"))
    caption = _safe_text(scene_data.get("caption"))

    title_obj = Text(title, font_size=50, color=BLACK)
    left_obj = Text(left or "왼쪽", font_size=42, color=BLACK)
    vs_obj = Text(":", font_size=46, color=BLACK)
    right_obj = Text(right or "오른쪽", font_size=42, color=BLACK)

    row = VGroup(left_obj, vs_obj, right_obj).arrange(buff=0.7)
    col = VGroup(title_obj, row).arrange(DOWN, buff=0.9)
    col.move_to([0, 0.8, 0])

    items = [col]

    caption_obj = _make_caption(caption)
    if caption_obj is not None:
        caption_obj.to_edge(DOWN, buff=0.5)
        items.append(caption_obj)

    group = VGroup(*items)
    _show_and_wait(ctx, group)


def register_renderers() -> None:
    registry.register("fallback", render_fallback)
    registry.register("question", render_question)
    registry.register("compare", render_compare)