from __future__ import annotations

from typing import List
from urllib.parse import parse_qs, urlparse

import httpx
from lxml import html

GOOGLE_URL = "https://www.google.com/search"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"


def _clean_url(raw: str) -> str | None:
    if raw.startswith("/url?"):
        parsed = parse_qs(urlparse(raw).query)
        target = parsed.get("q", [""])[0]
        raw = target
    if raw.startswith("http"):
        if "google.com" in urlparse(raw).netloc:
            return None
        return raw.split("#")[0]
    return None


def extract_google_results(html_text: str, max_results: int = 10) -> List[str]:
    tree = html.fromstring(html_text)
    links = []
    for a in tree.xpath("//a[@href]"):
        href = a.get("href")
        cleaned = _clean_url(href)
        if cleaned and cleaned not in links:
            links.append(cleaned)
        if len(links) >= max_results:
            break
    return links


async def search_google(query: str, max_results: int = 10) -> List[str]:
    params = {"q": query, "hl": "en"}
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(timeout=20, headers=headers) as client:
        resp = await client.get(GOOGLE_URL, params=params)
        resp.raise_for_status()
        return extract_google_results(resp.text, max_results=max_results)
