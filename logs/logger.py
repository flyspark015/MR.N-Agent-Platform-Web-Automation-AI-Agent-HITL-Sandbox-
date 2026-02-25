from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import time

from storage.fs import append_jsonl, logs_path

@dataclass
class LogEntry:
    ts: float
    level: str
    tag: str
    message: str
    fields: Optional[Dict[str, Any]] = None

class Logger:
    def __init__(self, task_id: str, jsonl: bool = False):
        self.task_id = task_id
        self.jsonl = jsonl
        self.entries: List[LogEntry] = []
        self._path = logs_path(task_id) if jsonl else None

    def log(self, tag: str, message: str, level: str = "INFO", fields: Optional[Dict[str, Any]] = None) -> None:
        entry = LogEntry(time.time(), level, tag, message, fields)
        self.entries.append(entry)
        if self.jsonl and self._path:
            append_jsonl(self._path, {
                "ts": entry.ts,
                "level": level,
                "tag": tag,
                "message": message,
                "fields": fields or {},
            })
