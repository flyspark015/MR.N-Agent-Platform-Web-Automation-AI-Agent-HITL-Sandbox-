from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

CACHE_DIR = Path("data/intelligence_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def cache_path(key: str) -> Path:
    return CACHE_DIR / f"{key}.json"


def get_cache(key: str) -> Dict[str, Any] | None:
    path = cache_path(key)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def set_cache(key: str, data: Dict[str, Any]) -> None:
    path = cache_path(key)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
