"""Intent routing orchestrator for the voice assistant."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict

from .config import VoiceConfig
from .intent_classifier import IntentClassifier


@dataclass(slots=True)
class Interpretation:
    intent: str
    confidence: float
    slots: Dict[str, str]
    source: str

    def as_payload(self) -> Dict[str, object]:
        return {
            "intent": self.intent,
            "confidence": self.confidence,
            "slots": self.slots,
            "source": self.source,
        }


class IntentRouter:
    """High-level orchestrator responsible for interpreting utterances."""

    def __init__(self, config: VoiceConfig | None = None):
        if config is None:
            model_path = os.getenv("VOICE_INTENT_ONNX_MODEL")
            config = VoiceConfig.load(onnx_model_path=model_path)
        self.config = config
        self._classifier = IntentClassifier(config)

    def interpret(self, text: str) -> Interpretation:
        """Return the canonical interpretation for the supplied text."""

        result = self._classifier.predict(text)
        return Interpretation(
            intent=result["intent"],
            confidence=float(result.get("confidence", 0.0)),
            slots=dict(result.get("slots", {})),
            source=str(result.get("source", "unknown")),
        )
