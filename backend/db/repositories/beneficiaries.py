"""Repository helpers for managing customer beneficiaries."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from ..models import Account, Beneficiary
from ..utils.enums import BeneficiaryStatus

IST = ZoneInfo("Asia/Kolkata")


def _base_query(user_id, include_blocked: bool) -> Select:
    stmt = select(Beneficiary).where(Beneficiary.user_id == user_id)
    if not include_blocked:
        stmt = stmt.where(Beneficiary.status != BeneficiaryStatus.BLOCKED)
    return stmt.order_by(Beneficiary.added_at.desc())


def list_beneficiaries(session: Session, *, user_id, include_blocked: bool = False):
    """Return beneficiaries for a user ordered by recent additions."""

    stmt = _base_query(user_id, include_blocked)
    return session.execute(stmt).scalars().all()


def get_beneficiary_by_id(session: Session, *, beneficiary_id, user_id=None) -> Optional[Beneficiary]:
    """Fetch a beneficiary by UUID with optional ownership check."""

    stmt = select(Beneficiary).where(Beneficiary.id == beneficiary_id)
    if user_id is not None:
        stmt = stmt.where(Beneficiary.user_id == user_id)
    return session.execute(stmt).scalar_one_or_none()


def get_beneficiary_by_account_number(session: Session, *, user_id, account_number) -> Optional[Beneficiary]:
    stmt = select(Beneficiary).where(
        Beneficiary.user_id == user_id,
        Beneficiary.account_number == account_number,
    )
    return session.execute(stmt).scalar_one_or_none()


def create_beneficiary(
    session: Session,
    *,
    user_id,
    account_number: str,
    display_name: str,
    bank_name: Optional[str] = None,
    ifsc_code: Optional[str] = None,
) -> Beneficiary:
    """Register a new beneficiary if the account exists and is unique for the user."""

    account = session.execute(
        select(Account).where(Account.account_number == account_number)
    ).scalar_one_or_none()
    if account is None:
        raise ValueError("account_not_found")

    existing = get_beneficiary_by_account_number(
        session, user_id=user_id, account_number=account_number
    )
    now = datetime.now(IST)

    if existing:
        if existing.status == BeneficiaryStatus.BLOCKED:
            existing.status = BeneficiaryStatus.ACTIVE
            existing.display_name = display_name
            existing.bank_name = bank_name or existing.bank_name
            existing.ifsc_code = ifsc_code or existing.ifsc_code
            existing.removed_at = None
            existing.added_at = now
            existing.verified_at = existing.verified_at or now
            existing.last_used_at = None
            return existing
        raise ValueError("beneficiary_exists")

    resolved_bank = bank_name or (account.branch.name if account.branch else "Sun National Bank")
    resolved_ifsc = ifsc_code or (account.branch.ifsc_code if account.branch else "SUNB0000000")

    beneficiary = Beneficiary(
        user_id=user_id,
        account_id=account.id,
        display_name=display_name,
        account_number=account.account_number,
        bank_name=resolved_bank,
        ifsc_code=resolved_ifsc,
        status=BeneficiaryStatus.ACTIVE,
        added_at=now,
        verified_at=now,
    )
    session.add(beneficiary)
    return beneficiary


def deactivate_beneficiary(session: Session, *, beneficiary: Beneficiary) -> Beneficiary:
    """Soft delete a beneficiary per compliance requirements."""

    beneficiary.status = BeneficiaryStatus.BLOCKED
    beneficiary.removed_at = datetime.now(IST)
    return beneficiary


def mark_beneficiary_used(session: Session, *, beneficiary: Beneficiary) -> None:
    beneficiary.last_used_at = datetime.now(IST)
    if beneficiary.verified_at is None:
        beneficiary.verified_at = beneficiary.last_used_at
