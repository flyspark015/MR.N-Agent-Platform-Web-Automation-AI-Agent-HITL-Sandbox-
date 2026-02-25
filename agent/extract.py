from __future__ import annotations

from typing import Dict

async def extract(schema_name: str, page) -> Dict[str, str]:
    if schema_name == "page_title":
        title = await page.title()
        return {"title": title}
    if schema_name == "page_url":
        return {"url": page.url}
    return {"note": f"Unknown schema: {schema_name}"}
