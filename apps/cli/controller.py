from __future__ import annotations

import asyncio
import threading
import uuid
from typing import List, Optional

from agent.actions import ActionRecord
from agent.executor import run_agent_loop
from logs.logger import Logger
from storage.files import result_path, save_json, trace_path

class ControllerState:
    def __init__(self) -> None:
        self.status = "IDLE"
        self.current_url = ""
        self.current_title = ""
        self.actions: List[ActionRecord] = []
        self.last_screenshot: Optional[str] = None
        self.evidence: List[str] = []
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

    def set_current_url(self, url: str) -> None:
        with self.state.lock:
            self.state.current_url = url

    def set_current_title(self, title: str) -> None:
        with self.state.lock:
            self.state.current_title = title

    def update_actions(self, actions: List[ActionRecord]) -> None:
        with self.state.lock:
            self.state.actions = actions

    def update_last_screenshot(self, path: str) -> None:
        with self.state.lock:
            self.state.last_screenshot = path
            self.state.evidence.append(path)

    def pause(self) -> None:
        self.pause_event.set()

    def resume(self) -> None:
        self.pause_event.clear()

    def cancel(self) -> None:
        self.cancel_event.set()

    def takeover_prompt(self, reason: str) -> None:
        with self.state.lock:
            self.state.status = "WAITING"
        self.log("TAKEOVER", f"TAKEOVER REQUIRED: {reason}")
        input("TAKEOVER REQUIRED: Complete login/OTP in browser. Press ENTER to continue.")
        with self.state.lock:
            self.state.status = "RUNNING"

    async def run_goal(self, goal: str):
        self.cancel_event.clear()
        self.pause_event.clear()
        task_id = str(uuid.uuid4())
        self._logger = Logger(task_id, jsonl=self.jsonl)

        with self.state.lock:
            self.state.status = "RUNNING"
            self.state.last_goal = goal
            self.state.task_id = task_id
            self.state.actions = []
            self.state.evidence = []

        self.log("PLAN", f"Starting agent loop for: {goal}")

        actions = await run_agent_loop(
            goal=goal,
            task_id=task_id,
            headless=self.headless,
            trace=self.trace,
            trace_path=trace_path(task_id) if self.trace else None,
            log=self.log,
            update_url=self.set_current_url,
            update_title=self.set_current_title,
            update_screenshot=self.update_last_screenshot,
            update_actions=self.update_actions,
            on_takeover=self.takeover_prompt,
        )

        final_url = self.state.current_url
        final_title = self.state.current_title
        with self.state.lock:
            evidence = list(self.state.evidence)

        status = "DONE"
        if any(a.status == "FAIL" for a in actions):
            status = "FAILED"
        if self.cancel_event.is_set():
            status = "CANCELLED"

        result = {
            "task_id": task_id,
            "goal": goal,
            "status": status,
            "final_url": final_url,
            "final_title": final_title,
            "evidence": evidence,
            "actions": [a.model_dump() for a in actions],
        }
        save_json(result_path(task_id), result)
        self.log("DONE", f"Saved result: {result_path(task_id)}")

        with self.state.lock:
            self.state.status = status

        return result

    def run_goal_sync(self, goal: str):
        return asyncio.run(self.run_goal(goal))
