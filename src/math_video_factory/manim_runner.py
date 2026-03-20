from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from .config import MANIM_ENTRY_FILE, MANIM_QUALITY, MANIM_SCENE_NAME, PROJECT_ROOT


def check_manim_available() -> None:
    """
    현재 환경에서 manim 실행이 가능한지 확인한다.
    """
    try:
        subprocess.run(
            [sys.executable, "-m", "manim", "--version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=PROJECT_ROOT,
        )
    except Exception as exc:
        raise RuntimeError(
            "manim을 실행할 수 없습니다. "
            "가상환경 설치 상태와 manim 의존성을 확인하세요."
        ) from exc


def render_script_with_manim(
    script_json_path: Path,
    *,
    entry_file: Path = MANIM_ENTRY_FILE,
    scene_name: str = MANIM_SCENE_NAME,
    quality_flag: str = MANIM_QUALITY,
    extra_env: dict[str, str] | None = None,
) -> None:
    """
    script JSON 경로를 환경변수로 넘겨 Manim 렌더를 수행한다.
    """
    if not script_json_path.exists():
        raise FileNotFoundError(f"script JSON 파일이 없습니다: {script_json_path}")

    if not entry_file.exists():
        raise FileNotFoundError(f"manim entry 파일이 없습니다: {entry_file}")

    check_manim_available()

    env = os.environ.copy()
    env["VIDEO_SCRIPT_PATH"] = str(script_json_path)

    if extra_env:
        env.update(extra_env)

    cmd = [
        sys.executable,
        "-m",
        "manim",
        quality_flag,
        str(entry_file),
        scene_name,
    ]

    print("\n=== Manim 렌더 ===")
    print(" ".join(cmd))
    print(f"[INFO] VIDEO_SCRIPT_PATH={script_json_path}")

    subprocess.run(
        cmd,
        check=True,
        cwd=PROJECT_ROOT,
        env=env,
    )


def find_latest_rendered_video(scene_name: str = MANIM_SCENE_NAME) -> Path:
    """
    Manim 렌더 후 생성된 mp4를 media/videos 아래에서 찾아 반환한다.
    """
    search_root = PROJECT_ROOT / "media" / "videos"

    if not search_root.exists():
        raise FileNotFoundError(
            f"Manim 렌더 출력 폴더가 없습니다: {search_root}"
        )

    candidates = sorted(search_root.glob(f"**/{scene_name}.mp4"))

    if not candidates:
        raise FileNotFoundError(
            f"Manim 렌더 결과를 찾지 못했습니다. scene_name={scene_name}"
        )

    return candidates[-1]


def copy_rendered_video_to(rendered_video_path: Path, out_path: Path) -> Path:
    """
    Manim이 만든 mp4를 원하는 위치로 복사한다.
    """
    if not rendered_video_path.exists():
        raise FileNotFoundError(f"렌더된 영상 파일이 없습니다: {rendered_video_path}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(rendered_video_path, out_path)
    return out_path


def render_and_collect_video(
    script_json_path: Path,
    output_video_path: Path,
    *,
    entry_file: Path = MANIM_ENTRY_FILE,
    scene_name: str = MANIM_SCENE_NAME,
    quality_flag: str = MANIM_QUALITY,
) -> Path:
    """
    Manim 렌더를 수행하고 결과 mp4를 지정 위치로 복사한다.
    """
    render_script_with_manim(
        script_json_path=script_json_path,
        entry_file=entry_file,
        scene_name=scene_name,
        quality_flag=quality_flag,
    )

    rendered = find_latest_rendered_video(scene_name=scene_name)
    final_path = copy_rendered_video_to(rendered, output_video_path)

    print(f"[DONE] 렌더 영상 복사 완료: {final_path}")
    return final_path