from __future__ import annotations

from typing import Dict, Any

from agent.actions import Action
from browser import selectors
from skills import google, extract as extract_skill, tables, download, research

async def execute_action(action: Action, page, task_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
    if action.type == "navigate":
        await page.goto(action.url or "", wait_until="networkidle")
        return {}
    if action.type == "google_search":
        await google.google_search(page, action.query or "")
        return {}
    if action.type == "open_result":
        idx = int(action.input_text or 0) if action.input_text else 0
        await google.open_result(page, idx)
        return {}
    if action.type == "click":
        if action.selector:
            await page.locator(action.selector).first.click()
            return {}
        if action.text_hint:
            await page.get_by_text(action.text_hint, exact=False).first.click()
            return {}
        raise ValueError("click requires selector or text_hint")
    if action.type == "type":
        if action.selector:
            await page.locator(action.selector).first.fill(action.input_text or "")
            return {}
        if action.text_hint:
            await page.get_by_text(action.text_hint, exact=False).first.fill(action.input_text or "")
            return {}
        raise ValueError("type requires selector or text_hint")
    if action.type == "scroll":
        await page.mouse.wheel(0, action.scroll_delta or 800)
        return {}
    if action.type == "wait":
        await page.wait_for_timeout(action.wait_ms or 1000)
        return {}
    if action.type == "back":
        await page.go_back()
        return {}
    if action.type == "extract":
        data = await extract_skill.extract_simple(action.input_text or "page_title", page)
        return {"extract": data}
    if action.type == "extract_table":
        paths = await tables.extract_tables(task_id, page)
        return {"tables": paths}
    if action.type == "download":
        items = await download.download_detected(task_id, page)
        return {"downloads": items}
    if action.type == "summarize":
        pages = context.get("pages", [])
        data = await research.summarize(task_id, context.get("goal", ""), pages)
        return {"summary": data}
    if action.type == "takeover":
        return {"takeover": True}
    if action.type == "done":
        return {"done": True}

    raise ValueError(f"Unsupported action type: {action.type}")

async def autopilot_handlers(page) -> None:
    await selectors.dismiss_common(page)
    await selectors.deny_prompts(page)
