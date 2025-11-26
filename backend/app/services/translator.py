from __future__ import annotations
from deep_translator import GoogleTranslator

# Lean translation to avoid heavy downloads. If you want
# local offline translation later, you can add MarianMT as optional.

class EnHiTranslator:
    def to_hindi(self, text: str) -> str:
        try:
            return GoogleTranslator(source="en", target="hi").translate(text)
        except Exception:
            # worst-case, return original English
            return text
