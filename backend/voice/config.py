"""Configuration utilities for the voice intent pipeline."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_INTENT_FILE = BASE_DIR / "intents.json"


class IntentDefinition(BaseModel):
    """Schema describing a supported intent, sample utterances, and slot metadata."""

    name: str
    description: str
    sample_utterances: list[str]
    required_slots: list[str] = []
    optional_slots: list[str] = []


@dataclass(slots=True)
class VoiceConfig:
    """Runtime configuration for the voice assistant."""

    onnx_model_path: Path | None
    intent_definitions: Dict[str, IntentDefinition]
    confidence_threshold: float = 0.65
    fallback_threshold: float = 65.0  # rapidfuzz score

    @classmethod
    def load(
        cls,
        onnx_model_path: str | None = None,
        intent_file: Path = DEFAULT_INTENT_FILE,
        confidence_threshold: float = 0.65,
        fallback_threshold: float = 65.0,
    ) -> "VoiceConfig":
        with intent_file.open("r", encoding="utf-8") as handle:
            payload: Dict[str, Any] = json.load(handle)
        definitions = {
            name: IntentDefinition(name=name, **definition)
            for name, definition in payload.items()
        }
        model_path = Path(onnx_model_path) if onnx_model_path else None
        if model_path is not None and not model_path.exists():
            model_path = None
        return cls(
            onnx_model_path=model_path,
            intent_definitions=definitions,
            confidence_threshold=confidence_threshold,
            fallback_threshold=fallback_threshold,
        )
