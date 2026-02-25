from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path("data")


def run_dir(task_id: str) -> Path:
    return DATA_DIR / f"run_{task_id}"


def ensure_run_dirs(task_id: str) -> None:
    base = run_dir(task_id)
    (base / "screenshots").mkdir(parents=True, exist_ok=True)
    (base / "traces").mkdir(parents=True, exist_ok=True)
    (base / "artifacts" / "csv").mkdir(parents=True, exist_ok=True)
    (base / "artifacts" / "downloads").mkdir(parents=True, exist_ok=True)
    (base / "artifacts" / "research").mkdir(parents=True, exist_ok=True)


def screenshots_dir(task_id: str) -> Path:
    ensure_run_dirs(task_id)
    return run_dir(task_id) / "screenshots"


def traces_dir(task_id: str) -> Path:
    ensure_run_dirs(task_id)
    return run_dir(task_id) / "traces"


def logs_path(task_id: str) -> Path:
    ensure_run_dirs(task_id)
    return run_dir(task_id) / "logs.jsonl"


def result_path(task_id: str) -> Path:
    ensure_run_dirs(task_id)
    return run_dir(task_id) / "result.json"


def csv_dir(task_id: str) -> Path:
    ensure_run_dirs(task_id)
    return run_dir(task_id) / "artifacts" / "csv"


def downloads_dir(task_id: str) -> Path:
    ensure_run_dirs(task_id)
    return run_dir(task_id) / "artifacts" / "downloads"


def research_dir(task_id: str) -> Path:
    ensure_run_dirs(task_id)
    return run_dir(task_id) / "artifacts" / "research"


def save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def append_jsonl(path: Path, data: Any) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(data) + "\n")
