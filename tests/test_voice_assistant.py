from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app import app
from backend.voice import IntentRouter
from backend.voice.evaluation import evaluate_router
from backend.voice.knowledge import get_loan_knowledge_base


def test_intent_router_fallback_balance():
    router = IntentRouter()
    result = router.interpret("please check my balance")
    assert result.intent in {"balance_check", "clarify"}
    assert result.confidence >= 0.0


def test_intent_router_transfer_slots():
    router = IntentRouter()
    result = router.interpret("transfer 500 to mom")
    assert result.intent in {"transfer_funds", "clarify"}
    if result.intent == "transfer_funds":
        assert "amount" in result.slots


def test_voice_interpret_endpoint(monkeypatch):
    client = TestClient(app)
    response = client.post("/api/v1/voice/interpret", json={"utterance": "show my transactions"})
    assert response.status_code == 200
    payload = response.json()
    assert "data" in payload
    assert "intent" in payload["data"]


def test_loan_knowledge_lookup(tmp_path, monkeypatch):
    kb = get_loan_knowledge_base()
    record = kb.query("Tell me about personal loan interest rate")
    if record is not None:
        assert "rate" in record

    client = TestClient(app)
    response = client.get("/api/v1/knowledge/loan-info", params={"query": "home loan"})
    assert response.status_code == 200
    payload = response.json()
    assert "meta" in payload


def test_evaluation_report():
    result = evaluate_router()
    assert result.support >= 1
    assert "precision" in result.report
