from __future__ import annotations

import asyncio
import threading
import time
import uuid
from typing import List, Optional

from agent.actions import ActionRecord
from core.events import EventBus
from core.runtime import RuntimeConfig, run_task
from logs.logger import Logger

class ControllerState:
    def __init__(self) -> None:
        self.status = "IDLE"
        self.current_url = ""
        self.current_title = ""
        self.actions: List[ActionRecord] = []
        self.last_screenshot: Optional[str] = None
        self.last_goal: Optional[str] = None
        self.task_id: Optional[str] = None
        self.lock = threading.Lock()

class AgentController:
    def __init__(self, headless: bool, trace: bool, jsonl: bool) -> None:
        self.headless = headless
        self.trace = trace
        self.jsonl = jsonl
        self.state = ControllerState()
        self.pause_event = threading.Event()
        self.cancel_event = threading.Event()
        self._logger: Optional[Logger] = None

    def log(self, tag: str, message: str) -> None:
        if self._logger:
            self._logger.log(tag, message)

    def get_logs(self):
        return self._logger.entries if self._logger else []

    def _handle_snapshot(self, payload) -> None:
        with self.state.lock:
            self.state.current_url = payload.get("url", "")
            self.state.current_title = payload.get("title", "")
            self.state.last_screenshot = payload.get("screenshot_path")

    def _handle_action(self, payload) -> None:
        record = payload.get("record")
        if not record:
            return
        with self.state.lock:
            existing = {r.index: r for r in self.state.actions}
            existing[record.index] = record
            self.state.actions = [existing[k] for k in sorted(existing.keys())]

    def run_goal_sync(self, goal: str):
        task_id = str(uuid.uuid4())
        self._logger = Logger(task_id, jsonl=self.jsonl)
        bus = EventBus()
        bus.on("snapshot", self._handle_snapshot)
        bus.on("action", self._handle_action)
        bus.on("log", lambda p: self.log(p["tag"], p["message"]))

        with self.state.lock:
            self.state.status = "RUNNING"
            self.state.last_goal = goal
            self.state.task_id = task_id
            self.state.actions = []

        config = RuntimeConfig(headless=self.headless, trace=self.trace, jsonl=self.jsonl)
        result = asyncio.run(run_task(goal, config, bus=bus, task_id=task_id))

        with self.state.lock:
            self.state.status = result.get("status", "DONE")

        return result
