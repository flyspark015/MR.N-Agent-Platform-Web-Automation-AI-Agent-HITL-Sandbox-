from __future__ import annotations

import asyncio
import threading
import uuid
from typing import Optional

from agent.executor import execute_plan
from agent.models import Plan, RunResult
from agent.planner import plan_goal
from logs.logger import Logger
from storage.files import result_path, save_json, trace_path

class ControllerState:
    def __init__(self) -> None:
        self.status = "IDLE"
        self.current_url = ""
        self.plan: Optional[Plan] = None
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

    def set_current_url(self, url: str) -> None:
        with self.state.lock:
            self.state.current_url = url

    def get_logs(self):
        return self._logger.entries if self._logger else []

    def should_pause(self) -> bool:
        return self.pause_event.is_set()

    def should_cancel(self) -> bool:
        return self.cancel_event.is_set()

    def pause(self) -> None:
        self.pause_event.set()

    def resume(self) -> None:
        self.pause_event.clear()

    def cancel(self) -> None:
        self.cancel_event.set()

    def takeover_prompt(self, reason: str) -> None:
        with self.state.lock:
            self.state.status = "WAITING"
        self.log("STEP", f"TAKEOVER REQUIRED: {reason}")
        input("TAKEOVER REQUIRED: Complete login/OTP in browser. Press ENTER to continue.")
        with self.state.lock:
            self.state.status = "RUNNING"

    async def run_goal(self, goal: str) -> RunResult:
        self.cancel_event.clear()
        self.pause_event.clear()
        task_id = str(uuid.uuid4())
        self._logger = Logger(task_id, jsonl=self.jsonl)

        with self.state.lock:
            self.state.status = "PLANNING"
            self.state.last_goal = goal
            self.state.task_id = task_id

        self.log("PLAN", f"Planning for goal: {goal}")
        plan = await plan_goal(goal)
        with self.state.lock:
            self.state.plan = plan
            self.state.status = "RUNNING"

        self.log("PLAN", f"Generated {len(plan.steps)} steps")

        plan = await execute_plan(
            plan=plan,
            task_id=task_id,
            headless=self.headless,
            trace=self.trace,
            trace_path=trace_path(task_id) if self.trace else None,
            log=self.log,
            update_url=self.set_current_url,
            on_takeover=self.takeover_prompt,
            should_cancel=self.should_cancel,
            should_pause=self.should_pause,
        )

        status = "DONE"
        if any(step.status == "FAIL" for step in plan.steps):
            status = "FAILED"
        if self.cancel_event.is_set():
            status = "CANCELLED"

        result = RunResult(task_id=task_id, goal=goal, status=status, steps=plan.steps)
        save_json(result_path(task_id), result.model_dump())
        self.log("DONE", f"Saved result: {result_path(task_id)}")

        with self.state.lock:
            self.state.status = status
            self.state.plan = plan

        return result

    def run_goal_sync(self, goal: str) -> RunResult:
        return asyncio.run(self.run_goal(goal))
