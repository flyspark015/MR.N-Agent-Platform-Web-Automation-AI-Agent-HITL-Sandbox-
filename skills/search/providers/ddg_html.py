from __future__ import annotations

from typing import List
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from skills.search.providers.base import SearchProvider, SearchResult

class DuckDuckGoHtmlProvider(SearchProvider):
    name = "ddg_html"

    async def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        self.last_error = None
        url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"
        self.last_url = url
        headers = {"User-Agent": "Mozilla/5.0"}
        async with httpx.AsyncClient(timeout=20, headers=headers) as client:
            try:
                resp = await client.get(url)
                resp.raise_for_status()
                html = resp.text
                self.last_html_snippet = html[:5000]
            except Exception as exc:
                self.last_error = str(exc)
                self.last_html_snippet = ""
                return []

        soup = BeautifulSoup(html, "html.parser")
        results: List[SearchResult] = []
        rank = 1
        for res in soup.select("div.result"):
            link = res.select_one("a.result__a")
            snippet = res.select_one("a.result__snippet") or res.select_one("div.result__snippet")
            if not link:
                continue
            href = link.get("href")
            if not href or "duckduckgo.com" in href:
                continue
            title = link.get_text(strip=True)
            snip = snippet.get_text(" ", strip=True) if snippet else ""
            results.append(
                SearchResult(
                    url=href,
                    domain=urlparse(href).netloc,
                    title=title,
                    snippet=snip,
                    rank=rank,
                    provider=self.name,
                    is_ad=False,
                )
            )
            rank += 1
            if len(results) >= max_results:
                break
        return results
