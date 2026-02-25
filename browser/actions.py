from __future__ import annotations

import asyncio
from typing import Optional

async def navigate(page, url: str) -> None:
    await page.goto(url, wait_until="networkidle")

async def search(page, query: str) -> None:
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    await page.goto(url, wait_until="networkidle")

async def click(page, selector: Optional[str], text_hint: Optional[str]) -> None:
    if selector:
        await page.locator(selector).first.click()
        return
    if text_hint:
        await page.get_by_text(text_hint, exact=False).first.click()
        return
    raise ValueError("CLICK requires selector or text_hint")

async def type_text(page, selector: Optional[str], text_hint: Optional[str], text: str) -> None:
    if selector:
        await page.locator(selector).first.fill(text)
        return
    if text_hint:
        await page.get_by_text(text_hint, exact=False).first.fill(text)
        return
    raise ValueError("TYPE requires selector or text_hint")

async def wait_ms(ms: int) -> None:
    await asyncio.sleep(ms / 1000)

async def screenshot(page, path: str) -> None:
    await page.screenshot(path=path, full_page=True)
