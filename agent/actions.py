from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

ActionType = Literal[
    "navigate",
    "click",
    "type",
    "scroll",
    "wait",
    "back",
    "extract",
    "extract_table",
    "download",
    "summarize",
    "done",
    "takeover",
    "google_search",
    "open_result",
]

class VerifyRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url_contains: Optional[str] = None
    text_contains: Optional[str] = None
    selector_exists: Optional[str] = None

class Action(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: ActionType
    selector: Optional[str] = None
    text_hint: Optional[str] = None
    x: Optional[int] = None
    y: Optional[int] = None
    input_text: Optional[str] = None
    scroll_delta: Optional[int] = None
    wait_ms: Optional[int] = Field(default=None, ge=0)
    url: Optional[str] = None
    query: Optional[str] = None
    verify: Optional[VerifyRule] = None
    reason: str

class ClickableText(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    tag: str

class Snapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: str
    title: str
    visible_text_summary: str
    clickable_texts: List[ClickableText]
    screenshot_path: str
    dom_hash: str
    screenshot_hash: str

class ActionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    index: int
    action: Action
    status: Literal["RUNNING", "DONE", "FAIL"] = "RUNNING"
    error: Optional[str] = None
