#!/usr/bin/env python3
"""
Quick test script to verify UUID user_id works with banking tools
"""
import sys
from pathlib import Path

# Add paths
ai_path = Path(__file__).parent
backend_path = ai_path.parent / "backend"
sys.path.insert(0, str(backend_path))

from tools.banking_tools import get_user_accounts

# Test with a real UUID from database
test_user_id = "3370530d-376d-400d-870a-41b36be9abab"  # Isaac Bakshi

print(f"Testing get_user_accounts with UUID: {test_user_id}")
print("-" * 60)

result = get_user_accounts.invoke({"user_id": test_user_id})

print(f"Success: {result.get('success')}")
print(f"Account count: {result.get('count', 0)}")
print()

if result.get("success") and result.get("accounts"):
    print("Accounts found:")
    for acc in result["accounts"]:
        print(f"  - {acc['account_type']}: {acc['account_number']}")
        print(f"    Balance: ₹{acc['balance']:,.2f}")
        print(f"    Status: {acc['status']}")
        print()
else:
    print(f"Error: {result.get('error', 'Unknown error')}")
