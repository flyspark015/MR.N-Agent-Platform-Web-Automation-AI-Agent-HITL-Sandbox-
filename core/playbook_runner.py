from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Type

from agent.critic import evaluate
from core.runtime import RuntimeConfig
from browser.session import BrowserSession
from browser.perceive import get_snapshot
from browser.tools import execute_action, autopilot_handlers
from skills.playbooks.research_playbook import ResearchPlaybook
from skills.playbooks.data_scraping_playbook import DataScrapingPlaybook
from skills.playbooks.supplier_playbook import SupplierPlaybook
from skills.playbooks.automation_playbook import AutomationPlaybook
from storage.fs import run_dir, save_json

@dataclass
class PlaybookState:
    goal: str
    playbook_type: str
    sources_visited: List[str] = field(default_factory=list)
    artifacts_collected: List[str] = field(default_factory=list)
    coverage_score: float = 0.0
    completion_status: str = "RUNNING"

@dataclass
class RuntimeContext:
    session: BrowserSession
    config: RuntimeConfig
    emit: Callable[[str, str], None]


class BasePlaybook:
    def plan(self, goal: str) -> None:
        raise NotImplementedError

    async def execute(self, runtime: RuntimeContext, state: PlaybookState) -> None:
        raise NotImplementedError

    async def evaluate(self, state: PlaybookState) -> Dict[str, object]:
        return {"goal_met": False, "missing_info": [], "next_step": ""}

    def finalize(self, state: PlaybookState) -> None:
        return None

class PlaybookRunner:
    def __init__(self) -> None:
        self.registry: Dict[str, Type[BasePlaybook]] = {
            "research": ResearchPlaybook,
            "data_scraping": DataScrapingPlaybook,
            "supplier": SupplierPlaybook,
            "automation": AutomationPlaybook,
        }

    def classify(self, goal: str) -> str:
        text = goal.lower()
        if any(k in text for k in ["research", "summarize", "compare", "sources"]):
            return "research"
        if any(k in text for k in ["table", "dataset", "csv", "scrape", "extract data"]):
            return "data_scraping"
        if any(k in text for k in ["supplier", "vendor", "wholesale", "manufacturer"]):
            return "supplier"
        if any(k in text for k in ["fill form", "submit", "automation", "apply"]):
            return "automation"
        return "research"

    async def run(self, goal: str, config: RuntimeConfig, bus: Optional[EventBus] = None) -> PlaybookState:
        playbook_type = self.classify(goal)
        playbook_cls = self.registry[playbook_type]
        playbook = playbook_cls()
        state = PlaybookState(goal=goal, playbook_type=playbook_type)
        playbook.plan(goal)

        session = BrowserSession(headless=config.headless, task_id=config.task_id, trace=config.trace)
        await session.start()
        def emit(tag: str, message: str, payload: Optional[Dict[str, str]] = None) -> None:
            if bus:
                bus.emit("log", {"tag": tag, "message": message})
                if payload and tag == "SNAPSHOT":
                    bus.emit("snapshot", payload)
        try:
            runtime = RuntimeContext(session=session, config=config, emit=emit)
            await playbook.execute(runtime, state)
            critic = await evaluate(goal, await get_snapshot(session.page, config.task_id, 0, 0), [])
            state.coverage_score = 1.0 if critic.get("goal_met") else 0.5
            state.completion_status = "DONE" if critic.get("goal_met") else "PARTIAL"
        finally:
            await session.stop()

        playbook.finalize(state)
        save_json(run_dir(config.task_id) / "playbook_state.json", json.loads(json.dumps(state.__dict__)))
        return state
