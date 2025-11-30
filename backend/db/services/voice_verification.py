"""Voice verification utilities built around open-source speaker models.

This module gracefully degrades when heavy audio/Speaker-ID dependencies are not
installed. In serverless deployments (e.g., Vercel) we skip voice verification
by returning ``None`` and logging a warning instead of importing libraries that
pull in large native binaries such as NumPy, SciPy, or Resemblyzer.
"""

from __future__ import annotations

import io
import logging
import os
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Optional, TYPE_CHECKING

try:  # pragma: no cover - exercised implicitly when dependencies exist
    import numpy as _np
    import soundfile as _sf
    from resemblyzer import VoiceEncoder as _VoiceEncoder
    from scipy.spatial.distance import cosine as _cosine
    _VOICE_LIBS_AVAILABLE = True
except ImportError:  # pragma: no cover - handled for lightweight deployments
    _np = None
    _sf = None
    _VoiceEncoder = None
    _cosine = None
    _VOICE_LIBS_AVAILABLE = False

if TYPE_CHECKING:  # pragma: no cover - typing aid only
    import numpy as np

if _VOICE_LIBS_AVAILABLE:
    np = _np  # type: ignore
    sf = _sf  # type: ignore
    cosine = _cosine  # type: ignore
else:
    np = None  # type: ignore
    sf = None  # type: ignore
    cosine = None  # type: ignore

logger = logging.getLogger(__name__)

DEFAULT_SAMPLE_RATE = 16000
MIN_DURATION_SECONDS = 1.2


def _voice_feature_enabled() -> bool:
    flag = os.getenv("VOICE_VERIFICATION_ENABLED", "true").lower()
    return flag in {"1", "true", "yes", "on"}


def _normalize_audio(samples):
    """Ensure mono float32 audio for the encoder."""
    if not _VOICE_LIBS_AVAILABLE:
        return samples
    if samples.ndim > 1:
        samples = np.mean(samples, axis=1)
    if samples.dtype != np.float32:
        samples = samples.astype(np.float32)
    max_abs = np.max(np.abs(samples)) or 1.0
    if max_abs > 1.0:
        samples = samples / max_abs
    return samples


@lru_cache(maxsize=1)
def _load_encoder():
    if not _VOICE_LIBS_AVAILABLE:
        return None
    return _VoiceEncoder()


@dataclass
class VoiceVerificationService:
    """Encapsulates speaker embedding and similarity scoring."""

    threshold: float = 0.75
    enabled: bool = field(default_factory=lambda: _VOICE_LIBS_AVAILABLE and _voice_feature_enabled())

    def compute_embedding(self, audio_bytes: bytes) -> Optional[np.ndarray]:
        """Compute a speaker embedding from raw audio bytes."""
        if not self.enabled:
            logger.info("voice_verification_disabled", reason="feature_flag_or_missing_dependencies")
            return None
        if not audio_bytes:
            return None
        with io.BytesIO(audio_bytes) as buffer:
            samples, sr = _sf.read(buffer)
        samples = _normalize_audio(samples)
        if sr != DEFAULT_SAMPLE_RATE:
            # Lazy import to avoid mandatory dependency unless needed.
            try:
                import librosa
            except ImportError:
                logger.warning("voice_resample_missing_librosa", current_rate=sr)
                return None

            samples = librosa.resample(samples, orig_sr=sr, target_sr=DEFAULT_SAMPLE_RATE)
            sr = DEFAULT_SAMPLE_RATE
        duration = len(samples) / float(sr)
        if duration < MIN_DURATION_SECONDS:
            # Pad with a small amount of reflected audio so the encoder has enough frames.
            pad_length = int((MIN_DURATION_SECONDS * sr) - len(samples))
            samples = np.pad(samples, (0, max(pad_length, 0)), mode="reflect")
        encoder = _load_encoder()
        if encoder is None:
            logger.warning("voice_encoder_unavailable")
            return None
        try:
            embedding = encoder.embed_utterance(samples)
        except AssertionError:
            # Re-sample one more time via librosa at the expected rate; if it still fails, bail.
            try:
                import librosa
            except ImportError:
                logger.warning("voice_resample_missing_librosa", retry=True)
                return None

            samples = librosa.resample(samples, orig_sr=sr, target_sr=DEFAULT_SAMPLE_RATE)
            try:
                embedding = encoder.embed_utterance(samples)
            except AssertionError:
                return None
        return embedding.astype(np.float32)

    @staticmethod
    def serialize_embedding(embedding: np.ndarray) -> bytes:
        if not _VOICE_LIBS_AVAILABLE:
            raise RuntimeError("Voice verification dependencies unavailable")
        return embedding.astype(np.float32).tobytes()

    @staticmethod
    def deserialize_embedding(payload: bytes) -> np.ndarray:
        if not _VOICE_LIBS_AVAILABLE:
            raise RuntimeError("Voice verification dependencies unavailable")
        return np.frombuffer(payload, dtype=np.float32)

    def similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        if not _VOICE_LIBS_AVAILABLE:
            return 0.0
        if not len(a) or not len(b):
            return 0.0
        return 1 - _cosine(a, b)

    def matches(self, stored: np.ndarray, candidate: np.ndarray) -> bool:
        if not _VOICE_LIBS_AVAILABLE:
            return False
        score = self.similarity(stored, candidate)
        return score >= self.threshold, score


__all__ = ["VoiceVerificationService"]

