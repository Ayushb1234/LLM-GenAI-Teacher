from __future__ import annotations
from typing import Dict, List
from ..config import settings
import re, json

def _sentences(text: str) -> List[str]:
    text = re.sub(r"\s+", " ", (text or "")).strip()
    if not text: return []
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(])", text)
    return [p.strip() for p in parts if p.strip()]

def _bullet_lines(text: str) -> List[str]:
    lines = re.findall(r"^(?:[-*•]\s+|\(?\d+\)\s+|\d+\.\s+|[A-Za-z]\)\s+)(.+)$", text or "", flags=re.M)
    return [re.sub(r"\s+", " ", l).strip() for l in lines if l.strip()]

def _truncate_list(xs: List[str], n: int, max_len: int = 140) -> List[str]:
    out = []
    for s in xs:
        s = s.strip()
        if len(s) > max_len:
            cut = s.rfind(" ", 0, max_len)
            s = (s[:max(cut, 0)] or s[:max_len]).strip()
        if s:
            out.append(s)
        if len(out) >= n:
            break
    return out

def _rule_based_slides(topic_title: str, topic_text: str) -> Dict:
    bullets = _bullet_lines(topic_text)
    sents = _sentences(topic_text)

    s1 = _truncate_list(bullets or sents, 6)
    facts = [s for s in sents if re.search(r"\b(is|are|means|refers to|consists of)\b", s, re.I)]
    s2 = _truncate_list(facts or sents[6:], 6)
    steps = [b for b in bullets if re.match(r"^\d+|^\(?\d+\)", b)]
    s3 = _truncate_list(steps or bullets[6:] or sents[12:], 6)

    slides = []
    if s1: slides.append({"heading": topic_title or "Overview", "bullets": s1})
    if s2: slides.append({"heading": "Key Details", "bullets": s2})
    if s3: slides.append({"heading": "Steps / Checklist", "bullets": s3})

    script = " ".join(_truncate_list(sents, 10, 160)) or f"Summary of {topic_title}."
    return {"slides": slides or [{"heading": topic_title or "Notes", "bullets": ["Key points"]}], "english_script": script}

class LLM:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.openai_key = settings.OPENAI_API_KEY
        self.ollama_model = settings.OLLAMA_MODEL

    async def plan_topics(self, sections: List[dict]) -> List[dict]:
        # Keep this as you already have; plan order doesn’t cause “Overview”
        lines = [f"- {s['id']} :: {s['title'][:120]} :: {s['text'][:260]}" for s in sections]
        prompt = ("Order these sections for teaching (prereqs first). Return STRICT JSON "
                  "{\"plan\":[{\"id\":\"...\",\"title\":\"...\",\"est_minutes\":<2..10>}...]}.\n\n" + "\n".join(lines))
        text = await self._complete(prompt)
        plan = None
        if text:
            try:
                m = re.search(r"\{[\s\S]*\}\s*$", text.strip())
                payload = m.group(0) if m else text
                data = json.loads(payload)
                plan = [{"id": str(x.get("id")), "title": (str(x.get("title") or "").strip() or "Topic")[:140],
                         "est_minutes": int(x.get("est_minutes") or 3)} for x in (data.get("plan") or [])]
            except Exception:
                plan = None
        valid = {s["id"] for s in sections}
        seen, out = set(), []
        for p in plan or []:
            if p["id"] in valid and p["id"] not in seen:
                out.append(p); seen.add(p["id"])
        if out: return out
        # fallback: natural order
        return [{"id": s["id"], "title": s["title"], "est_minutes": max(2, min(10, len(s["text"].split())//120))} for s in sections]

    async def teach_slides(self, topic_title: str, topic_text: str, simplify_level: int = 0) -> Dict:
        prompt = f"""
You are an excellent teacher. Create concise teaching slides.

Constraints:
- 3–6 slides total
- Each slide: short heading + 3–6 bullets + (optional) one simple example
- Tone: clear, friendly, precise
- English only (blackboard text)
- Simplify level: {simplify_level} (0..4)

Topic Title: {topic_title}
Raw Material:
{topic_text[:4000]}

Return STRICT JSON:
{{"slides":[{{"heading":"...", "bullets":["..."], "example":"..."}}, ...], "english_script":"..."}}
"""
        text = await self._complete(prompt)
        if text:
            try:
                m = re.search(r"\{[\s\S]*\}\s*$", text.strip())
                payload = m.group(0) if m else text
                data = json.loads(payload)
                slides = [{"heading": str(s.get("heading", topic_title))[:140],
                           "bullets": [str(b) for b in (s.get("bullets") or [])][:8],
                           "example": s.get("example")} for s in (data.get("slides") or [])]
                if slides:
                    return {"slides": slides, "english_script": str(data.get("english_script", ""))[:1500]}
            except Exception:
                pass
        # ➜ No LLM or parse failed: rule-based (never “Point A / Point B”)
        return _rule_based_slides(topic_title, topic_text)

    async def simplify_again(self, english_script: str, level: int) -> str:
        prompt = f"Rewrite more simply at level {level} (0..4). <=120 words.\n\n{english_script[:2000]}"
        return await self._complete(prompt) or english_script

    async def translate_to_hindi(self, english_text: str) -> str:
        prompt = f"Translate to natural Hindi (<=180 words):\n\n{english_text[:2000]}"
        return await self._complete(prompt) or english_text

    async def _complete(self, prompt: str) -> str:
        if self.provider == "openai" and self.openai_key:
            try:
                from openai import AsyncOpenAI
                client = AsyncOpenAI(api_key=self.openai_key)
                rsp = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                )
                return rsp.choices[0].message.content or ""
            except Exception:
                return ""
        elif self.provider == "ollama":
            try:
                import httpx
                async with httpx.AsyncClient(timeout=60) as http:
                    r = await http.post("http://localhost:11434/api/generate",
                                        json={"model": settings.OLLAMA_MODEL, "prompt": prompt, "stream": False})
                    r.raise_for_status()
                    return r.json().get("response", "")
            except Exception:
                return ""
        return ""  # provider=none
