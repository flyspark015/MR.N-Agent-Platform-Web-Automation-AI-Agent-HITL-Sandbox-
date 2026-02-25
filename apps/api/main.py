from __future__ import annotations

import json
import os
from typing import List, Literal, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel, ConfigDict, Field

load_dotenv()

app = FastAPI(title="MR.N Local Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"],
)

class StepParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: Optional[str] = None
    selector: Optional[str] = None
    text: Optional[str] = None
    value: Optional[str] = None
    wait_ms: Optional[int] = Field(default=None, ge=0)
    extract: Optional[str] = None


class Step(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int = Field(ge=1)
    type: Literal["NAVIGATE", "CLICK", "TYPE", "EXTRACT", "WAIT", "SCREENSHOT"]
    description: str
    params: StepParams = Field(default_factory=StepParams)


class Plan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    goal: str
    steps: List[Step]


class TaskRequest(BaseModel):
    task: str = Field(min_length=3)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/plan", response_model=Plan)
async def plan(request: TaskRequest):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not set")

    client = OpenAI(api_key=api_key)
    schema = Plan.model_json_schema()

    system_prompt = (
        "You are a web automation planner. Convert the user goal into a short, "
        "actionable sequence of steps for a browser agent. Use the provided JSON "
        "schema. Keep params minimal. If a field is not needed, omit it or leave it null. "
        "Always return valid JSON only, no extra text."
    )

    try:
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.task},
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "plan",
                    "schema": schema,
                    "strict": True,
                }
            },
        )
        raw = response.output_text
        data = json.loads(raw)
        if not data.get("goal"):
            data["goal"] = request.task
        return Plan.model_validate(data)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Planner failed: {exc}")
