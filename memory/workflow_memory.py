from __future__ import annotations

class WorkflowMemory:
    def __init__(self) -> None:
        self._flows = {}

    def get(self, name: str):
        return self._flows.get(name, [])

    def set(self, name: str, steps):
        self._flows[name] = steps
