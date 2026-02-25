from __future__ import annotations

from typing import List, Dict

from skills.research.source_scoring import SourceScore


def evaluate(state=None, context=None, artifacts=None, **kwargs) -> Dict[str, object]:
    """Backward-compatible evaluate entrypoint.

    Returns a minimal evaluation payload to keep legacy imports stable.
    """
    return {"goal_met": False, "missing_info": [], "next_step": ""}


def evaluate_research_coverage(
    domains: List[str],
    extractions: List[Dict[str, object]],
    scores: List[SourceScore],
) -> Dict[str, object]:
    missing = []
    coverage = 0

    if len(set(domains)) >= 4:
        coverage += 25
    else:
        missing.append("domain_diversity")

    claims = sum(len(x.get("claims", [])) for x in extractions)
    if claims >= 5:
        coverage += 25
    else:
        missing.append("claims")

    stats = sum(len(x.get("statistics", [])) for x in extractions)
    if stats >= 2:
        coverage += 15
    else:
        missing.append("statistics")

    opposing = sum(len(x.get("contradictions", [])) for x in extractions)
    if opposing >= 1:
        coverage += 15
    else:
        missing.append("opposing_view")

    recent = any("202" in d for x in extractions for d in x.get("dates", []))
    if recent:
        coverage += 20
    else:
        missing.append("recent_info")

    return {
        "coverage_score": coverage,
        "missing_dimensions": missing,
        "continue_required": coverage < 70,
    }
