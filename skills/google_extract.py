from __future__ import annotations

from dataclasses import dataclass
from typing import List
from urllib.parse import parse_qs, urlparse

import httpx
from lxml import html

GOOGLE_URL = "https://www.google.com/search"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"

@dataclass
class GoogleResult:
    url: str
    domain: str
    title: str
    snippet: str
    rank: int
    is_ad: bool = False


def _clean_url(raw: str) -> str | None:
    if raw.startswith("/url?"):
        parsed = parse_qs(urlparse(raw).query)
        target = parsed.get("q", [""])[0]
        raw = target
    if raw.startswith("http"):
        netloc = urlparse(raw).netloc.lower()
        if "google.com" in netloc or "support.google.com" in netloc or "maps.google.com" in netloc:
            return None
        return raw.split("#")[0]
    return None


def _detect_consent(tree) -> bool:
    text = " ".join(tree.xpath("//body//text()")[:200]).lower()
    return "before you continue" in text or "consent" in text


def _extract_strategy_standard(tree) -> List[GoogleResult]:
    results: List[GoogleResult] = []
    blocks = tree.xpath("//div[@data-snc]")
    rank = 1
    for block in blocks:
        link = block.xpath(".//a[@href]")
        title = block.xpath(".//h3//text()")
        snippet = block.xpath(".//div[@data-sncf]//text()")
        if not link or not title:
            continue
        href = link[0].get("href")
        url = _clean_url(href or "")
        if not url:
            continue
        results.append(
            GoogleResult(
                url=url,
                domain=urlparse(url).netloc,
                title=" ".join(title).strip(),
                snippet=" ".join(snippet).strip(),
                rank=rank,
                is_ad=False,
            )
        )
        rank += 1
    return results


def _extract_strategy_alt(tree) -> List[GoogleResult]:
    results: List[GoogleResult] = []
    rank = 1
    for block in tree.xpath("//div[@class='g']"):
        link = block.xpath(".//a[@href]")
        title = block.xpath(".//h3//text()")
        snippet = block.xpath(".//span[@class='aCOpRe']//text()")
        if not link or not title:
            continue
        href = link[0].get("href")
        url = _clean_url(href or "")
        if not url:
            continue
        results.append(
            GoogleResult(
                url=url,
                domain=urlparse(url).netloc,
                title=" ".join(title).strip(),
                snippet=" ".join(snippet).strip(),
                rank=rank,
                is_ad=False,
            )
        )
        rank += 1
    return results


def _extract_strategy_fallback(text: str) -> List[GoogleResult]:
    results: List[GoogleResult] = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("http"):
            url = _clean_url(line)
            if not url:
                continue
            results.append(
                GoogleResult(
                    url=url,
                    domain=urlparse(url).netloc,
                    title=urlparse(url).netloc,
                    snippet="",
                    rank=len(results) + 1,
                    is_ad=False,
                )
            )
        if len(results) >= 10:
            break
    return results


def extract_google_results(html_text: str, max_results: int = 10) -> List[GoogleResult]:
    tree = html.fromstring(html_text)
    if _detect_consent(tree):
        return []

    results = _extract_strategy_standard(tree)
    if not results:
        results = _extract_strategy_alt(tree)
    if not results:
        results = _extract_strategy_fallback(tree.text_content())

    # Filter ads/sponsored blocks by presence of "Ad" label near the block
    filtered: List[GoogleResult] = []
    for item in results:
        if item.url in [r.url for r in filtered]:
            continue
        filtered.append(item)
        if len(filtered) >= max_results:
            break
    return filtered


async def search_google(query: str, max_results: int = 10) -> List[GoogleResult]:
    params = {"q": query, "hl": "en", "gl": "us", "num": max_results}
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(timeout=20, headers=headers) as client:
        resp = await client.get(GOOGLE_URL, params=params)
        resp.raise_for_status()
        return extract_google_results(resp.text, max_results=max_results)
