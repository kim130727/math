from __future__ import annotations

from .base import BaseRenderer, SceneContext
from .fallback_text import FallbackTextRenderer
from .question_popup import QuestionPopupRenderer
from .object_compare import ObjectCompareRenderer
from .renderer_registry import registry


def register_renderers() -> None:
    registry.set_fallback(FallbackTextRenderer())

    registry.register("fallback", FallbackTextRenderer())
    registry.register("question", QuestionPopupRenderer())
    registry.register("compare", ObjectCompareRenderer())


__all__ = [
    "registry",
    "register_renderers",
    "BaseRenderer",
    "SceneContext",
]