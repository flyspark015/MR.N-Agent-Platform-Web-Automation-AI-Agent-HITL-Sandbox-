from __future__ import annotations

import json
import os
from typing import Dict, List

from dotenv import load_dotenv
from openai import OpenAI

from storage.artifacts import save_research_summary

load_dotenv()

SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "key_points": {"type": "array", "items": {"type": "string"}},
        "sources": {"type": "array", "items": {"type": "string"}},
        "comparison": {"type": "string"},
        "confidence": {"type": "string"},
    },
    "required": ["key_points", "sources", "comparison", "confidence"],
    "additionalProperties": False,
}

async def summarize(task_id: str, goal: str, pages: List[Dict[str, str]]) -> Dict[str, object]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    client = OpenAI(api_key=api_key)

    user_prompt = {
        "goal": goal,
        "pages": pages,
    }

    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        input=[
            {"role": "system", "content": "Summarize research. Return JSON only."},
            {"role": "user", "content": json.dumps(user_prompt)},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "research_summary",
                "schema": SUMMARY_SCHEMA,
                "strict": True,
            }
        },
    )

    data = json.loads(response.output_text)
    save_research_summary(task_id, data)
    return data
