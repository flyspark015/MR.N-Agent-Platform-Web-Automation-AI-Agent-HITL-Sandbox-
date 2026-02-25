from __future__ import annotations

from typing import Callable, Dict, List, Any

Subscriber = Callable[[Dict[str, Any]], None]

class EventBus:
    def __init__(self) -> None:
        self._subs: Dict[str, List[Subscriber]] = {}

    def on(self, event: str, handler: Subscriber) -> None:
        self._subs.setdefault(event, []).append(handler)

    def emit(self, event: str, payload: Dict[str, Any]) -> None:
        for handler in self._subs.get(event, []):
            handler(payload)
