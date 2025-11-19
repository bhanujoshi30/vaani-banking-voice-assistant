"""High-level services orchestrating banking workflows."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from ..engine import session_scope
from ..repositories import (
    TransferResult,
    create_reminder,
    execute_internal_transfer,
    fetch_due_reminders,
    get_account_balance,
    get_account_by_id,
    get_account_by_number,
    get_transaction_history,
    list_accounts_for_user,
    list_reminders_for_user,
    mark_reminder_status,
    list_beneficiaries as repo_list_beneficiaries,
    create_beneficiary as repo_create_beneficiary,
    get_beneficiary_by_id,
    get_beneficiary_by_account_number,
    deactivate_beneficiary,
    mark_beneficiary_used,
)
from ..utils.enums import CardType, ReminderStatus, ReminderType, TransactionChannel, BeneficiaryStatus


def _serialize_account(account) -> dict:
    return {
        "id": str(account.id),
        "accountNumber": account.account_number,
        "type": account.account_type.value,
        "status": account.status.value,
        "currency": account.currency_code,
        "balance": float(account.balance),
        "availableBalance": float(account.available_balance),
        "openedOn": account.opened_on.isoformat(),
        "branchId": str(account.branch_id) if account.branch_id else None,
        "debitCards": [
            {
                "id": str(card.id),
                "cardType": card.card_type.value,
                "status": card.status.value,
                "maskedNumber": card.masked_number,
                "network": card.network,
                "expiryMonth": card.expiry_month,
                "expiryYear": card.expiry_year,
            }
            for card in account.cards
            if card.card_type == CardType.DEBIT
        ],
        "creditCards": [
            {
                "id": str(card.id),
                "cardType": card.card_type.value,
                "status": card.status.value,
                "maskedNumber": card.masked_number,
                "network": card.network,
                "expiryMonth": card.expiry_month,
                "expiryYear": card.expiry_year,
            }
            for card in account.cards
            if card.card_type == CardType.CREDIT
        ],
    }


def _serialize_beneficiary(beneficiary) -> dict:
    return {
        "id": str(beneficiary.id),
        "name": beneficiary.display_name,
        "accountNumber": beneficiary.account_number,
        "bankName": beneficiary.bank_name,
        "ifsc": beneficiary.ifsc_code,
        "status": beneficiary.status.value,
        "addedAt": beneficiary.added_at,
        "verifiedAt": beneficiary.verified_at,
        "lastUsedAt": beneficiary.last_used_at,
        "removedAt": beneficiary.removed_at,
    }


class BankingService:
    """
    Domain service that encapsulates core operations exposed by the voice assistant.
    """

    def __init__(self, session_factory):
        self._session_factory = session_factory

    def list_accounts(self, *, user_id) -> list[dict]:
        with session_scope(self._session_factory) as session:
            accounts = list_accounts_for_user(session, user_id)
            return [_serialize_account(account) for account in accounts]

    def list_beneficiaries(self, *, user_id, include_blocked: bool = False) -> list[dict]:
        with session_scope(self._session_factory) as session:
            beneficiaries = repo_list_beneficiaries(
                session, user_id=user_id, include_blocked=include_blocked
            )
            return [_serialize_beneficiary(item) for item in beneficiaries]

    def add_beneficiary(
        self,
        *,
        user_id,
        display_name: str,
        account_number: str,
        bank_name: str | None = None,
        ifsc: str | None = None,
    ) -> dict:
        with session_scope(self._session_factory) as session:
            beneficiary = repo_create_beneficiary(
                session,
                user_id=user_id,
                display_name=display_name.strip(),
                account_number=account_number.strip(),
                bank_name=(bank_name.strip() if bank_name and bank_name.strip() else None),
                ifsc_code=(ifsc.strip() if ifsc and ifsc.strip() else None),
            )
            session.flush()
            return _serialize_beneficiary(beneficiary)

    def remove_beneficiary(self, *, user_id, beneficiary_id) -> Optional[dict]:
        with session_scope(self._session_factory) as session:
            beneficiary = get_beneficiary_by_id(
                session, beneficiary_id=beneficiary_id, user_id=user_id
            )
            if beneficiary is None:
                return None
            deactivate_beneficiary(session, beneficiary=beneficiary)
            session.flush()
            return _serialize_beneficiary(beneficiary)

    def get_account_for_user(self, *, user_id, account_id) -> Optional[dict]:
        with session_scope(self._session_factory) as session:
            account = get_account_by_id(session, account_id, user_id=user_id)
            if account is None:
                return None
            return _serialize_account(account)

    def get_account_by_number_for_user(self, *, user_id, account_number: str) -> Optional[dict]:
        """Get account by account number for a specific user"""
        with session_scope(self._session_factory) as session:
            # First try direct lookup
            account = get_account_by_number(session, account_number)
            if account is None:
                # Fallback: list all user accounts and find matching account number
                user_accounts = list_accounts_for_user(session, user_id)
                account = next(
                    (acc for acc in user_accounts if acc.account_number == account_number),
                    None
                )
                if account is None:
                    return None
            
            # Verify user ownership - convert both to strings for comparison
            import uuid as uuid_lib
            try:
                if isinstance(account.user_id, uuid_lib.UUID):
                    account_user_id = str(account.user_id)
                else:
                    account_user_id = str(account.user_id) if account.user_id else None
                
                if isinstance(user_id, uuid_lib.UUID):
                    user_id_str = str(user_id)
                else:
                    user_id_str = str(user_id) if user_id else None
                
                if account_user_id != user_id_str:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Account {account_number} belongs to different user: account_user_id={account_user_id}, requested_user_id={user_id_str}")
                    return None
            except Exception as e:
                # If comparison fails, log and return None
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error comparing user_id: {e}, account_user_id={account.user_id}, user_id={user_id}")
                return None
            return _serialize_account(account)

    def lookup_account_balance(self, *, account_id) -> dict:
        with session_scope(self._session_factory) as session:
            account = get_account_by_id(session, account_id)
            if account is None:
                raise ValueError("account_not_found")
            details = get_account_balance(session, account.account_number)
            return {
                "accountNumber": details["account_number"],
                "currency": details["currency"],
                "ledgerBalance": float(details["ledger_balance"]),
                "availableBalance": float(details["available_balance"]),
                "status": details["status"],
            }

    def transfer_between_accounts(
        self,
        *,
        source_account_number: str,
        destination_account_number: str,
        amount: Decimal | float | int,
        currency_code: str = "INR",
        description: Optional[str] = None,
        channel: TransactionChannel = TransactionChannel.VOICE,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        reference_id: Optional[str] = None,
    ) -> dict:
        with session_scope(self._session_factory) as session:
            result = execute_internal_transfer(
                session,
                source_account_number=source_account_number,
                destination_account_number=destination_account_number,
                amount=amount,
                currency_code=currency_code,
                description=description,
                channel=channel,
                initiated_session_id=session_id,
                reference_id=reference_id,
            )

            if user_id:
                beneficiary = get_beneficiary_by_account_number(
                    session,
                    user_id=user_id,
                    account_number=destination_account_number,
                )
                if beneficiary and beneficiary.status != BeneficiaryStatus.BLOCKED:
                    mark_beneficiary_used(session, beneficiary=beneficiary)

            session.flush()
            
            # Refresh the transactions to ensure all fields are loaded
            session.refresh(result.debit_transaction)
            session.refresh(result.credit_transaction)

            debit_txn = result.debit_transaction
            credit_txn = result.credit_transaction
            
            # Get source and destination account details
            source_account = get_account_by_number(session, source_account_number)
            destination_account = get_account_by_number(session, destination_account_number)
            
            beneficiary_name = None
            if user_id:
                beneficiary = get_beneficiary_by_account_number(
                    session,
                    user_id=user_id,
                    account_number=destination_account_number,
                )
                if beneficiary:
                    beneficiary_name = getattr(beneficiary, "display_name", None)

            # Ensure reference_id is available
            # Priority: 1) passed reference_id parameter, 2) transaction's reference_id
            # The passed reference_id is the source of truth since we just created the transaction with it
            reference_id_value = reference_id if reference_id else (debit_txn.reference_id if debit_txn.reference_id else None)
            
            # Log for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Transfer result - passed reference_id: {reference_id}, debit_txn.reference_id: {debit_txn.reference_id}, final reference_id_value: {reference_id_value}")
            
            # If still None, this is an error condition
            if not reference_id_value:
                logger.error(f"WARNING: reference_id is None! Transaction ID: {debit_txn.id}")
            
            return {
                "debit": {
                    "id": str(debit_txn.id),
                    "amount": debit_txn.amount,
                    "currency": debit_txn.currency_code,
                    "description": debit_txn.description,
                },
                "credit": {
                    "id": str(credit_txn.id),
                    "amount": credit_txn.amount,
                    "currency": credit_txn.currency_code,
                    "description": credit_txn.description,
                },
                "reference_id": reference_id_value,
                "timestamp": debit_txn.occurred_at.isoformat() if debit_txn.occurred_at else datetime.now().isoformat(),
                "source_account_number": source_account.account_number if source_account else None,
                "destination_account_number": destination_account.account_number if destination_account else None,
                "beneficiary_name": beneficiary_name or (destination_account.user.first_name + " " + destination_account.user.last_name if destination_account else None),
            }

    def fetch_transaction_history(
        self,
        *,
        user_id,
        account_id,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
    ) -> list[dict]:
        with session_scope(self._session_factory) as session:
            account = get_account_by_id(session, account_id, user_id=user_id)
            if account is None:
                raise ValueError("account_not_found")
            transactions = get_transaction_history(
                session,
                account_id=account.id,
                start_date=start_date,
                end_date=end_date,
                limit=limit,
            )
            return [
                {
                    "id": str(txn.id),
                    "type": txn.transaction_type.value,
                    "status": txn.status.value,
                    "amount": float(txn.amount),
                    "currency": txn.currency_code,
                    "description": txn.description,
                    "referenceId": txn.reference_id,
                    "counterpartyAccount": txn.counterparty_account,
                    "counterpartyName": txn.counterparty_name,
                    "occurredAt": txn.occurred_at,
                }
                for txn in transactions
            ]

    def generate_account_statement(
        self,
        *,
        user_id,
        account_number: str,
        from_date: datetime,
        to_date: datetime,
        period_type: str = "custom",
    ) -> dict:
        if (to_date - from_date).days > 365:
            raise ValueError("statement_period_too_long")

        with session_scope(self._session_factory) as session:
            account = get_account_by_number(session, account_number)
            if account is None or str(account.user_id) != str(user_id):
                raise ValueError("account_not_found")

            transactions = get_transaction_history(
                session,
                account_id=account.id,
                start_date=from_date,
                end_date=to_date,
                limit=500,
            )

            transactions_list = [
                {
                    "date": txn.occurred_at.strftime("%Y-%m-%d %H:%M"),
                    "type": txn.transaction_type.value,
                    "amount": float(txn.amount),
                    "currency": txn.currency_code,
                    "description": txn.description or "",
                    "status": txn.status.value,
                    "counterparty": txn.counterparty_name or "",
                    "reference_id": txn.reference_id or "",
                }
                for txn in transactions
            ]

            return {
                "account_number": account.account_number,
                "account_type": account.account_type.value
                if hasattr(account.account_type, "value")
                else str(account.account_type),
                "from_date": from_date.strftime("%Y-%m-%d"),
                "to_date": to_date.strftime("%Y-%m-%d"),
                "period_type": period_type,
                "transaction_count": len(transactions_list),
                "transactions": transactions_list,
                "current_balance": float(account.balance),
                "currency": account.currency_code,
            }

    def schedule_reminder(
        self,
        *,
        user_id,
        remind_at: datetime,
        message: str,
        reminder_type: ReminderType = ReminderType.BILL_PAYMENT,
        account_id=None,
        channel: str = "voice",
        recurrence_rule: Optional[str] = None,
    ) -> dict:
        with session_scope(self._session_factory) as session:
            reminder = create_reminder(
                session,
                user_id=user_id,
                remind_at=remind_at,
                message=message,
                reminder_type=reminder_type,
                account_id=account_id,
                channel=channel,
                recurrence_rule=recurrence_rule,
            )
            session.flush()
            return {
                "id": str(reminder.id),
                "reminderType": reminder.reminder_type.value,
                "status": reminder.status.value,
                "message": reminder.message,
                "remindAt": reminder.remind_at,
                "channel": reminder.channel,
                "accountId": str(reminder.account_id) if reminder.account_id else None,
                "recurrenceRule": reminder.recurrence_rule,
            }

    def get_due_reminders(self, *, as_of: datetime) -> list[dict]:
        with session_scope(self._session_factory) as session:
            reminders = fetch_due_reminders(session, as_of=as_of)
            return [
                {
                    "id": str(reminder.id),
                    "reminderType": reminder.reminder_type.value,
                    "status": reminder.status.value,
                    "message": reminder.message,
                    "remindAt": reminder.remind_at,
                    "channel": reminder.channel,
                    "accountId": str(reminder.account_id) if reminder.account_id else None,
                    "recurrenceRule": reminder.recurrence_rule,
                }
                for reminder in reminders
            ]

    def list_reminders(self, *, user_id) -> list[dict]:
        with session_scope(self._session_factory) as session:
            reminders = list_reminders_for_user(session, user_id=user_id)
            return [
                {
                    "id": str(reminder.id),
                    "reminderType": reminder.reminder_type.value,
                    "status": reminder.status.value,
                    "message": reminder.message,
                    "remindAt": reminder.remind_at,
                    "channel": reminder.channel,
                    "accountId": str(reminder.account_id) if reminder.account_id else None,
                    "recurrenceRule": reminder.recurrence_rule,
                }
                for reminder in reminders
            ]

    def update_reminder_status(self, *, reminder_id, status: ReminderStatus) -> Optional[dict]:
        with session_scope(self._session_factory) as session:
            reminder = mark_reminder_status(session, reminder_id, status)
            if reminder is None:
                return None
            session.flush()
            return {
                "id": str(reminder.id),
                "reminderType": reminder.reminder_type.value,
                "status": reminder.status.value,
                "message": reminder.message,
                "remindAt": reminder.remind_at,
                "channel": reminder.channel,
                "accountId": str(reminder.account_id) if reminder.account_id else None,
                "recurrenceRule": reminder.recurrence_rule,
            }


__all__ = ["BankingService"]


