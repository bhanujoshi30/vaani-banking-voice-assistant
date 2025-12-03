"""Unit tests for RAGService context caching helpers."""
from __future__ import annotations

from collections import OrderedDict
from typing import Any, Dict, List

import pytest

from services.rag_service import RAGService


class DummyDocument:
    """Minimal document stub replicating the fields used by RAGService."""

    def __init__(self, content: str, metadata: Dict[str, Any]) -> None:
        self.page_content = content
        self.metadata = metadata


def build_service(documents: List[DummyDocument]) -> RAGService:
    """Create a RAGService instance with a stubbed retrieve method."""

    service = RAGService.__new__(RAGService)
    service.vectorstore = True
    service._context_cache = OrderedDict()
    service._cache_max_size = 8
    service._cache_ttl_seconds = 60

    call_log: List[Dict[str, Any]] = []

    def fake_retrieve(query: str, k: int = 4, filter: Dict[str, Any] | None = None):
        call_log.append({"query": query, "k": k, "filter": filter})
        return documents

    service.retrieve = fake_retrieve  # type: ignore[assignment]
    service._retrieve_calls = call_log  # type: ignore[attr-defined]
    return service


def test_context_cache_hits(monkeypatch: pytest.MonkeyPatch) -> None:
    documents = [
        DummyDocument("Loan info chunk", {"source": "loan.pdf", "loan_type": "home_loan"}),
    ]
    service = build_service(documents)

    first_context = service.get_context_for_query("Home Loan interest", k=3)
    second_context = service.get_context_for_query("Home Loan interest", k=3)

    assert first_context == second_context
    assert len(service._retrieve_calls) == 1  # type: ignore[attr-defined]


def test_cache_key_includes_filter(monkeypatch: pytest.MonkeyPatch) -> None:
    documents = [
        DummyDocument("Investment info chunk", {"source": "investment.pdf", "scheme_type": "ppf"}),
    ]
    service = build_service(documents)

    service.get_context_for_query("Best schemes", k=2, filter={"scheme_type": "ppf"})
    service.get_context_for_query("Best schemes", k=2, filter={"scheme_type": "nps"})

    assert len(service._retrieve_calls) == 2  # type: ignore[attr-defined]
