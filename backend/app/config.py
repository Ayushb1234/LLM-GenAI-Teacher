from __future__ import annotations
from pydantic import BaseModel, Field
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_DIR = os.getenv("DATA_DIR", str(BASE_DIR / "data"))

class Settings(BaseModel):
    DATA_DIR: str = Field(default=DEFAULT_DATA_DIR)
    # LLM provider: "openai" | "ollama" | "none"
    LLM_PROVIDER: str = Field(default=os.getenv("LLM_PROVIDER", "openai"))
    OPENAI_API_KEY: str | None = Field(default=os.getenv("OPENAI_API_KEY"))
    OLLAMA_MODEL: str = Field(default=os.getenv("OLLAMA_MODEL", "llama3.1:8b-instruct"))
    EMB_MODEL: str = Field(default=os.getenv("EMB_MODEL", "sentence-transformers/all-MiniLM-L6-v2"))

settings = Settings()

# ensure data dirs exist
Path(settings.DATA_DIR).mkdir(parents=True, exist_ok=True)
(Path(settings.DATA_DIR) / "docs").mkdir(parents=True, exist_ok=True)
(Path(settings.DATA_DIR) / "index").mkdir(parents=True, exist_ok=True)
