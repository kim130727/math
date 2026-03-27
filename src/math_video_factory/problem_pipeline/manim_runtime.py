from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Callable

from manim import (
    Arrow,
    BLUE,
    DOWN,
    FadeIn,
    FadeOut,
    GREEN,
    Indicate,
    LEFT,
    MathTex,
    ORANGE,
    PURPLE,
    Rectangle,
    RIGHT,
    Scene,
    Square,
    SurroundingRectangle,
    Text,
    UP,
    VGroup,
    WHITE,
    Write,
    config,
)


class ProblemSpecLoader:
    def load(self, path: str) -> dict[str, Any]:
        return json.loads(open(path, encoding="utf-8").read())


@dataclass(slots=True)
class ObjectHandle:
    object_id: str
    object_type: str
    mobject: Any
    raw: dict[str, Any]
    extras: dict[str, Any]


@dataclass(slots=True)
class RuntimeContext:
    scene: Scene
    objects: dict[str, ObjectHandle]
    completed_steps: set[str]


class SceneObjectFactory:
    def _text(self, content: str, scale: float = 0.7) -> Text:
        return Text(content or "", font_size=int(36 * scale), color=WHITE)

    def _math(self, latex: str, scale: float = 1.0) -> MathTex:
        safe = latex or "x"
        return MathTex(safe).scale(scale)

    def _make_base10(self, raw: dict[str, Any]) -> VGroup:
        comp = raw.get("components", {})
        hundreds = int(comp.get("hundreds", {}).get("count", 0))
        tens = int(comp.get("tens", {}).get("count", 0))
        ones = int(comp.get("ones", {}).get("count", 0))

        parts = VGroup()

        h_group = VGroup(*[Square(side_length=0.35, color=BLUE) for _ in range(min(hundreds, 9))])
        if len(h_group) > 0:
            h_group.arrange_in_grid(rows=3, cols=3, buff=0.05)
            parts.add(h_group)

        t_group = VGroup(*[Rectangle(width=0.09, height=0.35, color=GREEN) for _ in range(min(tens, 10))])
        if len(t_group) > 0:
            t_group.arrange(RIGHT, buff=0.03)
            parts.add(t_group)

        o_group = VGroup(*[Square(side_length=0.08, color=ORANGE) for _ in range(min(ones, 10))])
        if len(o_group) > 0:
            o_group.arrange(RIGHT, buff=0.02)
            parts.add(o_group)

        if len(parts) == 0:
            parts.add(Text("base10", font_size=24))

        parts.arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        return parts

    def build(self, scene_objects: list[dict[str, Any]]) -> dict[str, ObjectHandle]:
        built: dict[str, ObjectHandle] = {}

        for raw in scene_objects:
            object_id = str(raw.get("id", ""))
            object_type = str(raw.get("type", "text_block"))
            extras: dict[str, Any] = {}

            if object_type == "text_block":
                mob = self._text(str(raw.get("text", "")), scale=0.8)
            elif object_type == "math_expression":
                mob = self._math(str(raw.get("latex", "x")), scale=1.0)
            elif object_type == "answer_box":
                box = Rectangle(width=2.0, height=1.0, color=WHITE)
                placeholder = self._text(str(raw.get("placeholder", "□")), scale=0.8)
                placeholder.move_to(box.get_center())
                mob = VGroup(box, placeholder)
                extras["placeholder"] = placeholder
            elif object_type == "base10_blocks":
                mob = self._make_base10(raw)
            elif object_type == "highlight_box":
                mob = Rectangle(width=2.6, height=1.2, color=ORANGE)
            elif object_type == "arrow":
                mob = Arrow(start=LEFT * 0.8, end=RIGHT * 0.8, color=PURPLE)
            elif object_type == "vertical_algorithm":
                rows = raw.get("rows", ["917", "353", "___"])
                text = "\n".join(str(x) for x in rows)
                mob = self._text(text, scale=0.7)
            else:
                mob = self._text(f"[{object_type}]", scale=0.6)

            built[object_id] = ObjectHandle(
                object_id=object_id,
                object_type=object_type,
                mobject=mob,
                raw=raw,
                extras=extras,
            )

        return built


class LayoutEngine:
    def _region_to_point(self, region: list[float]) -> tuple[float, float]:
        fw = config.frame_width
        fh = config.frame_height
        x, y, w, h = region
        cx = -fw / 2 + (x + w / 2) * fw
        cy = fh / 2 - (y + h / 2) * fh
        return cx, cy

    def apply(self, layout_template: dict[str, Any], objects: dict[str, ObjectHandle]) -> None:
        regions = layout_template.get("regions", {})

        if "problem_text" in objects and "problem" in regions:
            x, y = self._region_to_point(regions["problem"])
            objects["problem_text"].mobject.move_to([x, y, 0]).to_edge(UP)

        if "main_expression" in objects and "work" in regions:
            x, y = self._region_to_point(regions["work"])
            objects["main_expression"].mobject.move_to([x, y, 0])

        if "answer_box" in objects and "answer" in regions:
            x, y = self._region_to_point(regions["answer"])
            objects["answer_box"].mobject.move_to([x, y, 0])

        base10_ids = [k for k, v in objects.items() if v.object_type == "base10_blocks"]
        if base10_ids:
            anchor_y = 0.2
            for idx, bid in enumerate(base10_ids):
                objects[bid].mobject.move_to([-3 + idx * 3.0, anchor_y, 0])


class NarrationManager:
    def __init__(self) -> None:
        self.caption_mob: Text | None = None

    def render_caption(self, scene: Scene, caption: str) -> None:
        if not caption:
            return
        new_caption = Text(caption, font_size=26, color=WHITE).to_edge(DOWN)
        if self.caption_mob is None:
            scene.play(FadeIn(new_caption), run_time=0.2)
        else:
            scene.play(FadeOut(self.caption_mob), FadeIn(new_caption), run_time=0.2)
        self.caption_mob = new_caption

    def build_narration_text(self, step: dict[str, Any]) -> str:
        narration = step.get("narration", {})
        if isinstance(narration, dict):
            return str(narration.get("primary", ""))
        return ""


class ActionExecutor:
    def __init__(self, narration: NarrationManager) -> None:
        self.narration = narration
        self.action_map: dict[str, Callable[[RuntimeContext, dict[str, Any]], None]] = {
            "display_problem": self._display_problem,
            "show_object": self._show_object,
            "highlight": self._highlight,
            "show_place_value": self._show_place_value,
            "combine_place_values": self._combine_place_values,
            "regroup": self._regroup,
            "derive_intermediate_value": self._derive_intermediate_value,
            "write_equation": self._write_equation,
            "transform_expression": self._transform_expression,
            "fill_answer": self._fill_answer,
            "show_feedback": self._show_feedback,
            "summarize": self._summarize,
            "conclude": self._conclude,
        }

    def _duration(self, step: dict[str, Any], default: float = 0.8) -> float:
        anim = step.get("animation", {})
        if isinstance(anim, dict):
            d = anim.get("duration")
            if isinstance(d, (float, int)):
                return float(d)
        return default

    def _run_checks(self, ctx: RuntimeContext, step: dict[str, Any]) -> bool:
        checks = step.get("checks", [])
        for check in checks:
            ctype = check.get("type")
            if ctype == "target_exists":
                target = check.get("target")
                if target not in ctx.objects:
                    self.narration.render_caption(ctx.scene, f"검사 실패: target {target} 없음")
                    return False
            if ctype == "answer_not_null":
                if step.get("inputs", {}).get("answer") is None:
                    self.narration.render_caption(ctx.scene, "검사 실패: answer 없음")
                    return False
        return True

    def execute(self, ctx: RuntimeContext, step: dict[str, Any]) -> None:
        deps = step.get("depends_on", [])
        if any(dep not in ctx.completed_steps for dep in deps):
            self.narration.render_caption(ctx.scene, f"의존 단계 미완료: {step.get('id')}")
            return

        self.narration.render_caption(ctx.scene, str(step.get("caption", "")))
        narration_text = self.narration.build_narration_text(step)
        if narration_text:
            note = Text(narration_text, font_size=22).to_edge(UP)
            ctx.scene.play(FadeIn(note), run_time=0.2)
            ctx.scene.play(FadeOut(note), run_time=0.2)

        if not self._run_checks(ctx, step):
            return

        action = str(step.get("action", ""))
        fn = self.action_map.get(action)
        if fn is None:
            return

        fn(ctx, step)
        ctx.completed_steps.add(str(step.get("id", "")))

    def _get_target(self, ctx: RuntimeContext, step: dict[str, Any]) -> ObjectHandle | None:
        target = step.get("target")
        if isinstance(target, str):
            return ctx.objects.get(target)
        return None

    def _display_problem(self, ctx: RuntimeContext, step: dict[str, Any]) -> None:
        h = self._get_target(ctx, step)
        if h is None:
            return
        ctx.scene.play(Write(h.mobject), run_time=self._duration(step))

    def _show_object(self, ctx: RuntimeContext, step: dict[str, Any]) -> None:
        h = self._get_target(ctx, step)
        if h is None:
            return
        ctx.scene.play(FadeIn(h.mobject), run_time=self._duration(step))

    def _highlight(self, ctx: RuntimeContext, step: dict[str, Any]) -> None:
        h = self._get_target(ctx, step)
        if h is None:
            return
        ctx.scene.play(Indicate(h.mobject, color=ORANGE), run_time=self._duration(step))

    def _show_place_value(self, ctx: RuntimeContext, step: dict[str, Any]) -> None:
        h = self._get_target(ctx, step)
        if h is None:
            return
        labels = Text("백/십/일 자리", font_size=26, color=BLUE).next_to(h.mobject, DOWN)
        ctx.scene.play(FadeIn(labels), run_time=0.4)
        ctx.scene.play(Indicate(h.mobject, color=BLUE), run_time=self._duration(step))
        ctx.scene.play(FadeOut(labels), run_time=0.3)

    def _combine_place_values(self, ctx: RuntimeContext, step: dict[str, Any]) -> None:
        h = self._get_target(ctx, step)
        if h is None:
            return
        out = step.get("outputs", {})
        value = out.get("ones_sum") or out.get("tens_raw") or out.get("value")
        msg = Text(f"중간값: {value}", font_size=26, color=GREEN).next_to(h.mobject, DOWN)
        ctx.scene.play(Indicate(h.mobject, color=GREEN), run_time=0.5)
        ctx.scene.play(Write(msg), run_time=self._duration(step))
        ctx.scene.play(FadeOut(msg), run_time=0.3)

    def _regroup(self, ctx: RuntimeContext, step: dict[str, Any]) -> None:
        h = self._get_target(ctx, step)
        if h is None:
            return
        arrow = Arrow(h.mobject.get_left() + UP * 0.2, h.mobject.get_right() + UP * 0.2, color=PURPLE)
        text = Text("자리 올림/내림", font_size=24, color=PURPLE).next_to(arrow, UP)
        ctx.scene.play(FadeIn(arrow), FadeIn(text), run_time=0.4)
        ctx.scene.play(Indicate(h.mobject, color=PURPLE), run_time=self._duration(step))
        ctx.scene.play(FadeOut(arrow), FadeOut(text), run_time=0.3)

    def _derive_intermediate_value(self, ctx: RuntimeContext, step: dict[str, Any]) -> None:
        h = self._get_target(ctx, step)
        if h is None:
            return
        out = step.get("outputs", {})
        value = out.get("final_answer") or out.get("older_count") or out.get("value")
        t = Text(f"계산 결과: {value}", font_size=26, color=GREEN).next_to(h.mobject, DOWN)
        ctx.scene.play(Write(t), run_time=self._duration(step))
        ctx.scene.play(FadeOut(t), run_time=0.3)

    def _write_equation(self, ctx: RuntimeContext, step: dict[str, Any]) -> None:
        h = self._get_target(ctx, step)
        if h is None:
            return
        eq = str(step.get("inputs", {}).get("equation", ""))
        t = Text(eq, font_size=28, color=WHITE).next_to(h.mobject, DOWN)
        ctx.scene.play(Write(t), run_time=self._duration(step))
        ctx.scene.play(FadeOut(t), run_time=0.3)

    def _transform_expression(self, ctx: RuntimeContext, step: dict[str, Any]) -> None:
        h = self._get_target(ctx, step)
        if h is None:
            return
        to_expr = str(step.get("inputs", {}).get("to", ""))
        if h.object_type == "math_expression" and to_expr:
            new_mob = MathTex(to_expr).move_to(h.mobject.get_center())
            ctx.scene.play(h.mobject.animate.become(new_mob), run_time=self._duration(step))

    def _fill_answer(self, ctx: RuntimeContext, step: dict[str, Any]) -> None:
        h = self._get_target(ctx, step)
        if h is None:
            return
        answer = step.get("inputs", {}).get("answer")
        if h.object_type == "answer_box" and isinstance(h.mobject, VGroup) and len(h.mobject) >= 2:
            new_text = Text(str(answer), font_size=34).move_to(h.mobject[0].get_center())
            ctx.scene.play(h.mobject[1].animate.become(new_text), run_time=self._duration(step))
        else:
            t = Text(str(answer), font_size=32).next_to(h.mobject, RIGHT)
            ctx.scene.play(Write(t), run_time=self._duration(step))

    def _show_feedback(self, ctx: RuntimeContext, step: dict[str, Any]) -> None:
        msg = str(step.get("inputs", {}).get("message", "좋아요!"))
        t = Text(msg, font_size=26, color=GREEN).to_edge(DOWN)
        ctx.scene.play(FadeIn(t), run_time=self._duration(step))
        ctx.scene.play(FadeOut(t), run_time=0.3)

    def _summarize(self, ctx: RuntimeContext, step: dict[str, Any]) -> None:
        msg = Text("핵심 요약", font_size=28, color=BLUE).to_edge(UP)
        ctx.scene.play(FadeIn(msg), run_time=self._duration(step))
        ctx.scene.play(FadeOut(msg), run_time=0.3)

    def _conclude(self, ctx: RuntimeContext, step: dict[str, Any]) -> None:
        h = self._get_target(ctx, step)
        if h is None:
            return
        sr = SurroundingRectangle(h.mobject, color=GREEN, buff=0.2)
        ctx.scene.play(FadeIn(sr), run_time=0.4)
        ctx.scene.play(FadeOut(sr), FadeOut(h.mobject), run_time=self._duration(step))


class ProblemScene(Scene):
    SPEC_PATH_ENV = "PROBLEM_SPEC_PATH"

    def construct(self) -> None:
        spec_path = os.environ.get(self.SPEC_PATH_ENV, "")
        if not spec_path:
            msg = Text("PROBLEM_SPEC_PATH 환경변수가 필요합니다", font_size=28)
            self.play(Write(msg))
            self.wait(1)
            return

        loader = ProblemSpecLoader()
        spec = loader.load(spec_path)

        validation = spec.get("validation", {})
        if not validation.get("render_safe", False):
            warn = Text("render_safe=false: 검수 필요", font_size=28, color=ORANGE)
            self.play(Write(warn))
            self.wait(1)
            return

        factory = SceneObjectFactory()
        objects = factory.build(spec.get("scene_objects", []))

        layout = LayoutEngine()
        layout.apply(spec.get("layout_template", {}), objects)

        narration = NarrationManager()
        executor = ActionExecutor(narration)

        ctx = RuntimeContext(scene=self, objects=objects, completed_steps=set())

        for step in spec.get("solution_plan", {}).get("steps", []):
            executor.execute(ctx, step)

        self.wait(0.5)
