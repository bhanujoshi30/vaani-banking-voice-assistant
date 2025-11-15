"""
Data seeding utilities for Sun National Bank sandbox environments.

Generates 100 Indian-origin retail customers with related accounts,
transactions, cards, sessions, and reminders to support the hackathon
proof-of-concept workflows.
"""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Dict, Iterable

from faker import Faker
from sqlalchemy import select
from sqlalchemy.sql import func

from .base import Base
from .config import load_database_config
from .engine import create_db_engine, get_session_factory, session_scope
from .models import (
    Account,
    Branch,
    Card,
    Reminder,
    Session,
    Transaction,
    User,
)
from .utils.enums import (
    AccountStatus,
    AccountType,
    AuthenticationLevel,
    CardStatus,
    CardType,
    ReminderStatus,
    ReminderType,
    SessionStatus,
    TransactionChannel,
    TransactionStatus,
    TransactionType,
)
from .utils.security import hash_password


BRANCH_DEFINITIONS = [
    {
        "name": "Sun National Bank - Hyderabad",
        "code": "HYD001",
        "ifsc_code": "SUNB0001HYD",
        "address_line1": "1-10-60, Begumpet",
        "city": "Hyderabad",
        "state": "Telangana",
        "postal_code": "500016",
        "phone_number": "+91-40-1234-5678",
    },
    {
        "name": "Sun National Bank - New Delhi",
        "code": "DEL002",
        "ifsc_code": "SUNB0002DEL",
        "address_line1": "18, Barakhamba Road",
        "city": "New Delhi",
        "state": "Delhi",
        "postal_code": "110001",
        "phone_number": "+91-11-2465-2465",
    },
    {
        "name": "Sun National Bank - Bengaluru",
        "code": "BLR003",
        "ifsc_code": "SUNB0003BLR",
        "address_line1": "99, Residency Road",
        "city": "Bengaluru",
        "state": "Karnataka",
        "postal_code": "560025",
        "phone_number": "+91-80-2299-3300",
    },
]


def _ensure_branches(session) -> Dict[str, Branch]:
    existing = {
        branch.code: branch
        for branch in session.execute(select(Branch)).scalars().all()
    }
    for branch_def in BRANCH_DEFINITIONS:
        if branch_def["code"] in existing:
            continue
        branch = Branch(**branch_def)
        session.add(branch)
        existing[branch.code] = branch
    session.flush()
    return existing


def _generate_customer_number(index: int) -> str:
    return f"SNB{index + 1000:06d}"


def _generate_account_number(branch_code: str, sequence: int) -> str:
    core_digits = f"{random.randint(10**9, 10**10 - 1)}"
    return f"91{branch_code[-3:]}{sequence:03d}{core_digits}"


def _create_accounts_for_user(
    session,
    *,
    user: User,
    branch: Branch,
    fake: Faker,
    sequence_seed: int,
) -> Iterable[Account]:
    accounts = []
    product_mix = [
        AccountType.SAVINGS,
        AccountType.CURRENT if random.random() > 0.7 else AccountType.SAVINGS,
    ]

    for idx, account_type in enumerate(product_mix):
        account_number = _generate_account_number(branch.code, sequence_seed + idx)
        opening_balance = Decimal(random.randint(5_000, 200_000))
        interest_rate = Decimal("3.40") if account_type == AccountType.SAVINGS else None

        account = Account(
            user_id=user.id,
            branch_id=branch.id,
            account_number=account_number,
            account_type=account_type,
            status=AccountStatus.ACTIVE,
            currency_code="INR",
            balance=opening_balance,
            available_balance=opening_balance,
            interest_rate=interest_rate,
            nominee_name=fake.name(),
        )
        session.add(account)
        accounts.append(account)

    session.flush()
    return accounts


def _create_session_for_user(session, user: User, fake: Faker) -> Session:
    started_at = datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30))
    ended_at = started_at + timedelta(minutes=random.randint(5, 25))

    voice_session = Session(
        user_id=user.id,
        external_id=str(uuid.uuid4()),
        channel=TransactionChannel.VOICE,
        status=SessionStatus.COMPLETED,
        auth_level=AuthenticationLevel.FULL,
        device_fingerprint=fake.sha1(raw_output=False),
        mfa_method=random.choice(["voice_biometric", "otp", "device_binding"]),
        started_at=started_at,
        ended_at=ended_at,
        last_intent=random.choice(
            [
                "balance_inquiry",
                "fund_transfer",
                "transaction_history",
                "set_reminder",
            ]
        ),
    )
    session.add(voice_session)
    session.flush()
    return voice_session


def _create_card_for_account(session, user: User, account: Account, fake: Faker) -> Card:
    masked = f"XXXX-XXXX-XXXX-{fake.random_number(digits=4, fix_len=True)}"
    card = Card(
        user_id=user.id,
        account_id=account.id,
        card_type=CardType.DEBIT,
        card_token=fake.sha1(raw_output=False),
        masked_number=masked,
        network=random.choice(["RuPay", "Visa", "Mastercard"]),
        status=CardStatus.ACTIVE,
        expiry_month=f"{random.randint(1, 12):02d}",
        expiry_year=str(datetime.now().year + random.randint(2, 5)),
    )
    session.add(card)
    return card


def _create_transactions_for_account(
    session,
    *,
    account: Account,
    voice_session: Session,
    fake: Faker,
):
    # Seed deposits and payments to build history.
    for _ in range(random.randint(4, 6)):
        amount = Decimal(random.randint(500, 20_000))
        txn_type = random.choice(
            [
                TransactionType.DEPOSIT,
                TransactionType.PAYMENT,
                TransactionType.WITHDRAWAL,
            ]
        )
        if txn_type == TransactionType.DEPOSIT:
            account.balance += amount
            account.available_balance += amount
        else:
            debit_amount = min(account.available_balance, amount)
            account.balance -= debit_amount
            account.available_balance -= debit_amount

        transaction = Transaction(
            account_id=account.id,
            session_id=voice_session.id,
            transaction_type=txn_type,
            status=TransactionStatus.SETTLED,
            channel=random.choice([TransactionChannel.VOICE, TransactionChannel.UPI]),
            amount=amount,
            currency_code="INR",
            description=fake.sentence(nb_words=6),
            reference_id=str(uuid.uuid4())[:12],
            counterparty_account=fake.bban(),
            counterparty_name=fake.name(),
            occurred_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 90)),
        )
        session.add(transaction)


def _create_reminder(session, *, user: User, account: Account, fake: Faker):
    reminder = Reminder(
        user_id=user.id,
        account_id=account.id,
        reminder_type=random.choice(
            [ReminderType.BILL_PAYMENT, ReminderType.DUE_DATE, ReminderType.CUSTOM]
        ),
        status=random.choice([ReminderStatus.PENDING, ReminderStatus.SENT]),
        message=fake.sentence(nb_words=12),
        remind_at=datetime.now(timezone.utc) + timedelta(days=random.randint(3, 30)),
        channel=random.choice(["voice", "sms", "push"]),
        recurrence_rule=random.choice([None, "FREQ=MONTHLY;COUNT=6"]),
    )
    session.add(reminder)


def seed_database(user_count: int = 100):
    """Entry point for seeding the database."""

    config = load_database_config()
    engine = create_db_engine(config)
    Base.metadata.create_all(engine)
    session_factory = get_session_factory(engine)

    fake = Faker("en_IN")
    Faker.seed(42)
    random.seed(42)

    with session_scope(session_factory) as session:
        existing_users = session.execute(select(func.count()).select_from(User)).scalar()
        if existing_users and existing_users >= user_count:
            print("Seed data already present, skipping.")
            return

        branches = _ensure_branches(session)

        for idx in range(user_count):
            branch = branches[BRANCH_DEFINITIONS[idx % len(BRANCH_DEFINITIONS)]["code"]]
            first_name = fake.first_name()
            last_name = fake.last_name()
            date_of_birth = fake.date_of_birth(minimum_age=21, maximum_age=65)

            customer_number = _generate_customer_number(idx)
            password_plain = f"Sun@{customer_number[-4:]}"

            user = User(
                customer_number=customer_number,
                first_name=first_name,
                last_name=last_name,
                preferred_language=random.choice(["en-IN", "hi-IN", "te-IN"]),
                date_of_birth=date_of_birth,
                gender=random.choice(["male", "female", "other"]),
                email=f"{first_name.lower()}.{last_name.lower()}@example.com",
                phone_number=fake.phone_number(),
                aadhaar_last4=f"{random.randint(1000, 9999)}",
                pan_number=fake.bothify(text="?????####", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
                kyc_status=random.choice(["verified", "pending_review", "reverify"]),
                risk_segment=random.choice(["retail", "priority", "rural"]),
                primary_branch_id=branch.id,
                password_hash=hash_password(password_plain),
            )
            session.add(user)
            session.flush()

            accounts = _create_accounts_for_user(
                session, user=user, branch=branch, fake=fake, sequence_seed=idx * 10
            )

            voice_session = _create_session_for_user(session, user=user, fake=fake)
            user.last_login_at = voice_session.started_at

            for account in accounts:
                _create_transactions_for_account(
                    session, account=account, voice_session=voice_session, fake=fake
                )
                _create_card_for_account(session, user=user, account=account, fake=fake)
                _create_reminder(session, user=user, account=account, fake=fake)

        print(f"Seeded {user_count} customers successfully.")


if __name__ == "__main__":
    seed_database()


