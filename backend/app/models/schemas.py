from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional

class UploadResponse(BaseModel):
    doc_id: str
    title: str
    topic_ids: List[str]

class TeachPlanTopic(BaseModel):
    id: str
    title: str
    est_minutes: int

class TeachPlanResponse(BaseModel):
    doc_id: str
    plan: List[TeachPlanTopic]

class TeachRequest(BaseModel):
    doc_id: str
    topic_id: str
    simplify_level: int = Field(0, ge=0, le=4)

class Slide(BaseModel):
    heading: str
    bullets: List[str]
    example: Optional[str] = None

class TeachResponse(BaseModel):
    topic_id: str
    slides: List[Slide]
    english_script: str
    hindi_script: str

class FeedbackRequest(BaseModel):
    doc_id: str
    topic_id: str
    understood: bool
    last_simplify_level: int
