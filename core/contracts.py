from __future__ import annotations
from typing import List, Dict, Any, Protocol
from pydantic import BaseModel, Field


class PlanItem(BaseModel):
    path: str = Field(..., description="Relative file path")
    action: str = Field(..., description="create|update|delete")
    content: str | None = None


class Plan(BaseModel):
    version: str = "1.0"
    items: List[PlanItem] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Recommendation(BaseModel):
    rationale: str
    proposed: Plan


class Plugin(Protocol):
    name: str
    version: str

    def analyze(self, repo_root: str, context: Dict[str, Any]) -> Recommendation: ...


READ_ONLY_CONTEXT_KEYS = {"repo_root", "seed", "filters"}