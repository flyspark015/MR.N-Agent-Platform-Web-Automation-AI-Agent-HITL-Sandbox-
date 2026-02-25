import asyncio
import json
from datetime import datetime
from pathlib import Path

from core.research_service import discover_sources
from browser.session import BrowserSession
from browser.perceive import get_snapshot

async def main():
    report = {
        "discover_sources": {},
        "playwright": {},
    }

    urls = await discover_sources("OpenAI official site")
    report["discover_sources"] = {
        "urls": urls,
        "ok": len(urls) >= 3 and all("google.com" not in u for u in urls),
    }

    session = BrowserSession(headless=True, task_id="smoke")
    await session.start()
    await session.page.goto("https://example.com", wait_until="networkidle")
    title = await session.page.title()
    await session.stop()

    report["playwright"] = {
        "title": title,
        "ok": "Example" in title,
    }

    out_dir = Path("data/smoke")
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"smoke_{ts}.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Smoke report: {out_path}")
    print(report)

if __name__ == "__main__":
    asyncio.run(main())
