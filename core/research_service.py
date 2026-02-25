from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from skills.research.query_engine import generate_query_variants
from skills.research.source_scoring import score_source
from skills.research.extract import extract_structured
from skills.research.synthesis import synthesize
from browser.session import BrowserSession
from browser.perceive import get_snapshot
from browser.tools import execute_action
from agent.actions import Action

CACHE_DIR = Path("data/intelligence_cache")

async def discover_sources(goal: str, max_results: int = 10) -> List[str]:
    queries = await generate_query_variants(goal)
    urls: List[str] = []
    for q in queries:
        urls.append(f"https://www.google.com/search?q={q['query'].replace(' ', '+')}")
    return urls[:max_results]

async def generate_context(goal: str) -> Dict[str, object]:
    return {"goal": goal, "queries": await generate_query_variants(goal)}

async def rank_sites(urls: List[str]) -> List[Dict[str, object]]:
    ranked = []
    for url in urls:
        score = score_source(url)
        ranked.append({"url": url, "score": score.score, "source_type": score.source_type})
    ranked.sort(key=lambda x: -x["score"])
    return ranked

async def extract_intelligence(pages: List[Dict[str, str]]) -> Dict[str, object]:
    extractions = []
    scores = []
    for page in pages:
        extraction = await extract_structured(page.get("goal", ""), page["url"], page.get("text", ""))
        extractions.append(extraction)
        scores.append(score_source(page["url"]))
    return synthesize(extractions, scores)
