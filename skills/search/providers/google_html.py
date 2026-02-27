from __future__ import annotations

from typing import List
from urllib.parse import parse_qs, urlparse

import httpx
from bs4 import BeautifulSoup

from skills.search.providers.base import SearchProvider, SearchResult

GOOGLE_URL = "https://www.google.com/search"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"

class GoogleHtmlProvider(SearchProvider):
    name = "google_html"

    def _clean_url(self, raw: str) -> str | None:
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

    def _detect_consent(self, text: str) -> bool:
        t = text.lower()
        return "before you continue" in t or "consent" in t

    def _extract(self, html_text: str) -> List[SearchResult]:
        soup = BeautifulSoup(html_text, "html.parser")
        if self._detect_consent(soup.get_text(" ", strip=True)[:500]):
            return []

        results: List[SearchResult] = []
        rank = 1
        for block in soup.select("div.g"):
            link = block.select_one("a[href]")
            title = block.select_one("h3")
            snippet = block.select_one("div.VwiC3b") or block.select_one("span.aCOpRe")
            if not link or not title:
                continue
            href = link.get("href") or ""
            url = self._clean_url(href)
            if not url:
                continue
            results.append(
                SearchResult(
                    url=url,
                    domain=urlparse(url).netloc,
                    title=title.get_text(" ", strip=True),
                    snippet=snippet.get_text(" ", strip=True) if snippet else "",
                    rank=rank,
                    provider=self.name,
                    is_ad=False,
                )
            )
            rank += 1
        return results

    async def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        self.last_error = None
        params = {"q": query, "hl": "en", "gl": "us", "num": max_results}
        headers = {"User-Agent": USER_AGENT}
        async with httpx.AsyncClient(timeout=10, headers=headers, follow_redirects=True) as client:
            try:
                resp = await client.get(GOOGLE_URL, params=params)
                self.last_url = str(resp.request.url)
                self.last_status = resp.status_code
                resp.raise_for_status()
                self.last_html_snippet = resp.text[:5000]
                if "/sorry/" in str(resp.url):
                    self.last_error = "blocked_sorry"
                    return []
                results = self._extract(resp.text)
                if not results and self._detect_consent(resp.text):
                    self.last_error = "consent_or_blocked"
                return results[:max_results]
            except Exception as exc:
                self.last_error = str(exc)
                self.last_html_snippet = ""
                return []
