from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from agent.models import Plan

load_dotenv()

SYSTEM_PROMPT = (
    "You are a web automation planner. Convert the user goal into a short, "
    "actionable sequence of steps for a browser agent. Use the provided JSON "
    "schema. Keep params minimal. If a field is not needed, omit it or leave it null. "
    "Always return valid JSON only, no extra text."
)

async def plan_goal(goal: str) -> Plan:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    client = OpenAI(api_key=api_key)
    schema = Plan.model_json_schema()

    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": goal},
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
    data = json.loads(response.output_text)
    if not data.get("goal"):
        data["goal"] = goal
    return Plan.model_validate(data)
