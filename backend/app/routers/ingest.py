from __future__ import annotations
from fastapi import APIRouter, UploadFile, File, HTTPException
from ..services.pdf_parser import parse_pdf_to_sections
from ..services.vectorstore import VectorStore
from ..models.schemas import UploadResponse
from ..config import settings
import os, json

router = APIRouter(prefix="/ingest", tags=["ingest"])

@router.post("/pdf", response_model=UploadResponse)
async def ingest_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
    pdf_bytes = await file.read()

    parsed = parse_pdf_to_sections(pdf_bytes)

    docs_dir = os.path.join(settings.DATA_DIR, "docs", parsed.doc_id)
    os.makedirs(docs_dir, exist_ok=True)
    with open(os.path.join(docs_dir, "sections.json"), "w", encoding="utf-8") as f:
        json.dump(parsed.sections, f, ensure_ascii=False, indent=2)

    vs = VectorStore(os.path.join(settings.DATA_DIR, "index"))
    vs.index_sections(parsed.doc_id, parsed.sections)

    return UploadResponse(doc_id=parsed.doc_id, title=parsed.title, topic_ids=[s["id"] for s in parsed.sections])
