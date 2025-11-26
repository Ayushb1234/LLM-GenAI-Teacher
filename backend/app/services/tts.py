from __future__ import annotations
from gtts import gTTS
from io import BytesIO

def synthesize(text: str, lang: str = "hi") -> bytes:
    """
    Simple online TTS (no API key) using gTTS.
    Returns MP3 bytes. lang: 'hi' or 'en'
    """
    text = (text or "").strip()
    if not text:
        return b""
    buf = BytesIO()
    tts = gTTS(text=text, lang=("hi" if lang.lower().startswith("hi") else "en"))
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()
