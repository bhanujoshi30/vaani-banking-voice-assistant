"""Utilities to evaluate the intent router against labelled utterances."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

from sklearn.metrics import classification_report

from . import IntentRouter

EVAL_DATA_PATH = Path(__file__).resolve().parents[2] / "docs" / "testing" / "utterances.json"


@dataclass(slots=True)
class EvaluationResult:
    report: str
    support: int


def evaluate_router(dataset_path: Path = EVAL_DATA_PATH) -> EvaluationResult:
    router = IntentRouter()
    texts: List[str] = []
    expected: List[str] = []
    predictions: List[str] = []

    with dataset_path.open("r", encoding="utf-8") as handle:
        samples = json.load(handle)

    for sample in samples:
        utterance: str = sample["text"]
        expected_intent: str = sample["expected_intent"]
        result = router.interpret(utterance)
        texts.append(utterance)
        expected.append(expected_intent)
        predictions.append(result.intent)

    report = classification_report(expected, predictions, zero_division=0)
    return EvaluationResult(report=report, support=len(samples))


if __name__ == "__main__":  # pragma: no cover
    evaluation = evaluate_router()
    print(evaluation.report)
