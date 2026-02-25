from __future__ import annotations

import hashlib
from pathlib import Path
from typing import List

from agent.actions import ClickableText, Snapshot
from browser.selectors import rank_clickables
from storage.fs import screenshots_dir

async def get_snapshot(page, task_id: str, step_id: int, index: int = 0) -> Snapshot:
    url = page.url
    title = await page.title()

    try:
        visible_text = await page.evaluate("() => document.body ? document.body.innerText : ''")
    except Exception:
        visible_text = ""

    visible_text = " ".join(visible_text.split())[:2000]

    clickables = await rank_clickables(page, visible_text)
    clickable_texts: List[ClickableText] = [ClickableText(text=c[0], tag=c[1]) for c in clickables]

    shot_path = screenshots_dir(task_id) / f"{task_id}_{step_id}_{index}.png"
    await page.screenshot(path=str(shot_path), full_page=True)

    dom_content = await page.content()
    dom_hash = hashlib.sha256(dom_content.encode("utf-8")).hexdigest()
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
