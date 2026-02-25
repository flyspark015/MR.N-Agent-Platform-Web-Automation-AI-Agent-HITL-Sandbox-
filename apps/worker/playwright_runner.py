from __future__ import annotations

import os
from pathlib import Path

from playwright.async_api import async_playwright

DATA_DIR = Path("/data")
SCREENSHOT_DIR = DATA_DIR / "screenshots"

async def run_navigate(url: str, task_id: str, step_id: str) -> dict:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    screenshot_name = f"{task_id}_{step_id}.png"
    screenshot_path = SCREENSHOT_DIR / screenshot_name

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        await page.screenshot(path=str(screenshot_path), full_page=True)
        title = await page.title()
        final_url = page.url
        await browser.close()

    return {
        "screenshot_path": str(screenshot_path),
        "screenshot_url": f"/screenshots/{screenshot_name}",
        "title": title,
        "final_url": final_url,
    }
