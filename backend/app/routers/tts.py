from __future__ import annotations
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from ..services.tts import synthesize
import io, asyncio

router = APIRouter(prefix="/tts", tags=["tts"])

@router.get("")
async def tts(text: str = Query(..., min_length=1), lang: str = Query("hi")):
    data = await asyncio.to_thread(synthesize, text, lang)
    return StreamingResponse(
        io.BytesIO(data),
        media_type="audio/mpeg",
        headers={"Cache-Control": "no-store"},
    )
