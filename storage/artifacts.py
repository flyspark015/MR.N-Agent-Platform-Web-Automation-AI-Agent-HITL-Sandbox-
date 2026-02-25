from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from storage.fs import csv_dir, downloads_dir, research_dir


def save_table_csv(task_id: str, name: str, df) -> Path:
    out = csv_dir(task_id) / f"{name}.csv"
    df.to_csv(out, index=False)
    return out


def save_download_metadata(task_id: str, items: List[Dict[str, Any]]) -> Path:
    out = downloads_dir(task_id) / "metadata.json"
    out.write_text(json.dumps(items, indent=2), encoding="utf-8")
    return out


def save_research_summary(task_id: str, data: Dict[str, Any]) -> Path:
    out = research_dir(task_id) / "summary.json"
    out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return out
