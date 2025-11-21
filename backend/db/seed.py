"""
Data seeding utilities for Sun National Bank sandbox environments.

Generates 100 Indian-origin retail customers with related accounts,
transactions, cards, sessions, and reminders to support the hackathon
proof-of-concept workflows.
"""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
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
    DeviceBinding,
    Reminder,
    Session,
    Transaction,
    User,
    Beneficiary,
)
from .utils.enums import (
    AccountStatus,
    AccountType,
    AuthenticationLevel,
    CardStatus,
    CardType,
    DeviceTrustLevel,
    ReminderStatus,
    ReminderType,
    SessionStatus,
    TransactionChannel,
    TransactionStatus,
    TransactionType,
    BeneficiaryStatus,
)
from .utils.security import hash_password


# Indian names for seeding
INDIAN_MALE_NAMES = [
    "Rahul Kumar", "Aarav Sharma", "Vihaan Singh", "Arjun Reddy", "Mohammed Khan",
    "Rohan Gupta", "Aditya Varma", "Kabir Desai", "Sanjay Patel", "Karthik Menon"
]

INDIAN_FEMALE_NAMES = [
    "Ananya Singh", "Priya Sharma", "Saanvi Gupta", "Diya Kapoor", "Ayesha Khan",
    "Neha Verma", "Kiara Joshi", "Pooja Iyer", "Myra Reddy", "Shruti Narayan"
]

# Realistic transaction descriptions (English/Hinglish)
TRANSACTION_DESCRIPTIONS = {
    "DEPOSIT": [
        "Salary credit from employer",
        "UPI payment received from friend",
        "Bank transfer received",
        "Cash deposit at branch",
        "NEFT credit from account transfer",
        "IMPS transfer received",
        "Refund received from merchant",
        "Interest credit",
        "Dividend received",
        "Gift money received",
        "Reimbursement received",
        "Loan disbursement",
        "Rental income received",
        "Freelance payment received",
        "Investment maturity amount",
    ],
    "PAYMENT": [
        "UPI payment to merchant",
        "Electricity bill payment",
        "Mobile recharge",
        "Internet bill payment",
        "Credit card bill payment",
        "EMI payment",
        "School fees payment",
        "Hospital bill payment",
        "Grocery purchase via UPI",
        "Restaurant payment",
        "Online shopping payment",
        "Petrol payment",
        "Insurance premium payment",
        "Mutual fund investment",
        "SIP payment",
        "Rent payment",
        "Water bill payment",
        "Gas bill payment",
        "DTH recharge",
        "Movie ticket booking",
    ],
    "WITHDRAWAL": [
        "ATM cash withdrawal",
        "Cash withdrawal at branch",
        "UPI cash withdrawal",
        "Cheque payment",
        "Online transfer",
        "NEFT transfer",
        "IMPS transfer",
        "RTGS transfer",
        "Fund transfer to another account",
        "Investment withdrawal",
    ],
}

# Realistic reminder messages (English/Hinglish)
REMINDER_MESSAGES = {
    "BILL_PAYMENT": [
        "Your electricity bill of ₹{amount} is due on {date}. Please pay on time to avoid late fees.",
        "Reminder: Mobile bill payment of ₹{amount} due on {date}. Pay now via UPI.",
        "Credit card bill of ₹{amount} is due on {date}. Make payment to avoid interest charges.",
        "Internet bill payment reminder: ₹{amount} due on {date}. Pay via app or UPI.",
        "Your water bill of ₹{amount} is due on {date}. Please make payment.",
        "Gas bill payment reminder: ₹{amount} due on {date}. Pay now to avoid disconnection.",
        "DTH recharge reminder: ₹{amount} due on {date}. Recharge now to continue services.",
        "Insurance premium of ₹{amount} is due on {date}. Please pay to keep policy active.",
    ],
    "DUE_DATE": [
        "Your EMI of ₹{amount} is due on {date}. Please ensure sufficient balance.",
        "Loan EMI reminder: ₹{amount} due on {date}. Auto-debit will be processed.",
        "EMI payment of ₹{amount} scheduled for {date}. Keep account funded.",
        "Reminder: Personal loan EMI of ₹{amount} due on {date}.",
        "Home loan EMI of ₹{amount} is due on {date}. Please maintain balance.",
        "Car loan EMI reminder: ₹{amount} due on {date}.",
        "Education loan EMI of ₹{amount} is due on {date}. Please pay on time.",
    ],
    "CUSTOM": [
        "Don't forget to transfer money to your savings account this month.",
        "Reminder: Review your monthly expenses and budget.",
        "Your fixed deposit is maturing soon. Consider renewal options.",
        "Reminder: Update your KYC documents if expired.",
        "Check your account statement for any unauthorized transactions.",
        "Don't forget to pay your credit card bill this week.",
        "Reminder: Set up auto-pay for recurring bills to avoid late fees.",
        "Your investment SIP is due. Ensure sufficient balance in account.",
        "Reminder: Review and update your beneficiary list.",
        "Don't forget to check your account balance regularly.",
        "Reminder: Keep your UPI PIN secure and don't share with anyone.",
        "Your account maintenance charges will be debited this month.",
    ],
}


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


def _generate_upi_id(phone_number: str, first_name: str, last_name: str, existing_upi_ids: set, account_suffix: str = "") -> str:
    """Generate a unique UPI ID for a user or account."""
    # Clean phone number (remove spaces, dashes, etc.)
    clean_phone = ''.join(filter(str.isdigit, phone_number))
    if len(clean_phone) >= 10:
        clean_phone = clean_phone[-10:]  # Take last 10 digits
    
    # If account_suffix is provided, use it to make account-specific UPI IDs
    if account_suffix:
        # Try phone number format with suffix first
        phone_upi = f"{clean_phone}{account_suffix}@sunbank"
        if phone_upi not in existing_upi_ids:
            return phone_upi
        
        # Fallback to name-based format with suffix
        name_upi = f"{first_name.lower()}.{last_name.lower()}{account_suffix}@sunbank"
        if name_upi not in existing_upi_ids:
            return name_upi
        
        # If both exist, add a number
        counter = 1
        while True:
            name_upi = f"{first_name.lower()}.{last_name.lower()}{account_suffix}{counter}@sunbank"
            if name_upi not in existing_upi_ids:
                return name_upi
            counter += 1
    else:
        # Original logic for user-level UPI ID
        # Try phone number format first
        phone_upi = f"{clean_phone}@sunbank"
        if phone_upi not in existing_upi_ids:
            return phone_upi
        
        # Fallback to name-based format
        name_upi = f"{first_name.lower()}.{last_name.lower()}@sunbank"
        if name_upi not in existing_upi_ids:
            return name_upi
        
        # If both exist, add a number
        counter = 1
        while True:
            name_upi = f"{first_name.lower()}.{last_name.lower()}{counter}@sunbank"
            if name_upi not in existing_upi_ids:
                return name_upi
            counter += 1


def _create_accounts_for_user(
    session,
    *,
    user: User,
    branch: Branch,
    fake: Faker,
    sequence_seed: int,
    existing_upi_ids: set,
    first_name: str,
    last_name: str,
    phone_number: str,
) -> Iterable[Account]:
    accounts = []
    product_mix = [
        AccountType.SAVINGS,
        AccountType.CURRENT if random.random() > 0.7 else AccountType.SAVINGS,
    ]

    savings_account_count = 0
    for idx, account_type in enumerate(product_mix):
        account_number = _generate_account_number(branch.code, sequence_seed + idx)
        opening_balance = Decimal(random.randint(5_000, 200_000))
        interest_rate = Decimal("3.40") if account_type == AccountType.SAVINGS else None

        # Generate unique UPI ID for each savings account
        upi_id = None
        if account_type == AccountType.SAVINGS:
            savings_account_count += 1
            # Use account suffix to make unique UPI IDs for each savings account
            # First account gets .acc1, second gets .acc2, etc.
            account_suffix = f".acc{savings_account_count}"
            upi_id = _generate_upi_id(phone_number, first_name, last_name, existing_upi_ids, account_suffix)
            existing_upi_ids.add(upi_id)

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
            upi_id=upi_id,
        )
        session.add(account)
        accounts.append(account)

    session.flush()
    return accounts


def _create_session_for_user(session, user: User, fake: Faker) -> Session:
    started_at = datetime.now(ZoneInfo("Asia/Kolkata")) - timedelta(days=random.randint(1, 30))
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
        last_activity_at=ended_at,
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


def _create_device_binding(session, *, user: User, fake: Faker):
    binding = DeviceBinding(
        user_id=user.id,
        device_identifier=fake.md5(raw_output=False),
        fingerprint_hash=fake.sha1(raw_output=False),
        voice_signature_hash=fake.sha1(raw_output=False),
        voice_signature_vector=None,
        registration_method="seeded",
        platform=random.choice(["android", "ios", "web"]),
        device_label=random.choice(
            ["Primary Phone", "Home Laptop", "Village CSC Kiosk", "Family Tablet"]
        ),
        trust_level=DeviceTrustLevel.TRUSTED,
        last_verified_at=datetime.now(ZoneInfo("Asia/Kolkata"))
        - timedelta(days=random.randint(0, 10)),
    )
    session.add(binding)


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

        # Use realistic transaction descriptions
        txn_type_str = txn_type.value if hasattr(txn_type, 'value') else str(txn_type).lower()
        # Map enum values to our description keys
        if txn_type_str == "deposit":
            description = random.choice(TRANSACTION_DESCRIPTIONS["DEPOSIT"])
        elif txn_type_str == "withdrawal":
            description = random.choice(TRANSACTION_DESCRIPTIONS["WITHDRAWAL"])
        elif txn_type_str in ["payment", "transfer_out"]:
            description = random.choice(TRANSACTION_DESCRIPTIONS["PAYMENT"])
        else:
            description = random.choice(TRANSACTION_DESCRIPTIONS["PAYMENT"])

        transaction = Transaction(
            account_id=account.id,
            session_id=voice_session.id,
            transaction_type=txn_type,
            status=TransactionStatus.SETTLED,
            channel=random.choice([TransactionChannel.VOICE, TransactionChannel.UPI]),
            amount=amount,
            currency_code="INR",
            description=description,
            reference_id=str(uuid.uuid4())[:12],
            counterparty_account=fake.bban(),
            counterparty_name=fake.name(),
            occurred_at=datetime.now(ZoneInfo("Asia/Kolkata")) - timedelta(days=random.randint(1, 90)),
        )
        session.add(transaction)


def _create_reminder(session, *, user: User, account: Account, fake: Faker):
    reminder_type = random.choice(
        [ReminderType.BILL_PAYMENT, ReminderType.DUE_DATE, ReminderType.CUSTOM]
    )
    remind_at = datetime.now(ZoneInfo("Asia/Kolkata")) + timedelta(days=random.randint(3, 30))
    
    # Generate realistic reminder message
    reminder_type_str = reminder_type.value if hasattr(reminder_type, 'value') else str(reminder_type).lower()
    # Map enum values to our message keys
    if reminder_type_str == "bill_payment":
        message_template = random.choice(REMINDER_MESSAGES["BILL_PAYMENT"])
        amount = Decimal(random.randint(500, 50_000))
        date_str = remind_at.strftime("%d %b %Y")
        message = message_template.format(amount=int(amount), date=date_str)
    elif reminder_type_str == "due_date":
        message_template = random.choice(REMINDER_MESSAGES["DUE_DATE"])
        amount = Decimal(random.randint(5_000, 1_00_000))
        date_str = remind_at.strftime("%d %b %Y")
        message = message_template.format(amount=int(amount), date=date_str)
    else:
        # Custom reminders don't need placeholders
        message = random.choice(REMINDER_MESSAGES["CUSTOM"])
    
    reminder = Reminder(
        user_id=user.id,
        account_id=account.id,
        reminder_type=reminder_type,
        status=random.choice([ReminderStatus.PENDING, ReminderStatus.SENT]),
        message=message,
        remind_at=remind_at,
        channel=random.choice(["voice", "sms", "push"]),
        recurrence_rule=random.choice([None, "FREQ=MONTHLY;COUNT=6"]),
    )
    session.add(reminder)


def _create_beneficiaries(
    session,
    *,
    user: User,
    candidate_accounts: list[Account],
    fake: Faker,
):
    if not candidate_accounts:
        return

    available_accounts = [
        account for account in candidate_accounts if account.user_id != user.id
    ]
    if not available_accounts:
        return

    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    sample_size = min(len(available_accounts), random.randint(1, 3))
    for account in random.sample(available_accounts, sample_size):
        beneficiary = Beneficiary(
            user_id=user.id,
            account_id=account.id,
            display_name=fake.name(),
            account_number=account.account_number,
            bank_name=account.branch.name if account.branch else "Sun National Bank",
            ifsc_code=account.branch.ifsc_code if account.branch else "SUNB0000000",
            status=BeneficiaryStatus.ACTIVE,
            added_at=now,
            verified_at=now,
        )
        session.add(beneficiary)


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
            print("Seed data already present, updating UPI PINs for existing users...")
            # Update existing users with UPI PIN if not set
            from sqlalchemy import update
            upi_pin_hash = hash_password("123456")
            stmt = (
                update(User)
                .where(User.upi_pin_hash.is_(None))
                .values(upi_pin_hash=upi_pin_hash)
            )
            result = session.execute(stmt)
            session.commit()
            print(f"Updated {result.rowcount} existing users with UPI PIN 123456")
            return

        branches = _ensure_branches(session)
        account_registry: list[Account] = []
        existing_upi_ids: set = set()

        for idx in range(user_count):
            branch = branches[BRANCH_DEFINITIONS[idx % len(BRANCH_DEFINITIONS)]["code"]]
            
            # Use Indian names from the provided list
            gender = random.choice(["male", "female", "other"])
            if gender == "male":
                full_name = random.choice(INDIAN_MALE_NAMES)
            elif gender == "female":
                full_name = random.choice(INDIAN_FEMALE_NAMES)
            else:
                # For "other" gender, randomly pick from either list
                full_name = random.choice(INDIAN_MALE_NAMES + INDIAN_FEMALE_NAMES)
            
            # Split the full name into first and last name
            name_parts = full_name.split(maxsplit=1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            
            date_of_birth = fake.date_of_birth(minimum_age=21, maximum_age=65)

            customer_number = _generate_customer_number(idx)
            password_plain = f"Sun@{customer_number[-4:]}"
            phone_number = fake.phone_number()
            
            # Generate unique UPI ID for user (primary UPI ID)
            upi_id = _generate_upi_id(phone_number, first_name, last_name, existing_upi_ids)
            existing_upi_ids.add(upi_id)

            user = User(
                customer_number=customer_number,
                first_name=first_name,
                last_name=last_name,
                preferred_language=random.choice(["en-IN", "hi-IN", "te-IN"]),
                date_of_birth=date_of_birth,
                gender=gender,
                email=f"{first_name.lower()}.{last_name.lower()}.{customer_number.lower()}@example.com",
                phone_number=phone_number,
                upi_id=upi_id,
                upi_pin_hash=hash_password("123456"),  # Set UPI PIN to 123456 for all users
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
                session, 
                user=user, 
                branch=branch, 
                fake=fake, 
                sequence_seed=idx * 10,
                existing_upi_ids=existing_upi_ids,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
            )
            account_registry.extend(accounts)

            voice_session = _create_session_for_user(session, user=user, fake=fake)
            user.last_login_at = voice_session.started_at
            _create_device_binding(session, user=user, fake=fake)

            for account in accounts:
                _create_transactions_for_account(
                    session, account=account, voice_session=voice_session, fake=fake
                )
                _create_card_for_account(session, user=user, account=account, fake=fake)
                _create_reminder(session, user=user, account=account, fake=fake)

            _create_beneficiaries(
                session,
                user=user,
                candidate_accounts=account_registry,
                fake=fake,
            )

        print(f"Seeded {user_count} customers successfully.")


if __name__ == "__main__":
    seed_database()


