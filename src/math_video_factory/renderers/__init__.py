from __future__ import annotations

from .base import BaseRenderer, SceneContext
from .fallback_text import FallbackTextRenderer
from .question_popup import QuestionPopupRenderer
from .object_compare import ObjectCompareRenderer
from .shape_renderer import ShapeRenderer
from .clock_renderer import ClockRenderer
from .renderer_registry import registry


def register_renderers() -> None:
    registry.set_fallback(FallbackTextRenderer())

    registry.register("fallback", FallbackTextRenderer())
    registry.register("question", QuestionPopupRenderer())
    registry.register("compare", ObjectCompareRenderer())
    registry.register("shape", ShapeRenderer())
    registry.register("clock", ClockRenderer())


__all__ = [
    "registry",
    "register_renderers",
    "BaseRenderer",
    "SceneContext",
]