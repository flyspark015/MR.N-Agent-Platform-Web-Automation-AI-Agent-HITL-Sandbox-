from __future__ import annotations

from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright

class PlaywrightDriver:
    def __init__(self, headless: bool, trace: bool, trace_path: Optional[Path]):
        self.headless = headless
        self.trace = trace
        self.trace_path = trace_path
        self._playwright = None
        self._browser = None
        self._context = None
        self.page = None

    async def start(self) -> None:
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self.headless)
        self._context = await self._browser.new_context()
        if self.trace and self._context and self.trace_path:
            await self._context.tracing.start(screenshots=True, snapshots=True, sources=True)
        self.page = await self._context.new_page()

    async def stop(self) -> None:
        if self.trace and self._context and self.trace_path:
            await self._context.tracing.stop(path=str(self.trace_path))
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
