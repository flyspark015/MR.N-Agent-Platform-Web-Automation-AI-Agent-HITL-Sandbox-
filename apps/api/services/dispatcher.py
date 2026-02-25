from __future__ import annotations

import os
import httpx

WORKER_URL = os.getenv("WORKER_URL", "http://worker:8001")

async def dispatch_navigate(url: str, task_id: str, step_id: str) -> dict:
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{WORKER_URL}/navigate",
            json={"url": url, "task_id": task_id, "step_id": step_id},
        )
        resp.raise_for_status()
        return resp.json()
