from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import re
from urllib.parse import urlparse

MAJOR_NEWS = {
    "nytimes.com",
    "wsj.com",
    "ft.com",
    "bbc.com",
    "reuters.com",
    "bloomberg.com",
    "apnews.com",
}

SPAM_DOMAINS = {
    "pinterest.com",
    "medium.com",
    "reddit.com",
    "quora.com",
    "facebook.com",
    "linkedin.com",
    "twitter.com",
    "x.com",
    "tiktok.com",
    "instagram.com",
    "youtube.com",
}
BONUS_KEYWORDS = ["official", "docs", "documentation", "pdf", "whitepaper", "download", "pricing"]

@dataclass
class SourceScore:
    url: str
    domain: str
    score: int
    source_type: str


def score_source(url: str, snippet: Optional[str] = None) -> SourceScore:
    domain = urlparse(url).netloc.lower()
    score = 40
    source_type = "unknown"
    date_hint = re.search(r"/(20\\d{2})/(0[1-9]|1[0-2])/", url)

    if domain.endswith(".gov") or domain.endswith(".edu"):
        score = 90
        source_type = "official"
    elif domain in MAJOR_NEWS:
        score = 75
        source_type = "news"
    elif domain.endswith(".org"):
        score = 60
        source_type = "organization"
    elif any(k in domain for k in ["support", "help", "docs"]):
        score = 65
        source_type = "documentation"
    else:
        score = 45
        source_type = "blog"

    if domain in SPAM_DOMAINS:
        score -= 15

    if any(k in url.lower() for k in ["/docs", ".pdf", "whitepaper", "download"]):
        score += 10

    if snippet:
        snip = snippet.lower()
        if any(k in snip for k in BONUS_KEYWORDS):
            score += 5

    if date_hint:
        score = min(100, score + 5)

    score = max(0, min(100, score))
    return SourceScore(url=url, domain=domain, score=score, source_type=source_type)
