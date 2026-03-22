from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MANIM_ENTRY_FILE = PROJECT_ROOT / "src" / "math_video_factory" / "manim_entry.py"


def make_scene_class_name(grade: int, video_id: str) -> str:
    """
    예:
        grade=0, video_id='g0_v0' -> Grade0Video0
    """
    video_id = str(video_id).strip()

    try:
        grade_part, video_part = video_id.split("_", 1)
        if not grade_part.startswith("g") or not video_part.startswith("v"):
            raise ValueError

        parsed_grade = int(grade_part[1:])
        parsed_video = int(video_part[1:])
    except Exception as exc:
        raise ValueError(
            f"video_id 형식이 올바르지 않습니다: {video_id} (예: g0_v0)"
        ) from exc

    if parsed_grade != int(grade):
        raise ValueError(
            f"--grade 값({grade})과 --video 값({video_id})의 학년 번호가 다릅니다."
        )

    return f"Grade{parsed_grade}Video{parsed_video}"


def ensure_manim_entry_file() -> None:
    if not MANIM_ENTRY_FILE.exists():
        raise FileNotFoundError(f"manim_entry.py 파일이 없습니다: {MANIM_ENTRY_FILE}")


def build_manim_command(
    *,
    grade: int,
    video_id: str,
    quality: str = "l",
    preview: bool = False,
    save_last_frame: bool = False,
    extra_args: list[str] | None = None,
) -> list[str]:
    """
    Manim 실행 명령을 생성한다.
    """
    ensure_manim_entry_file()

    scene_class_name = make_scene_class_name(grade, video_id)

    cmd: list[str] = [
        sys.executable,
        "-m",
        "manim",
    ]

    if preview:
        cmd.append("-p")

    if save_last_frame:
        cmd.append("-s")

    cmd.append(f"-q{quality}")
    cmd.append(str(MANIM_ENTRY_FILE))
    cmd.append(scene_class_name)

    if extra_args:
        cmd.extend(extra_args)

    return cmd


def run_manim(
    *,
    grade: int,
    video_id: str,
    quality: str = "l",
    preview: bool = False,
    save_last_frame: bool = False,
    extra_args: list[str] | None = None,
    check: bool = False,
) -> int:
    """
    Manim 명령을 실제 실행하고 종료 코드를 반환한다.
    """
    cmd = build_manim_command(
        grade=grade,
        video_id=video_id,
        quality=quality,
        preview=preview,
        save_last_frame=save_last_frame,
        extra_args=extra_args,
    )

    print("[INFO] Manim 실행 명령:")
    print(" ".join(cmd))
    print()

    result = subprocess.run(
        cmd,
        cwd=str(PROJECT_ROOT),
        check=check,
    )
    return int(result.returncode)


def render_video(
    *,
    grade: int,
    video_id: str,
    quality: str = "l",
    preview: bool = False,
) -> int:
    """
    일반적인 영상 렌더링용 편의 함수
    """
    return run_manim(
        grade=grade,
        video_id=video_id,
        quality=quality,
        preview=preview,
    )