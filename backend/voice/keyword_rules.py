"""Keyword heuristics to support deterministic fallback behaviour for voice intents."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from rapidfuzz import fuzz, process

ACCOUNT_KEYWORDS = ["savings", "current", "salary", "primary", "account"]
TRANSFER_KEYWORDS = ["transfer", "send", "bhejo", "pay", "deposit"]
BALANCE_KEYWORDS = ["balance", "kitna", "amount"]
TRANSACTION_KEYWORDS = ["transaction", "statement", "history", "recent"]
REMINDER_KEYWORDS = ["remind", "reminder", "alert"]
LOAN_KEYWORDS = ["loan", "credit", "interest", "rate", "emi"]

CURRENCY_RE = re.compile(r"(?P<amount>\d+(?:[.,]\d{1,2})?)")
DATE_RE = re.compile(
    r"(?P<date>\b(?:tomorrow|today|day after|\d{1,2}\s*(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*|\d{4}-\d{2}-\d{2})\b)",
    re.IGNORECASE,
)


@dataclass(slots=True)
class FallbackResult:
    intent: str
    confidence: float
    slots: Dict[str, str]


def _score(text: str, choices: Iterable[str]) -> float:
    if not choices:
        return 0.0
    _, score, _ = process.extractOne(text, choices, scorer=fuzz.token_set_ratio)
    return float(score)


def classify_with_keywords(text: str) -> FallbackResult:
    lowered = text.lower()
    candidate_scores: List[Tuple[str, float]] = []

    candidate_scores.append(("balance_check", _score(lowered, BALANCE_KEYWORDS)))
    candidate_scores.append(("transfer_funds", _score(lowered, TRANSFER_KEYWORDS)))
    candidate_scores.append(("transaction_history", _score(lowered, TRANSACTION_KEYWORDS)))
    candidate_scores.append(("set_reminder", _score(lowered, REMINDER_KEYWORDS)))
    candidate_scores.append(("loan_info", _score(lowered, LOAN_KEYWORDS)))

    intent, confidence = max(candidate_scores, key=lambda item: item[1])

    slots: Dict[str, str] = {}
    if intent == "balance_check":
        for keyword in ACCOUNT_KEYWORDS:
            if keyword in lowered:
                slots["account"] = keyword
                break
    elif intent == "transfer_funds":
        match = CURRENCY_RE.search(lowered)
        if match:
            slots["amount"] = match.group("amount").replace(",", "")
        for keyword in ACCOUNT_KEYWORDS:
            if keyword in lowered and "source" not in slots:
                slots["source"] = keyword
        # naive beneficiary inference
        to_match = re.search(r"(?:to|for)\s+(?P<dest>[a-zA-Z']+)", lowered)
        if to_match:
            slots["destination"] = to_match.group("dest")
    elif intent == "transaction_history":
        for keyword in ACCOUNT_KEYWORDS:
            if keyword in lowered:
                slots["account"] = keyword
                break
    elif intent == "set_reminder":
        match = DATE_RE.search(lowered)
        if match:
            slots["due_date"] = match.group("date")
        slots["message"] = text
    elif intent == "loan_info":
        # optional product extraction
        product_match = re.search(r"(home|personal|auto|car|education)", lowered)
        if product_match:
            slots["product"] = product_match.group(0)

    return FallbackResult(intent=intent, confidence=confidence / 100.0, slots=slots)
