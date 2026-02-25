from __future__ import annotations

import threading
import uuid
from typing import List, Optional

from agent.actions import ActionRecord
from core.playbook_selector import PlaybookSelector
from core.runtime import RuntimeConfig
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
        self.mode = "SAFE"
        self.playbook_type = ""
        self.playbook_confidence = 0.0
        self.budget = "0/0"
        self.session_status = "idle"
        self.lock = threading.Lock()

class AgentController:
    def __init__(self, headless: bool, trace: bool, jsonl: bool) -> None:
        self.headless = headless
        self.trace = trace
        self.jsonl = jsonl
        self.state = ControllerState()
        self._logger: Optional[Logger] = None

    def log(self, tag: str, message: str, level: str = "INFO") -> None:
        if self._logger:
            self._logger.log(tag, message, level=level)

    def get_logs(self):
        return self._logger.entries if self._logger else []

    def _handle_snapshot(self, payload) -> None:
        with self.state.lock:
            self.state.current_url = payload.get("url", "")
            self.state.current_title = payload.get("title", "")
            self.state.last_screenshot = payload.get("screenshot_path")

    def run_goal_sync(self, goal: str):
        task_id = str(uuid.uuid4())
        self._logger = Logger(task_id, jsonl=self.jsonl)

        with self.state.lock:
            self.state.status = "RUNNING"
            self.state.last_goal = goal
            self.state.task_id = task_id
            self.state.actions = []
            self.state.session_status = "running"

        config = RuntimeConfig(headless=self.headless, trace=self.trace, jsonl=self.jsonl, task_id=task_id)
        selector = PlaybookSelector()
        state = asyncio_run(selector.run(goal, config, bus=None))

        with self.state.lock:
            self.state.status = state.completion_status
            self.state.session_status = "stopped"

        return state


def asyncio_run(coro):
    import asyncio
    return asyncio.run(coro)
