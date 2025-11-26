from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import ingest, teach, tts  # <— add tts

app = FastAPI(title="AI Tutor — Bilingual Blackboard", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router)
app.include_router(teach.router)
app.include_router(tts.router)  # <— add tts

@app.get("/")
def root():
    return {"ok": True, "service": "ai-tutor-backend"}
