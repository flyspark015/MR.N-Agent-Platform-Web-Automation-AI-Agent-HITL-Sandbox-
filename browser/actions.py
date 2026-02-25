from __future__ import annotations

import asyncio
from typing import Optional

async def navigate(page, url: str) -> None:
    await page.goto(url, wait_until="networkidle")

async def search(page, query: str) -> None:
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    await page.goto(url, wait_until="networkidle")

async def action_google_search(page, query: str) -> None:
    await page.goto("https://www.google.com", wait_until="networkidle")
    await dismiss_cookie_banner(page)
    box = page.locator("input[name='q']").first
    await box.click()
    await box.fill(query)
    await box.press("Enter")
    await page.wait_for_load_state("networkidle")

async def open_top_result(page, index: int = 0) -> None:
    results = page.locator("a h3").all()
    if not results:
        raise ValueError("No search results found")
    target = results[index]
    await target.click()
    await page.wait_for_load_state("networkidle")

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

async def dismiss_cookie_banner(page) -> None:
    for text in ["Accept", "I agree", "Agree", "OK", "Accept all"]:
        try:
            btn = page.get_by_text(text, exact=False).first
            if await btn.is_visible():
                await btn.click()
                return
        except Exception:
            continue

async def close_modal(page) -> None:
    for text in ["Close", "X", "Dismiss"]:
        try:
            btn = page.get_by_text(text, exact=False).first
            if await btn.is_visible():
                await btn.click()
                return
        except Exception:
            continue

async def deny_prompts(page) -> None:
    for text in ["Deny", "Block", "Not now"]:
        try:
            btn = page.get_by_text(text, exact=False).first
            if await btn.is_visible():
                await btn.click()
                return
        except Exception:
            continue
