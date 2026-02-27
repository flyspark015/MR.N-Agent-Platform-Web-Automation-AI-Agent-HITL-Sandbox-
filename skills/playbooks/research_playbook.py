from __future__ import annotations

import json
from typing import List, Set
from urllib.parse import urlparse

from agent.actions import Action
from agent.critic import evaluate_research_coverage
from browser.perceive import get_snapshot
from browser.tools import execute_action
from skills.research.extract import extract_structured
from core.research_service import discover_sources
from skills.research.source_scoring import score_source
from skills.research.synthesis import synthesize
from storage.fs import run_dir

class ResearchPlaybook:
    def __init__(self, top_n: int = 3, min_domains: int = 4, max_query_budget: int = 6) -> None:
        self.top_n = top_n
        self.min_domains = min_domains
        self.max_query_budget = max_query_budget
        self.sources: List[dict] = []
        self.domains: Set[str] = set()
        self.extractions: List[dict] = []
        self.scores: List[dict] = []

    def plan(self, goal: str) -> None:
        return None

    async def execute(self, runtime, state) -> None:
        sources = await discover_sources(
            state.goal,
            task_id=runtime.config.task_id,
            emit=runtime.emit,
        )
        for i, url in enumerate(sources[: self.top_n]):
            await execute_action(
                Action(type="navigate", url=url, reason="research source"),
                runtime.session.page,
                runtime.config.task_id,
                {"goal": state.goal},
            )
            snap = await get_snapshot(runtime.session.page, runtime.config.task_id, i + 1, 0)
            domain = urlparse(snap.url).netloc
            self.domains.add(domain)
            source = {"url": snap.url, "title": snap.title, "text": snap.visible_text_summary}
            self.sources.append(source)
            state.sources_visited.append(snap.url)
            runtime.emit(
                "SNAPSHOT",
                f"{snap.url} | {snap.title} | screenshot={snap.screenshot_path}",
                {"url": snap.url, "title": snap.title, "screenshot_path": snap.screenshot_path},
            )

            extraction = await extract_structured(state.goal, snap.url, snap.visible_text_summary)
            self.extractions.append(extraction)

            score = score_source(snap.url)
            self.scores.append(score.__dict__)

        synthesis = synthesize(self.extractions, [score_source(s["url"]) for s in self.scores])

        report_dir = run_dir(runtime.config.task_id) / "research"
        report_dir.mkdir(parents=True, exist_ok=True)

        structured_path = report_dir / "structured.json"
        structured_path.write_text(json.dumps(self.extractions, indent=2), encoding="utf-8")

        sources_path = report_dir / "sources.json"
        sources_path.write_text(json.dumps(self.sources, indent=2), encoding="utf-8")

        credibility_path = report_dir / "credibility.json"
        credibility_path.write_text(json.dumps(self.scores, indent=2), encoding="utf-8")

        coverage = evaluate_research_coverage(list(self.domains), self.extractions, [score_source(s["url"]) for s in self.scores])
        coverage_path = report_dir / "coverage.json"
        coverage_path.write_text(json.dumps(coverage, indent=2), encoding="utf-8")

        summary_path = report_dir / "summary.md"
        summary_path.write_text(
            "# Executive Summary\n" + "\n".join(synthesis["consolidated_findings"]) + "\n\n"
            "# Key Findings\n" + "\n".join(synthesis["consolidated_findings"]) + "\n\n"
            "# Statistical Data\n" + "\n".join(synthesis["numeric_facts"]) + "\n\n"
            "# Contradictions / Debates\n" + "\n".join(synthesis["conflicting_points"]) + "\n\n"
            "# Timeline (if applicable)\n" + "\n".join(synthesis["timeline"]) + "\n\n"
            "# Source Credibility Overview\n" + json.dumps(self.scores, indent=2) + "\n\n"
            f"# Confidence Score\n{synthesis['confidence_level']}\n",
            encoding="utf-8",
        )

        state.artifacts_collected.extend(
            [str(structured_path), str(sources_path), str(credibility_path), str(coverage_path), str(summary_path)]
        )

    async def evaluate(self, critic) -> dict:
        return critic

    def finalize(self, state) -> None:
        return None
