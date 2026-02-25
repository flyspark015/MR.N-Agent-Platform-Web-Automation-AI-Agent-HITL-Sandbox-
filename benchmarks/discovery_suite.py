from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from urllib.parse import urlparse

from core.research_service import discover_sources

GOALS = [
    "find drone manufacturers in India",
    "EU AI Act compliance overview",
    "latest FAA drone regulations",
    "supplier of lithium battery packs",
    "open-source LLM benchmarks",
    "USB-C power delivery specification",
    "ISO 9001 certification requirements",
    "open data portal crime statistics",
    "WHO malaria report 2023",
    "climate change IPCC summary",
    "machine learning optimization techniques",
    "top solar panel manufacturers",
    "semiconductor supply chain report",
    "NIST cybersecurity framework",
    "product pricing for DJI Mini 4 Pro",
    "GPU memory bandwidth table",
    "EU vehicle emissions standards",
    "FDA medical device guidance",
    "Python asyncio documentation",
    "UK Companies House filing rules",
]


def _domain(url: str) -> str:
    return urlparse(url).netloc.lower()


async def run_suite() -> Dict[str, object]:
    results = []
    success = 0
    domain_counts = []
    failures = []

    for goal in GOALS:
        try:
            urls = await discover_sources(goal)
            domains = {d for d in map(_domain, urls) if d and "google.com" not in d}
            ok = len(domains) >= 4
            if ok:
                success += 1
            else:
                failures.append({"goal": goal, "domains": list(domains)})
            domain_counts.append(len(domains))
            results.append({"goal": goal, "urls": urls, "domains": list(domains), "ok": ok})
        except Exception as exc:
            failures.append({"goal": goal, "error": str(exc)})
            results.append({"goal": goal, "urls": [], "domains": [], "ok": False, "error": str(exc)})

    success_rate = success / max(len(GOALS), 1)
    median_domains = sorted(domain_counts)[len(domain_counts) // 2] if domain_counts else 0

    report = {
        "success_rate": success_rate,
        "median_domains": median_domains,
        "failures": failures,
        "results": results,
    }

    out_dir = Path("data/benchmarks")
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"discovery_{timestamp}.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Success rate: {success_rate:.2%}")
    print(f"Median domains: {median_domains}")
    print(f"Report: {out_path}")
    return report


if __name__ == "__main__":
    asyncio.run(run_suite())
