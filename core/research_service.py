from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List
from urllib.parse import urlparse

from core.intelligence_cache import get_cache, set_cache
from skills.research.query_engine import generate_query_variants
from skills.google_extract import search_google
from skills.research.source_scoring import score_source
from skills.research.extract import extract_structured
from skills.research.synthesis import synthesize
from browser.session import BrowserSession
from browser.perceive import get_snapshot
from browser.tools import execute_action
from agent.actions import Action

CACHE_DIR = Path("data/intelligence_cache")

async def discover_sources(goal: str, max_results: int = 10, min_domains: int = 4) -> List[str]:
    cached = get_cache(f"discover_{goal}")
    if cached:
        return cached.get("urls", [])
    queries = await generate_query_variants(goal)
    urls: List[str] = []
    for q in queries:
        results = await search_google(q["query"], max_results=5)
        for r in results:
            if r.url not in urls:
                urls.append(r.url)
        if len(urls) >= max_results:
            break

    if len(urls) < 5:
        refinements = [
            f"{goal} official",
            f"{goal} documentation",
            f"{goal} manufacturer",
            f\"{goal} site:.gov\",
            f\"{goal} site:.edu\",
        ]
        for q in refinements:
            results = await search_google(q, max_results=5)
            for r in results:
                if r.url not in urls:
                    urls.append(r.url)
            if len(urls) >= max_results:
                break

    ranked = await rank_sites(urls)
    final = [r["url"] for r in ranked][:max_results]

    # enforce domain diversity
    if len({urlparse(u).netloc for u in final}) < min_domains:
        extra = [r["url"] for r in ranked][max_results:]
        for u in extra:
            if u not in final:
                final.append(u)
            if len({urlparse(x).netloc for x in final}) >= min_domains:
                break

    set_cache(f"discover_{goal}", {"urls": final})
    return final

async def generate_context(goal: str) -> Dict[str, object]:
    cached = get_cache(f"context_{goal}")
    if cached:
        return cached
    ctx = {"goal": goal, "queries": await generate_query_variants(goal)}
    set_cache(f"context_{goal}", ctx)
    return ctx

async def rank_sites(urls: List[str]) -> List[Dict[str, object]]:
    cache_key = f"rank_{hash(tuple(urls))}"
    cached = get_cache(cache_key)
    if cached:
        return cached.get("ranked", [])
    ranked = []
    for url in urls:
        score = score_source(url)
        ranked.append({"url": url, "score": score.score, "source_type": score.source_type})
    ranked.sort(key=lambda x: -x["score"])
    set_cache(cache_key, {"ranked": ranked})
    return ranked

async def extract_intelligence(pages: List[Dict[str, str]]) -> Dict[str, object]:
    extractions = []
    scores = []
    for page in pages:
        extraction = await extract_structured(page.get("goal", ""), page["url"], page.get("text", ""))
        extractions.append(extraction)
        scores.append(score_source(page["url"]))
    return synthesize(extractions, scores)
