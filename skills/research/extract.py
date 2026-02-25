from __future__ import annotations

import json
import os
from typing import Dict

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    def load_dotenv():
        return None

load_dotenv()

STRUCTURED_SCHEMA = {
    "type": "object",
    "properties": {
        "claims": {"type": "array", "items": {"type": "string"}},
        "statistics": {"type": "array", "items": {"type": "string"}},
        "dates": {"type": "array", "items": {"type": "string"}},
        "contradictions": {"type": "array", "items": {"type": "string"}},
        "definitions": {"type": "array", "items": {"type": "string"}},
        "source_url": {"type": "string"},
    },
    "required": ["claims", "statistics", "dates", "contradictions", "definitions", "source_url"],
    "additionalProperties": False,
}

async def extract_structured(goal: str, source_url: str, text: str) -> Dict[str, object]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    from openai import OpenAI

    client = OpenAI(api_key=api_key)

    payload = {
        "goal": goal,
        "source_url": source_url,
        "text": text,
    }

    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        input=[
            {"role": "system", "content": "Extract structured facts. Return JSON only."},
            {"role": "user", "content": json.dumps(payload)},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "structured_extraction",
                "schema": STRUCTURED_SCHEMA,
                "strict": True,
            }
        },
    )

    data = json.loads(response.output_text)
    return data
