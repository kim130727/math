from __future__ import annotations

from pathlib import Path

from .config import (
    CURRICULUM_DIR,
    RENDERS_DIR,
    SCRIPTS_DIR,
    TIMINGS_DIR,
    TTS_DIR,
    VIDEOS_DIR,
    ensure_directories,
    validate_runtime_config,
)
from .curriculum_to_script import build_scripts_for_grade
from .ffmpeg_utils import build_final_video
from .loader import load_curriculum_by_grade
from .manim_runner import render_and_collect_video
from .save_script import save_script
from .timing import measure_and_save_timings
from .tts_engine import rebuild_tts_files


class BuildPipeline:
    """
    커리큘럼 YAML부터 최종 mp4까지 한 번에 생성하는 파이프라인
    """

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root
        ensure_directories()

    def build_grade(self, grade: int, video_id: str | None = None) -> list[Path]:
        """
        특정 학년 전체 또는 특정 video_id 하나만 빌드한다.
        반환값은 최종 mp4 경로 리스트이다.
        """
        validate_runtime_config(require_tts=True)

        curriculum = load_curriculum_by_grade(CURRICULUM_DIR, grade)
        scripts = build_scripts_for_grade(curriculum.grade, curriculum.videos)

        if video_id is not None:
            scripts = [script for script in scripts if script.video_id == video_id]
            if not scripts:
                raise ValueError(
                    f"{grade}학년 커리큘럼에 video_id='{video_id}'가 없습니다."
                )

        built_videos: list[Path] = []

        for script in scripts:
            print("\n" + "=" * 60)
            print(f"[BUILD START] {script.video_id} | {script.title}")
            print("=" * 60)

            final_video_path = self.build_video(script)
            built_videos.append(final_video_path)

            print(f"[BUILD DONE] {final_video_path}")

        return built_videos

    def build_video(self, script) -> Path:
        """
        ScriptSpec 1개를 받아 최종 영상까지 생성한다.
        """
        video_id = script.video_id

        script_json_path = SCRIPTS_DIR / f"{video_id}.json"
        tts_output_dir = TTS_DIR / video_id
        timing_json_path = TIMINGS_DIR / f"{video_id}.json"
        render_video_path = RENDERS_DIR / f"{video_id}.mp4"
        merged_audio_path = TTS_DIR / video_id / f"{video_id}_merged.mp3"
        final_video_path = VIDEOS_DIR / f"{video_id}_final.mp4"

        # 1) script json 저장
        print(f"[STEP 1] script 저장: {script_json_path}")
        save_script(script, script_json_path)

        # 2) TTS 재생성
        print(f"[STEP 2] TTS 생성: {tts_output_dir}")
        rebuild_tts_files(script_json_path, tts_output_dir)

        # 3) timings 저장
        print(f"[STEP 3] timings 저장: {timing_json_path}")
        measure_and_save_timings(video_id, tts_output_dir, timing_json_path)

        # 4) Manim 렌더
        print(f"[STEP 4] Manim 렌더: {render_video_path}")
        render_and_collect_video(
            script_json_path=script_json_path,
            timing_json_path=timing_json_path,
            output_video_path=render_video_path,
        )

        # 5) 영상 + 오디오 합성
        print(f"[STEP 5] 최종 영상 생성: {final_video_path}")
        build_final_video(
            render_video_path=render_video_path,
            tts_audio_dir=tts_output_dir,
            merged_audio_path=merged_audio_path,
            final_video_path=final_video_path,
        )

        return final_video_path