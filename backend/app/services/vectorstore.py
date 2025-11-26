from __future__ import annotations
import os, json
from typing import List, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from ..config import settings

# Try FAISS, fallback to pure NumPy inner-product search to avoid platform pain.
try:
    import faiss  # type: ignore
    HAVE_FAISS = True
except Exception:
    faiss = None
    HAVE_FAISS = False

class VectorStore:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        self.model = SentenceTransformer(settings.EMB_MODEL)

    def _paths(self, doc_id: str) -> Tuple[str, str, str, str]:
        ddir = os.path.join(self.base_dir, doc_id)
        os.makedirs(ddir, exist_ok=True)
        return (
            ddir,
            os.path.join(ddir, "index.faiss"),
            os.path.join(ddir, "embeddings.npy"),
            os.path.join(ddir, "meta.json"),
        )

    def index_sections(self, doc_id: str, sections: List[dict]):
        ddir, idx_path, emb_path, meta_path = self._paths(doc_id)
        texts = [s["text"] for s in sections]
        embs = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True).astype(np.float32)

        if HAVE_FAISS:
            index = faiss.IndexFlatIP(embs.shape[1])
            index.add(embs)
            faiss.write_index(index, idx_path)
        else:
            # Save embeddings for NumPy fallback
            np.save(emb_path, embs)

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump({"sections": sections}, f, ensure_ascii=False, indent=2)

    def _load_meta(self, doc_id: str):
        _, _, _, meta_path = self._paths(doc_id)
        return json.load(open(meta_path, "r", encoding="utf-8"))

    def search(self, doc_id: str, query: str, k: int = 5) -> List[dict]:
        ddir, idx_path, emb_path, meta_path = self._paths(doc_id)
        meta = json.load(open(meta_path, "r", encoding="utf-8"))
        sections = meta["sections"]

        q = self.model.encode([query], convert_to_numpy=True, normalize_embeddings=True).astype(np.float32)

        if HAVE_FAISS and os.path.exists(idx_path):
            index = faiss.read_index(idx_path)
            D, I = index.search(q, k)
            ids = I[0]
        else:
            embs = np.load(emb_path)  # (N, d)
            sims = (embs @ q[0])  # inner product with normalized vecs
            ids = np.argsort(-sims)[:k]

        return [sections[int(i)] for i in ids]
