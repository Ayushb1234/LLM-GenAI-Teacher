from __future__ import annotations
import re

def clean_text(s: str) -> str:
    s = s.replace("\x00", "")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def soft_truncate(s: str, max_len: int) -> str:
    if len(s) <= max_len:
        return s
    # cut at word boundary
    cut = s.rfind(" ", 0, max_len)
    return s[: max(0, cut)].strip()
