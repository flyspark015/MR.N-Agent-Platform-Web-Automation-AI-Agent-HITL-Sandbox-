from __future__ import annotations

async def google_search(page, query: str) -> None:
    await page.goto("https://www.google.com", wait_until="networkidle")
    box = page.locator("input[name='q']").first
    await box.click()
    await box.fill(query)
    await box.press("Enter")
    await page.wait_for_load_state("networkidle")

async def open_result(page, index: int = 0) -> None:
    results = page.locator("a h3")
    if await results.count() == 0:
        raise ValueError("No search results found")
    target = results.nth(index)
    await target.click()
    await page.wait_for_load_state("networkidle")
