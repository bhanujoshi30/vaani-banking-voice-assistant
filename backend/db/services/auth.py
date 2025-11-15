"""Authentication service bridging repositories and security helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
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
    access_token: str
    expires_at: datetime


ACCESS_TOKEN_TTL_SECONDS = 60 * 30  # 30 minutes


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

            now = datetime.now(timezone.utc)
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

    def validate_token(self, *, token: str) -> AuthenticatedSession | None:
        with session_scope(self._session_factory) as session:
            session_record = get_session_by_token(session, token)
            if (
                session_record is None
                or session_record.status != SessionStatus.ACTIVE
                or session_record.token_expires_at is None
            ):
                return None

            expires_at = session_record.token_expires_at
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)

            if expires_at < datetime.now(timezone.utc):
                return None

            user = session_record.user
            return AuthenticatedSession(
                user_id=str(user.id),
                customer_number=user.customer_number,
                access_token=session_record.access_token,
                expires_at=expires_at,
            )


__all__ = ["AuthService", "AuthResult", "AuthenticatedSession", "ACCESS_TOKEN_TTL_SECONDS"]


