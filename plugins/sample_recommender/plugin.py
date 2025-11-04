from __future__ import annotations
import pathlib
from typing import Dict, Any
from core.contracts import Recommendation, Plan, PlanItem


class SamplePlugin:
    name = "sample-recommender"
    version = "0.1.0"

    def analyze(self, repo_root: str, context: Dict[str, Any]) -> Recommendation:
        root = pathlib.Path(repo_root)
        items = []
        if not (root / "README.md").exists():
            items.append(PlanItem(path="README.md", action="create", content="# Project\n").model_dump())
        return Recommendation(rationale="Ensure README exists", proposed=Plan(items=items))