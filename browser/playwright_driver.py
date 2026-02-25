from __future__ import annotations

from pathlib import Path
from typing import Optional
import hashlib

from playwright.async_api import async_playwright

from agent.actions import ClickableText, Snapshot
from storage.files import screenshot_path

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

    async def get_snapshot(self, task_id: str, step_id: int, index: int = 0) -> Snapshot:
        if not self.page:
            raise RuntimeError("Playwright page not initialized")

        url = self.page.url
        title = await self.page.title()

        try:
            visible_text = await self.page.evaluate("() => document.body ? document.body.innerText : ''")
        except Exception:
            visible_text = ""
        visible_text = " ".join(visible_text.split())
        visible_text = visible_text[:2000]

        try:
            clickable = await self.page.evaluate(
                "() => Array.from(document.querySelectorAll('a,button,[role=\"button\"]')).slice(0,25).map(el => ({text:(el.innerText||'').trim(), tag:el.tagName.toLowerCase()}))"
            )
        except Exception:
            clickable = []
        clickable_texts = [ClickableText(text=c.get("text",""), tag=c.get("tag","")) for c in clickable if c.get("text")]

        shot_path = screenshot_path(task_id, step_id, f\"{step_id}_{index}\")
        await self.page.screenshot(path=str(shot_path), full_page=True)

        dom_content = await self.page.content()
        dom_hash = hashlib.sha256(dom_content.encode(\"utf-8\")).hexdigest()
        screenshot_hash = hashlib.sha256(Path(shot_path).read_bytes()).hexdigest()

        return Snapshot(
            url=url,
            title=title,
            visible_text_summary=visible_text,
            clickable_texts=clickable_texts,
            screenshot_path=str(shot_path),
            dom_hash=dom_hash,
            screenshot_hash=screenshot_hash,
        )
