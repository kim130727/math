from __future__ import annotations

import argparse
from pathlib import Path

from src.math_video_factory.problem_pipeline.problem_converter import ProblemConverter
from src.math_video_factory.problem_pipeline.save_problem_spec import save_problem_spec


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert legacy json/*.json to executable schema json_re/*.json")
    parser.add_argument("--input-dir", type=Path, default=Path("json"))
    parser.add_argument("--output-dir", type=Path, default=Path("json_re"))
    parser.add_argument("--use-llm", action="store_true", help="Use ChatGPT API enrichment")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    converter = ProblemConverter()

    input_files = sorted(args.input_dir.glob("*.json"))
    if not input_files:
        print(f"[WARN] no json files in {args.input_dir}")
        return 1

    for path in input_files:
        spec = converter.convert_file(path, use_llm=args.use_llm)
        out = save_problem_spec(problem_spec=spec, output_dir=args.output_dir, filename=path.name)
        print(f"[OK] {path.name} -> {out}")

    print(f"[DONE] converted {len(input_files)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
