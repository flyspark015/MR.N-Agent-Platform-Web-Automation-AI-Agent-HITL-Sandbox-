from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from agent.actions import ActionRecord

@dataclass
class TaskState:
    task_id: str
    goal: str
    status: str = "IDLE"
    current_url: str = ""
    current_title: str = ""
    actions: List[ActionRecord] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)

@dataclass
class RunState:
    task_id: str
    started_at: float
    status: str = "RUNNING"
    last_error: Optional[str] = None
