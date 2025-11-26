from __future__ import annotations
from typing import List

class TopicGraph:
    """Lightweight sequential plan based on PDF sections."""
    def __init__(self, sections: List[dict]):
        self.sections = sections

    def plan(self) -> List[dict]:
        plan = []
        for s in self.sections:
            est = max(2, min(10, len(s["text"].split()) // 120))  # rough minutes
            plan.append({"id": s["id"], "title": s["title"], "est_minutes": est})
        return plan
