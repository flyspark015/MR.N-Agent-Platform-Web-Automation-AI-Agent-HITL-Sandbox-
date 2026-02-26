from __future__ import annotations

from dataclasses import dataclass
from typing import List

@dataclass
class SearchResult:
    url: str
    domain: str
    title: str
    snippet: str
    rank: int
    provider: str
    is_ad: bool = False

class SearchProvider:
    name: str = "base"
    last_url: str | None = None
    last_html_snippet: str | None = None
    last_error: str | None = None

    async def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        raise NotImplementedError
