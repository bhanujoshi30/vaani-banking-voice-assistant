"""
UPI Payment Tools for AI agent
Handles UPI ID resolution and payment processing
"""
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Add project root to sys.path so 'db' is importable
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from langchain.tools import tool
from pydantic import BaseModel, Field

# Import backend functions
from db.repositories import accounts as account_repo
from db.repositories import beneficiaries as beneficiary_repo
from db.services.banking import BankingService
from db.engine import get_session_factory
from db.config import load_database_config
from db.engine import create_db_engine
from utils.db_helper import get_db
from sqlalchemy import select
from db.models import User, Account


# Tool input schemas
class ResolveUPIIDInput(BaseModel):
    """Input for resolve_upi_id tool"""
    upi_identifier: str = Field(description="UPI ID, phone number, or name to resolve")


class InitiateUPIPaymentInput(BaseModel):
    """Input for initiate_upi_payment tool"""
    source_account_number: str = Field(description="Source account number")
    recipient_identifier: str = Field(description="UPI ID, phone number, or beneficiary name")
    amount: float = Field(description="Amount to transfer in rupees")
    remarks: Optional[str] = Field(default=None, description="Payment remarks")
    user_id: str = Field(description="User ID initiating the payment")
    session_id: Optional[str] = Field(default=None, description="Session ID")


@tool("resolve_upi_id", args_schema=ResolveUPIIDInput)
def resolve_upi_id(upi_identifier: str) -> Dict[str, Any]:
    """
    Resolve UPI ID, phone number, or name to a user account.
    Use this to find the recipient account for UPI payments.
    
    Args:
        upi_identifier: UPI ID (e.g., "9876543210@sunbank"), phone number, or name
        
    Returns:
        Dictionary with account information if found
    """
    try:
        with get_db() as db:
            # Try to find by UPI ID first
            if "@" in upi_identifier:
                # Trim whitespace and use case-insensitive comparison
                trimmed_upi_id = upi_identifier.strip()
                from sqlalchemy import func
                
                # First, try to find by User.upi_id
                stmt = select(User).where(
                    func.lower(User.upi_id) == func.lower(trimmed_upi_id)
                ).where(User.upi_id.isnot(None))  # Exclude NULL values
                user = db.execute(stmt).scalars().first()
                
                # If not found in User table, try Account table
                if not user:
                    account_stmt = select(Account).where(
                        func.lower(Account.upi_id) == func.lower(trimmed_upi_id)
                    ).where(Account.upi_id.isnot(None))  # Exclude NULL values
                    account = db.execute(account_stmt).scalars().first()
                    
                    if account:
                        # Found account with UPI ID - get the user
                        user = account.user
                        return {
                            "success": True,
                            "user_id": str(user.id),
                            "account_number": account.account_number,
                            "account_id": str(account.id),
                            "name": f"{user.first_name} {user.last_name}",
                            "upi_id": account.upi_id,  # Use account's UPI ID
                            "phone_number": user.phone_number,
                        }
                
                # If found via User table, get the account
                if user:
                    # Get user's primary account (first active account)
                    accounts = account_repo.list_accounts_for_user(db, user.id)
                    primary_account = next(iter(accounts), None)
                    if primary_account:
                        return {
                            "success": True,
                            "user_id": str(user.id),
                            "account_number": primary_account.account_number,
                            "account_id": str(primary_account.id),
                            "name": f"{user.first_name} {user.last_name}",
                            "upi_id": user.upi_id or primary_account.upi_id,  # Prefer user's UPI ID, fallback to account's
                            "phone_number": user.phone_number,
                        }
            
            # Try to find by phone number
            clean_phone = ''.join(filter(str.isdigit, upi_identifier))
            if len(clean_phone) >= 10:
                clean_phone = clean_phone[-10:]  # Take last 10 digits
                stmt = select(User).where(User.phone_number.like(f"%{clean_phone}%"))
                user = db.execute(stmt).scalars().first()
                if user:
                    accounts = account_repo.list_accounts_for_user(db, user.id)
                    primary_account = next(iter(accounts), None)
                    if primary_account:
                        return {
                            "success": True,
                            "user_id": str(user.id),
                            "account_number": primary_account.account_number,
                            "account_id": str(primary_account.id),
                            "name": f"{user.first_name} {user.last_name}",
                            "upi_id": user.upi_id,
                            "phone_number": user.phone_number,
                        }
            
            # Try to find by name (partial match on first or last name)
            name_parts = upi_identifier.lower().split()
            if name_parts:
                stmt = select(User).where(
                    (User.first_name.ilike(f"%{name_parts[0]}%")) |
                    (User.last_name.ilike(f"%{name_parts[0]}%"))
                )
                users = db.execute(stmt).scalars().all()
                if users:
                    # Return first match
                    user = users[0]
                    accounts = account_repo.list_accounts_for_user(db, user.id)
                    primary_account = next(iter(accounts), None)
                    if primary_account:
                        return {
                            "success": True,
                            "user_id": str(user.id),
                            "account_number": primary_account.account_number,
                            "account_id": str(primary_account.id),
                            "name": f"{user.first_name} {user.last_name}",
                            "upi_id": user.upi_id,
                            "phone_number": user.phone_number,
                        }
            
            return {
                "success": False,
                "error": "Recipient not found"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@tool("initiate_upi_payment", args_schema=InitiateUPIPaymentInput)
def initiate_upi_payment(
    source_account_number: str,
    recipient_identifier: str,
    amount: float,
    user_id: str,
    remarks: Optional[str] = None,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Initiate a UPI payment transaction.
    This resolves the recipient, validates the payment, and processes the transfer.
    
    Args:
        source_account_number: Source account number
        recipient_identifier: UPI ID, phone number, or name of recipient
        amount: Amount to transfer
        user_id: User ID initiating the payment
        remarks: Optional payment remarks
        session_id: Optional session ID
        
    Returns:
        Dictionary with transaction result
    """
    try:
        # First resolve the recipient
        recipient_info = resolve_upi_id.invoke({"upi_identifier": recipient_identifier})
        
        if not recipient_info.get("success"):
            return {
                "success": False,
                "error": f"Recipient not found: {recipient_identifier}"
            }
        
        destination_account_number = recipient_info["account_number"]
        
        # Generate UPI reference ID
        upi_ref_id = f"UPI-{datetime.now().strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"
        
        # Use banking service to process the transfer
        config = load_database_config()
        engine = create_db_engine(config)
        session_factory = get_session_factory(engine)
        banking_service = BankingService(session_factory)
        
        # Process the transfer with UPI channel
        from db.utils.enums import TransactionChannel
        result = banking_service.transfer_between_accounts(
            source_account_number=source_account_number,
            destination_account_number=destination_account_number,
            amount=amount,
            currency_code="INR",
            description=remarks or f"UPI Payment to {recipient_info.get('name', recipient_identifier)}",
            channel=TransactionChannel.UPI,
            user_id=user_id,
            session_id=session_id,
            reference_id=upi_ref_id
        )
        
        return {
            "success": True,
            "transaction_id": result.get("reference_id"),
            "amount": amount,
            "recipient": recipient_info.get("name"),
            "recipient_account": destination_account_number,
            "timestamp": result.get("timestamp"),
            "message": f"UPI payment of ₹{amount} to {recipient_info.get('name')} successful"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# Export tools
__all__ = [
    "resolve_upi_id",
    "initiate_upi_payment",
]

