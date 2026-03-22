from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from . import config as app_config


def _get_setting(name: str, default):
    return getattr(app_config, name, default)


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _entry_file_path() -> Path:
    """
    Manim에 직접 넘길 엔트리 파일 경로.
    모듈명이 아니라 실제 .py 파일 경로를 사용한다.
    """
    return _project_root() / "src" / "math_video_factory" / "manim_entry.py"


def _scene_class_name(grade: int, video_id: str) -> str:
    """
    예:
        grade=0, video_id='g0_v0' -> Grade0Video0
        grade=1, video_id='g1_v2' -> Grade1Video2
    """
    try:
        suffix = video_id.split("_v", 1)[1]
        video_no = int(suffix)
    except (IndexError, ValueError) as exc:
        raise ValueError(f"video_id 형식이 올바르지 않습니다: {video_id}") from exc

    return f"Grade{grade}Video{video_no}"


def _quality_flag(quality: str | None) -> str:
    """
    manim 품질 옵션을 CLI 플래그로 변환한다.
    허용값:
      - l, low
      - m, medium
      - h, high
      - p, production
      - k, 4k
      - -pql / -pqm / -pqh / -pqp / -pqk
    """
    raw = (quality or str(_get_setting("MANIM_QUALITY", "m"))).strip().lower()

    mapping = {
        "l": "l",
        "low": "l",
        "m": "m",
        "medium": "m",
        "h": "h",
        "high": "h",
        "p": "p",
        "production": "p",
        "k": "k",
        "4k": "k",
    }

    if raw.startswith("-pq"):
        tail = raw[-1]
        if tail in {"l", "m", "h", "p", "k"}:
            return tail

    if raw not in mapping:
        allowed = "l, m, h, p, k"
        raise ValueError(f"지원하지 않는 quality 값입니다: {quality!r} (allowed: {allowed})")

    return mapping[raw]


def _write_temp_manim_cfg(
    *,
    media_dir: Path,
    pixel_width: int,
    pixel_height: int,
    frame_width: float,
    frame_height: float,
) -> Path:
    """
    세로형 쇼츠 렌더를 위한 임시 manim config 파일 생성.
    """
    cfg_text = f"""
[CLI]
media_dir = {media_dir.as_posix()}
pixel_width = {pixel_width}
pixel_height = {pixel_height}
frame_width = {frame_width}
frame_height = {frame_height}
background_color = WHITE
    """.strip()

    temp_dir = Path(tempfile.mkdtemp(prefix="manim_cfg_"))
    cfg_path = temp_dir / "manim.cfg"
    cfg_path.write_text(cfg_text, encoding="utf-8")
    return cfg_path


def _build_manim_command(
    *,
    grade: int,
    video_id: str,
    quality: str | None,
    preview: bool,
    media_dir: Path,
) -> list[str]:
    scene_class = _scene_class_name(grade, video_id)
    entry_file = _entry_file_path()

    if not entry_file.exists():
        raise FileNotFoundError(f"manim 엔트리 파일이 없습니다: {entry_file}")

    q = _quality_flag(quality)

    python_exe = shutil.which("python") or "python"

    command = [
        python_exe,
        "-m",
        "manim",
        f"-q{q}",
    ]

    if preview:
        command.append("-p")

    shorts_mode = bool(_get_setting("SHORTS_MODE", True))
    if shorts_mode:
        pixel_width = int(_get_setting("VIDEO_WIDTH", 1080))
        pixel_height = int(_get_setting("VIDEO_HEIGHT", 1920))
        frame_width = float(_get_setting("FRAME_WIDTH", 9.0))
        frame_height = float(_get_setting("FRAME_HEIGHT", 16.0))

        cfg_path = _write_temp_manim_cfg(
            media_dir=media_dir,
            pixel_width=pixel_width,
            pixel_height=pixel_height,
            frame_width=frame_width,
            frame_height=frame_height,
        )

        command.extend(
            [
                "--config_file",
                str(cfg_path),
            ]
        )

    command.extend(
        [
            "-o",
            video_id,
            str(entry_file),
            scene_class,
        ]
    )

    return command


def _find_rendered_video(media_dir: Path, video_id: str) -> Path:
    """
    manim 출력물 위치를 재귀적으로 탐색해서 최종 mp4를 찾는다.
    """
    matches = sorted(media_dir.rglob(f"{video_id}.mp4"))
    if not matches:
        raise FileNotFoundError(
            f"렌더링된 mp4를 찾을 수 없습니다: {video_id}.mp4 (search_root={media_dir})"
        )
    return matches[-1]


def render_video(
    *,
    grade: int,
    video_id: str,
    quality: str | None = None,
    preview: bool = False,
) -> Path:
    """
    커리큘럼 기반 Manim 영상을 렌더링하고 최종 mp4 경로를 반환한다.
    """
    project_root = _project_root()
    media_dir = project_root / "generated" / "manim_media"
    output_dir = project_root / "generated" / "videos"
    output_dir.mkdir(parents=True, exist_ok=True)
    media_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(project_root) + (os.pathsep + existing_pythonpath if existing_pythonpath else "")

    command = _build_manim_command(
        grade=grade,
        video_id=video_id,
        quality=quality,
        preview=preview,
        media_dir=media_dir,
    )

    result = subprocess.run(
        command,
        cwd=project_root,
        env=env,
        text=True,
        capture_output=True,
    )

    if result.returncode != 0:
        stdout_text = (result.stdout or "").strip()
        stderr_text = (result.stderr or "").strip()

        message_parts = [
            "[ERROR] Manim 렌더링 실패",
            f"command: {' '.join(command)}",
        ]

        if stdout_text:
            message_parts.append("=== MANIM STDOUT ===")
            message_parts.append(stdout_text)

        if stderr_text:
            message_parts.append("=== MANIM STDERR ===")
            message_parts.append(stderr_text)

        raise RuntimeError("\n".join(message_parts))

    rendered = _find_rendered_video(media_dir, video_id)
    final_path = output_dir / f"{video_id}.mp4"

    if rendered.resolve() != final_path.resolve():
        final_path.write_bytes(rendered.read_bytes())

    return final_path