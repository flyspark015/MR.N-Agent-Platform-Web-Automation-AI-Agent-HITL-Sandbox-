from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from playwright_runner import run_navigate

app = FastAPI(title="MR.N Local Agent Worker")

class NavigateRequest(BaseModel):
    url: str = Field(min_length=3)
    task_id: str
    step_id: str

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/navigate")
async def navigate(request: NavigateRequest):
    try:
        return await run_navigate(request.url, request.task_id, request.step_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
