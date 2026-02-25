from __future__ import annotations

from typing import List, Set
from urllib.parse import urlparse

from agent.actions import Action
from browser.perceive import get_snapshot
from browser.tools import execute_action
from skills.research.query_engine import generate_query_variants

class ResearchPlaybook:
    def __init__(self, top_n: int = 3, min_domains: int = 4, max_query_budget: int = 6) -> None:
        self.top_n = top_n
        self.min_domains = min_domains
        self.max_query_budget = max_query_budget
        self.sources: List[dict] = []
        self.domains: Set[str] = set()

    def plan(self, goal: str) -> None:
        return None

    async def execute(self, runtime, state) -> None:
        queries = await generate_query_variants(state.goal)
        used = 0

        for item in queries:
            if used >= self.max_query_budget:
                break
            used += 1

            await execute_action(
                Action(type="google_search", query=item["query"], reason="research search"),
                runtime.session.page,
                runtime.config.task_id,
                {"goal": state.goal},
            )

            for i in range(self.top_n):
                await execute_action(
                    Action(type="open_result", input_text=str(i), reason="open result"),
                    runtime.session.page,
                    runtime.config.task_id,
                    {"goal": state.goal},
                )
                snap = await get_snapshot(runtime.session.page, runtime.config.task_id, i + 1, used)
                domain = urlparse(snap.url).netloc
                self.domains.add(domain)
                self.sources.append({"url": snap.url, "title": snap.title, "text": snap.visible_text_summary})
                state.sources_visited.append(snap.url)
                runtime.emit(
                    "SNAPSHOT",
                    f"{snap.url} | {snap.title} | screenshot={snap.screenshot_path}",
                    {"url": snap.url, "title": snap.title, "screenshot_path": snap.screenshot_path},
                )

            if len(self.domains) >= self.min_domains:
                break

    async def evaluate(self, critic) -> dict:
        return critic

    def finalize(self, state) -> None:
        return None
