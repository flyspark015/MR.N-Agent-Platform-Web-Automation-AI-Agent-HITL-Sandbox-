from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict, List

import httpx

from storage.artifacts import save_download_metadata
from storage.fs import downloads_dir

FILE_EXTS = [".pdf", ".png", ".jpg", ".jpeg", ".csv", ".xlsx", ".zip"]

async def download_detected(task_id: str, page) -> List[Dict[str, str]]:
    links = await page.evaluate(
        "() => Array.from(document.querySelectorAll('a[href]')).map(a => a.href)"
    )
    targets = [l for l in links if any(l.lower().endswith(ext) for ext in FILE_EXTS)]
    results: List[Dict[str, str]] = []
    for url in targets:
        try:
            filename = url.split("/")[-1].split("?")[0] or "download"
            dest = downloads_dir(task_id) / filename
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                dest.write_bytes(resp.content)
            sha = hashlib.sha256(dest.read_bytes()).hexdigest()
            results.append({"url": url, "path": str(dest), "sha256": sha})
        except Exception:
            continue

    save_download_metadata(task_id, results)
    return results
