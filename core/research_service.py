from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Callable, Dict, List, Optional
from urllib.parse import urlparse

from core.intelligence_cache import get_cache, set_cache
from skills.research.query_engine import generate_query_variants
from skills.research.source_scoring import score_source
from skills.research.extract import extract_structured
from skills.research.synthesis import synthesize
from skills.search.providers.base import SearchResult
from skills.search.providers.google_html import GoogleHtmlProvider
from skills.search.providers.ddg_html import DuckDuckGoHtmlProvider
from skills.search.providers.ddg_lite import DuckDuckGoLiteProvider
from skills.search.providers.bing_html import BingHtmlProvider
from skills.search.providers.heuristic import HeuristicProvider

CACHE_DIR = Path("data/intelligence_cache")

async def discover_sources(
    goal: str,
    max_results: int = 10,
    min_domains: int = 4,
    task_id: str = "adhoc",
    emit: Optional[Callable[[str, str, Optional[Dict[str, object]]], None]] = None,
) -> List[str]:
    cached = get_cache(f"discover_{goal}")
    if not os.getenv("MRN_FAST_DISCOVERY") and cached and cached.get("urls"):
        cached_urls = cached.get("urls", [])
        if all("google.com" not in u and "duckduckgo.com" not in u and "bing.com" not in u for u in cached_urls):
            return cached_urls

    fast_mode = os.getenv("MRN_FAST_DISCOVERY") == "1"
    if fast_mode:
        queries = [
            {"type": "primary", "query": goal},
            {"type": "variation", "query": f"{goal} official"},
        ]
    else:
        try:
            queries = await generate_query_variants(goal)
        except Exception:
            queries = [{"type": "primary", "query": goal}]

    if os.getenv("MRN_SKIP_NETWORK") == "1":
        providers = [HeuristicProvider()]
    elif fast_mode:
        providers = [DuckDuckGoLiteProvider(), DuckDuckGoHtmlProvider(), HeuristicProvider()]
    else:
        providers = [GoogleHtmlProvider(), DuckDuckGoHtmlProvider(), DuckDuckGoLiteProvider(), BingHtmlProvider(), HeuristicProvider()]
    result_map: Dict[str, SearchResult] = {}
    max_pool = max_results * 3

    for q in queries:
        for provider in providers:
            results = await provider.search(q["query"], max_results=5)
            _emit_discovery(emit, provider.name, results)
            if _needs_debug(results):
                _write_debug(task_id, provider, q["query"], results)
            for r in results:
                domain = urlparse(r.url).netloc.lower()
                if "google.com" in domain or "duckduckgo.com" in domain or "bing.com" in domain:
                    continue
                if r.url not in result_map:
                    result_map[r.url] = r
            unique_domains = len({urlparse(u).netloc for u in result_map})
            if len(result_map) >= max_results and unique_domains >= min_domains:
                break
        unique_domains = len({urlparse(u).netloc for u in result_map})
        if len(result_map) >= max_results and unique_domains >= min_domains:
            break

    if len(result_map) < 5:
        refinements = [
            f"{goal} official",
            f"{goal} documentation",
            f"{goal} manufacturer",
            f"{goal} site:.gov",
            f"{goal} site:.edu",
        ]
        if fast_mode:
            refinements = []
        for q in refinements:
            for provider in providers:
                results = await provider.search(q, max_results=5)
                _emit_discovery(emit, provider.name, results)
                if _needs_debug(results):
                    _write_debug(task_id, provider, q, results)
                for r in results:
                    domain = urlparse(r.url).netloc.lower()
                    if "google.com" in domain or "duckduckgo.com" in domain or "bing.com" in domain:
                        continue
                    if r.url not in result_map:
                        result_map[r.url] = r
                unique_domains = len({urlparse(u).netloc for u in result_map})
                if len(result_map) >= max_results and unique_domains >= min_domains:
                    break
            unique_domains = len({urlparse(u).netloc for u in result_map})
            if len(result_map) >= max_results and unique_domains >= min_domains:
                break

    if len(result_map) > max_pool:
        # trim to keep ranking manageable
        result_map = dict(list(result_map.items())[:max_pool])

    if len({urlparse(u).netloc for u in result_map}) < min_domains:
        heuristic = HeuristicProvider()
        results = await heuristic.search(goal, max_results=10)
        _emit_discovery(emit, heuristic.name, results)
        if _needs_debug(results):
            _write_debug(task_id, heuristic, goal, results)
        for r in results:
            domain = urlparse(r.url).netloc.lower()
            if "google.com" in domain or "duckduckgo.com" in domain or "bing.com" in domain:
                continue
            if r.url not in result_map:
                result_map[r.url] = r

    ranked = await rank_sites(list(result_map.values()))
    final = [r["url"] for r in ranked][:max_results]

    if len({urlparse(u).netloc for u in final}) < min_domains:
        extra = [r["url"] for r in ranked][max_results:]
        for u in extra:
            if u not in final:
                final.append(u)
            if len({urlparse(x).netloc for x in final}) >= min_domains:
                break

    if final:
        set_cache(f"discover_{goal}", {"urls": final})
    return final


def _write_debug(task_id: str, provider: object, query: str, results: List[object]) -> None:
    debug_dir = Path("data") / f"run_{task_id}" / "research" / "debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    provider_name = getattr(provider, "name", "provider")
    last_url = getattr(provider, "last_url", "") or ""
    last_html = getattr(provider, "last_html_snippet", "") or ""
    last_error = getattr(provider, "last_error", "") or ""
    (debug_dir / f"{provider_name}_last_url.txt").write_text(last_url or query, encoding="utf-8")
    (debug_dir / f"{provider_name}_html_snippet.txt").write_text(
        last_html[:5000],
        encoding="utf-8",
    )
    (debug_dir / f"{provider_name}_error.txt").write_text(last_error, encoding="utf-8")
    (debug_dir / f"{provider_name}_status.txt").write_text(str(getattr(provider, "last_status", "")), encoding="utf-8")
    (debug_dir / f"{provider_name}_results.json").write_text(
        json.dumps([r.__dict__ for r in results], indent=2)[:20000],
        encoding="utf-8",
    )

def _emit_discovery(emit: Optional[Callable[[str, str, Optional[Dict[str, object]]], None]], provider: str, results: List[object]) -> None:
    if not emit:
        return
    unique_domains = len({getattr(r, "domain", "") for r in results})
    emit(
        "DISCOVERY",
        f"provider={provider} results={len(results)} unique_domains={unique_domains}",
        {"provider": provider, "results": len(results), "unique_domains": unique_domains},
    )

def _needs_debug(results: List[object]) -> bool:
    unique_domains = len({getattr(r, "domain", "") for r in results})
    return len(results) < 3 or unique_domains < 3

async def generate_context(goal: str) -> Dict[str, object]:
    cached = get_cache(f"context_{goal}")
    if cached:
        return cached
    ctx = {"goal": goal, "queries": await generate_query_variants(goal)}
    set_cache(f"context_{goal}", ctx)
    return ctx

async def rank_sites(items: List[object]) -> List[Dict[str, object]]:
    cache_key = f"rank_{hash(tuple((getattr(i, 'url', str(i)), getattr(i, 'snippet', '')) for i in items))}"
    cached = get_cache(cache_key)
    if cached:
        return cached.get("ranked", [])
    ranked = []
    for item in items:
        if isinstance(item, SearchResult):
            score = score_source(item.url, item.snippet)
            ranked.append({"url": item.url, "score": score.score, "source_type": score.source_type})
        else:
            url = str(item)
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
