"""Account transaction ledger entries."""

from __future__ import annotations

import uuid

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship

from sqlalchemy.sql import func

from ..base import Base
from ..utils.enums import TransactionChannel, TransactionStatus, TransactionType
from ..utils.types import GUID


class Transaction(Base):
    """Represents a financial transaction against a bank account."""

    __tablename__ = "transactions"
    __table_args__ = (
        Index("ix_transactions_account_occurred", "account_id", "occurred_at"),
        Index("ix_transactions_reference", "reference_id"),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, nullable=False)
    account_id = Column(
        GUID(), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
    )
    session_id = Column(
        GUID(), ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True
    )
    transaction_type = Column(
        Enum(TransactionType, name="transaction_type", native_enum=False), nullable=False
    )
    status = Column(
        Enum(TransactionStatus, name="transaction_status", native_enum=False),
        nullable=False,
        default=TransactionStatus.PENDING,
    )
    channel = Column(
        Enum(TransactionChannel, name="transaction_channel", native_enum=False),
        nullable=False,
        default=TransactionChannel.SYSTEM,
    )
    amount = Column(Numeric(precision=18, scale=2), nullable=False)
    currency_code = Column(String(3), nullable=False, default="INR")
    description = Column(String(255), nullable=True)
    reference_id = Column(String(36), nullable=True)
    counterparty_account = Column(String(32), nullable=True)
    counterparty_name = Column(String(120), nullable=True)
    occurred_at = Column(DateTime(timezone=True), default=func.now, nullable=False)
    value_date = Column(DateTime(timezone=True), nullable=True)

    account = relationship("Account", back_populates="transactions")
    session = relationship("Session", back_populates="transactions")


__all__ = ["Transaction"]


