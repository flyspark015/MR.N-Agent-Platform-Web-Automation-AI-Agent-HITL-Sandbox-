from __future__ import annotations

from typing import Dict, List

from skills.research.source_scoring import SourceScore


def synthesize(extractions: List[Dict[str, object]], scores: List[SourceScore]) -> Dict[str, object]:
    claims = []
    stats = []
    dates = []
    contradictions = []
    definitions = []

    for item in extractions:
        claims.extend(item.get("claims", []))
        stats.extend(item.get("statistics", []))
        dates.extend(item.get("dates", []))
        contradictions.extend(item.get("contradictions", []))
        definitions.extend(item.get("definitions", []))

    domain_diversity = len({s.domain for s in scores})
    avg_score = sum(s.score for s in scores) / max(len(scores), 1)
    agreement = max(0, 100 - len(set(contradictions)) * 10)
    confidence = int(min(100, (avg_score * 0.4) + (domain_diversity * 10) + (agreement * 0.2)))

    return {
        "consolidated_findings": list(dict.fromkeys(claims))[:20],
        "conflicting_points": list(dict.fromkeys(contradictions))[:10],
        "numeric_facts": list(dict.fromkeys(stats))[:20],
        "timeline": list(dict.fromkeys(dates))[:20],
        "confidence_level": confidence,
    }
