"""Transaction orchestration utilities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Iterable, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Account, Transaction
from ..utils.enums import TransactionChannel, TransactionStatus, TransactionType
from .accounts import get_account_by_number


@dataclass(frozen=True)
class TransferResult:
    debit_transaction: Transaction
    credit_transaction: Transaction


def execute_internal_transfer(
    session: Session,
    *,
    source_account_number: str,
    destination_account_number: str,
    amount: Decimal | float | int,
    currency_code: str = "INR",
    description: Optional[str] = None,
    initiated_session_id: Optional[str] = None,
    reference_id: Optional[str] = None,
    channel: TransactionChannel = TransactionChannel.VOICE,
) -> TransferResult:
    """
    Perform an intra-bank transfer between two Sun National Bank accounts.

    Validates available balance, ensures currency alignment, and creates
    corresponding debit and credit ledger entries.
    """

    amount_decimal = Decimal(str(amount)).quantize(Decimal("0.01"))
    if amount_decimal <= Decimal("0.00"):
        raise ValueError("Transfer amount must be positive.")

    source_account = get_account_by_number(session, source_account_number, for_update=True)
    if source_account is None:
        raise ValueError(f"Source account {source_account_number} not found.")

    destination_account = get_account_by_number(
        session, destination_account_number, for_update=True
    )
    if destination_account is None:
        raise ValueError(f"Destination account {destination_account_number} not found.")

    if source_account.currency_code != currency_code:
        raise ValueError("Source account currency mismatch.")

    if destination_account.currency_code != currency_code:
        raise ValueError("Destination account currency mismatch.")

    if source_account.available_balance < amount_decimal:
        raise ValueError("Insufficient funds for transfer.")

    # Apply debits and credits.
    source_account.balance -= amount_decimal
    source_account.available_balance -= amount_decimal
    destination_account.balance += amount_decimal
    destination_account.available_balance += amount_decimal

    occurrence_time = datetime.now(timezone.utc)

    debit_txn = Transaction(
        account_id=source_account.id,
        session_id=initiated_session_id,
        transaction_type=TransactionType.TRANSFER_OUT,
        status=TransactionStatus.SETTLED,
        channel=channel,
        amount=amount_decimal,
        currency_code=currency_code,
        description=description or f"Transfer to {destination_account.account_number}",
        reference_id=reference_id,
        counterparty_account=destination_account.account_number,
        counterparty_name=f"{destination_account.user.first_name} {destination_account.user.last_name}",
        occurred_at=occurrence_time,
    )

    credit_txn = Transaction(
        account_id=destination_account.id,
        session_id=initiated_session_id,
        transaction_type=TransactionType.TRANSFER_IN,
        status=TransactionStatus.SETTLED,
        channel=channel,
        amount=amount_decimal,
        currency_code=currency_code,
        description=description or f"Transfer from {source_account.account_number}",
        reference_id=reference_id,
        counterparty_account=source_account.account_number,
        counterparty_name=f"{source_account.user.first_name} {source_account.user.last_name}",
        occurred_at=occurrence_time,
    )

    session.add_all([debit_txn, credit_txn])

    return TransferResult(debit_transaction=debit_txn, credit_transaction=credit_txn)


def get_transaction_history(
    session: Session,
    *,
    account_id,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 50,
) -> Iterable[Transaction]:
    """
    Retrieve reverse-chronological transaction history for an account.
    """

    stmt = select(Transaction).where(Transaction.account_id == account_id)

    if start_date is not None:
        stmt = stmt.where(Transaction.occurred_at >= start_date)
    if end_date is not None:
        stmt = stmt.where(Transaction.occurred_at <= end_date)

    stmt = stmt.order_by(Transaction.occurred_at.desc()).limit(limit)

    return session.execute(stmt).scalars().all()


def get_transaction_by_reference(session: Session, reference_id: str) -> Optional[Transaction]:
    """Lookup a transaction using an external reference id."""

    stmt = select(Transaction).where(Transaction.reference_id == reference_id)
    return session.execute(stmt).scalars().first()


__all__ = [
    "TransferResult",
    "execute_internal_transfer",
    "get_transaction_history",
    "get_transaction_by_reference",
]


