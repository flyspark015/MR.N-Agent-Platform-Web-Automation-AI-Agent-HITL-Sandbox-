from __future__ import annotations

from pathlib import Path
from typing import Optional

from storage.fs import traces_dir

class BrowserSession:
    def __init__(self, headless: bool, task_id: str, trace: bool = False) -> None:
        self.headless = headless
        self.task_id = task_id
        self.trace = trace
        self._playwright = None
        self._browser = None
        self._context = None
        self.page = None

    async def start(self) -> None:
        from playwright.async_api import async_playwright
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self.headless)
        self._context = await self._browser.new_context()
        if self.trace:
            trace_path = traces_dir(self.task_id) / "trace.zip"
            await self._context.tracing.start(screenshots=True, snapshots=True, sources=True)
            self._trace_path = trace_path
        self.page = await self._context.new_page()

    async def restart(self) -> None:
        await self.stop()
        await self.start()

    async def stop(self) -> None:
        if self.trace and self._context and hasattr(self, "_trace_path"):
            await self._context.tracing.stop(path=str(self._trace_path))
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def clear_cookies(self) -> None:
        if self._context:
            await self._context.clear_cookies()
