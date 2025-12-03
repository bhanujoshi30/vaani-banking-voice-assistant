"""
Test cases for UPI mode routing
Tests whether balance and transfer queries are correctly routed when UPI mode is active
"""
import asyncio
import sys
from pathlib import Path

# Ensure backend paths are importable
repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(repo_root / "backend" / "ai"))
sys.path.insert(0, str(repo_root / "backend"))

from agents.agent_graph import process_message
from agents.intent_classifier import classify_intent
from langchain_core.messages import HumanMessage


async def test_upi_mode_balance_check():
    """Test: UPI mode active + balance query should route to UPI agent"""
    print("\n=== TEST 1: UPI Mode Active + Balance Query ===")
    
    state = {
        "messages": [HumanMessage(content="Mera account balance kitna hai")],
        "user_id": "test-user-1",
        "session_id": "test-session-1",
        "language": "hi-IN",
        "user_context": {},
        "current_intent": "",
        "authenticated": True,
        "next_action": "",
        "upi_mode": True,  # UPI mode is ACTIVE
        "statement_data": {},
        "structured_data": {}
    }
    
    result = await classify_intent(state)
    print(f"UPI Mode Active: {state.get('upi_mode')}")
    print(f"Message: Mera account balance kitna hai")
    print(f"Intent: {result.get('current_intent')}")
    print(f"Expected: upi_payment")
    print(f"Result: {'✅ PASS' if result.get('current_intent') == 'upi_payment' else '❌ FAIL'}")
    
    return result.get('current_intent') == 'upi_payment'


async def test_upi_mode_inactive_balance_check():
    """Test: UPI mode inactive + balance query should route to banking agent"""
    print("\n=== TEST 2: UPI Mode Inactive + Balance Query ===")
    
    state = {
        "messages": [HumanMessage(content="Mera account balance kitna hai")],
        "user_id": "test-user-2",
        "session_id": "test-session-2",
        "language": "hi-IN",
        "user_context": {},
        "current_intent": "",
        "authenticated": True,
        "next_action": "",
        "upi_mode": False,  # UPI mode is INACTIVE
        "statement_data": {},
        "structured_data": {}
    }
    
    result = await classify_intent(state)
    print(f"UPI Mode Active: {state.get('upi_mode')}")
    print(f"Message: Mera account balance kitna hai")
    print(f"Intent: {result.get('current_intent')}")
    print(f"Expected: banking_operation")
    print(f"Result: {'✅ PASS' if result.get('current_intent') == 'banking_operation' else '❌ FAIL'}")
    
    return result.get('current_intent') == 'banking_operation'


async def test_upi_mode_transfer():
    """Test: UPI mode active + transfer query should route to UPI agent"""
    print("\n=== TEST 3: UPI Mode Active + Transfer Query ===")
    
    state = {
        "messages": [HumanMessage(content="Transfer 100 rupees")],
        "user_id": "test-user-3",
        "session_id": "test-session-3",
        "language": "en-IN",
        "user_context": {},
        "current_intent": "",
        "authenticated": True,
        "next_action": "",
        "upi_mode": True,  # UPI mode is ACTIVE
        "statement_data": {},
        "structured_data": {}
    }
    
    result = await classify_intent(state)
    print(f"UPI Mode Active: {state.get('upi_mode')}")
    print(f"Message: Transfer 100 rupees")
    print(f"Intent: {result.get('current_intent')}")
    print(f"Expected: upi_payment")
    print(f"Result: {'✅ PASS' if result.get('current_intent') == 'upi_payment' else '❌ FAIL'}")
    
    return result.get('current_intent') == 'upi_payment'


async def test_process_message_with_upi_mode():
    """Test: Full flow with process_message when UPI mode is passed"""
    print("\n=== TEST 4: Full Flow with process_message (UPI Mode Active) ===")
    
    result = await process_message(
        message="Mera account balance kitna hai",
        user_id="test-user-4",
        session_id="test-session-4",
        language="hi-IN",
        user_context={},
        message_history=[],
        upi_mode=True  # Pass UPI mode explicitly
    )
    
    print(f"UPI Mode Passed: True")
    print(f"Message: Mera account balance kitna hai")
    print(f"Intent: {result.get('intent')}")
    print(f"Expected: upi_payment")
    print(f"Result: {'✅ PASS' if result.get('intent') == 'upi_payment' else '❌ FAIL'}")
    
    return result.get('intent') == 'upi_payment'


async def test_process_message_without_upi_mode():
    """Test: Full flow with process_message when UPI mode is not passed"""
    print("\n=== TEST 5: Full Flow with process_message (UPI Mode Inactive) ===")
    
    result = await process_message(
        message="Mera account balance kitna hai",
        user_id="test-user-5",
        session_id="test-session-5",
        language="hi-IN",
        user_context={},
        message_history=[],
        upi_mode=False  # Pass UPI mode as False
    )
    
    print(f"UPI Mode Passed: False")
    print(f"Message: Mera account balance kitna hai")
    print(f"Intent: {result.get('intent')}")
    print(f"Expected: banking_operation")
    print(f"Result: {'✅ PASS' if result.get('intent') == 'banking_operation' else '❌ FAIL'}")
    
    return result.get('intent') == 'banking_operation'


async def run_all_tests():
    """Run all test cases"""
    print("=" * 60)
    print("UPI MODE ROUTING TEST SUITE")
    print("=" * 60)
    
    results = []
    
    try:
        results.append(await test_upi_mode_balance_check())
    except Exception as e:
        print(f"❌ TEST 1 FAILED with error: {e}")
        results.append(False)
    
    try:
        results.append(await test_upi_mode_inactive_balance_check())
    except Exception as e:
        print(f"❌ TEST 2 FAILED with error: {e}")
        results.append(False)
    
    try:
        results.append(await test_upi_mode_transfer())
    except Exception as e:
        print(f"❌ TEST 3 FAILED with error: {e}")
        results.append(False)
    
    try:
        results.append(await test_process_message_with_upi_mode())
    except Exception as e:
        print(f"❌ TEST 4 FAILED with error: {e}")
        results.append(False)
    
    try:
        results.append(await test_process_message_without_upi_mode())
    except Exception as e:
        print(f"❌ TEST 5 FAILED with error: {e}")
        results.append(False)
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if all(results):
        print("\n✅ ALL TESTS PASSED")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("\nCheck the logs above to identify the issue.")
    
    return all(results)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
