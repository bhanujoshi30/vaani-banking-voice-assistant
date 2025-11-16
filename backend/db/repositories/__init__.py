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
from .device_bindings import (
    create_device_binding,
    list_device_bindings,
    get_device_binding_by_id,
    get_device_binding_for_device,
    mark_device_binding_trust,
)
from .beneficiaries import (
    list_beneficiaries,
    create_beneficiary,
    get_beneficiary_by_id,
    get_beneficiary_by_account_number,
    deactivate_beneficiary,
    mark_beneficiary_used,
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
    "create_device_binding",
    "list_device_bindings",
    "get_device_binding_by_id",
    "get_device_binding_for_device",
    "mark_device_binding_trust",
    "list_beneficiaries",
    "create_beneficiary",
    "get_beneficiary_by_id",
    "get_beneficiary_by_account_number",
    "deactivate_beneficiary",
    "mark_beneficiary_used",
]


