"""Beneficiary model capturing trusted payees per RBI guidance."""

from __future__ import annotations

import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship

from ..base import Base
from ..utils.enums import BeneficiaryStatus
from ..utils.types import GUID


class Beneficiary(Base):
    """Represents a trusted beneficiary account registered by a customer."""

    __tablename__ = "beneficiaries"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "account_number",
            name="uq_beneficiaries_user_account",
        ),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    account_id = Column(GUID(), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    display_name = Column(String(120), nullable=False)
    account_number = Column(String(20), nullable=False)
    bank_name = Column(String(120), nullable=False, default="Sun National Bank")
    ifsc_code = Column(String(16), nullable=False)
    status = Column(
        Enum(BeneficiaryStatus, name="beneficiary_status", native_enum=False),
        nullable=False,
        default=BeneficiaryStatus.ACTIVE,
    )
    added_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")),
    )
    verified_at = Column(DateTime(timezone=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    removed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="beneficiaries")
    account = relationship("Account", back_populates="beneficiaries")


__all__ = ["Beneficiary"]
