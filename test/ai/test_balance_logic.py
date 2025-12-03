#!/usr/bin/env python3
"""
Simple test to verify the balance response logic
"""
import sys
from pathlib import Path

# Ensure backend paths are importable after moving tests to repo-root/test
repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(repo_root / "backend" / "ai"))
sys.path.insert(0, str(repo_root / "backend"))

from tools.banking_tools import get_user_accounts

# Test user with SAVINGS and CURRENT (Mohammed Khalsa)
test_user_id = "8dbbd434-168e-4cdd-9450-ca6b77b2d061"

print("Testing balance display logic")
print("=" * 70)
print(f"User ID: {test_user_id} (Mohammed Khalsa)")
print()

# Get accounts
result = get_user_accounts.invoke({"user_id": test_user_id})

if result["success"] and result["accounts"]:
    print(f"Found {result['count']} account(s):\n")
    
    # Test 1: Show all accounts (no type specified)
    print("Test 1: 'Check balance' - Should show ALL accounts")
    print("-" * 70)
    response = "Your account balances:\n\n"
    for acc in result["accounts"]:
        acc_type = acc["account_type"].replace("AccountType.", "")
        response += f"• {acc_type}: ₹{acc['balance']:,.2f}\n"
    print(response)
    
    # Test 2: Show SAVINGS only
    print("Test 2: 'Check my savings account balance'")
    print("-" * 70)
    for acc in result["accounts"]:
        if "savings" in acc["account_type"].lower():
            acc_type = acc["account_type"].replace("AccountType.", "")
            print(f"Your {acc_type} account balance is ₹{acc['balance']:,.2f}.\n")
            break
    
    # Test 3: Show CURRENT only
    print("Test 3: 'Check my current account balance'")
    print("-" * 70)
    for acc in result["accounts"]:
        if "current" in acc["account_type"].lower():
            acc_type = acc["account_type"].replace("AccountType.", "")
            print(f"Your {acc_type} account balance is ₹{acc['balance']:,.2f}.\n")
            break
    
    # Test 4: Hindi - All accounts
    print("Test 4: 'बैलेंस चेक करो' - Should show ALL accounts in Hindi")
    print("-" * 70)
    response = "आपके खातों का बैलेंस:\n\n"
    for acc in result["accounts"]:
        acc_type = acc["account_type"].replace("AccountType.", "")
        response += f"• {acc_type}: ₹{acc['balance']:,.2f}\n"
    print(response)
    
else:
    print(f"Error: {result.get('error', 'Unknown error')}")
