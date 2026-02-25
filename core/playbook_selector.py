from __future__ import annotations

import asyncio

from core.playbook_runner import PlaybookRunner
from core.research_service import generate_context
from core.runtime import RuntimeConfig

class PlaybookSelector:
    def __init__(self) -> None:
        self.runner = PlaybookRunner()

    async def classify(self, goal: str) -> str:
        ctx = await generate_context(goal)
        text = (ctx.get("goal") or goal).lower()
        if any(k in text for k in ["supplier", "vendor", "wholesale", "manufacturer"]):
            return "supplier"
        if any(k in text for k in ["table", "dataset", "csv", "scrape", "extract data"]):
            return "data_scraping"
        if any(k in text for k in ["fill form", "submit", "automation", "apply"]):
            return "automation"
        return "research"

    async def run(self, goal: str, config: RuntimeConfig, bus=None):
        playbook_type = await self.classify(goal)
        self.runner.classify = lambda _: playbook_type
        return await self.runner.run(goal, config, bus=bus)
