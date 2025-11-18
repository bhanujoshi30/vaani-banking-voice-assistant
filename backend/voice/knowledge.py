"""Knowledge retrieval helpers for banking products and FAQs."""
from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

try:  # pragma: no cover - optional dependency
    import yaml  # type: ignore
except Exception:  # pylint: disable=broad-except
    yaml = None  # type: ignore

from rapidfuzz import process

LOGGER = logging.getLogger(__name__)

try:  # pragma: no cover - optional heavy dependency
    import faiss  # type: ignore
    from sentence_transformers import SentenceTransformer
except Exception:  # pylint: disable=broad-except
    faiss = None  # type: ignore
    SentenceTransformer = None  # type: ignore

KNOWLEDGE_PATH = Path(__file__).resolve().parents[2] / "docs" / "knowledge" / "finance.yaml"


class LoanKnowledgeBase:
    """Semantic and keyword retriever over curated financial knowledge."""

    def __init__(self, knowledge_file: Path = KNOWLEDGE_PATH):
        self.knowledge_file = knowledge_file
        self._records: List[Dict[str, str]] = []
        self._model: Optional[SentenceTransformer] = None
        self._index = None
        self._load()

    def _load(self) -> None:
        if not self.knowledge_file.exists():
            LOGGER.warning("Loan knowledge file not found at %s", self.knowledge_file)
            return
        if yaml is None:
            LOGGER.info("PyYAML is not installed; loan knowledge disabled")
            return
        with self.knowledge_file.open("r", encoding="utf-8") as handle:
            raw_records = yaml.safe_load(handle) or []
        self._records = []
        for idx, record in enumerate(raw_records):
            if not isinstance(record, dict):
                continue
            enriched = {
                "id": record.get("id") or f"record_{idx}",
                "title": record.get("title", "Unnamed product"),
                "category": record.get("category", "loan"),
                "rate": record.get("rate"),
                "maxAmount": record.get("maxAmount") or record.get("max_amount"),
                "tenure": record.get("tenure"),
                "description": record.get("description", ""),
                "tags": record.get("tags") or [],
            }
            self._records.append(enriched)
        if SentenceTransformer is None or faiss is None:
            LOGGER.info("sentence-transformers/faiss unavailable; using keyword fallback for loan knowledge")
            return
        try:
            self._model = SentenceTransformer("all-mpnet-base-v2")
            embeddings = self._model.encode(
                [
                    f"{record['title']} {record['description']} {' '.join(record.get('tags', []))}"
                    for record in self._records
                ],
            )
            dim = embeddings.shape[1]
            self._index = faiss.IndexFlatIP(dim)
            self._index.add(embeddings.astype("float32"))
        except Exception as exc:  # pylint: disable=broad-except
            LOGGER.error("Failed to build FAISS index: %s", exc, exc_info=exc)
            self._model = None
            self._index = None

    def query(self, question: str) -> Optional[Dict[str, str]]:
        if not question.strip():
            return None
        if self._index is not None and self._model is not None:
            try:
                vector = self._model.encode([question])
                scores, indices = self._index.search(vector.astype("float32"), k=1)
                idx = int(indices[0][0])
                score = float(scores[0][0])
                if 0 <= idx < len(self._records) and score > 0.2:
                    return self._records[idx]
            except Exception as exc:  # pylint: disable=broad-except
                LOGGER.error("Semantic retrieval failed: %s", exc, exc_info=exc)
        # fallback to keyword-based best match
        if not self._records:
            return None
        lookup_terms = {
            record["title"]: record
            for record in self._records
        }
        # include tag combinations for better matching
        for record in self._records:
            for tag in record.get("tags", []):
                lookup_terms.setdefault(f"{record['title']} {tag}", record)

        best = process.extractOne(question, list(lookup_terms.keys()))
        if not best:
            return None
        match, score, _ = best
        if score < 55:
            return None
        return lookup_terms[match]


@lru_cache(maxsize=1)
def get_loan_knowledge_base() -> LoanKnowledgeBase:
    return LoanKnowledgeBase()
