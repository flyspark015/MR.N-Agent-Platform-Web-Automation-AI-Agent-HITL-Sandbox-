from __future__ import annotations

from dataclasses import dataclass
from typing import Dict
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

@dataclass
class SourceScore:
    url: str
    domain: str
    score: int
    source_type: str


def score_source(url: str) -> SourceScore:
    domain = urlparse(url).netloc.lower()
    score = 40
    source_type = "unknown"

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

    return SourceScore(url=url, domain=domain, score=score, source_type=source_type)
