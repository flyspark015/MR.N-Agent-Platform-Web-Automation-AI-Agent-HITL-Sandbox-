from __future__ import annotations

from typing import List, Tuple

COMMON_BUTTONS = ["Accept", "Agree", "I agree", "OK", "Close", "X"]
DENY_BUTTONS = ["Deny", "Block", "Not now"]

async def dismiss_common(page) -> bool:
    for text in COMMON_BUTTONS:
        try:
            btn = page.get_by_text(text, exact=False).first
            if await btn.is_visible():
                await btn.click()
                return True
        except Exception:
            continue
    return False

async def deny_prompts(page) -> bool:
    for text in DENY_BUTTONS:
        try:
            btn = page.get_by_text(text, exact=False).first
            if await btn.is_visible():
                await btn.click()
                return True
        except Exception:
            continue
    return False

async def rank_clickables(page, visible_text: str) -> List[Tuple[str, str]]:
    try:
        items = await page.evaluate(
            "() => Array.from(document.querySelectorAll('a,button,input,[role=\"button\"]')).slice(0,50).map(el => ({text:(el.innerText||el.value||'').trim(), tag:el.tagName.toLowerCase()}))"
        )
    except Exception:
        items = []

    words = set(visible_text.lower().split())
    scored = []
    for item in items:
        text = (item.get("text") or "").strip()
        if not text:
            continue
        score = 0
        for w in text.lower().split():
            if w in words:
                score += 1
        scored.append((score, text, item.get("tag") or ""))

    scored.sort(key=lambda x: (-x[0], len(x[1])))
    return [(t, tag) for _, t, tag in scored[:25]]
