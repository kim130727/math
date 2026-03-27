from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def save_problem_spec(
    *,
    problem_spec: dict[str, Any],
    output_dir: Path,
    filename: str,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / filename
    out_path.write_text(
        json.dumps(problem_spec, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return out_path
