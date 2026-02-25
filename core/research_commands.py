from __future__ import annotations

from core.research_service import discover_sources, generate_context, extract_intelligence

async def cmd_research(goal: str):
    return await generate_context(goal)

async def cmd_sources(goal: str):
    return await discover_sources(goal)

async def cmd_intelligence(goal: str):
    ctx = await generate_context(goal)
    return ctx
