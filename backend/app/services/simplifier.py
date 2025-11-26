from __future__ import annotations
from .llm import LLM

class Simplifier:
    def __init__(self, llm: LLM):
        self.llm = llm

    async def simplify(self, english_script: str, level: int) -> str:
        level = max(0, min(4, int(level)))
        return await self.llm.simplify_again(english_script, level)
