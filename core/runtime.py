from __future__ import annotations

import asyncio
import time
import uuid
from typing import Dict, List, Optional

from agent.actions import Action, ActionRecord
from agent.critic import evaluate
from agent.decide import decide_action
from agent.recovery import recover
from agent.verifier import verify
from browser.perceive import get_snapshot
from browser.session import BrowserSession
from browser.tools import execute_action, autopilot_handlers
from core.events import EventBus
from core.state import TaskState
from logs.logger import Logger
from storage.fs import result_path, save_json

class RuntimeConfig:
    def __init__(
        self,
        headless: bool = False,
        trace: bool = False,
        jsonl: bool = False,
        max_actions: int = 40,
        step_timeout: int = 30,
    ) -> None:
        self.headless = headless
        self.trace = trace
        self.jsonl = jsonl
        self.max_actions = max_actions
        self.step_timeout = step_timeout

async def run_task(goal: str, config: RuntimeConfig, bus: Optional[EventBus] = None, task_id: Optional[str] = None) -> Dict[str, object]:
    task_id = task_id or str(uuid.uuid4())
    logger = Logger(task_id, jsonl=config.jsonl)
    state = TaskState(task_id=task_id, goal=goal, status="RUNNING")

    def emit(tag: str, message: str) -> None:
        logger.log(tag, message)
        if bus:
            bus.emit("log", {"tag": tag, "message": message})

    session = BrowserSession(headless=config.headless, task_id=task_id, trace=config.trace)
    await session.start()
    page = session.page

    actions_history: List[Action] = []
    records: List[ActionRecord] = []
    seen_keys: List[str] = []
    pages_for_research: List[Dict[str, str]] = []

    try:
        for idx in range(1, config.max_actions + 1):
            await autopilot_handlers(page)
            snapshot = await get_snapshot(page, task_id, idx, 0)
            state.current_url = snapshot.url
            state.current_title = snapshot.title
            state.evidence.append(snapshot.screenshot_path)
            emit("SNAPSHOT", f"{snapshot.url} | {snapshot.title} | screenshot={snapshot.screenshot_path}")
            if bus:
                bus.emit(
                    "snapshot",
                    {
                        "url": snapshot.url,
                        "title": snapshot.title,
                        "screenshot_path": snapshot.screenshot_path,
                    },
                )

            action = await decide_action(goal, snapshot, actions_history)
            record = ActionRecord(index=idx, action=action)
            records.append(record)
            state.actions = records
            emit("ACTION", f"type={action.type} reason={action.reason}")
            if bus:
                bus.emit("action", {"record": record})

            if action.type == "takeover":
                record.status = "FAIL"
                emit("TAKEOVER", "Takeover required")
                state.status = "WAITING"
                if bus:
                    bus.emit("action", {"record": record})
                break

            if action.type == "done":
                record.status = "DONE"
                emit("DONE", "Agent marked task as done")
                state.status = "DONE"
                if bus:
                    bus.emit("action", {"record": record})
                break

            try:
                result = await asyncio.wait_for(
                    execute_action(action, page, task_id, {"goal": goal, "pages": pages_for_research}),
                    timeout=config.step_timeout,
                )
                if action.type in ["navigate", "open_result", "click", "google_search"]:
                    pages_for_research.append(
                        {
                            "url": page.url,
                            "title": await page.title(),
                            "text": snapshot.visible_text_summary,
                        }
                    )
                if action.verify:
                    ok = await verify(page, action.verify)
                    emit("VERIFY", "pass" if ok else "fail")
                    if not ok:
                        await recover(page, goal, emit)

                if result.get("extract"):
                    emit("STEP", f"Extracted: {result['extract']}")
                if result.get("tables"):
                    emit("EVIDENCE", f"Tables saved: {result['tables']}")
                if result.get("downloads"):
                    emit("EVIDENCE", "Downloads saved")
                if result.get("summary"):
                    emit("STEP", "Research summary saved")

                record.status = "DONE"
                if bus:
                    bus.emit("action", {"record": record})
            except Exception as exc:
                record.status = "FAIL"
                record.error = str(exc)
                emit("ERROR", f"Action failed: {exc}")
                state.status = "FAILED"
                if bus:
                    bus.emit("action", {"record": record})
                break

            next_snapshot = await get_snapshot(page, task_id, idx, 1)
            state.current_title = next_snapshot.title
            state.evidence.append(next_snapshot.screenshot_path)
            if bus:
                bus.emit(
                    "snapshot",
                    {
                        "url": next_snapshot.url,
                        "title": next_snapshot.title,
                        "screenshot_path": next_snapshot.screenshot_path,
                    },
                )
            key = f"{next_snapshot.screenshot_hash}:{next_snapshot.dom_hash}:{next_snapshot.url}"
            seen_keys.append(key)
            if len(seen_keys) > 3:
                seen_keys.pop(0)
            if len(seen_keys) == 3 and len(set(seen_keys)) == 1:
                emit("RECOVERY", "Stuck detected")
                await recover(page, goal, emit)

            actions_history.append(action)

            critic = await evaluate(goal, next_snapshot, actions_history)
            emit("VERIFY", f"critic goal_met={critic.get('goal_met')}")
            if critic.get("goal_met"):
                state.status = "DONE"
                break

        if state.status == "RUNNING":
            state.status = "DONE"

    finally:
        await session.stop()

    result = {
        "task_id": task_id,
        "goal": goal,
        "status": state.status,
        "final_url": state.current_url,
        "final_title": state.current_title,
        "evidence": state.evidence,
        "actions": [r.model_dump() for r in records],
    }
    save_json(result_path(task_id), result)
    emit("DONE", f"Saved result: {result_path(task_id)}")
    return result
