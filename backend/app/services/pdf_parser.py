from __future__ import annotations
from typing import List, Dict
import uuid, re

def _clean(s: str) -> str:
    s = s.replace("\x00", "")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def _soft_truncate(s: str, n: int) -> str:
    if len(s) <= n: return s
    cut = s.rfind(" ", 0, n)
    return (s[: max(0, cut)] or s[:n]).strip()

class ParsedDoc:
    def __init__(self, doc_id: str, title: str, sections: list[dict]):
        self.doc_id = doc_id
        self.title = title
        self.sections = sections  # [{id,title,text}]

def parse_pdf_to_sections(pdf_bytes: bytes) -> ParsedDoc:
    """
    1) Try PyMuPDF with font-size aware heading detection
    2) Fallback to PyPDF with regex heading detection
    """
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        items = []
        for page in doc:
            d = page.get_text("dict")
            for b in d.get("blocks", []):
                for l in b.get("lines", []):
                    # each line: concatenate spans; take max size for line
                    spans = l.get("spans", [])
                    if not spans: continue
                    txt = " ".join(s.get("text", "") for s in spans).strip()
                    if not txt: continue
                    sizes = [float(s.get("size", 0)) for s in spans]
                    maxsize = max(sizes) if sizes else 0
                    items.append({"text": txt, "size": maxsize})

        if not items:
            raise ValueError("No text")

        # bucket font sizes
        sizes = sorted(set(round(x["size"], 1) for x in items if x["size"] > 0), reverse=True)
        # consider top 2 sizes as headings; if only 1, use a relative threshold
        h1 = sizes[0] if sizes else 20.0
        h2 = sizes[1] if len(sizes) > 1 else max(h1 - 2, 14.0)
        min_head_len = 140

        sections: List[Dict] = []
        cur = {"title": "Introduction", "text": ""}

        for it in items:
            t = it["text"]
            sz = it["size"]
            looks_numbered = bool(re.match(r"^(\d+(\.\d+)*|[A-Z]\.)\s+\S", t))
            is_heading = (sz >= h2 and len(t) < min_head_len) or looks_numbered
            if is_heading:
                if cur["text"].strip():
                    sections.append(cur)
                cur = {"title": t, "text": ""}
            else:
                cur["text"] += " " + t

        if cur["text"].strip():
            sections.append(cur)

        # cleanup
        for s in sections:
            s["title"] = _soft_truncate(_clean(s["title"]), 200) or "Section"
            s["text"]  = _soft_truncate(_clean(s["text"]), 20000)

        doc_id = str(uuid.uuid4())
        title = doc.metadata.get("title") or (sections[0]["title"] if sections else f"Document {doc_id[:8]}")
        for i, s in enumerate(sections):
            s["id"] = f"sec-{i:03d}"
        return ParsedDoc(doc_id, title, sections)

    except Exception:
        # PyPDF fallback
        from pypdf import PdfReader
        import io
        r = PdfReader(io.BytesIO(pdf_bytes))

        raw: List[Dict] = []
        cur = {"title": "Introduction", "text": ""}

        for page in r.pages:
            txt = (page.extract_text() or "").strip()
            if not txt: continue
            lines = [ln.strip() for ln in txt.splitlines() if ln.strip()]
            for ln in lines:
                looks_numbered = bool(re.match(r"^(\d+(\.\d+)*|[A-Z]\.|Chapter\s+\d+|SECTION\s+\d+)\s+.*", ln))
                looks_header   = looks_numbered or (ln.isupper() and 3 <= len(ln) <= 120) or (ln.endswith(":") and len(ln) < 120)
                if looks_header:
                    if cur["text"].strip():
                        raw.append(cur)
                    cur = {"title": ln.rstrip(":"), "text": ""}
                else:
                    cur["text"] += " " + ln
        if cur["text"].strip():
            raw.append(cur)

        if not raw:
            whole = " ".join([(p.extract_text() or "") for p in r.pages])
            raw = [{"title": "Document", "text": whole or ""}]

        for s in raw:
            s["title"] = _soft_truncate(_clean(s["title"]), 200) or "Section"
            s["text"]  = _soft_truncate(_clean(s["text"]), 20000)

        doc_id = str(uuid.uuid4())
        title = (getattr(r, "metadata", None) and r.metadata.title) or raw[0]["title"] or f"Document {doc_id[:8]}"
        for i, s in enumerate(raw):
            s["id"] = f"sec-{i:03d}"
        return ParsedDoc(doc_id, title, raw)
