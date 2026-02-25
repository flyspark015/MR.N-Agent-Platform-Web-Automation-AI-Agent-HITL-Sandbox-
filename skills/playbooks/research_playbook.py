from __future__ import annotations

import json
from typing import List

from agent.actions import Action
from browser.perceive import get_snapshot
from browser.tools import execute_action
from skills.research import summarize
from storage.fs import run_dir

class ResearchPlaybook:
    def __init__(self, top_n: int = 5) -> None:
        self.top_n = top_n
        self.sources: List[dict] = []

    def plan(self, goal: str) -> None:
        return None

    async def execute(self, runtime, state) -> None:
        page = runtime.session.page
        await execute_action(
            Action(type="google_search", query=state.goal, reason="research search"),
            page,
            runtime.config.task_id,
            {"goal": state.goal},
        )

        for i in range(self.top_n):
            await execute_action(
                Action(type="open_result", input_text=str(i), reason="open result"),
                page,
                runtime.config.task_id,
                {"goal": state.goal},
            )
            snap = await get_snapshot(page, runtime.config.task_id, i + 1, 0)
            runtime.emit(
                "SNAPSHOT",
                f"{snap.url} | {snap.title} | screenshot={snap.screenshot_path}",
                {"url": snap.url, "title": snap.title, "screenshot_path": snap.screenshot_path},
            )
            self.sources.append({"url": snap.url, "title": snap.title, "text": snap.visible_text_summary})
            state.sources_visited.append(snap.url)

        summary = await summarize(runtime.config.task_id, state.goal, self.sources)
        report_path = run_dir(runtime.config.task_id) / "report.md"
        report_path.write_text(
            "# Research Report\n\n" + "\n".join(summary.get("key_points", [])),
            encoding="utf-8",
        )
        sources_path = run_dir(runtime.config.task_id) / "sources.json"
        sources_path.write_text(json.dumps(self.sources, indent=2), encoding="utf-8")
        state.artifacts_collected.extend([str(report_path), str(sources_path)])

    async def evaluate(self, critic) -> dict:
        return critic

    def finalize(self, state) -> None:
        return None
