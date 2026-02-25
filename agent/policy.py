from __future__ import annotations

import re

LOGIN_HINTS = re.compile(r"login|sign in|signin|otp|verification|captcha", re.I)

async def needs_takeover(page, error: str | None = None) -> bool:
    if error and LOGIN_HINTS.search(error):
        return True
    try:
        title = await page.title()
    except Exception:
        title = ""
    url = getattr(page, "url", "") or ""
    if LOGIN_HINTS.search(title) or LOGIN_HINTS.search(url):
        return True
    return False
