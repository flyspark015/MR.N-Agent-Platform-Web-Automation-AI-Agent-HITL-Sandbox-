from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

StepType = Literal["NAVIGATE", "SEARCH", "CLICK", "TYPE", "WAIT", "EXTRACT", "SCREENSHOT"]
StepStatus = Literal["PENDING", "RUNNING", "DONE", "FAIL"]

class StepParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: Optional[str] = None
    query: Optional[str] = None
    selector: Optional[str] = None
    text_hint: Optional[str] = None
    text: Optional[str] = None
    ms: Optional[int] = Field(default=None, ge=0)
    schema_name: Optional[str] = None
    label: Optional[str] = None

class StepResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    screenshot_path: Optional[str] = None
    final_url: Optional[str] = None
    title: Optional[str] = None
    extract: Optional[Dict[str, str]] = None

class Step(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int = Field(ge=1)
    type: StepType
    description: str
    params: StepParams = Field(default_factory=StepParams)
    status: StepStatus = "PENDING"
    result: Optional[StepResult] = None
    error: Optional[str] = None

class Plan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    goal: str
    steps: List[Step]

class RunResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str
    goal: str
    status: Literal["DONE", "FAILED", "CANCELLED"]
    steps: List[Step]
    summary: Optional[str] = None
