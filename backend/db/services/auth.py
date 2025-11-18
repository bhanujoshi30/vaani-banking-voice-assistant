"""Authentication service bridging repositories and security helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from secrets import token_urlsafe
from typing import Optional

from sqlalchemy.orm import Session

from ..models import Session as SessionModel
from ..utils.enums import AuthenticationLevel, SessionStatus, TransactionChannel
from ..engine import session_scope
from ..repositories.auth import get_session_by_token, get_user_by_customer_number
from ..utils.security import verify_password


@dataclass
class AuthResult:
    success: bool
    reason: Optional[str] = None
    user_profile: Optional[dict] = None
    access_token: Optional[str] = None
    expires_in: Optional[int] = None


@dataclass
class AuthenticatedSession:
    user_id: str
    customer_number: str
    session_id: str
    access_token: str
    expires_at: datetime


ACCESS_TOKEN_TTL_SECONDS = 60 * 30  # 30 minutes
SESSION_INACTIVITY_TIMEOUT = timedelta(minutes=5)  # RBI-recommended inactivity threshold


class SessionValidationError(Exception):
    """Represents an invalid or expired session state."""

    def __init__(self, *, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class AuthService:
    """Provides user authentication and profile retrieval."""

    def __init__(self, session_factory):
        self._session_factory = session_factory

    def authenticate(self, *, customer_number: str, password: str) -> AuthResult:
        with session_scope(self._session_factory) as session:
            user = get_user_by_customer_number(session, customer_number)
            if user is None:
                return AuthResult(success=False, reason="invalid_credentials")

            if not verify_password(password, user.password_hash):
                return AuthResult(success=False, reason="invalid_credentials")

            now = datetime.now(ZoneInfo("Asia/Kolkata"))
            token = token_urlsafe(32)
            expires_at = now + timedelta(seconds=ACCESS_TOKEN_TTL_SECONDS)

            session_record = SessionModel(
                user_id=user.id,
                external_id=token,
                access_token=token,
                channel=TransactionChannel.VOICE,
                status=SessionStatus.ACTIVE,
                auth_level=AuthenticationLevel.FULL,
                device_fingerprint=None,
                mfa_method="password+voice",
                started_at=now,
                last_activity_at=now,
                last_intent="login",
                token_expires_at=expires_at,
            )
            session.add(session_record)
            user.last_login_at = now

            # Build profile payload
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
                "id": str(user.id),  # Add UUID for AI backend
                "customerId": user.customer_number,
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

            return AuthResult(
                success=True,
                user_profile=profile,
                access_token=token,
                expires_in=ACCESS_TOKEN_TTL_SECONDS,
            )

    def validate_token(self, *, token: str) -> AuthenticatedSession:
        error: SessionValidationError | None = None
        result: AuthenticatedSession | None = None

        with session_scope(self._session_factory) as session:
            session_record = get_session_by_token(session, token)
            tz = ZoneInfo("Asia/Kolkata")
            now = datetime.now(tz)

            if session_record is None:
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


