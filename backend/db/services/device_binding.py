"""Device binding domain service."""

from __future__ import annotations

import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional

from ..engine import session_scope

logger = logging.getLogger(__name__)
from ..repositories import (
    create_device_binding,
    get_device_binding_by_id,
    get_device_binding_for_device,
    list_device_bindings,
    mark_device_binding_trust,
)
from ..repositories.auth import invalidate_all_user_sessions
from ..utils.enums import DeviceTrustLevel

IST = ZoneInfo("Asia/Kolkata")


def _serialize_binding(binding) -> dict:
    return {
        "id": str(binding.id),
        "deviceIdentifier": binding.device_identifier,
        "registrationMethod": binding.registration_method,
        "platform": binding.platform,
        "deviceLabel": binding.device_label,
        "trustLevel": binding.trust_level.value,
        # Only consider voice signature present if voice_signature_vector exists
        # voice_signature_hash alone (from seeded data) doesn't count as actual voice enrollment
        "voiceSignaturePresent": bool(binding.voice_signature_vector),
        "lastVerifiedAt": binding.last_verified_at.isoformat() if binding.last_verified_at else None,
        "revokedAt": binding.revoked_at.isoformat() if binding.revoked_at else None,
        "createdAt": binding.created_at.isoformat() if binding.created_at else None,
        "updatedAt": binding.updated_at.isoformat() if binding.updated_at else None,
    }


class DeviceBindingService:
    """Encapsulates CRUD operations for trusted device bindings."""

    def __init__(self, session_factory):
        self._session_factory = session_factory

    def list_bindings(self, *, user_id) -> list[dict]:
        with session_scope(self._session_factory) as session:
            bindings = list_device_bindings(session, user_id=user_id)
            # Enforce strict one trusted device rule - only return the most recent trusted binding
            trusted_bindings = [b for b in bindings if b.trust_level == DeviceTrustLevel.TRUSTED]
            if len(trusted_bindings) > 1:
                # If multiple trusted bindings exist, revoke all except the most recent one
                trusted_bindings.sort(key=lambda b: b.last_verified_at or b.created_at, reverse=True)
                for binding in trusted_bindings[1:]:
                    mark_device_binding_trust(session, binding=binding, trust_level=DeviceTrustLevel.REVOKED)
                    binding.voice_signature_hash = None
                    binding.voice_signature_vector = None
                session.flush()
            return [_serialize_binding(binding) for binding in bindings]

    def register_or_refresh_binding(
        self,
        *,
        user_id,
        device_identifier: str,
        fingerprint_hash: str,
        registration_method: str,
        platform: Optional[str] = None,
        device_label: Optional[str] = None,
        voice_signature_hash: Optional[str] = None,
        voice_signature_vector: Optional[bytes] = None,
    ) -> dict:
        with session_scope(self._session_factory) as session:
            # First try to find binding with same device_identifier
            existing = get_device_binding_for_device(
                session, user_id=user_id, device_identifier=device_identifier
            )
            
            # If not found, check for ANY existing trusted binding (for password->voice conversion)
            # This ensures we replace password bindings when adding voice through the endpoint
            if not existing:
                all_bindings = list(list_device_bindings(session, user_id=user_id, include_revoked=False))
                # Find the first trusted binding (could be password or voice)
                for binding in all_bindings:
                    if binding.trust_level == DeviceTrustLevel.TRUSTED:
                        existing = binding
                        logger.info(
                            f"[Device Binding] Found existing trusted binding to convert: "
                            f"binding_id={binding.id}, has_voice={binding.voice_signature_vector is not None}, "
                            f"old_device_identifier={binding.device_identifier}, "
                            f"new_device_identifier={device_identifier}"
                        )
                        # Update device_identifier to match the new one
                        break
            
            # STRICT RULE: Revoke ALL other bindings (including revoked ones) to ensure only one active binding exists
            # This enforces the rule: one user = one trusted device
            all_bindings = list(list_device_bindings(session, user_id=user_id, include_revoked=True))
            for other_binding in all_bindings:
                if existing and other_binding.id == existing.id:
                    continue  # Skip the current binding
                if other_binding.trust_level != DeviceTrustLevel.REVOKED:
                    mark_device_binding_trust(
                        session, binding=other_binding, trust_level=DeviceTrustLevel.REVOKED
                    )
                    # Clear voice signature when revoking - user must re-enroll voice
                    other_binding.voice_signature_hash = None
                    other_binding.voice_signature_vector = None
            
            if existing:
                # Check if this is converting from password to voice binding
                had_voice_signature = existing.voice_signature_vector is not None
                converting_from_password = not had_voice_signature and voice_signature_vector is not None
                
                # Update all fields including voice signature and device_identifier
                # Update device_identifier if it changed (e.g., password-{id} -> voice-{id} or browser fingerprint)
                if existing.device_identifier != device_identifier:
                    logger.info(
                        f"[Device Binding] Updating device_identifier: "
                        f"old='{existing.device_identifier}' -> new='{device_identifier}'"
                    )
                    existing.device_identifier = device_identifier
                
                existing.fingerprint_hash = fingerprint_hash
                existing.registration_method = registration_method
                existing.platform = platform
                existing.device_label = device_label
                
                # Always update voice signature if provided (important for re-binding)
                if voice_signature_hash is not None:
                    existing.voice_signature_hash = voice_signature_hash
                if voice_signature_vector is not None:
                    existing.voice_signature_vector = voice_signature_vector
                
                # Reset revoked status and update timestamps
                existing.last_verified_at = datetime.now(IST)
                existing.revoked_at = None  # Clear revoked_at when re-binding
                
                # Restore trust level to TRUSTED (important for re-binding after revocation)
                mark_device_binding_trust(
                    session, binding=existing, trust_level=DeviceTrustLevel.TRUSTED
                )
                
                if converting_from_password:
                    logger.info(
                        f"[Device Binding] Converting password binding to voice binding: "
                        f"binding_id={existing.id}"
                    )
                
                binding = existing
            else:
                # Create new binding
                binding = create_device_binding(
                    session,
                    user_id=user_id,
                    device_identifier=device_identifier,
                    fingerprint_hash=fingerprint_hash,
                    registration_method=registration_method,
                    platform=platform,
                    device_label=device_label,
                    trust_level=DeviceTrustLevel.TRUSTED,
                    voice_signature_hash=voice_signature_hash,
                    voice_signature_vector=voice_signature_vector,
                )
            session.flush()
            session.refresh(binding)
            return _serialize_binding(binding)

    def revoke_binding(self, *, binding_id) -> Optional[dict]:
        with session_scope(self._session_factory) as session:
            binding = get_device_binding_by_id(session, binding_id)
            if binding is None:
                return None
            
            # Check if this is the only binding (trusted or revoked) for this user
            # If it's the only binding, revoking it means the user has no trusted device
            all_bindings = list(list_device_bindings(session, user_id=binding.user_id, include_revoked=True))
            trusted_bindings = [b for b in all_bindings if b.trust_level == DeviceTrustLevel.TRUSTED]
            # Check if this is the only trusted binding, OR if it's the only binding overall
            is_only_trusted_binding = len(trusted_bindings) == 1 and trusted_bindings[0].id == binding.id
            is_only_binding_overall = len(all_bindings) == 1 and all_bindings[0].id == binding.id
            # Show logout if it's the only trusted binding OR the only binding overall
            should_force_logout = is_only_trusted_binding or is_only_binding_overall
            
            # Revoke the binding
            mark_device_binding_trust(
                session, binding=binding, trust_level=DeviceTrustLevel.REVOKED
            )
            # Clear voice signature when revoking - user must re-enroll voice
            had_voice_signature = binding.voice_signature_vector is not None
            binding.voice_signature_hash = None
            binding.voice_signature_vector = None
            if had_voice_signature:
                logger.info(
                    f"[Device Binding] Voice signature cleared for revoked binding: "
                    f"binding_id={binding_id}, user_id={binding.user_id}"
                )
            
            # If this was the only trusted binding (or only binding overall), invalidate all user sessions
            if should_force_logout:
                invalidated_count = invalidate_all_user_sessions(session, binding.user_id)
                logger.info(
                    f"[Device Binding] Revoked only trusted binding, invalidated {invalidated_count} sessions: "
                    f"binding_id={binding_id}, user_id={binding.user_id}"
                )
            
            session.flush()
            session.refresh(binding)
            result = _serialize_binding(binding)
            # Add flag to indicate logout is required
            if should_force_logout:
                result["logoutRequired"] = True
            return result

    def touch_binding(self, *, binding_id) -> Optional[dict]:
        """Refresh last_verified_at timestamp after successful voice validation."""
        with session_scope(self._session_factory) as session:
            binding = get_device_binding_by_id(session, binding_id)
            if binding is None:
                return None
            binding.last_verified_at = datetime.now(IST)
            session.flush()
            session.refresh(binding)
            return _serialize_binding(binding)


__all__ = ["DeviceBindingService"]

