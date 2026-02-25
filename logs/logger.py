from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List

from storage.fs import append_jsonl, logs_path

@dataclass
class LogEntry:
    ts: float
    tag: str
    message: str

class Logger:
    def __init__(self, task_id: str, jsonl: bool = False):
        self.task_id = task_id
        self.jsonl = jsonl
        self.entries: List[LogEntry] = []
        self._path = logs_path(task_id) if jsonl else None

    def log(self, tag: str, message: str) -> None:
        entry = LogEntry(time.time(), tag, message)
        self.entries.append(entry)
        if self.jsonl and self._path:
            append_jsonl(self._path, {"ts": entry.ts, "tag": tag, "message": message})
