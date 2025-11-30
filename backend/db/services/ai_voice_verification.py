"""
AI-Enhanced Voice Verification Service
Leverages Ollama AI module for improved voice authentication accuracy
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any, TYPE_CHECKING
import httpx

from .voice_verification import VoiceVerificationService

# AI Backend Configuration
AI_BACKEND_URL = "http://localhost:8001"
AI_VERIFICATION_ENABLED = True  # Can be made configurable
AI_VERIFICATION_TIMEOUT = 8.0  # seconds (increased to allow for LLM processing time)

logger = logging.getLogger(__name__)


@dataclass
class AIVoiceVerificationResult:
    """Result from AI-enhanced voice verification"""
    matches: bool
    similarity_score: float
    confidence: float
    ai_analysis: Optional[Dict[str, Any]] = None
    fallback_to_basic: bool = False


if TYPE_CHECKING:  # pragma: no cover - typing aids only
    import numpy as np


class AIVoiceVerificationService:
    """
    Enhanced voice verification service that combines:
    1. Traditional Resemblyzer embeddings (fast, reliable baseline)
    2. AI-powered analysis via Ollama (context-aware, adaptive)
    """

    def __init__(
        self,
        base_verifier: VoiceVerificationService,
        ai_backend_url: str = AI_BACKEND_URL,
        enabled: bool = AI_VERIFICATION_ENABLED,
    ):
        self._base_verifier = base_verifier
        self._ai_backend_url = ai_backend_url.rstrip('/')
        self._enabled = enabled and base_verifier.enabled
        self._client = httpx.Client(timeout=AI_VERIFICATION_TIMEOUT)
        self._threshold = base_verifier.threshold

    def compute_embedding(self, audio_bytes: bytes):  # type: ignore[override]
        """Compute embedding using base verifier (Resemblyzer)"""
        return self._base_verifier.compute_embedding(audio_bytes)

    def serialize_embedding(self, embedding):
        """Serialize embedding"""
        return self._base_verifier.serialize_embedding(embedding)

    def deserialize_embedding(self, payload: bytes):
        """Deserialize embedding"""
        return self._base_verifier.deserialize_embedding(payload)

    def similarity(self, a, b) -> float:
        """Compute similarity using base verifier"""
        return self._base_verifier.similarity(a, b)

    def _analyze_voice_with_ai(
        self,
        stored_embedding,
        candidate_embedding,
        similarity_score: float,
        user_context: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Use AI to analyze voice characteristics and provide additional verification context
        
        Args:
            stored_embedding: Previously stored voice embedding
            candidate_embedding: New voice sample embedding
            similarity_score: Cosine similarity score from base verifier
            user_context: Optional user context (user_id, customer_number, etc.)
            
        Returns:
            AI analysis dict with confidence, recommendations, etc.
        """
        if not self._enabled:
            return None

        # Prepare analysis request
        analysis_prompt = self._build_analysis_prompt(
            similarity_score=similarity_score,
            user_context=user_context,
        )

        # Call AI backend for analysis
        try:
            response = self._client.post(
                f"{self._ai_backend_url}/api/voice-verification",
                json={
                    "similarity_score": float(similarity_score),
                    "threshold": float(self._threshold),
                    "user_context": user_context or {},
                    "analysis_prompt": analysis_prompt,
                },
                timeout=AI_VERIFICATION_TIMEOUT,
            )
            # Log that AI verification was called
            logger.info(
                f"[Voice Verification] Calling AI backend: similarity={similarity_score:.4f}, "
                f"threshold={self._threshold:.4f}, user_id={user_context.get('user_id') if user_context else 'unknown'}"
            )
            
            if response.status_code == 200:
                ai_response = response.json()
                logger.info(
                    f"[Voice Verification] AI backend response: confidence={ai_response.get('confidence', 'N/A'):.4f}, "
                    f"risk_level={ai_response.get('risk_level', 'N/A')}, "
                    f"recommendation={ai_response.get('recommendation', 'N/A')}, "
                    f"reasoning={ai_response.get('reasoning', 'N/A')[:100]}"
                )
                return ai_response
            else:
                # AI service returned non-200, fallback to basic verification
                logger.debug(
                    f"AI backend returned status {response.status_code}, falling back to basic verification"
                )
                return None
        except httpx.TimeoutException:
            # Timeout is expected if AI backend is slow - fallback gracefully
            logger.debug(
                f"AI backend timeout (>{AI_VERIFICATION_TIMEOUT}s), using basic verification"
            )
            return None
        except httpx.ConnectError as e:
            # Connection error - AI backend may not be running
            logger.debug(
                f"AI backend connection failed (may not be running), using basic verification: {e}"
            )
            return None
        except Exception as e:
            # Other unexpected errors - log at warning level
            logger.warning(
                f"Unexpected error calling AI backend, falling back to basic verification: {e}",
                exc_info=True
            )
            return None

    def _build_analysis_prompt(
        self,
        similarity_score: float,
        user_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build prompt for AI analysis"""
        prompt = f"""Analyze this voice authentication attempt:

Similarity Score: {similarity_score:.4f}
Threshold: {self._threshold:.4f}
Status: {'ABOVE' if similarity_score >= self._threshold else 'BELOW'} threshold

User Context: {json.dumps(user_context or {}, indent=2)}

Provide analysis:
1. Confidence level (0.0-1.0) - how confident are you this is the same speaker?
2. Risk assessment (LOW/MEDIUM/HIGH) - any suspicious patterns?
3. Recommendation (ACCEPT/REJECT/REVIEW) - should authentication proceed?
4. Reasoning - brief explanation

Respond in JSON format:
{{
    "confidence": 0.0-1.0,
    "risk_level": "LOW|MEDIUM|HIGH",
    "recommendation": "ACCEPT|REJECT|REVIEW",
    "reasoning": "brief explanation"
}}"""
        return prompt

    def verify_with_ai(
        self,
        stored_embedding,
        candidate_embedding,
        user_context: Optional[Dict[str, Any]] = None,
    ) -> AIVoiceVerificationResult:
        """
        Enhanced verification combining traditional and AI methods
        
        Args:
            stored_embedding: Previously stored voice embedding
            candidate_embedding: New voice sample embedding
            user_context: Optional user context for AI analysis
            
        Returns:
            AIVoiceVerificationResult with combined analysis
        """
        # Step 1: Basic similarity check (always performed)
        similarity_score = self.similarity(stored_embedding, candidate_embedding)
        basic_matches = similarity_score >= self._threshold
        
        logger.info(
            f"[Voice Verification] Basic similarity check: score={similarity_score:.4f}, "
            f"threshold={self._threshold:.4f}, matches={basic_matches}, "
            f"status={'ABOVE' if similarity_score >= self._threshold else 'BELOW'} threshold"
        )

        # Step 2: AI analysis (if enabled and available)
        ai_analysis = None
        if self._enabled:
            logger.info(
                f"[Voice Verification] Starting AI-enhanced verification for user_id={user_context.get('user_id') if user_context else 'unknown'}"
            )
            ai_analysis = self._analyze_voice_with_ai(
                stored_embedding=stored_embedding,
                candidate_embedding=candidate_embedding,
                similarity_score=similarity_score,
                user_context=user_context,
            )

        # Step 3: Combine results
        if ai_analysis:
            ai_confidence = ai_analysis.get("confidence", similarity_score)
            ai_recommendation = ai_analysis.get("recommendation", "REVIEW")
            ai_risk = ai_analysis.get("risk_level", "MEDIUM")

            # Adaptive decision logic
            if ai_recommendation == "ACCEPT" and ai_risk == "LOW":
                # AI strongly confirms - accept even if slightly below threshold
                final_matches = True
                confidence = max(similarity_score, ai_confidence)
            elif ai_recommendation == "REJECT" or ai_risk == "HIGH":
                # AI flags as suspicious - reject even if above threshold
                final_matches = False
                confidence = min(similarity_score, ai_confidence)
            else:
                # Use basic similarity as primary, AI as secondary
                final_matches = basic_matches
                confidence = (similarity_score + ai_confidence) / 2.0

            logger.info(
                f"[Voice Verification] AI-enhanced result: final_matches={final_matches}, "
                f"similarity_score={similarity_score:.4f}, ai_confidence={ai_confidence:.4f}, "
                f"final_confidence={confidence:.4f}, ai_recommendation={ai_recommendation}, "
                f"ai_risk={ai_risk}"
            )

            return AIVoiceVerificationResult(
                matches=final_matches,
                similarity_score=similarity_score,
                confidence=confidence,
                ai_analysis=ai_analysis,
                fallback_to_basic=False,
            )
        else:
            # Fallback to basic verification
            logger.info(
                f"[Voice Verification] Using basic verification (AI unavailable): "
                f"matches={basic_matches}, similarity_score={similarity_score:.4f}"
            )
            return AIVoiceVerificationResult(
                matches=basic_matches,
                similarity_score=similarity_score,
                confidence=similarity_score,
                ai_analysis=None,
                fallback_to_basic=True,
            )

    def matches(
        self,
        stored,
        candidate,
        use_ai: bool = True,
        user_context: Optional[Dict[str, Any]] = None,
    ) -> tuple[bool, float]:
        """
        Check if voice samples match (backward compatible with base verifier)
        
        Args:
            stored: Stored voice embedding
            candidate: Candidate voice embedding
            use_ai: Whether to use AI enhancement
            user_context: Optional user context
            
        Returns:
            Tuple of (matches: bool, score: float)
        """
        if use_ai and self._enabled:
            result = self.verify_with_ai(
                stored_embedding=stored,
                candidate_embedding=candidate,
                user_context=user_context,
            )
            return result.matches, result.confidence
        else:
            # Use basic verification
            return self._base_verifier.matches(stored, candidate)

    def get_adaptive_threshold(
        self,
        similarity_score: float,
        user_context: Optional[Dict[str, Any]] = None,
    ) -> float:
        """
        Get adaptive threshold based on user context and AI analysis
        
        Args:
            similarity_score: Current similarity score
            user_context: User context (login history, device trust, etc.)
            
        Returns:
            Adaptive threshold value
        """
        base_threshold = self._threshold

        # Adjust threshold based on user context
        if user_context:
            # Lower threshold for trusted devices
            if user_context.get("device_trust_level") == "TRUSTED":
                base_threshold -= 0.05

            # Higher threshold for new devices
            if user_context.get("is_new_device", False):
                base_threshold += 0.05

            # Adjust based on login history
            failed_attempts = user_context.get("recent_failed_attempts", 0)
            if failed_attempts > 2:
                base_threshold += 0.05

        # Ensure threshold stays within reasonable bounds
        return max(0.65, min(0.90, base_threshold))


__all__ = ["AIVoiceVerificationService", "AIVoiceVerificationResult"]

