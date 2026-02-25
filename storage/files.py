from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path("data")
SCREENSHOTS_DIR = DATA_DIR / "screenshots"
RESULTS_DIR = DATA_DIR / "results"
TRACES_DIR = DATA_DIR / "traces"
LOGS_DIR = DATA_DIR / "logs"


def ensure_dirs() -> None:
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    TRACES_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def screenshot_path(task_id: str, step_id: int, label: str | None = None) -> Path:
    ensure_dirs()
    suffix = label or f"step_{step_id}"
    return SCREENSHOTS_DIR / f"{task_id}_{suffix}.png"


def result_path(task_id: str) -> Path:
    ensure_dirs()
    return RESULTS_DIR / f"{task_id}.json"


def trace_path(task_id: str) -> Path:
    ensure_dirs()
    return TRACES_DIR / f"{task_id}.zip"


def log_path(task_id: str) -> Path:
    ensure_dirs()
    return LOGS_DIR / f"{task_id}.jsonl"


def save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def append_jsonl(path: Path, data: Any) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(data) + "\n")
