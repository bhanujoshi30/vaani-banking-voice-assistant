"""
Simple banking tools for AI agent
Uses existing backend database functions
"""
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from langchain.tools import tool
from pydantic import BaseModel, Field

# Import backend functions
from db.repositories import accounts as account_repo
from db.repositories import transactions as transaction_repo
from utils.db_helper import get_db


# Tool input schemas
class GetBalanceInput(BaseModel):
    """Input for get_balance tool"""
    account_number: str = Field(description="The user's account number")


class GetUserAccountsInput(BaseModel):
    """Input for get_user_accounts tool"""
    user_id: str = Field(description="The user's ID (UUID string)")


class GetTransactionHistoryInput(BaseModel):
    """Input for get_transaction_history tool"""
    account_number: str = Field(description="The account number to get transactions for")
    days: Optional[int] = Field(default=30, description="Number of days to look back")
    limit: Optional[int] = Field(default=10, description="Maximum number of transactions to return")


class DownloadStatementInput(BaseModel):
    """Input for download_statement tool"""
    account_number: str = Field(description="The account number to download statement for")
    from_date: str = Field(description="Start date in YYYY-MM-DD format")
    to_date: str = Field(description="End date in YYYY-MM-DD format")
    period_type: Optional[str] = Field(default="custom", description="Type of period: 'week', 'month', 'year', or 'custom'")


@tool("get_user_accounts", args_schema=GetUserAccountsInput)
def get_user_accounts(user_id: str) -> Dict[str, Any]:
    """
    Get all accounts for a user.
    Use this when the user asks about their accounts, or to find a specific account type.
    
    Args:
        user_id: The user's ID (UUID string)
        
    Returns:
        Dictionary with list of all user accounts
    """
    try:
        with get_db() as db:
            accounts = account_repo.list_accounts_for_user(db, user_id)
            
            if not accounts:
                return {
                    "success": False,
                    "error": "No accounts found for user"
                }
            
            accounts_list = []
            for account in accounts:
                accounts_list.append({
                    "id": str(account.id),  # Include account ID for frontend matching
                    "accountId": str(account.id),  # Also include as accountId for compatibility
                    "account_number": account.account_number,
                    "accountNumber": account.account_number,  # Include camelCase version too
                    "account_type": account.account_type,
                    "accountType": account.account_type.value if hasattr(account.account_type, 'value') else str(account.account_type),
                    "balance": float(account.balance),
                    "currency": "INR",
                    "status": account.status.value if hasattr(account.status, 'value') else str(account.status)
                })
            
            return {
                "success": True,
                "accounts": accounts_list,
                "count": len(accounts_list)
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@tool("get_account_balance", args_schema=GetBalanceInput)
def get_account_balance(account_number: str) -> Dict[str, Any]:
    """
    Get the current balance for a specific bank account.
    Use this when you have a specific account number.
    
    Args:
        account_number: The account number to check
        
    Returns:
        Dictionary with balance information
    """
    try:
        with get_db() as db:
            account = account_repo.get_account_by_number(db, account_number)
            
            if not account:
                return {
                    "success": False,
                    "error": "Account not found"
                }
            
            return {
                "success": True,
                "account_number": account.account_number,
                "account_type": account.account_type,
                "balance": float(account.balance),
                "currency": "INR"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@tool("get_transaction_history", args_schema=GetTransactionHistoryInput)
def get_transaction_history(account_number: str, days: int = 30, limit: int = 10) -> Dict[str, Any]:
    """
    Get recent transaction history for an account.
    Use this when user asks about transactions, transaction history, or recent activity.
    
    Args:
        account_number: The account number to get transactions for
        days: Number of days to look back (default 30)
        limit: Maximum number of transactions to return (default 10)
        
    Returns:
        Dictionary with transaction list
    """
    try:
        with get_db() as db:
            # Get account first
            account = account_repo.get_account_by_number(db, account_number)
            
            if not account:
                return {
                    "success": False,
                    "error": "Account not found"
                }
            
            # Calculate date range
            start_date = datetime.now() - timedelta(days=days)
            
            # Get transactions
            transactions = transaction_repo.get_transaction_history(
                db,
                account_id=account.id,
                start_date=start_date,
                limit=limit
            )
            
            transactions_list = []
            for txn in transactions:
                transactions_list.append({
                    "date": txn.occurred_at.strftime("%Y-%m-%d %H:%M"),
                    "type": txn.transaction_type.value if hasattr(txn.transaction_type, 'value') else str(txn.transaction_type),
                    "amount": float(txn.amount),
                    "currency": txn.currency_code,
                    "description": txn.description or "",
                    "status": txn.status.value if hasattr(txn.status, 'value') else str(txn.status),
                    "counterparty": txn.counterparty_name or ""
                })
            
            return {
                "success": True,
                "account_number": account_number,
                "transactions": transactions_list,
                "count": len(transactions_list)
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@tool("download_statement", args_schema=DownloadStatementInput)
def download_statement(account_number: str, from_date: str, to_date: str, period_type: str = "custom") -> Dict[str, Any]:
    """
    Prepare account statement for download.
    Use this when user asks to download statement, get statement, or export transactions.
    
    The statement can be for:
    - Last week (period_type='week')
    - Last month (period_type='month') 
    - Last year (period_type='year')
    - Custom date range (period_type='custom')
    
    Args:
        account_number: The account number to download statement for
        from_date: Start date in YYYY-MM-DD format
        to_date: End date in YYYY-MM-DD format
        period_type: Type of period requested
        
    Returns:
        Dictionary with statement information and download instructions
    """
    try:
        # Parse dates
        try:
            start_dt = datetime.strptime(from_date, "%Y-%m-%d")
            end_dt = datetime.strptime(to_date, "%Y-%m-%d")
        except ValueError:
            return {
                "success": False,
                "error": "Invalid date format. Please use YYYY-MM-DD format."
            }
        
        # Validate date range
        if start_dt > end_dt:
            return {
                "success": False,
                "error": "Start date must be before end date."
            }
        
        # Check max 365 days (RBI compliance)
        diff_days = (end_dt - start_dt).days
        if diff_days > 365:
            return {
                "success": False,
                "error": "Statement period cannot exceed 365 days (RBI compliance). Please select a shorter period."
            }
        
        with get_db() as db:
            # Get account
            account = account_repo.get_account_by_number(db, account_number)
            
            if not account:
                return {
                    "success": False,
                    "error": "Account not found"
                }
            
            # Get transactions for the period
            transactions = transaction_repo.get_transaction_history(
                db,
                account_id=account.id,
                start_date=start_dt,
                end_date=end_dt,
                limit=500  # Max statement limit
            )
            
            transactions_list = []
            for txn in transactions:
                transactions_list.append({
                    "date": txn.occurred_at.strftime("%Y-%m-%d %H:%M"),
                    "type": txn.transaction_type.value if hasattr(txn.transaction_type, 'value') else str(txn.transaction_type),
                    "amount": float(txn.amount),
                    "currency": txn.currency_code,
                    "description": txn.description or "",
                    "status": txn.status.value if hasattr(txn.status, 'value') else str(txn.status),
                    "counterparty": txn.counterparty_name or "",
                    "reference_id": txn.reference_id or ""
                })
            
            return {
                "success": True,
                "statement_ready": True,
                "account_number": account_number,
                "account_type": account.account_type,
                "from_date": from_date,
                "to_date": to_date,
                "period_type": period_type,
                "transaction_count": len(transactions_list),
                "transactions": transactions_list,
                "current_balance": float(account.balance),
                "currency": "INR",
                "message": f"Statement prepared for {account.account_type} account {account_number} from {from_date} to {to_date} with {len(transactions_list)} transaction(s)."
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# Export tools
__all__ = [
    "get_account_balance",
    "get_user_accounts",
    "get_transaction_history",
    "download_statement",
]
