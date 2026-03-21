from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from . import config as app_config
from .config import (
    MANIM_ENTRY_FILE,
    MANIM_QUALITY,
    MANIM_SCENE_NAME,
)


def _get_setting(name: str, default):
    return getattr(app_config, name, default)


def _build_manim_command(
    *,
    media_dir: Path,
    env: dict[str, str],
) -> list[str]:
    """
    Manim CLI 실행 명령을 구성한다.
    쇼츠 모드일 때는 1080x1920 세로 해상도를 우선 적용한다.
    """

    shorts_mode = bool(_get_setting("SHORTS_MODE", True))
    video_width = int(_get_setting("VIDEO_WIDTH", 1080))
    video_height = int(_get_setting("VIDEO_HEIGHT", 1920))
    frame_rate = int(_get_setting("FRAME_RATE", 30))

    cmd = [
        "manim",
        MANIM_QUALITY,
        str(MANIM_ENTRY_FILE),
        MANIM_SCENE_NAME,
        "--media_dir",
        str(media_dir),
        "--fps",
        str(frame_rate),
    ]

    if shorts_mode:
        cmd.extend(
            [
                "-r",
                f"{video_width},{video_height}",
            ]
        )

    return cmd


def _find_rendered_video(media_dir: Path) -> Path:
    """
    Manim이 생성한 mp4를 media_dir 아래에서 찾아 반환한다.
    """
    candidates = sorted(media_dir.glob(f"videos/**/{MANIM_SCENE_NAME}.mp4"))
    if not candidates:
        raise FileNotFoundError(
            "Manim 렌더 결과 mp4를 찾지 못했습니다. "
            f"검색 경로: {media_dir / 'videos'}"
        )
    return candidates[-1]


def _run_subprocess(cmd: list[str], env: dict[str, str]) -> None:
    print("[MANIM CMD]")
    print(" ".join(cmd))

    try:
        subprocess.run(
            cmd,
            check=True,
            env=env,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "manim 명령을 찾을 수 없습니다. "
            "가상환경이 활성화되어 있는지, manim이 설치되어 있는지 확인하세요."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"Manim 렌더 실행에 실패했습니다. 종료 코드: {exc.returncode}"
        ) from exc


def render_and_collect_video(
    *,
    script_json_path: Path,
    timing_json_path: Path,
    output_video_path: Path,
) -> Path:
    """
    script/timing JSON을 환경변수로 넘겨 Manim 엔트리 파일을 실행하고,
    생성된 mp4를 output_video_path로 복사한다.

    Parameters
    ----------
    script_json_path:
        save_script()로 저장된 장면 스크립트 JSON 경로
    timing_json_path:
        measure_and_save_timings()로 저장된 timing JSON 경로
    output_video_path:
        최종 render mp4를 저장할 경로 (generated/renders/*.mp4)
    """
    if not script_json_path.exists():
        raise FileNotFoundError(f"script JSON이 없습니다: {script_json_path}")

    if not timing_json_path.exists():
        raise FileNotFoundError(f"timing JSON이 없습니다: {timing_json_path}")

    output_video_path.parent.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["MATH_SCRIPT_JSON"] = str(script_json_path.resolve())
    env["MATH_TIMING_JSON"] = str(timing_json_path.resolve())
    env["SHORTS_MODE"] = "1" if bool(_get_setting("SHORTS_MODE", True)) else "0"
    env["VIDEO_WIDTH"] = str(int(_get_setting("VIDEO_WIDTH", 1080)))
    env["VIDEO_HEIGHT"] = str(int(_get_setting("VIDEO_HEIGHT", 1920)))
    env["FRAME_RATE"] = str(int(_get_setting("FRAME_RATE", 30)))
    env["FRAME_WIDTH"] = str(float(_get_setting("FRAME_WIDTH", 9)))
    env["FRAME_HEIGHT"] = str(float(_get_setting("FRAME_HEIGHT", 16)))
    env["DEFAULT_FONT"] = str(_get_setting("DEFAULT_FONT", "Malgun Gothic"))

    with tempfile.TemporaryDirectory(prefix="math_video_manim_") as tmp_dir:
        media_dir = Path(tmp_dir)

        cmd = _build_manim_command(
            media_dir=media_dir,
            env=env,
        )
        _run_subprocess(cmd, env)

        rendered_video = _find_rendered_video(media_dir)
        shutil.copy2(rendered_video, output_video_path)

    print(f"[DONE] 렌더 영상 저장: {output_video_path}")
    return output_video_path


def _load_video_id_from_script(script_path: Path) -> str:
    """
    script JSON에서 video_id를 읽어온다.
    없으면 파일 stem을 사용한다.
    """
    try:
        data = json.loads(script_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"script JSON을 읽을 수 없습니다: {script_path}") from exc

    video_id = str(data.get("video_id", "")).strip()
    if video_id:
        return video_id
    return script_path.stem


def _guess_timing_json_path(script_path: Path, video_id: str) -> Path:
    """
    generated/scripts/{video_id}.json -> generated/timings/{video_id}.json
    규칙으로 timing JSON 경로를 추정한다.
    """
    scripts_dir = script_path.parent
    generated_dir = scripts_dir.parent
    timing_json_path = generated_dir / "timings" / f"{video_id}.json"
    return timing_json_path


def render_video(
    *,
    script_path: Path,
    output_path: Path,
    scene_id: str | None = None,
) -> Path:
    """
    build_pipeline.py가 호출할 표준 렌더 엔트리.

    Parameters
    ----------
    script_path:
        generated/scripts/{video_id}.json
    output_path:
        generated/renders/{video_id}.mp4
    scene_id:
        부분 렌더용 인자. 현재 구현에서는 사용하지 않지만,
        인터페이스 호환을 위해 받는다.
    """
    script_path = Path(script_path)
    output_path = Path(output_path)

    if scene_id:
        print(
            f"[WARN] scene_id={scene_id} 부분 렌더는 현재 manim_runner.py에서 "
            "아직 지원하지 않아 전체 렌더로 진행합니다."
        )

    video_id = _load_video_id_from_script(script_path)
    timing_json_path = _guess_timing_json_path(script_path, video_id)

    if not timing_json_path.exists():
        raise FileNotFoundError(
            "timing JSON이 없습니다. 먼저 timing 단계를 실행하세요.\n"
            f"- 예상 경로: {timing_json_path}\n"
            f"- 실행 예시: uv run main.py --grade 0 --video {video_id} --step timing"
        )

    return render_and_collect_video(
        script_json_path=script_path,
        timing_json_path=timing_json_path,
        output_video_path=output_path,
    )