from __future__ import annotations

import asyncio

from browser import selectors
from skills import google

async def recover(page, goal: str, log) -> None:
    log("RECOVERY", "Attempting scroll/close/back/search")
    await selectors.dismiss_common(page)
    await selectors.deny_prompts(page)
    await page.mouse.wheel(0, 800)
    await asyncio.sleep(0.5)
    if "http" not in goal:
        try:
            await google.google_search(page, goal)
        except Exception:
            pass
