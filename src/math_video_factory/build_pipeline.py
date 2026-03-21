from __future__ import annotations

import importlib
import inspect
import json
from pathlib import Path
from typing import Any

import yaml
from pydub import AudioSegment

from .ffmpeg_utils import build_final_video


class BuildPipeline:
    """
    단계별 검증형 빌드 파이프라인

    지원 단계:
    - script : YAML -> Script JSON
    - review : Script JSON -> 사람이 읽기 쉬운 review markdown
    - tts    : 장면별 mp3 생성
    - timing : 장면별 mp3 길이 측정
    - render : Manim 렌더
    - final  : 병합 오디오 + 최종 mp4 합성
    - all    : 전체 실행
    """

    def __init__(self, project_root: Path | None = None) -> None:
        self.project_root = (
            project_root
            if project_root is not None
            else Path(__file__).resolve().parents[2]
        )

        self.curriculum_dir = self.project_root / "curriculum"
        self.generated_dir = self.project_root / "generated"

        self.scripts_dir = self.generated_dir / "scripts"
        self.reviews_dir = self.generated_dir / "reviews"
        self.tts_dir = self.generated_dir / "tts"
        self.timings_dir = self.generated_dir / "timings"
        self.renders_dir = self.generated_dir / "renders"
        self.videos_dir = self.generated_dir / "videos"

        for path in [
            self.generated_dir,
            self.scripts_dir,
            self.reviews_dir,
            self.tts_dir,
            self.timings_dir,
            self.renders_dir,
            self.videos_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # public
    # ------------------------------------------------------------------

    def build_grade(
        self,
        *,
        grade: int,
        video_id: str | None = None,
        step: str = "all",
        limit_scenes: int | None = None,
        scene: str | None = None,
    ) -> list[str]:
        curriculum = self._load_curriculum(grade=grade)
        videos = curriculum.get("videos", [])

        if not isinstance(videos, list) or not videos:
            raise ValueError(
                f"커리큘럼 파일 형식이 올바르지 않습니다: {self._curriculum_path(grade)}"
            )

        if video_id:
            videos = [video for video in videos if video.get("id") == video_id]
            if not videos:
                raise ValueError(
                    f"video_id={video_id} 를 curriculum/grade_{grade}.yaml 에서 찾지 못했습니다."
                )

        outputs: list[str] = []

        for video in videos:
            current_video_id = str(video["id"])

            if step == "script":
                outputs.append(str(self.build_script(grade=grade, video=video)))

            elif step == "review":
                script_path = self._ensure_script_exists(grade=grade, video=video)
                outputs.append(
                    str(
                        self.build_review(
                            script_path=script_path,
                            video_id=current_video_id,
                        )
                    )
                )

            elif step == "tts":
                script_path = self._ensure_script_exists(grade=grade, video=video)
                outputs.extend(
                    [
                        str(path)
                        for path in self.build_tts(
                            script_path=script_path,
                            video_id=current_video_id,
                            limit_scenes=limit_scenes,
                        )
                    ]
                )

            elif step == "timing":
                outputs.append(
                    str(
                        self.build_timing(
                            video_id=current_video_id,
                        )
                    )
                )

            elif step == "render":
                script_path = self._ensure_script_exists(grade=grade, video=video)
                outputs.append(
                    str(
                        self.build_render(
                            script_path=script_path,
                            video_id=current_video_id,
                            scene=scene,
                        )
                    )
                )

            elif step == "final":
                outputs.append(
                    str(
                        self.build_final(
                            video_id=current_video_id,
                        )
                    )
                )

            elif step == "all":
                script_path = self.build_script(grade=grade, video=video)
                review_path = self.build_review(
                    script_path=script_path,
                    video_id=current_video_id,
                )
                tts_paths = self.build_tts(
                    script_path=script_path,
                    video_id=current_video_id,
                    limit_scenes=limit_scenes,
                )
                timing_path = self.build_timing(video_id=current_video_id)
                render_path = self.build_render(
                    script_path=script_path,
                    video_id=current_video_id,
                    scene=scene,
                )
                final_path = self.build_final(video_id=current_video_id)

                outputs.extend(
                    [str(script_path), str(review_path)]
                    + [str(path) for path in tts_paths]
                    + [str(timing_path), str(render_path), str(final_path)]
                )

            else:
                raise ValueError(f"지원하지 않는 step입니다: {step}")

        return outputs

    def build_script(self, *, grade: int, video: dict[str, Any]) -> Path:
        script = self._video_to_script(grade=grade, video=video)
        script_path = self.scripts_dir / f"{video['id']}.json"

        script_path.write_text(
            json.dumps(script, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"[STEP script] 저장 완료: {script_path}")
        return script_path

    def build_review(self, *, script_path: Path, video_id: str) -> Path:
        if not script_path.exists():
            raise FileNotFoundError(f"script JSON이 없습니다: {script_path}")

        data = json.loads(script_path.read_text(encoding="utf-8"))
        scenes = data.get("scenes", [])

        lines: list[str] = []
        lines.append(f"# Review - {video_id}")
        lines.append("")
        lines.append(f"- 제목: {data.get('title', '')}")
        lines.append(f"- 개념: {data.get('concept', '')}")
        lines.append(f"- 시각 모델: {data.get('visual_model', '')}")
        lines.append("")

        for idx, scene in enumerate(scenes, start=1):
            lines.append(f"## [{idx}] {scene.get('type', '')}")
            lines.append("")
            lines.append(f"- scene_id: {scene.get('scene_id', '')}")
            lines.append(f"- visual: {scene.get('visual', '')}")
            lines.append(f"- 화면 문구: {scene.get('text', '')}")

            subtitle = scene.get("subtitle")
            if subtitle:
                lines.append(f"- 부제: {subtitle}")

            items = scene.get("items")
            if items:
                lines.append(f"- items: {', '.join(str(x) for x in items)}")

            sequence = scene.get("sequence")
            if sequence:
                lines.append(
                    f"- sequence: {' -> '.join(str(x) for x in sequence)}"
                )

            focus_word = scene.get("focus_word")
            if focus_word:
                lines.append(f"- focus_word: {focus_word}")

            lines.append(f"- 내레이션: {scene.get('tts', '')}")
            lines.append("")

        review_path = self.reviews_dir / f"{video_id}_review.md"
        review_path.write_text("\n".join(lines), encoding="utf-8")

        print(f"[STEP review] 저장 완료: {review_path}")
        return review_path

    def build_tts(
        self,
        *,
        script_path: Path,
        video_id: str,
        limit_scenes: int | None = None,
    ) -> list[Path]:
        if not script_path.exists():
            raise FileNotFoundError(f"script JSON이 없습니다: {script_path}")

        output_dir = self.tts_dir / video_id
        output_dir.mkdir(parents=True, exist_ok=True)

        module = self._safe_import(".tts_engine")
        if module is not None:
            result = self._try_call_tts_module(
                module=module,
                script_path=script_path,
                output_dir=output_dir,
                limit_scenes=limit_scenes,
            )
            if result:
                print(f"[STEP tts] 생성 완료: {output_dir}")
                return sorted(result)

        raise RuntimeError(
            "tts_engine 호출 규칙을 찾지 못했습니다.\n"
            "현재 프로젝트의 tts_engine.py 함수명을 아래 후보 중 하나로 맞추거나,\n"
            "build_pipeline.py의 _try_call_tts_module() 후보 목록을 맞게 수정해주세요.\n"
            "- generate_tts_from_script\n"
            "- generate_tts_for_script\n"
            "- build_tts\n"
            "- generate_tts"
        )

    def build_timing(self, *, video_id: str) -> Path:
        audio_dir = self.tts_dir / video_id
        if not audio_dir.exists():
            raise FileNotFoundError(f"TTS 디렉터리가 없습니다: {audio_dir}")

        module = self._safe_import(".timing")
        if module is not None:
            result = self._try_call_timing_module(
                module=module,
                video_id=video_id,
                audio_dir=audio_dir,
            )
            if result is not None:
                return result

        # fallback: 내부 구현으로 길이 측정
        mp3_files = sorted(
            [
                path
                for path in audio_dir.glob("*.mp3")
                if not path.name.endswith("_merged.mp3")
            ]
        )
        if not mp3_files:
            raise FileNotFoundError(f"mp3 파일이 없습니다: {audio_dir}")

        rows: list[dict[str, Any]] = []
        total_sec = 0.0

        for idx, mp3_path in enumerate(mp3_files, start=1):
            audio = AudioSegment.from_file(mp3_path)
            sec = round(len(audio) / 1000.0, 3)
            total_sec += sec
            rows.append(
                {
                    "scene_index": idx,
                    "file": mp3_path.name,
                    "duration_sec": sec,
                }
            )

        timing_data = {
            "video_id": video_id,
            "scene_count": len(rows),
            "total_duration_sec": round(total_sec, 3),
            "items": rows,
        }

        timing_path = self.timings_dir / f"{video_id}.json"
        timing_path.write_text(
            json.dumps(timing_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        print(f"[STEP timing] 저장 완료: {timing_path}")
        return timing_path

    def build_render(
        self,
        *,
        script_path: Path,
        video_id: str,
        scene: str | None = None,
    ) -> Path:
        if not script_path.exists():
            raise FileNotFoundError(f"script JSON이 없습니다: {script_path}")

        render_path = self.renders_dir / f"{video_id}.mp4"

        module = self._safe_import(".manim_runner")
        if module is not None:
            result = self._try_call_render_module(
                module=module,
                script_path=script_path,
                render_path=render_path,
                video_id=video_id,
                scene=scene,
            )
            if result is not None:
                print(f"[STEP render] 생성 완료: {result}")
                return result

        raise RuntimeError(
            "manim_runner 호출 규칙을 찾지 못했습니다.\n"
            "현재 프로젝트의 manim_runner.py 함수명을 아래 후보 중 하나로 맞추거나,\n"
            "build_pipeline.py의 _try_call_render_module() 후보 목록을 맞게 수정해주세요.\n"
            "- render_video\n"
            "- render_script\n"
            "- render_manim\n"
            "- build_render"
        )

    def build_final(self, *, video_id: str) -> Path:
        render_video_path = self.renders_dir / f"{video_id}.mp4"
        tts_audio_dir = self.tts_dir / video_id
        merged_audio_path = self.tts_dir / video_id / f"{video_id}_merged.mp3"
        final_video_path = self.videos_dir / f"{video_id}_final.mp4"

        result = build_final_video(
            render_video_path=render_video_path,
            tts_audio_dir=tts_audio_dir,
            merged_audio_path=merged_audio_path,
            final_video_path=final_video_path,
        )

        print(f"[STEP final] 생성 완료: {result}")
        return result

    # ------------------------------------------------------------------
    # private: curriculum / script
    # ------------------------------------------------------------------

    def _curriculum_path(self, grade: int) -> Path:
        return self.curriculum_dir / f"grade_{grade}.yaml"

    def _load_curriculum(self, *, grade: int) -> dict[str, Any]:
        path = self._curriculum_path(grade)
        if not path.exists():
            raise FileNotFoundError(f"커리큘럼 파일이 없습니다: {path}")

        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"커리큘럼 파일 형식이 올바르지 않습니다: {path}")
        return data

    def _ensure_script_exists(self, *, grade: int, video: dict[str, Any]) -> Path:
        script_path = self.scripts_dir / f"{video['id']}.json"
        if not script_path.exists():
            return self.build_script(grade=grade, video=video)
        return script_path

    def _video_to_script(self, *, grade: int, video: dict[str, Any]) -> dict[str, Any]:
        """
        YAML의 flow 기반 구조를 script JSON으로 변환한다.
        flow가 없을 때는 기본 장면 세트를 자동 구성한다.
        """
        video_id = str(video["id"])
        title = str(video.get("title", ""))
        concept = str(video.get("concept", ""))
        visual_model = str(video.get("visual_model", "default"))
        narration_style = str(video.get("narration_style", "기본"))
        conclusion = str(video.get("conclusion", ""))
        flow = video.get("flow") or []

        scenes: list[dict[str, Any]] = []

        # 시작 title 장면은 항상 하나 넣어준다.
        scenes.append(
            {
                "scene_id": "s1",
                "type": "title",
                "text": title,
                "subtitle": conclusion if conclusion else concept,
                "visual": "title_emphasis",
                "tts": self._title_tts(title=title, conclusion=conclusion, concept=concept),
            }
        )

        if isinstance(flow, list) and flow:
            for idx, item in enumerate(flow, start=2):
                if not isinstance(item, dict):
                    continue

                scene_type = str(item.get("scene", f"scene_{idx}"))
                text = str(item.get("text", "")).strip()
                visual = str(item.get("visual", "default")).strip() or "default"

                scene_data: dict[str, Any] = {
                    "scene_id": f"s{idx}",
                    "type": scene_type,
                    "text": text,
                    "visual": visual,
                    "tts": self._flow_scene_tts(scene_type=scene_type, text=text),
                }

                if scene_type == "problem":
                    scene_data["items"] = self._extract_items_from_text(text)

                if scene_type == "observation":
                    focus_word = self._guess_focus_word(text)
                    if focus_word:
                        scene_data["focus_word"] = focus_word

                if scene_type in {"transformation", "transform"}:
                    sequence = self._make_sequence_from_example(video)
                    if sequence:
                        scene_data["sequence"] = sequence
                        scene_data["type"] = "transform"

                scenes.append(scene_data)
        else:
            # fallback: flow가 없을 때 최소 장면 자동 생성
            example_story = str((video.get("example") or {}).get("story", ""))
            key_understanding = str(video.get("key_understanding", ""))

            fallback_scenes = [
                {
                    "type": "hook",
                    "text": f"{title}는 어떤 뜻일까요?",
                    "visual": "question_popup",
                    "tts": f"{title}는 어떤 뜻일까요?",
                },
                {
                    "type": "concept",
                    "text": key_understanding,
                    "visual": visual_model,
                    "tts": key_understanding,
                },
                {
                    "type": "example",
                    "text": example_story,
                    "visual": "example_focus",
                    "tts": example_story,
                },
                {
                    "type": "wrap_up",
                    "text": conclusion or key_understanding,
                    "visual": "title_emphasis",
                    "tts": conclusion or key_understanding,
                },
            ]

            start_index = len(scenes) + 1
            for offset, item in enumerate(fallback_scenes):
                scene = {
                    "scene_id": f"s{start_index + offset}",
                    **item,
                }
                scenes.append(scene)

        return {
            "video_id": video_id,
            "grade": grade,
            "title": title,
            "concept": concept,
            "visual_model": visual_model,
            "narration_style": narration_style,
            "scenes": scenes,
            "conclusion": conclusion,
        }

    # ------------------------------------------------------------------
    # private: helpers
    # ------------------------------------------------------------------

    def _title_tts(self, *, title: str, conclusion: str, concept: str) -> str:
        if conclusion:
            return f"{title}. {conclusion}"
        if concept:
            return f"{title}. 이번 영상에서는 {concept}을 알아봅니다."
        return title

    def _flow_scene_tts(self, *, scene_type: str, text: str) -> str:
        if not text:
            return ""

        if scene_type == "hook":
            return text
        if scene_type == "problem":
            return text
        if scene_type == "observation":
            return text
        if scene_type in {"abstraction", "concept", "realization"}:
            return text
        if scene_type in {"transformation", "transform"}:
            return text
        if scene_type == "wrap_up":
            return text
        return text

    def _extract_items_from_text(self, text: str) -> list[str]:
        candidates = ["사과", "공", "자동차", "연필", "책", "사탕", "블록"]
        found = [word for word in candidates if word in text]
        return found

    def _guess_focus_word(self, text: str) -> str | None:
        focus_candidates = ["개수", "규칙", "구조", "관계", "길이", "시간", "수"]
        for word in focus_candidates:
            if word in text:
                return word
        return None

    def _make_sequence_from_example(self, video: dict[str, Any]) -> list[str]:
        example = video.get("example") or {}
        story = str(example.get("story", "")).strip()

        if "->" in story:
            return [part.strip() for part in story.split("->") if part.strip()]
        if "→" in story:
            return [part.strip() for part in story.split("→") if part.strip()]
        return []

    def _safe_import(self, module_name: str):
        try:
            return importlib.import_module(module_name, package=__package__)
        except Exception:
            return None

    # ------------------------------------------------------------------
    # private: dynamic module adapters
    # ------------------------------------------------------------------

    def _try_call_tts_module(
        self,
        *,
        module,
        script_path: Path,
        output_dir: Path,
        limit_scenes: int | None,
    ) -> list[Path] | None:
        candidates = [
            "generate_tts_from_script",
            "generate_tts_for_script",
            "build_tts",
            "generate_tts",
        ]

        for name in candidates:
            func = getattr(module, name, None)
            if not callable(func):
                continue

            kwargs_candidates = [
                {
                    "script_path": script_path,
                    "output_dir": output_dir,
                    "limit_scenes": limit_scenes,
                },
                {
                    "script_json_path": script_path,
                    "output_dir": output_dir,
                    "limit_scenes": limit_scenes,
                },
                {
                    "script_path": script_path,
                    "tts_output_dir": output_dir,
                    "limit_scenes": limit_scenes,
                },
                {
                    "script_path": script_path,
                    "output_dir": output_dir,
                },
            ]

            for kwargs in kwargs_candidates:
                filtered_kwargs = self._filter_kwargs(func, kwargs)
                try:
                    func(**filtered_kwargs)
                    return sorted(output_dir.glob("*.mp3"))
                except TypeError:
                    continue

        return None

    def _try_call_timing_module(
        self,
        *,
        module,
        video_id: str,
        audio_dir: Path,
    ) -> Path | None:
        candidates = [
            "measure_tts_dir",
            "measure_tts_timings",
            "build_timing",
            "measure_timings",
        ]

        timing_path = self.timings_dir / f"{video_id}.json"

        for name in candidates:
            func = getattr(module, name, None)
            if not callable(func):
                continue

            kwargs_candidates = [
                {
                    "tts_audio_dir": audio_dir,
                    "output_path": timing_path,
                },
                {
                    "audio_dir": audio_dir,
                    "output_path": timing_path,
                },
                {
                    "tts_dir": audio_dir,
                    "timing_output_path": timing_path,
                },
                {
                    "audio_dir": audio_dir,
                },
            ]

            for kwargs in kwargs_candidates:
                filtered_kwargs = self._filter_kwargs(func, kwargs)
                try:
                    result = func(**filtered_kwargs)
                    if isinstance(result, Path):
                        print(f"[STEP timing] 저장 완료: {result}")
                        return result
                    if timing_path.exists():
                        print(f"[STEP timing] 저장 완료: {timing_path}")
                        return timing_path
                except TypeError:
                    continue

        return None

    def _try_call_render_module(
        self,
        *,
        module,
        script_path: Path,
        render_path: Path,
        video_id: str,
        scene: str | None,
    ) -> Path | None:
        candidates = [
            "render_video",
            "render_script",
            "render_manim",
            "build_render",
        ]

        for name in candidates:
            func = getattr(module, name, None)
            if not callable(func):
                continue

            kwargs_candidates = [
                {
                    "script_path": script_path,
                    "output_path": render_path,
                    "scene_id": scene,
                },
                {
                    "script_json_path": script_path,
                    "output_path": render_path,
                    "scene_id": scene,
                },
                {
                    "script_path": script_path,
                    "render_video_path": render_path,
                    "scene_id": scene,
                },
                {
                    "script_path": script_path,
                    "video_id": video_id,
                    "output_path": render_path,
                    "scene_id": scene,
                },
                {
                    "script_path": script_path,
                    "output_path": render_path,
                },
            ]

            for kwargs in kwargs_candidates:
                filtered_kwargs = self._filter_kwargs(func, kwargs)
                try:
                    result = func(**filtered_kwargs)
                    if isinstance(result, Path):
                        return result
                    if render_path.exists():
                        return render_path
                except TypeError:
                    continue

        return None

    def _filter_kwargs(self, func, kwargs: dict[str, Any]) -> dict[str, Any]:
        sig = inspect.signature(func)
        accepted = set(sig.parameters.keys())
        return {k: v for k, v in kwargs.items() if k in accepted}