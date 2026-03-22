from __future__ import annotations

import textwrap
from dataclasses import dataclass
from typing import Any, Callable

from manim import (
    BLACK,
    DOWN,
    FadeIn,
    FadeOut,
    Paragraph,
    Scene,
    Text,
    UP,
    VGroup,
    config,
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


def _wrap_text(text: str, width: int = 14) -> str:
    lines: list[str] = []

    for raw in str(text).splitlines():
        raw = raw.strip()
        if not raw:
            continue

        wrapped = textwrap.wrap(
            raw,
            width=width,
            break_long_words=False,
            break_on_hyphens=False,
        )
        if wrapped:
            lines.extend(wrapped)
        else:
            lines.append(raw)

    return "\n".join(lines).strip()


def _fit_width(mobj, max_width: float):
    if mobj.width > max_width:
        mobj.scale_to_fit_width(max_width)
    return mobj


def _make_title(text: str) -> Text:
    obj = Text(
        _wrap_text(text, width=12),
        font_size=40,
        color=BLACK,
        line_spacing=0.9,
    )
    return _fit_width(obj, config.frame_width * 0.82)


def _make_body(text: str) -> Paragraph:
    wrapped = _wrap_text(text, width=16)
    lines = [line.strip() for line in wrapped.splitlines() if line.strip()]
    if not lines:
        lines = [""]

    obj = Paragraph(
        *lines,
        line_spacing=0.82,
        font_size=28,
        alignment="center",
        color=BLACK,
    )
    return _fit_width(obj, config.frame_width * 0.84)


def _make_caption(text: str) -> Text | None:
    text = _safe_text(text)
    if not text:
        return None

    obj = Text(
        _wrap_text(text, width=20),
        font_size=20,
        color=BLACK,
        line_spacing=0.85,
    )
    return _fit_width(obj, config.frame_width * 0.88)


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

    group = VGroup(*parts) if parts else VGroup(Text("", font_size=28, color=BLACK))
    group.arrange(DOWN, buff=0.45)
    group.move_to([0, 0.9, 0])

    # 세로형에서 너무 커지면 한 번 더 줄임
    max_group_width = config.frame_width * 0.86
    max_group_height = config.frame_height * 0.62

    if group.width > max_group_width:
        group.scale_to_fit_width(max_group_width)
    if group.height > max_group_height:
        group.scale_to_fit_height(max_group_height)

    caption_obj = _make_caption(caption)
    if caption_obj is not None:
        caption_obj.to_edge(DOWN, buff=0.6)
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
        _wrap_text(question, width=13),
        font_size=38,
        color=BLACK,
        line_spacing=0.9,
    )
    _fit_width(title_obj, config.frame_width * 0.84)
    title_obj.to_edge(UP, buff=1.0)

    body_obj = _make_body(body if body else "생각해 봅시다.")
    body_obj.next_to(title_obj, DOWN, buff=0.7)

    content = VGroup(title_obj, body_obj)
    if content.height > config.frame_height * 0.68:
        content.scale_to_fit_height(config.frame_height * 0.68)

    items = [content]

    caption_obj = _make_caption(caption)
    if caption_obj is not None:
        caption_obj.to_edge(DOWN, buff=0.6)
        items.append(caption_obj)

    group = VGroup(*items)
    _show_and_wait(ctx, group)


def render_compare(ctx: SceneContext, scene_data: dict[str, Any]) -> None:
    title = _safe_text(scene_data.get("title"), "비교하기")
    left = _safe_text(scene_data.get("left"))
    right = _safe_text(scene_data.get("right"))
    caption = _safe_text(scene_data.get("caption"))

    title_obj = Text(_wrap_text(title, width=12), font_size=38, color=BLACK)
    left_obj = Text(_wrap_text(left or "왼쪽", width=8), font_size=30, color=BLACK)
    vs_obj = Text(":", font_size=32, color=BLACK)
    right_obj = Text(_wrap_text(right or "오른쪽", width=8), font_size=30, color=BLACK)

    _fit_width(title_obj, config.frame_width * 0.84)
    _fit_width(left_obj, config.frame_width * 0.32)
    _fit_width(right_obj, config.frame_width * 0.32)

    row = VGroup(left_obj, vs_obj, right_obj).arrange(buff=0.35)
    col = VGroup(title_obj, row).arrange(DOWN, buff=0.7)
    col.move_to([0, 1.0, 0])

    if col.width > config.frame_width * 0.88:
        col.scale_to_fit_width(config.frame_width * 0.88)
    if col.height > config.frame_height * 0.62:
        col.scale_to_fit_height(config.frame_height * 0.62)

    items = [col]

    caption_obj = _make_caption(caption)
    if caption_obj is not None:
        caption_obj.to_edge(DOWN, buff=0.6)
        items.append(caption_obj)

    group = VGroup(*items)
    _show_and_wait(ctx, group)


def register_renderers() -> None:
    registry.register("fallback", render_fallback)
    registry.register("question", render_question)
    registry.register("compare", render_compare)