"""Reminder scheduling repository."""

from __future__ import annotations

from datetime import datetime
from typing import Iterable, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Reminder
from ..utils.enums import ReminderStatus, ReminderType


def create_reminder(
    session: Session,
    *,
    user_id,
    remind_at: datetime,
    message: str,
    reminder_type: ReminderType = ReminderType.BILL_PAYMENT,
    account_id=None,
    channel: str = "voice",
    recurrence_rule: Optional[str] = None,
) -> Reminder:
    """Persist a new reminder for proactive nudging."""

    reminder = Reminder(
        user_id=user_id,
        account_id=account_id,
        reminder_type=reminder_type,
        status=ReminderStatus.PENDING,
        message=message,
        remind_at=remind_at,
        channel=channel,
        recurrence_rule=recurrence_rule,
    )
    session.add(reminder)
    return reminder


def mark_reminder_status(
    session: Session, reminder_id, status: ReminderStatus
) -> Optional[Reminder]:
    """Update the lifecycle status of a reminder."""

    reminder = session.get(Reminder, reminder_id)
    if reminder is None:
        return None
    reminder.status = status
    return reminder


def fetch_due_reminders(session: Session, *, as_of: datetime) -> Iterable[Reminder]:
    """Retrieve reminders that are due (or overdue) for dispatch."""

    stmt = (
        select(Reminder)
        .where(Reminder.remind_at <= as_of)
        .where(Reminder.status == ReminderStatus.PENDING)
        .order_by(Reminder.remind_at.asc())
    )
    return session.execute(stmt).scalars().all()


def list_reminders_for_user(session: Session, *, user_id) -> Iterable[Reminder]:
    """List reminders configured by a user."""

    stmt = (
        select(Reminder)
        .where(Reminder.user_id == user_id)
        .order_by(Reminder.remind_at.asc())
    )
    return session.execute(stmt).scalars().all()


__all__ = [
    "create_reminder",
    "mark_reminder_status",
    "fetch_due_reminders",
    "list_reminders_for_user",
]


