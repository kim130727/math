from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render one executable JSON with Manim MVP runtime")
    parser.add_argument("--spec", required=True, type=Path, help="path to json_re/*.json")
    parser.add_argument("--quality", default="l", choices=["l", "m", "h", "p", "k"])
    parser.add_argument("--preview", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.spec.exists():
        raise FileNotFoundError(args.spec)

    runtime_py = Path("src/math_video_factory/problem_pipeline/manim_runtime.py")
    cmd = [
        "uv",
        "run",
        "manim",
        f"-q{args.quality}",
    ]
    if args.preview:
        cmd.append("-p")
    cmd.extend([str(runtime_py), "ProblemScene"])

    env = os.environ.copy()
    env["PROBLEM_SPEC_PATH"] = str(args.spec.resolve())

    print("[RUN]", " ".join(cmd))
    return subprocess.call(cmd, env=env)


if __name__ == "__main__":
    raise SystemExit(main())
