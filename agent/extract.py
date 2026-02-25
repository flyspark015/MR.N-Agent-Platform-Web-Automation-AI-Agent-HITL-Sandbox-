from __future__ import annotations

from typing import Dict

async def extract(schema_name: str, page) -> Dict[str, str]:
    if schema_name == "page_title":
        title = await page.title()
        return {"title": title}
    if schema_name == "page_url":
        return {"url": page.url}
    if schema_name == "google_top3":
        items = []
        locator = page.locator("a h3")
        count = await locator.count()
        for i in range(min(3, count)):
            h3 = locator.nth(i)
            title = (await h3.inner_text()).strip()
            link = await h3.evaluate("el => el.closest('a').href")
            items.append({"title": title, "url": link})
        return {"results": items}
    return {"note": f"Unknown schema: {schema_name}"}
