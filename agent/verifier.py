from __future__ import annotations

from agent.actions import VerifyRule

async def verify(page, rule: VerifyRule) -> bool:
    if rule.url_contains and rule.url_contains not in page.url:
        return False
    if rule.selector_exists:
        if await page.locator(rule.selector_exists).count() == 0:
            return False
    if rule.text_contains:
        content = await page.content()
        if rule.text_contains not in content:
            return False
    return True
