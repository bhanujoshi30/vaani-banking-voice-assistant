#!/usr/bin/env python3
"""
Test the updated balance logic with all accounts
"""
import asyncio
import sys
from pathlib import Path

# Add paths
ai_path = Path(__file__).parent
backend_path = ai_path.parent / "backend"
sys.path.insert(0, str(backend_path))

from agents.agent_graph import process_message

# Test user with multiple accounts (Mohammed Khalsa)
test_user_id = "8dbbd434-168e-4cdd-9450-ca6b77b2d061"
test_session = "test-session-123"

async def test_balance_queries():
    """Test different balance query scenarios"""
    
    test_cases = [
        ("Check balance", "en-IN", "Should show ALL accounts"),
        ("Check my savings account balance", "en-IN", "Should show SAVINGS only"),
        ("Check my current account balance", "en-IN", "Should show CURRENT only"),
        ("बैलेंस चेक करो", "hi-IN", "Should show ALL accounts in Hindi"),
        ("मेरा बचत खाता बैलेंस दिखाओ", "hi-IN", "Should show SAVINGS in Hindi"),
        ("मेरा चालू खाता बैलेंस दिखाओ", "hi-IN", "Should show CURRENT in Hindi"),
    ]
    
    for message, language, expected in test_cases:
        print(f"\n{'='*70}")
        print(f"Query: {message}")
        print(f"Language: {language}")
        print(f"Expected: {expected}")
        print(f"{'='*70}")
        
        try:
            result = await process_message(
                message=message,
                user_id=test_user_id,
                session_id=test_session,
                language=language,
                user_context={"name": "Mohammed Khalsa"},
                message_history=[]
            )
            
            print(f"Response: {result['response']}")
            print(f"Success: {result['success']}")
            
        except Exception as e:
            print(f"ERROR: {e}")
        
        print()

if __name__ == "__main__":
    asyncio.run(test_balance_queries())
