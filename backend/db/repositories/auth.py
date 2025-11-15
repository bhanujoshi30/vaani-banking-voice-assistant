"""Authentication-related data access helpers."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Session as SessionModel, User


def get_user_by_customer_number(session: Session, customer_number: str) -> User | None:
    """Return the user matching the given customer number, if any."""

    stmt = select(User).where(User.customer_number == customer_number)
    return session.execute(stmt).scalars().first()


def get_session_by_token(session: Session, token: str) -> SessionModel | None:
    """Return the active session matching an access token, if any."""

    stmt = select(SessionModel).where(SessionModel.access_token == token)
    return session.execute(stmt).scalars().first()


__all__ = ["get_user_by_customer_number", "get_session_by_token"]


