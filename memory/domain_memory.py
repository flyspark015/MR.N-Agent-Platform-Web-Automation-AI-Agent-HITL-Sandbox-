from __future__ import annotations

class DomainMemory:
    def __init__(self) -> None:
        self._store = {}

    def get(self, domain: str):
        return self._store.get(domain, {})

    def set(self, domain: str, data):
        self._store[domain] = data
