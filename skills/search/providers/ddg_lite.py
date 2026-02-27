from __future__ import annotations

from typing import List
from urllib.parse import parse_qs, urlparse, unquote

import httpx
from bs4 import BeautifulSoup

from skills.search.providers.base import SearchProvider, SearchResult

class DuckDuckGoLiteProvider(SearchProvider):
    name = "ddg_lite"

    def _clean_url(self, raw: str) -> str | None:
        if not raw:
            return None
        if "duckduckgo.com/l/?" in raw:
            parsed = parse_qs(urlparse(raw).query)
            target = parsed.get("uddg", [""])[0]
            raw = unquote(target)
        if raw.startswith("http"):
            netloc = urlparse(raw).netloc.lower()
            if "duckduckgo.com" in netloc:
                return None
            return raw.split("#")[0]
        return None

    async def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        self.last_error = None
        url = f"https://lite.duckduckgo.com/lite/?q={query.replace(' ', '+')}"
        self.last_url = url
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://duckduckgo.com/",
        }
        async with httpx.AsyncClient(timeout=10, headers=headers, follow_redirects=True) as client:
            try:
                resp = await client.get(url)
                self.last_status = resp.status_code
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
        for link in soup.select("a.result-link"):
            href = link.get("href")
            cleaned = self._clean_url(href)
            if not cleaned:
                continue
            title = link.get_text(" ", strip=True)
            results.append(
                SearchResult(
                    url=cleaned,
                    domain=urlparse(cleaned).netloc,
                    title=title,
                    snippet="",
                    rank=rank,
                    provider=self.name,
                    is_ad=False,
                )
            )
            rank += 1
            if len(results) >= max_results:
                break
        return results
