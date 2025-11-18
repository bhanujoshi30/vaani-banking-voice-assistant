"""Intent classification utilities combining ONNX models with deterministic fallbacks."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, Optional

from .config import IntentDefinition, VoiceConfig
from .keyword_rules import FallbackResult, classify_with_keywords

LOGGER = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency
    import onnxruntime as ort
except Exception:  # pylint: disable=broad-except
    ort = None  # type: ignore

try:  # pragma: no cover - optional dependency
    from transformers import AutoTokenizer
except Exception:  # pylint: disable=broad-except
    AutoTokenizer = None  # type: ignore


class IntentClassifier:
    """Hybrid classifier that prefers an ONNX transformer but gracefully falls back to keywords."""

    def __init__(self, config: VoiceConfig):
        self.config = config
        self._session = None
        self._tokenizer = None
        self._id2label: Dict[int, str] = {}
        if config.onnx_model_path and ort is not None:
            self._load_onnx_assets(config.onnx_model_path)
        else:
            if config.onnx_model_path:
                LOGGER.warning(
                    "onnxruntime is not available; falling back to keyword matching for intents",
                )

    def _load_onnx_assets(self, model_path: Path) -> None:
        try:
            self._session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
        except Exception as exc:  # pylint: disable=broad-except
            LOGGER.error("Unable to load ONNX model: {exc}", exc_info=exc)
            self._session = None
            return

        tokenizer_dir = model_path.parent
        labels_path = tokenizer_dir / "labels.json"
        if labels_path.exists():
            with labels_path.open("r", encoding="utf-8") as handle:
                labels_payload = json.load(handle)
            self._id2label = {int(idx): label for idx, label in labels_payload.items()}
        else:
            # default to alphabetical ordering of configured intents
            self._id2label = {
                idx: name for idx, name in enumerate(sorted(self.config.intent_definitions))
            }

        if AutoTokenizer is not None:
            try:
                self._tokenizer = AutoTokenizer.from_pretrained(tokenizer_dir)
            except Exception as exc:  # pylint: disable=broad-except
                LOGGER.error("Unable to load tokenizer for ONNX model: {exc}", exc_info=exc)
                self._tokenizer = None
        else:
            LOGGER.warning("transformers is not available; ONNX model cannot be used")
            self._session = None

    def predict(self, text: str) -> Dict[str, object]:
        """Return the best intent, slots, and metadata for the supplied text."""

        if self._session is not None and self._tokenizer is not None:
            try:
                encoded = self._tokenizer(
                    text,
                    return_tensors="np",
                    padding="max_length",
                    truncation=True,
                    max_length=64,
                )
                onnx_inputs = {name: encoded[name] for name in self._session.get_inputs()}
                logits = self._session.run(None, onnx_inputs)[0]
                # softmax
                exp = logits - logits.max(axis=1, keepdims=True)
                probabilities = (exp).astype("float64")
                probabilities = probabilities / probabilities.sum(axis=1, keepdims=True)
                index = int(probabilities.argmax())
                confidence = float(probabilities[0, index])
                intent = self._id2label.get(index, list(self.config.intent_definitions)[0])
                source = "onnx"
                if confidence < self.config.confidence_threshold:
                    return self._fallback(text, reason="low_confidence")
                slots = self._extract_slots(intent, text)
                return {
                    "intent": intent,
                    "confidence": confidence,
                    "slots": slots,
                    "source": source,
                }
            except Exception as exc:  # pylint: disable=broad-except
                LOGGER.error("ONNX inference failed: %s", exc, exc_info=exc)

        return self._fallback(text, reason="no_model")

    def _fallback(self, text: str, reason: str) -> Dict[str, object]:
        fallback: FallbackResult = classify_with_keywords(text)
        confidence = float(fallback.confidence)
        if confidence * 100 < self.config.fallback_threshold:
            # treat as unknown intent and request clarification
            return {
                "intent": "clarify",
                "confidence": confidence,
                "slots": {},
                "source": f"fallback:{reason}",
            }
        return {
            "intent": fallback.intent,
            "confidence": confidence,
            "slots": fallback.slots,
            "source": f"fallback:{reason}",
        }

    def _extract_slots(self, intent: str, text: str) -> Dict[str, str]:
        definition: Optional[IntentDefinition] = self.config.intent_definitions.get(intent)
        if not definition:
            return {}
        # For now rely on the fallback extractor, which already contains heuristics
        fallback = classify_with_keywords(text)
        return fallback.slots
