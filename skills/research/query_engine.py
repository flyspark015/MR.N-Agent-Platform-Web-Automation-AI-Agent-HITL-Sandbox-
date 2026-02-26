from __future__ import annotations

import json
import os
from typing import List

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    def load_dotenv():
        return None

load_dotenv()

QUERY_SCHEMA = {
    "type": "object",
    "properties": {
        "queries": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "query": {"type": "string"},
                },
                "required": ["type", "query"],
                "additionalProperties": False,
            },
            "minItems": 1,
        }
    },
    "required": ["queries"],
    "additionalProperties": False,
}

SYSTEM = (
    "Generate search queries for web research. Return JSON only. "
    "Include: 1 primary, 3 variations, 1 comparison, 1 opposing."
)

async def generate_query_variants(goal: str) -> List[dict]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        input=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": goal},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "queries",
                "schema": QUERY_SCHEMA,
                "strict": True,
            }
        },
    )

    data = json.loads(response.output_text)
    return data["queries"]
