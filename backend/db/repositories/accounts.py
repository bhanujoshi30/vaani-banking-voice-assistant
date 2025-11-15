"""Account-centric data access utilities."""

from __future__ import annotations

from typing import Iterable, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Account, User


def get_account_by_id(
    session: Session, account_id, *, user_id=None, for_update: bool = False
) -> Optional[Account]:
    """
    Fetch an account by its primary key, optionally ensuring user ownership.
    """

    stmt = select(Account).where(Account.id == account_id)
    if user_id is not None:
        stmt = stmt.where(Account.user_id == user_id)
    if for_update:
        stmt = stmt.with_for_update()
    return session.execute(stmt).scalars().first()


def get_account_by_number(
    session: Session, account_number: str, *, for_update: bool = False
) -> Optional[Account]:
    """
    Fetch an account by its unique account number.

    Parameters:
        session: Database session.
        account_number: Core banking account number.
        for_update: Apply row-level locking where supported.
    """

    stmt = select(Account).where(Account.account_number == account_number)
    if for_update:
        stmt = stmt.with_for_update()
    return session.execute(stmt).scalars().first()


def list_accounts_for_user(session: Session, user_id) -> Iterable[Account]:
    """Return all active accounts for a user."""

    stmt = (
        select(Account)
        .where(Account.user_id == user_id)
        .order_by(Account.created_at.asc())
    )
    return session.execute(stmt).scalars().all()


def get_account_balance(session: Session, account_number: str):
    """Return account balance and currency details."""

    account = get_account_by_number(session, account_number)
    if account is None:
        raise ValueError(f"Account {account_number} not found")
    return {
        "account_number": account.account_number,
        "currency": account.currency_code,
        "ledger_balance": account.balance,
        "available_balance": account.available_balance,
        "status": account.status.value,
    }


def get_user_profile(session: Session, user_id) -> Optional[User]:
    """Fetch a user's core profile."""

    stmt = select(User).where(User.id == user_id)
    return session.execute(stmt).scalars().first()


__all__ = [
    "get_account_by_id",
    "get_account_by_number",
    "list_accounts_for_user",
    "get_account_balance",
    "get_user_profile",
]


