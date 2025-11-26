from __future__ import annotations
from fastapi import APIRouter, HTTPException
from ..models.schemas import TeachPlanResponse, TeachPlanTopic, TeachRequest, TeachResponse, FeedbackRequest
from ..services.llm import LLM
from ..services.translator import EnHiTranslator
from ..config import settings
from rapidfuzz import process, fuzz
import os, json, logging, re

router = APIRouter(prefix="/teach", tags=["teach"])
log = logging.getLogger("ai_tutor")
logging.basicConfig(level=logging.INFO)

def _sections_path(doc_id: str) -> str:
    return os.path.join(settings.DATA_DIR, "docs", doc_id, "sections.json")

@router.get("/plan/{doc_id}", response_model=TeachPlanResponse)
async def get_plan(doc_id: str):
    path = _sections_path(doc_id)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Document not found.")
    sections = json.load(open(path, "r", encoding="utf-8"))

    # ask LLM for order/titles, but never change IDs
    try:
        llm = LLM()
        llm_plan = await llm.plan_topics(sections)
    except Exception as e:
        log.warning("LLM plan failed: %s", e)
        llm_plan = []

    by_id = {s["id"]: s for s in sections}
    seen = set()
    plan = []

    # keep valid IDs in LLM order
    for p in llm_plan:
        sid = str(p.get("id"))
        if sid in by_id and sid not in seen:
            seen.add(sid)
            plan.append({
                "id": sid,
                "title": (p.get("title") or by_id[sid]["title"])[:140],
                "est_minutes": int(p.get("est_minutes") or max(2, min(10, len(by_id[sid]["text"].split()) // 120))),
            })

    # append missing sections by natural order
    for s in sections:
        if s["id"] not in seen:
            plan.append({
                "id": s["id"],
                "title": s["title"],
                "est_minutes": max(2, min(10, len(s["text"].split()) // 120)),
            })
            seen.add(s["id"])

    log.info("PLAN doc_id=%s topics=%d", doc_id, len(plan))
    return TeachPlanResponse(doc_id=doc_id, plan=[TeachPlanTopic(**p) for p in plan])

def _resolve_section(sections, topic_id_or_title: str):
    # 1) exact id
    sec = next((s for s in sections if s["id"] == topic_id_or_title), None)
    if sec: return sec, "id"

    # 2) accept "index:N" debug pattern
    m = re.match(r"^index:(\d+)$", topic_id_or_title or "")
    if m:
        i = int(m.group(1))
        if 0 <= i < len(sections):
            return sections[i], "index"

    # 3) exact title
    sec = next((s for s in sections if s["title"] == topic_id_or_title), None)
    if sec: return sec, "title"

    # 4) fuzzy title
    choices = {s["title"]: s for s in sections}
    if choices:
        match = process.extractOne(topic_id_or_title, list(choices.keys()), scorer=fuzz.WRatio)
        if match and match[1] >= 80:
            return choices[match[0]], f"fuzzy({match[1]})"

    # 5) fallback first
    return (sections[0] if sections else None), "fallback-first"

@router.post("/next", response_model=TeachResponse)
async def next_slide(req: TeachRequest):
    path = _sections_path(req.doc_id)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Document not found.")
    sections = json.load(open(path, "r", encoding="utf-8"))
    sec, how = _resolve_section(sections, req.topic_id)
    if not sec:
        raise HTTPException(status_code=404, detail="No sections available for this document.")

    log.info("NEXT doc=%s req=%s -> resolved=%s via %s title=%s",
             req.doc_id, req.topic_id, sec["id"], how, sec["title"])

    llm = LLM()
    data = await llm.teach_slides(sec["title"], sec["text"], req.simplify_level)
    english_script = data.get("english_script", "")
    slides = data.get("slides", [])

    hi = EnHiTranslator().to_hindi(english_script) if english_script else ""
    return TeachResponse(topic_id=sec["id"], slides=slides, english_script=english_script, hindi_script=hi)

@router.post("/feedback")
async def feedback(req: FeedbackRequest):
    if req.understood:
        return {"action": "advance", "next_simplify_level": max(0, req.last_simplify_level - 1)}
    return {"action": "retry_simpler", "next_simplify_level": min(4, req.last_simplify_level + 1)}
