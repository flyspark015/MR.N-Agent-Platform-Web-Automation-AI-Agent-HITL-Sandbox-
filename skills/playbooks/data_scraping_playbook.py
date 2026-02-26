from __future__ import annotations

import json
from typing import List

from core.research_service import discover_sources, rank_sites
from agent.actions import Action
from browser.perceive import get_snapshot
from browser.tools import execute_action
from storage.fs import run_dir

class DataScrapingPlaybook:
    def __init__(self) -> None:
        self.tables: List[str] = []
        self.downloads: List[dict] = []

    def plan(self, goal: str) -> None:
        return None

    async def execute(self, runtime, state) -> None:
        sources = await discover_sources(
            state.goal,
            task_id=runtime.config.task_id,
            emit=runtime.emit,
        )
        ranked = await rank_sites(sources)

        if ranked:
            await execute_action(Action(type="navigate", url=ranked[0]["url"], reason="authoritative source"), runtime.session.page, runtime.config.task_id, {"goal": state.goal})
        else:
            await execute_action(Action(type="google_search", query=state.goal, reason="search"), runtime.session.page, runtime.config.task_id, {"goal": state.goal})
            await execute_action(Action(type="open_result", input_text="0", reason="open top result"), runtime.session.page, runtime.config.task_id, {"goal": state.goal})

        snap = await get_snapshot(runtime.session.page, runtime.config.task_id, 1, 0)
        state.sources_visited.append(snap.url)

        result = await execute_action(Action(type="extract_table", reason="extract tables"), runtime.session.page, runtime.config.task_id, {"goal": state.goal})
        self.tables = result.get("tables", [])

        result = await execute_action(Action(type="download", reason="download assets"), runtime.session.page, runtime.config.task_id, {"goal": state.goal})
        self.downloads = result.get("downloads", [])

        dataset = {
            "tables": self.tables,
            "downloads": self.downloads,
        }
        out = run_dir(runtime.config.task_id) / "dataset.json"
        out.write_text(json.dumps(dataset, indent=2), encoding="utf-8")
        state.artifacts_collected.extend([str(out)] + self.tables)

    async def evaluate(self, critic) -> dict:
        return critic

    def finalize(self, state) -> None:
        return None
