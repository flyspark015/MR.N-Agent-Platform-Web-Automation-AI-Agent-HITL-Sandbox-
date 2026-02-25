from __future__ import annotations

import asyncio

from core.playbook_runner import PlaybookRunner
from core.research_service import generate_context
from core.runtime import RuntimeConfig

class PlaybookSelector:
    def __init__(self) -> None:
        self.runner = PlaybookRunner()

    async def classify(self, goal: str) -> dict:
        ctx = await generate_context(goal)
        text = (ctx.get("goal") or goal).lower()
        playbook = "research"
        confidence = 0.6
        summary = "default to research"
        if any(k in text for k in ["supplier", "vendor", "wholesale", "manufacturer"]):
            playbook = "supplier"
            confidence = 0.8
            summary = "supplier keywords detected"
        if any(k in text for k in ["table", "dataset", "csv", "scrape", "extract data"]):
            playbook = "data_scraping"
            confidence = 0.8
            summary = "data scraping keywords detected"
        if any(k in text for k in ["fill form", "submit", "automation", "apply"]):
            playbook = "automation"
            confidence = 0.8
            summary = "automation keywords detected"
        return {"playbook_type": playbook, "confidence": confidence, "reasoning_summary": summary}

    async def run(self, goal: str, config: RuntimeConfig, bus=None):
        decision = await self.classify(goal)
        playbook_type = decision["playbook_type"]
        if bus:
            bus.emit("log", {"tag": "PLAN", "message": f"playbook={playbook_type} confidence={decision['confidence']} reason={decision['reasoning_summary']}"})
        self.runner.classify = lambda _: playbook_type
        return await self.runner.run(goal, config, bus=bus)
