from __future__ import annotations

from core.research_service import generate_context
from agent.actions import Action
from browser.perceive import get_snapshot
from browser.tools import execute_action
from storage.fs import run_dir

class AutomationPlaybook:
    def plan(self, goal: str) -> None:
        return None

    async def execute(self, runtime, state) -> None:
        context = await generate_context(state.goal)
        context_path = run_dir(runtime.config.task_id) / "pre_automation_context.json"
        context_path.write_text(str(context), encoding="utf-8")
        state.artifacts_collected.append(str(context_path))

        page = runtime.session.page
        if "http" in state.goal:
            await execute_action(Action(type="navigate", url=state.goal, reason="navigate"), page, runtime.config.task_id, {"goal": state.goal})
        else:
            await execute_action(Action(type="google_search", query=state.goal, reason="search"), page, runtime.config.task_id, {"goal": state.goal})
            await execute_action(Action(type="open_result", input_text="0", reason="open top result"), page, runtime.config.task_id, {"goal": state.goal})

        snap = await get_snapshot(page, runtime.config.task_id, 1, 0)
        state.sources_visited.append(snap.url)

        proof_path = run_dir(runtime.config.task_id) / "automation_proof.txt"
        proof_path.write_text("Automation requires manual confirmation for submit actions.", encoding="utf-8")
        state.artifacts_collected.append(str(proof_path))

    async def evaluate(self, critic) -> dict:
        return critic

    def finalize(self, state) -> None:
        return None
