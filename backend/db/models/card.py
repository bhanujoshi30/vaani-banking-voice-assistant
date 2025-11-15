"""Payment card representation."""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import Column, Date, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship

from ..base import Base
from ..utils.enums import CardStatus, CardType
from ..utils.types import GUID


class Card(Base):
    """Represents a debit/credit card issued to a customer."""

    __tablename__ = "cards"
    __table_args__ = (
        UniqueConstraint("card_token", name="uq_cards_token"),
        UniqueConstraint("masked_number", "user_id", name="uq_cards_masked_per_user"),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    account_id = Column(
        GUID(), ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True
    )
    card_type = Column(Enum(CardType, name="card_type", native_enum=False), nullable=False)
    card_token = Column(String(64), nullable=False)  # tokenised PAN
    masked_number = Column(String(19), nullable=False)
    network = Column(String(20), nullable=False)
    status = Column(Enum(CardStatus, name="card_status", native_enum=False), nullable=False, default=CardStatus.ACTIVE)
    issued_on = Column(Date, nullable=False, default=date.today)
    expiry_month = Column(String(2), nullable=False)
    expiry_year = Column(String(4), nullable=False)

    user = relationship("User", back_populates="cards")
    account = relationship("Account", back_populates="cards")


__all__ = ["Card"]


