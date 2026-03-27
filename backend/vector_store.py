import json
import os
from datetime import datetime, timezone
from threading import RLock
from typing import Any

import faiss
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv()

EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./faiss_index/index.faiss")
FAISS_META_PATH = os.getenv("FAISS_META_PATH", "./faiss_index/metadata.json")

_model: SentenceTransformer | None = None
_index: faiss.IndexFlatIP | None = None
_metadata: list[dict[str, Any]] = []
_lock = RLock()


def _project_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _abs_path(path: str) -> str:
    if os.path.isabs(path):
        return path
    return os.path.abspath(os.path.join(_project_root(), path))


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


def _embed_text(text: str) -> np.ndarray:
    model = _get_model()
    vec = model.encode([text])[0].astype(np.float32).reshape(1, -1)
    faiss.normalize_L2(vec)
    return vec


def load_index() -> None:
    global _index, _metadata
    with _lock:
        index_path = _abs_path(FAISS_INDEX_PATH)
        meta_path = _abs_path(FAISS_META_PATH)
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        os.makedirs(os.path.dirname(meta_path), exist_ok=True)

        if os.path.exists(index_path):
            _index = faiss.read_index(index_path)
        else:
            dim = _get_model().get_sentence_embedding_dimension()
            _index = faiss.IndexFlatIP(dim)

        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                _metadata = json.load(f)
        else:
            _metadata = []

        if _index.ntotal != len(_metadata):
            raise RuntimeError("FAISS index and metadata are misaligned.")


def save_index() -> None:
    with _lock:
        if _index is None:
            raise RuntimeError("FAISS index not initialized. Call load_index() first.")
        index_path = _abs_path(FAISS_INDEX_PATH)
        meta_path = _abs_path(FAISS_META_PATH)
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        os.makedirs(os.path.dirname(meta_path), exist_ok=True)

        faiss.write_index(_index, index_path)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(_metadata, f, ensure_ascii=True, indent=2)


def add_document(text: str, metadata: dict[str, Any]) -> dict[str, Any]:
    global _metadata
    with _lock:
        if _index is None:
            load_index()
        if _index is None:
            raise RuntimeError("Unable to initialize FAISS index.")

        vector = _embed_text(text)
        doc = dict(metadata)
        doc.setdefault("uploaded_at", datetime.now(timezone.utc).isoformat())
        _index.add(vector)
        _metadata.append(doc)
        save_index()
        return doc


def search(query_text: str, top_k: int, doc_type: str, recruiter_id: str) -> list[dict[str, Any]]:
    with _lock:
        if _index is None:
            load_index()
        if _index is None or _index.ntotal == 0:
            return []

        query_vec = _embed_text(query_text)
        scores, indices = _index.search(query_vec, _index.ntotal)

        results: list[dict[str, Any]] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            item = _metadata[idx]
            if item.get("doc_type") != doc_type:
                continue
            if str(item.get("recruiter_id")) != str(recruiter_id):
                continue
            enriched = dict(item)
            enriched["semantic_similarity"] = float(max(0.0, min(1.0, score)))
            results.append(enriched)
            if len(results) >= top_k:
                break
        return results
