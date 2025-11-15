"""
Repository layer abstracts database access patterns from business logic.
"""

from .accounts import (
    get_account_balance,
    get_account_by_id,
    get_account_by_number,
    get_user_profile,
    list_accounts_for_user,
)
from .transactions import (
    TransferResult,
    execute_internal_transfer,
    get_transaction_by_reference,
    get_transaction_history,
)
from .reminders import (
    create_reminder,
    fetch_due_reminders,
    list_reminders_for_user,
    mark_reminder_status,
)

__all__ = [
    "get_account_balance",
    "get_account_by_id",
    "get_account_by_number",
    "get_user_profile",
    "list_accounts_for_user",
    "TransferResult",
    "execute_internal_transfer",
    "get_transaction_by_reference",
    "get_transaction_history",
    "create_reminder",
    "fetch_due_reminders",
    "list_reminders_for_user",
    "mark_reminder_status",
]


