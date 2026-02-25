from __future__ import annotations

import json
from typing import List

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
        page = runtime.session.page
        if "http" in state.goal:
            await execute_action(Action(type="navigate", url=state.goal, reason="navigate"), page, runtime.config.task_id, {"goal": state.goal})
        else:
            await execute_action(Action(type="google_search", query=state.goal, reason="search"), page, runtime.config.task_id, {"goal": state.goal})
            await execute_action(Action(type="open_result", input_text="0", reason="open top result"), page, runtime.config.task_id, {"goal": state.goal})

        snap = await get_snapshot(page, runtime.config.task_id, 1, 0)
        runtime.emit(
            "SNAPSHOT",
            f"{snap.url} | {snap.title} | screenshot={snap.screenshot_path}",
            {"url": snap.url, "title": snap.title, "screenshot_path": snap.screenshot_path},
        )
        state.sources_visited.append(snap.url)

        result = await execute_action(Action(type="extract_table", reason="extract tables"), page, runtime.config.task_id, {"goal": state.goal})
        self.tables = result.get("tables", [])

        result = await execute_action(Action(type="download", reason="download assets"), page, runtime.config.task_id, {"goal": state.goal})
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
