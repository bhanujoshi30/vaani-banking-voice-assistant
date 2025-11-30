"""Authentication service bridging repositories and security helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from secrets import token_urlsafe
from typing import Optional
import hashlib
import logging

from sqlalchemy.orm import Session

from ..models import Session as SessionModel
from ..utils.enums import (
    AuthenticationLevel,
    DeviceTrustLevel,
    SessionStatus,
    TransactionChannel,
)
from ..engine import session_scope
from ..repositories.auth import (
    get_session_by_token,
    get_user_by_customer_number,
    invalidate_all_user_sessions,
)
from ..models import User
from ..repositories import (
    create_device_binding,
    get_device_binding_for_device,
    list_device_bindings,
    mark_device_binding_trust,
)
from ..utils.security import verify_password
from .voice_verification import VoiceVerificationService

logger = logging.getLogger(__name__)


@dataclass
class AuthResult:
    success: bool
    reason: Optional[str] = None
    user_profile: Optional[dict] = None
    access_token: Optional[str] = None
    expires_in: Optional[int] = None
    detail: Optional[dict] = None
    user_id: Optional[str] = None  # User UUID for AI backend


@dataclass
class AuthenticatedSession:
    user_id: str
    customer_number: str
    session_id: str
    access_token: str
    expires_at: datetime
    binding_id: Optional[str] = None


ACCESS_TOKEN_TTL_SECONDS = 60 * 30  # 30 minutes
SESSION_INACTIVITY_TIMEOUT = timedelta(minutes=5)  # RBI-recommended inactivity threshold
VOICE_VERIFICATION_VALIDITY = timedelta(days=7)
VOICE_ENROLLMENT_PHRASE = "Sun Bank mera saathi, har kadam surakshit banking ka vaada"


class SessionValidationError(Exception):
    """Represents an invalid or expired session state."""

    def __init__(self, *, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class AuthService:
    """Provides user authentication and profile retrieval."""

    def __init__(self, session_factory, voice_verifier: VoiceVerificationService):
        self._session_factory = session_factory
        self._voice_verifier = voice_verifier

    def authenticate(
        self,
        *,
        customer_number: str,
        password: str,
        device_identifier: Optional[str] = None,
        fingerprint_hash: Optional[str] = None,
        platform: Optional[str] = None,
        device_label: Optional[str] = None,
        voice_sample: Optional[bytes] = None,
        registration_method: Optional[str] = None,
        login_mode: str = "password",
        validate_only: bool = False,
    ) -> AuthResult:
        try:
            with session_scope(self._session_factory) as session:
                # Trim customer_number for lookup
                customer_number_clean = customer_number.strip() if customer_number else customer_number
                user = get_user_by_customer_number(session, customer_number_clean)
                if user is None:
                    logger.warning(
                        f"[Auth] User not found: customer_number='{customer_number_clean}' "
                        f"(original='{customer_number}')"
                    )
                    return AuthResult(success=False, reason="invalid_credentials")

                # Define user_id_value early to avoid UnboundLocalError
                user_id_value = user.id
                customer_number_value = user.customer_number
                
                # Define timezone and now early - needed for password login device binding
                tz = ZoneInfo("Asia/Kolkata")
                now = datetime.now(tz)

                if login_mode != "voice":
                    # Initialize detail dict for password login flow
                    detail: dict = {"loginMode": login_mode}
                    
                    # Ensure password is provided and not empty
                    if not password or not password.strip():
                        logger.warning(
                            f"[Auth] Empty password provided for user: customer_number='{customer_number_value}'"
                        )
                        return AuthResult(success=False, reason="invalid_credentials")
                    
                    # Access password_hash while session is active to avoid DetachedInstanceError
                    password_hash_value = user.password_hash
                    if not password_hash_value:
                        logger.error(
                            f"[Auth] User has no password_hash: customer_number='{customer_number_value}'"
                        )
                        return AuthResult(success=False, reason="invalid_credentials")
                    
                    password_clean = password.strip()
                    is_valid = verify_password(password_clean, password_hash_value)
                    if not is_valid:
                        logger.warning(
                            f"[Auth] Password verification failed: customer_number='{customer_number_value}', "
                            f"password_length={len(password_clean)}, password_hash_exists={bool(password_hash_value)}"
                        )
                        return AuthResult(success=False, reason="invalid_credentials")
                    logger.info(
                        f"[Auth] Password verification successful: customer_number='{customer_number_value}'"
                    )
                    
                    # For validate_only mode with password login, return immediately after password verification
                    if validate_only:
                        logger.info(
                            f"[Auth] Validation only mode (password) - returning success: customer_number='{customer_number_value}'"
                        )
                        return AuthResult(
                            success=True,
                            reason="validated",
                            detail={"loginMode": login_mode},
                            user_id=str(user_id_value),
                        )
                    
                    # Keep device_identifier and fingerprint_hash if provided (for device binding creation)
                    # Only clear voice_sample for password login
                    voice_sample = None
                    # Set defaults if not provided
                    if device_identifier is None:
                        device_identifier = f"password-{user_id_value}"
                    if fingerprint_hash is None:
                        fingerprint_hash = device_identifier
                    if platform is None:
                        platform = "web"
                    if device_label is None:
                        device_label = "Password-secured device"
                    
                    # Revoke all existing voice-secured bindings on password login
                    # Password login means user is not using voice authentication,
                    # so any previous voice-secured sessions should be invalidated
                    binding_id: Optional[str] = None
                    if not validate_only:
                        # Get all bindings for the user (including revoked ones)
                        all_bindings = list(list_device_bindings(session, user_id=user_id_value, include_revoked=True))
                        
                        # First pass: Revoke bindings that have voice signatures (voice-secured sessions)
                        # This isolates password login from voice login
                        for binding in all_bindings:
                            # Revoke bindings that have voice signatures (voice-secured sessions)
                            if binding.voice_signature_vector is not None and binding.trust_level != DeviceTrustLevel.REVOKED:
                                mark_device_binding_trust(
                                    session, binding=binding, trust_level=DeviceTrustLevel.REVOKED
                                )
                                # Clear voice signature when revoking - user must re-enroll voice
                                binding.voice_signature_hash = None
                                binding.voice_signature_vector = None
                        
                        # Create or update a password-based device binding (without voice signature)
                        # This ensures there's always a binding to manage, even for password login
                        current_binding = get_device_binding_for_device(
                            session, user_id=user_id_value, device_identifier=device_identifier
                        )
                        if current_binding:
                            # Update existing binding (might be revoked from previous voice login)
                            logger.info(
                                f"[Auth] Updating existing device binding for password login: "
                                f"user_id={user_id_value}, binding_id={current_binding.id}, "
                                f"trust_level={current_binding.trust_level.value}"
                            )
                            current_binding.fingerprint_hash = fingerprint_hash
                            current_binding.platform = platform
                            current_binding.device_label = device_label
                            current_binding.last_verified_at = now
                            current_binding.revoked_at = None  # Clear revoked status
                            # Restore to TRUSTED if it was revoked
                            if current_binding.trust_level == DeviceTrustLevel.REVOKED:
                                logger.info(
                                    f"[Auth] Restoring revoked binding to TRUSTED: binding_id={current_binding.id}"
                                )
                                mark_device_binding_trust(session, binding=current_binding, trust_level=DeviceTrustLevel.TRUSTED)
                            binding_id = str(current_binding.id)
                            logger.info(
                                f"[Auth] Device binding updated successfully: binding_id={binding_id}, "
                                f"trust_level={current_binding.trust_level.value}"
                            )
                        else:
                            # Create new password-based binding (no voice signature)
                            logger.info(
                                f"[Auth] Creating new device binding for password login: "
                                f"user_id={user_id_value}, device_identifier={device_identifier}"
                            )
                            new_binding = create_device_binding(
                                session,
                                user_id=user_id_value,
                                device_identifier=device_identifier,
                                fingerprint_hash=fingerprint_hash,
                                registration_method="password",
                                platform=platform,
                                device_label=device_label,
                                trust_level=DeviceTrustLevel.TRUSTED,
                                voice_signature_hash=None,
                                voice_signature_vector=None,
                            )
                            session.flush()
                            session.refresh(new_binding)
                            binding_id = str(new_binding.id)
                            current_binding = new_binding
                            logger.info(
                                f"[Auth] Device binding created successfully: binding_id={binding_id}, "
                                f"trust_level={new_binding.trust_level.value}"
                            )
                            # Refresh all_bindings to include the newly created binding
                            all_bindings = list(list_device_bindings(session, user_id=user_id_value, include_revoked=True))
                        
                        # Second pass: Revoke all other password-based bindings to ensure only one active binding
                        # This keeps password login isolated - only one active password binding at a time
                        for other_binding in all_bindings:
                            if current_binding and other_binding.id != current_binding.id:
                                # Only revoke password-based bindings (those without voice signatures)
                                # Voice-secured bindings were already revoked in the first pass
                                if (other_binding.voice_signature_vector is None and 
                                    other_binding.trust_level != DeviceTrustLevel.REVOKED):
                                    mark_device_binding_trust(
                                        session, binding=other_binding, trust_level=DeviceTrustLevel.REVOKED
                                    )
                                    other_binding.voice_signature_hash = None
                                    other_binding.voice_signature_vector = None
                        
                        # Ensure binding_id is set for password login
                        if not binding_id and current_binding:
                            binding_id = str(current_binding.id)
                            logger.info(
                                f"[Auth] Set binding_id from current_binding: binding_id={binding_id}"
                            )
                        
                        logger.info(
                            f"[Auth] Password login device binding complete: binding_id={binding_id}, "
                            f"device_identifier={device_identifier}, continuing to session creation"
                        )
                        
                        # Password login is complete - proceed directly to session creation
                        # Ensure we have user_id_value and customer_number_value for session creation
                        if not user_id_value:
                            user_id_value = user.id
                        if not customer_number_value:
                            customer_number_value = user.customer_number
                        
                        # PASSWORD LOGIN FLOW - Create session immediately, skip all voice processing
                        logger.info(
                            f"[Auth] Password login flow complete, proceeding to session creation: "
                            f"binding_id={binding_id}, user_id={user_id_value}"
                        )
                        
                        # Create session for password login
                        return self._create_session_for_password_login(
                            session=session,
                            user=user,
                            user_id_value=user_id_value,
                            customer_number_value=customer_number_value,
                            device_identifier=device_identifier,
                            fingerprint_hash=fingerprint_hash,
                            binding_id=binding_id,
                            login_mode=login_mode,
                            detail=detail,
                            now=now,
                            tz=tz,
                        )
                else:
                    # ============================================================
                    # VOICE LOGIN - Clean, Simple Implementation
                    # ============================================================
                    detail: dict = {"loginMode": "voice"}
                    
                    logger.info(
                        f"[Auth] Starting voice login: customer_number='{customer_number_value}', "
                        f"voice_sample_provided={voice_sample is not None}"
                    )
                    
                    if not self._voice_verifier.enabled:
                        logger.warning(
                            "[Voice] Voice verification disabled or dependencies missing; rejecting voice login"
                        )
                        return AuthResult(
                            success=False,
                            reason="voice_verification_unavailable",
                            detail={
                                "message": "Voice login is temporarily unavailable. Please use OTP/password login instead.",
                            },
                        )

                    # Validate voice sample is provided
                    if not voice_sample:
                        return AuthResult(
                            success=False,
                            reason="voice_sample_invalid",
                            detail={
                                "message": "Voice sample required for voice login.",
                                "voicePhrase": VOICE_ENROLLMENT_PHRASE,
                            },
                        )
                    
                    # Optional password verification (if provided)
                    if password:
                        if not verify_password(password.strip(), user.password_hash):
                            return AuthResult(success=False, reason="invalid_credentials")
                    
                    # Set defaults for device info
                    if device_identifier is None:
                        device_identifier = f"voice-{user_id_value}"
                    if fingerprint_hash is None:
                        fingerprint_hash = device_identifier
                    if platform is None:
                        platform = "web"
                    if device_label is None:
                        device_label = "Voice Device"
                    
                    # Compute voice embedding
                    logger.info(
                        f"[Voice] Computing embedding: user_id={user_id_value}, "
                        f"sample_size={len(voice_sample)} bytes"
                    )
                    voice_embedding = self._voice_verifier.compute_embedding(voice_sample)
                    if voice_embedding is None:
                        return AuthResult(
                            success=False,
                            reason="voice_sample_invalid",
                            detail={
                                "message": "Voice sample was too short or unclear. Please record again.",
                                "voicePhrase": VOICE_ENROLLMENT_PHRASE,
                            },
                        )

                    voice_vector_bytes = self._voice_verifier.serialize_embedding(voice_embedding)
                    voice_hash = hashlib.sha256(voice_sample).hexdigest()
                    logger.info(
                        f"[Voice] Embedding computed: shape={voice_embedding.shape}, "
                        f"hash={voice_hash[:16]}..."
                    )
                    
                    # Check for existing device binding
                    # First try to find binding with same device_identifier
                    existing_binding = get_device_binding_for_device(
                        session, user_id=user_id_value, device_identifier=device_identifier
                    )
                    logger.info(
                        f"[Voice] Initial binding lookup by device_identifier: "
                        f"device_identifier='{device_identifier}', found={existing_binding is not None}, "
                        f"has_voice={existing_binding.voice_signature_vector is not None if existing_binding else False}"
                    )
                    
                    # If not found, check for any existing trusted binding (for password->voice conversion)
                    # In validate_only mode, prioritize voice bindings
                    if not existing_binding:
                        # First check non-revoked bindings
                        all_bindings = list(list_device_bindings(session, user_id=user_id_value, include_revoked=False))
                        logger.info(
                            f"[Voice] Fallback lookup (non-revoked): found {len(all_bindings)} bindings for user_id={user_id_value}"
                        )
                        
                        # In validate_only mode, prioritize voice bindings
                        if validate_only:
                            # First try to find a trusted binding WITH voice signature
                            for binding in all_bindings:
                                if (binding.trust_level == DeviceTrustLevel.TRUSTED and 
                                    binding.voice_signature_vector is not None):
                                    existing_binding = binding
                                    logger.info(
                                        f"[Voice] Found existing VOICE binding for validation: "
                                        f"binding_id={binding.id}, device_identifier={binding.device_identifier}"
                                    )
                                    device_identifier = binding.device_identifier
                                    break
                            
                            # If still not found, check revoked bindings too (in case binding was revoked somehow)
                            if not existing_binding:
                                all_bindings_revoked = list(list_device_bindings(session, user_id=user_id_value, include_revoked=True))
                                logger.info(
                                    f"[Voice] Fallback lookup (including revoked): found {len(all_bindings_revoked)} total bindings"
                                )
                                for binding in all_bindings_revoked:
                                    if (binding.voice_signature_vector is not None):
                                        existing_binding = binding
                                        logger.info(
                                            f"[Voice] Found VOICE binding (including revoked) for validation: "
                                            f"binding_id={binding.id}, trust_level={binding.trust_level.value}, "
                                            f"device_identifier={binding.device_identifier}"
                                        )
                                        device_identifier = binding.device_identifier
                                        break
                        
                        # If still not found (or not validate_only), find any trusted binding
                        if not existing_binding:
                            for binding in all_bindings:
                                if binding.trust_level == DeviceTrustLevel.TRUSTED:
                                    existing_binding = binding
                                    logger.info(
                                        f"[Voice] Found existing trusted binding to convert: "
                                        f"binding_id={binding.id}, has_voice={binding.voice_signature_vector is not None}, "
                                        f"device_identifier={binding.device_identifier}"
                                    )
                                    # Update device_identifier to match the found binding for consistency
                                    device_identifier = binding.device_identifier
                                    break
                    
                    # Handle validate_only mode
                    if validate_only:
                        if existing_binding and existing_binding.voice_signature_vector:
                            # Has binding - validate voice matches
                            logger.info(
                                f"[Voice Verification] Validate-only mode: checking voice match for "
                                f"binding_id={existing_binding.id}, user_id={user_id_value}"
                            )
                            stored_vector = self._voice_verifier.deserialize_embedding(
                                existing_binding.voice_signature_vector
                            )
                            if stored_vector is not None:
                                logger.info(
                                    f"[Voice Verification] Stored vector deserialized for validation: "
                                    f"shape={stored_vector.shape}, current_voice_shape={voice_embedding.shape}"
                                )
                                matches, score = self._voice_verifier.matches(stored_vector, voice_embedding)
                                similarity_score = round(float(score), 4)
                                detail["similarityScore"] = similarity_score
                                
                                logger.info(
                                    f"[Voice Verification] Validation comparison result: "
                                    f"matches={matches}, similarity_score={similarity_score:.4f}, "
                                    f"binding_id={existing_binding.id}, user_id={user_id_value}"
                                )
                                
                                if not matches:
                                    logger.warning(
                                        f"[Voice Verification] Validation failed - voice mismatch: "
                                        f"score={similarity_score:.4f} (below threshold), "
                                        f"binding_id={existing_binding.id}, user_id={user_id_value}"
                                    )
                                    return AuthResult(
                                        success=False,
                                        reason="voice_mismatch",
                                        detail={
                                            "message": "Voice sample did not match stored signature.",
                                            "voicePhrase": VOICE_ENROLLMENT_PHRASE,
                                            "similarityScore": similarity_score,
                                        },
                                    )
                                logger.info(
                                    f"[Voice Verification] Validation passed: "
                                    f"similarity_score={similarity_score:.4f} (above threshold), "
                                    f"binding_id={existing_binding.id}, user_id={user_id_value}"
                                )
                            else:
                                logger.warning(
                                    f"[Voice Verification] Failed to deserialize stored voice vector for validation: "
                                    f"binding_id={existing_binding.id}, user_id={user_id_value}"
                                )
                        else:
                            # Log detailed information about why no voice binding was found
                            all_bindings_debug = list(list_device_bindings(session, user_id=user_id_value, include_revoked=True))
                            logger.info(
                                f"[Voice Verification] Validate-only mode: no existing voice binding found. "
                                f"Debug info: user_id={user_id_value}, device_identifier='{device_identifier}', "
                                f"total_bindings={len(all_bindings_debug)}, "
                                f"trusted_bindings={[b.id for b in all_bindings_debug if b.trust_level == DeviceTrustLevel.TRUSTED]}, "
                                f"voice_bindings={[b.id for b in all_bindings_debug if b.voice_signature_vector is not None]}, "
                                f"validation passed (first-time enrollment or binding not found)"
                            )
                        # Validation passed
                        detail["validated"] = True
                        if existing_binding:
                            detail["deviceBindingId"] = str(existing_binding.id)
                        return AuthResult(
                            success=True,
                            reason="validated",
                            detail=detail,
                            user_id=str(user_id_value),
                        )

                    # CRITICAL: Revoke ALL other bindings (password and voice) to ensure only ONE trusted device
                    # When switching from password to voice, password bindings should be replaced
                    all_bindings = list(list_device_bindings(session, user_id=user_id_value, include_revoked=True))
                    for other_binding in all_bindings:
                        if existing_binding and other_binding.id == existing_binding.id:
                            continue  # Skip current binding
                        # Revoke any non-revoked binding (both password and voice)
                        if other_binding.trust_level != DeviceTrustLevel.REVOKED:
                            logger.info(
                                f"[Voice] Revoking other binding to ensure single trusted device: "
                                f"binding_id={other_binding.id}, has_voice={other_binding.voice_signature_vector is not None}"
                            )
                            mark_device_binding_trust(
                                session, binding=other_binding, trust_level=DeviceTrustLevel.REVOKED
                            )
                            # Clear voice signature if it exists
                            if other_binding.voice_signature_vector is not None:
                                other_binding.voice_signature_hash = None
                                other_binding.voice_signature_vector = None
                            
                    # Create or update device binding
                    if existing_binding:
                        # Check if this is converting from password to voice binding
                        # Store OLD voice signature before we update it
                        old_voice_signature_vector = existing_binding.voice_signature_vector
                        had_voice_signature = old_voice_signature_vector is not None
                        
                        # Verify voice matches BEFORE updating (if binding already had voice signature)
                        if had_voice_signature:
                            logger.info(
                                f"[Voice Verification] Starting voice verification: "
                                f"binding_id={existing_binding.id}, user_id={user_id_value}, "
                                f"stored_vector_size={len(old_voice_signature_vector)} bytes"
                            )
                            stored_vector = self._voice_verifier.deserialize_embedding(
                                old_voice_signature_vector
                            )
                            if stored_vector is not None:
                                logger.info(
                                    f"[Voice Verification] Stored vector deserialized: "
                                    f"shape={stored_vector.shape}, current_voice_shape={voice_embedding.shape}"
                                )
                                matches, score = self._voice_verifier.matches(stored_vector, voice_embedding)
                                similarity_score = round(float(score), 4)
                                detail["similarityScore"] = similarity_score
                                
                                logger.info(
                                    f"[Voice Verification] Voice comparison result: "
                                    f"matches={matches}, similarity_score={similarity_score:.4f}, "
                                    f"binding_id={existing_binding.id}, user_id={user_id_value}"
                                )
                                
                                if not matches:
                                    logger.warning(
                                        f"[Voice Verification] Voice mismatch - authentication failed: "
                                        f"score={similarity_score:.4f} (below threshold), "
                                        f"binding_id={existing_binding.id}, user_id={user_id_value}"
                                    )
                                    return AuthResult(
                                        success=False,
                                        reason="voice_mismatch",
                                        detail={
                                            "bindingId": str(existing_binding.id),
                                            "message": "Voice sample did not match stored signature.",
                                            "voicePhrase": VOICE_ENROLLMENT_PHRASE,
                                            "similarityScore": similarity_score,
                                        },
                                    )
                                logger.info(
                                    f"[Voice Verification] Voice verified successfully: "
                                    f"similarity_score={similarity_score:.4f} (above threshold), "
                                    f"binding_id={existing_binding.id}, user_id={user_id_value}"
                                )
                            else:
                                logger.warning(
                                    f"[Voice Verification] Failed to deserialize stored voice vector: "
                                    f"binding_id={existing_binding.id}, user_id={user_id_value}"
                                )
                        else:
                            logger.info(
                                f"[Voice Verification] Skipping voice verification - binding has no stored voice signature "
                                f"(converting from password to voice): binding_id={existing_binding.id}"
                            )
                        
                        # Update existing binding
                        logger.info(
                            f"[Voice] Updating existing binding: binding_id={existing_binding.id}, "
                            f"converting_from_password={not had_voice_signature}"
                        )
                        existing_binding.voice_signature_hash = voice_hash
                        existing_binding.voice_signature_vector = voice_vector_bytes
                        existing_binding.fingerprint_hash = fingerprint_hash
                        existing_binding.platform = platform
                        existing_binding.device_label = device_label
                        existing_binding.last_verified_at = now
                        existing_binding.revoked_at = None
                        
                        if not had_voice_signature:
                            # Converting password binding to voice binding (first voice enrollment)
                            logger.info(
                                f"[Voice] Converting password binding to voice binding: "
                                f"binding_id={existing_binding.id}"
                            )
                            detail["firstVoiceEnrollment"] = True
                        
                        # Ensure binding is trusted
                        if existing_binding.trust_level != DeviceTrustLevel.TRUSTED:
                            mark_device_binding_trust(
                                session, binding=existing_binding, trust_level=DeviceTrustLevel.TRUSTED
                            )
                        
                        binding_id = str(existing_binding.id)
                        detail["deviceBindingId"] = binding_id
                        detail["enrolled"] = True
                    else:
                        # Create new binding
                        logger.info(
                            f"[Voice] Creating new binding: device_identifier={device_identifier}"
                        )
                        new_binding = create_device_binding(
                            session,
                            user_id=user_id_value,
                            device_identifier=device_identifier,
                            fingerprint_hash=fingerprint_hash,
                            registration_method="voice",
                            platform=platform,
                            device_label=device_label,
                            trust_level=DeviceTrustLevel.TRUSTED,
                            voice_signature_hash=voice_hash,
                            voice_signature_vector=voice_vector_bytes,
                        )
                        session.flush()
                        session.refresh(new_binding)
                        binding_id = str(new_binding.id)
                        detail["deviceBindingId"] = binding_id
                        detail["enrolled"] = True
                        detail["firstVoiceEnrollment"] = True
                        logger.info(
                            f"[Voice] New binding created: binding_id={binding_id}"
                        )
                
                    # Create session for voice login (same pattern as password login)
                    logger.info(
                        f"[Auth] Voice login complete, creating session: "
                        f"binding_id={binding_id}, user_id={user_id_value}"
                    )
                    
                    return self._create_session_for_voice_login(
                        session=session,
                        user=user,
                        user_id_value=user_id_value,
                        customer_number_value=customer_number_value,
                        device_identifier=device_identifier,
                        fingerprint_hash=fingerprint_hash,
                        binding_id=binding_id,
                        login_mode=login_mode,
                        detail=detail,
                        now=now,
                        tz=tz,
                    )
        except Exception as e:
            logger.error(
                f"[Auth] Exception during authentication: customer_number='{customer_number}', "
                f"login_mode='{login_mode}', error={type(e).__name__}: {str(e)}",
                exc_info=True
            )
            return AuthResult(success=False, reason="authentication_error")

    def _create_session_for_password_login(
        self,
        *,
        session,
        user,
        user_id_value: str,
        customer_number_value: str,
        device_identifier: str,
        fingerprint_hash: Optional[str],
        binding_id: str,
        login_mode: str,
        detail: dict,
        now: datetime,
        tz: ZoneInfo,
    ) -> AuthResult:
        """Create session for password login - completely isolated from voice login flow."""
        logger.info(
            f"[Auth] Creating session for password login: customer_number='{customer_number_value}', "
            f"user_id={user_id_value}, binding_id={binding_id}"
        )
        
        # CRITICAL: Clear ALL existing sessions for this user before creating a new one
        # This ensures only ONE active session exists per user at any time
        invalidated_count = invalidate_all_user_sessions(session, user_id_value)
        if invalidated_count > 0:
            logger.info(
                f"[Auth] Invalidated {invalidated_count} existing session(s) for user_id={user_id_value} "
                f"before creating new password login session"
            )
            # Flush invalidated sessions to ensure they're persisted
            session.flush()
        
        token = token_urlsafe(32)
        expires_at = now + timedelta(seconds=ACCESS_TOKEN_TTL_SECONDS)

        session_record = SessionModel(
            user_id=user_id_value,
            external_id=token,
            access_token=token,
            channel=TransactionChannel.SYSTEM,
            status=SessionStatus.ACTIVE,
            auth_level=AuthenticationLevel.FULL,
            device_fingerprint=device_identifier or fingerprint_hash,
            mfa_method="password+otp",
            started_at=now,
            last_activity_at=now,
            last_intent="login",
            token_expires_at=expires_at,
        )
        session.add(session_record)
        user.last_login_at = now
        
        # Flush to persist session_record
        # The session_scope will commit this transaction when exiting successfully
        session.flush()
        session.refresh(user)

        primary_branch = user.primary_branch
        accounts = [
            {
                "accountNumber": account.account_number,
                "type": account.account_type.value.replace("_", " ").title(),
                "balance": f"{account.currency_code} {float(account.available_balance):,.2f}",
                "currency": account.currency_code,
            }
            for account in user.accounts
        ]

        upcoming_reminder = None
        if user.reminders:
            reminder_obj = min(user.reminders, key=lambda r: r.remind_at)
            upcoming_reminder = {
                "label": reminder_obj.message,
                "date": reminder_obj.remind_at,
            }

        profile = {
            "id": str(user.id),
            "customerId": customer_number_value,
            "fullName": f"{user.first_name} {user.last_name}",
            "segment": user.risk_segment.title(),
            "branch": {
                "name": primary_branch.name if primary_branch else "Sun National Bank",
                "city": primary_branch.city if primary_branch else "Bharat",
            },
            "accountSummary": accounts,
            "preferredLanguage": user.preferred_language,
            "lastLogin": (
                user.last_login_at.isoformat() if user.last_login_at else None
            ),
            "nextReminder": upcoming_reminder,
        }

        if binding_id:
            detail.setdefault("deviceBindingId", binding_id)
        detail.setdefault("passwordDeviceBinding", True)

        logger.info(
            f"[Auth] Password login authentication successful: customer_number='{customer_number_value}', "
            f"has_profile={profile is not None}, has_token={bool(token)}"
        )
        return AuthResult(
            success=True,
            user_profile=profile,
            access_token=token,
            expires_in=ACCESS_TOKEN_TTL_SECONDS,
            detail=detail or None,
        )

    def _create_session_for_voice_login(
        self,
        *,
        session,
        user,
        user_id_value: str,
        customer_number_value: str,
        device_identifier: str,
        fingerprint_hash: Optional[str],
        binding_id: str,
        login_mode: str,
        detail: dict,
        now: datetime,
        tz: ZoneInfo,
    ) -> AuthResult:
        """Create session for voice login - follows exact same pattern as password login."""
        logger.info(
            f"[Auth] Creating session for voice login: customer_number='{customer_number_value}', "
            f"user_id={user_id_value}, binding_id={binding_id}"
        )
        
        # Clear ALL existing sessions for this user before creating a new one
        invalidated_count = invalidate_all_user_sessions(session, user_id_value)
        if invalidated_count > 0:
            logger.info(
                f"[Auth] Invalidated {invalidated_count} existing session(s) for user_id={user_id_value} "
                f"before creating new voice login session"
            )
            session.flush()
        
        # Generate token and create session record
        token = token_urlsafe(32)
        expires_at = now + timedelta(seconds=ACCESS_TOKEN_TTL_SECONDS)

        session_record = SessionModel(
            user_id=user_id_value,
            external_id=token,
            access_token=token,
            channel=TransactionChannel.VOICE,
            status=SessionStatus.ACTIVE,
            auth_level=AuthenticationLevel.FULL,
            device_fingerprint=device_identifier or fingerprint_hash,
            mfa_method="voice+otp",
            started_at=now,
            last_activity_at=now,
            last_intent="login",
            token_expires_at=expires_at,
        )
        session.add(session_record)
        user.last_login_at = now
        
        # Flush to persist session_record
        session.flush()
        session.refresh(user)

        # Access user relationships (same as password login)
        primary_branch = user.primary_branch
        accounts = [
            {
                "accountNumber": account.account_number,
                "type": account.account_type.value.replace("_", " ").title(),
                "balance": f"{account.currency_code} {float(account.available_balance):,.2f}",
                "currency": account.currency_code,
            }
            for account in user.accounts
        ]

        upcoming_reminder = None
        if user.reminders:
            reminder_obj = min(user.reminders, key=lambda r: r.remind_at)
            upcoming_reminder = {
                "label": reminder_obj.message,
                "date": reminder_obj.remind_at,
            }
        
        profile = {
            "id": str(user.id),
            "customerId": customer_number_value,
            "fullName": f"{user.first_name} {user.last_name}",
            "segment": user.risk_segment.title(),
            "branch": {
                "name": primary_branch.name if primary_branch else "Sun National Bank",
                "city": primary_branch.city if primary_branch else "Bharat",
            },
            "accountSummary": accounts,
            "preferredLanguage": user.preferred_language,
            "lastLogin": (
                user.last_login_at.isoformat() if user.last_login_at else None
            ),
            "nextReminder": upcoming_reminder,
        }

        if binding_id:
            detail.setdefault("deviceBindingId", binding_id)
        detail.setdefault("voiceLogin", True)

        logger.info(
            f"[Auth] Voice login authentication successful: customer_number='{customer_number_value}', "
            f"has_profile={profile is not None}, has_token={bool(token)}"
        )
        return AuthResult(
            success=True,
            user_profile=profile,
            access_token=token,
            expires_in=ACCESS_TOKEN_TTL_SECONDS,
            detail=detail or None,
        )

    def validate_token(self, *, token: str) -> AuthenticatedSession:
        error: SessionValidationError | None = None
        result: AuthenticatedSession | None = None

        with session_scope(self._session_factory) as session:
            session_record = get_session_by_token(session, token)
            tz = ZoneInfo("Asia/Kolkata")
            now = datetime.now(tz)

            if session_record is None:
                logger.warning(
                    f"[Auth] Token validation failed - session not found: token={token[:10]}... "
                    f"(length={len(token)}), checking database..."
                )
                # Debug: Try to find any sessions for this token pattern
                from sqlalchemy import select
                all_sessions = session.execute(
                    select(SessionModel).where(SessionModel.access_token.like(f"{token[:10]}%"))
                ).scalars().all()
                logger.warning(
                    f"[Auth] Found {len(all_sessions)} sessions with similar token prefix"
                )
                error = SessionValidationError(
                    code="session_invalid",
                    message="Invalid or expired access token.",
                )
            elif session_record.status != SessionStatus.ACTIVE:
                error = SessionValidationError(
                    code="session_inactive",
                    message="Session is no longer active. Please sign in again.",
                )
            elif session_record.token_expires_at is None:
                error = SessionValidationError(
                    code="session_invalid",
                    message="Session metadata is incomplete. Please sign in again.",
                )
            else:
                expires_at = session_record.token_expires_at
                if expires_at is not None and expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=tz)

                if expires_at is not None and expires_at < now:
                    session_record.status = SessionStatus.EXPIRED
                    session_record.ended_at = now
                    session.flush()
                    error = SessionValidationError(
                        code="session_expired",
                        message="Your session has expired. Please sign in again.",
                    )
                else:
                    last_activity = session_record.last_activity_at or session_record.started_at
                    if last_activity is not None:
                        if last_activity.tzinfo is None:
                            last_activity = last_activity.replace(tzinfo=tz)
                        if (now - last_activity) > SESSION_INACTIVITY_TIMEOUT:
                            session_record.status = SessionStatus.EXPIRED
                            session_record.ended_at = now
                            session.flush()
                            error = SessionValidationError(
                                code="session_timeout",
                                message="Your session ended due to inactivity. Please sign in again.",
                            )
                    if error is None:
                        session_record.last_activity_at = now
                        session.flush()
                        user = session_record.user
                        result = AuthenticatedSession(
                            user_id=str(user.id),
                            customer_number=user.customer_number,
                            session_id=str(session_record.id),
                            access_token=session_record.access_token,
                            expires_at=expires_at,
                        )

        if error is not None:
            raise error
        if result is None:
            raise SessionValidationError(
                code="session_invalid",
                message="Invalid or expired access token.",
            )
        return result


__all__ = ["AuthService", "AuthResult", "AuthenticatedSession", "ACCESS_TOKEN_TTL_SECONDS"]


