from __future__ import annotations

from typing import List
from urllib.parse import parse_qs, urlparse
import base64
from urllib.parse import unquote

import httpx
from bs4 import BeautifulSoup

from skills.search.providers.base import SearchProvider, SearchResult

class BingHtmlProvider(SearchProvider):
    name = "bing_html"

    def _clean_url(self, raw: str) -> str | None:
        if not raw:
            return None
        if "bing.com/ck/a" in raw or "bing.com/aclick" in raw:
            parsed = parse_qs(urlparse(raw).query)
            token = parsed.get("u", [""])[0]
            if token.startswith("a1"):
                token = token[2:]
            if token:
                try:
                    padding = "=" * (-len(token) % 4)
                    decoded = base64.urlsafe_b64decode(token + padding).decode("utf-8", errors="ignore")
                    decoded = unquote(decoded)
                    if decoded.startswith("http"):
                        raw = decoded
                except Exception:
                    return None
        if raw.startswith("http"):
            netloc = urlparse(raw).netloc.lower()
            if "bing.com" in netloc:
                return None
            return raw.split("#")[0]
        return None

    async def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        self.last_error = None
        url = f"https://www.bing.com/search?q={query.replace(' ', '+')}"
        self.last_url = url
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9",
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
        for li in soup.select("li.b_algo"):
            link = li.select_one("h2 a[href]")
            snippet = li.select_one("p")
            if not link:
                continue
            href = link.get("href")
            cleaned = self._clean_url(href)
            if not cleaned:
                continue
            title = link.get_text(" ", strip=True)
            snip = snippet.get_text(" ", strip=True) if snippet else ""
            results.append(
                SearchResult(
                    url=cleaned,
                    domain=urlparse(cleaned).netloc,
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
