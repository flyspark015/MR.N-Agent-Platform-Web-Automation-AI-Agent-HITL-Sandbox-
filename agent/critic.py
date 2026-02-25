from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

CRITIC_SCHEMA = {
    "type": "object",
    "properties": {
        "goal_met": {"type": "boolean"},
        "missing_info": {"type": "array", "items": {"type": "string"}},
        "next_step": {"type": "string"},
    },
    "required": ["goal_met", "missing_info", "next_step"],
    "additionalProperties": False,
}

async def evaluate(goal: str, snapshot, actions) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"goal_met": False, "missing_info": ["OPENAI_API_KEY missing"], "next_step": "Set API key"}

    client = OpenAI(api_key=api_key)

    payload = {
        "goal": goal,
        "url": snapshot.url,
        "title": snapshot.title,
        "visible_text": snapshot.visible_text_summary,
        "actions": [a.type for a in actions[-5:]],
    }

    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        input=[
            {"role": "system", "content": "Evaluate if goal is achieved. Return JSON only."},
            {"role": "user", "content": json.dumps(payload)},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "critic",
                "schema": CRITIC_SCHEMA,
                "strict": True,
            }
        },
    )

    return json.loads(response.output_text)
