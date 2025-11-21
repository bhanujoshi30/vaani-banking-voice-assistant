"""Authentication-related data access helpers."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Session as SessionModel, User
from ..utils.enums import SessionStatus

IST = ZoneInfo("Asia/Kolkata")


def get_user_by_customer_number(session: Session, customer_number: str) -> User | None:
    """Return the user matching the given customer number, if any."""
    # Trim whitespace from customer number for lookup
    customer_number_clean = customer_number.strip() if customer_number else customer_number
    stmt = select(User).where(User.customer_number == customer_number_clean)
    return session.execute(stmt).scalars().first()


def get_session_by_token(session: Session, token: str) -> SessionModel | None:
    """Return the active session matching an access token, if any."""

    stmt = select(SessionModel).where(SessionModel.access_token == token)
    return session.execute(stmt).scalars().first()


def invalidate_all_user_sessions(session: Session, user_id) -> int:
    """
    Invalidate all active sessions for a user.
    Returns the number of sessions invalidated.
    """
    now = datetime.now(IST)
    stmt = (
        select(SessionModel)
        .where(SessionModel.user_id == user_id)
        .where(SessionModel.status == SessionStatus.ACTIVE)
    )
    active_sessions = session.execute(stmt).scalars().all()
    count = 0
    for session_record in active_sessions:
        session_record.status = SessionStatus.TERMINATED
        session_record.ended_at = now
        count += 1
    return count


__all__ = ["get_user_by_customer_number", "get_session_by_token", "invalidate_all_user_sessions"]


