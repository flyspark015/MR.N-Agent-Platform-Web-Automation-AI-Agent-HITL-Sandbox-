from __future__ import annotations

import json
import re
from typing import List

import pandas as pd

from core.research_service import discover_sources, rank_sites
from agent.actions import Action
from browser.perceive import get_snapshot
from browser.tools import execute_action
from storage.artifacts import save_table_csv
from storage.fs import run_dir

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PRICE_RE = re.compile(r"\$\s?\d+(?:\.\d{2})?")

class SupplierPlaybook:
    def __init__(self, top_n: int = 5) -> None:
        self.top_n = top_n
        self.rows: List[dict] = []

    def plan(self, goal: str) -> None:
        return None

    async def execute(self, runtime, state) -> None:
        sources = await discover_sources(state.goal)
        ranked = await rank_sites(sources)

        for item in ranked[: self.top_n]:
            await execute_action(Action(type="navigate", url=item["url"], reason="supplier source"), runtime.session.page, runtime.config.task_id, {"goal": state.goal})
            snap = await get_snapshot(runtime.session.page, runtime.config.task_id, 1, 0)
            state.sources_visited.append(snap.url)

            emails = EMAIL_RE.findall(snap.visible_text_summary)
            prices = PRICE_RE.findall(snap.visible_text_summary)
            self.rows.append(
                {
                    "company": snap.title,
                    "product": state.goal,
                    "price": prices[0] if prices else "",
                    "contact": emails[0] if emails else "",
                    "url": snap.url,
                }
            )

        df = pd.DataFrame(self.rows)
        csv_path = save_table_csv(runtime.config.task_id, "suppliers", df)
        summary_path = run_dir(runtime.config.task_id) / "supplier_intelligence.json"
        summary_path.write_text(json.dumps(self.rows, indent=2), encoding="utf-8")
        state.artifacts_collected.extend([str(csv_path), str(summary_path)])

    async def evaluate(self, critic) -> dict:
        return critic

    def finalize(self, state) -> None:
        return None
