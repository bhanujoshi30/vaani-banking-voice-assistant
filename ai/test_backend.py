#!/usr/bin/env python3
"""
Test script for Vaani AI Backend
Run this to verify your setup is working correctly
"""
import asyncio
import httpx
import json
from datetime import datetime


BASE_URL = "http://localhost:8001"
COLORS = {
    "green": "\033[92m",
    "red": "\033[91m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "reset": "\033[0m",
}


def print_colored(text, color="reset"):
    """Print colored text"""
    print(f"{COLORS.get(color, COLORS['reset'])}{text}{COLORS['reset']}")


def print_test(name):
    """Print test name"""
    print(f"\n{'='*60}")
    print_colored(f"TEST: {name}", "blue")
    print('='*60)


async def test_health():
    """Test health endpoint"""
    print_test("Health Check")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")
            data = response.json()
            
            print(json.dumps(data, indent=2))
            
            if data["status"] == "healthy" and data["ollama_status"]:
                print_colored("✅ PASSED: Backend is healthy", "green")
                return True
            else:
                print_colored("❌ FAILED: Backend is not fully healthy", "red")
                return False
    except Exception as e:
        print_colored(f"❌ FAILED: {e}", "red")
        return False


async def test_english_chat():
    """Test English chat"""
    print_test("English Chat")
    
    payload = {
        "message": "What is my account balance?",
        "user_id": 1,
        "session_id": "test-session",
        "language": "en-IN",
        "user_context": {
            "account_number": "ACC001",
            "name": "Test User"
        }
    }
    
    print(f"Request: {payload['message']}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{BASE_URL}/api/chat",
                json=payload
            )
            data = response.json()
            
            print(f"\nResponse: {data.get('response', 'No response')}")
            print(f"Intent: {data.get('intent', 'unknown')}")
            print(f"Language: {data.get('language', 'unknown')}")
            
            if data.get("success"):
                print_colored("✅ PASSED: English chat works", "green")
                return True
            else:
                print_colored("❌ FAILED: Chat unsuccessful", "red")
                return False
    except Exception as e:
        print_colored(f"❌ FAILED: {e}", "red")
        return False


async def test_hindi_chat():
    """Test Hindi chat"""
    print_test("Hindi Chat")
    
    payload = {
        "message": "मेरा खाते का बैलेंस क्या है?",
        "user_id": 1,
        "session_id": "test-session",
        "language": "hi-IN",
        "user_context": {
            "account_number": "ACC001"
        }
    }
    
    print(f"Request: {payload['message']}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{BASE_URL}/api/chat",
                json=payload
            )
            data = response.json()
            
            print(f"\nResponse: {data.get('response', 'No response')}")
            print(f"Intent: {data.get('intent', 'unknown')}")
            
            if data.get("success"):
                print_colored("✅ PASSED: Hindi chat works", "green")
                return True
            else:
                print_colored("❌ FAILED: Chat unsuccessful", "red")
                return False
    except Exception as e:
        print_colored(f"❌ FAILED: {e}", "red")
        return False


async def test_faq():
    """Test FAQ agent"""
    print_test("FAQ Agent")
    
    payload = {
        "message": "What is the interest rate for savings account?",
        "user_id": 1,
        "session_id": "test-session",
        "language": "en-IN"
    }
    
    print(f"Request: {payload['message']}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{BASE_URL}/api/chat",
                json=payload
            )
            data = response.json()
            
            print(f"\nResponse: {data.get('response', 'No response')}")
            print(f"Intent: {data.get('intent', 'unknown')}")
            
            if data.get("success") and data.get("intent") == "general_faq":
                print_colored("✅ PASSED: FAQ agent works", "green")
                return True
            else:
                print_colored("❌ FAILED: FAQ agent issue", "red")
                return False
    except Exception as e:
        print_colored(f"❌ FAILED: {e}", "red")
        return False


async def test_voice_mode():
    """Test voice mode (fast model)"""
    print_test("Voice Mode (Fast Model)")
    
    payload = {
        "message": "Check balance",
        "user_id": 1,
        "session_id": "test-session",
        "language": "en-IN",
        "user_context": {
            "account_number": "ACC001"
        },
        "voice_mode": True
    }
    
    print(f"Request: {payload['message']} (voice_mode=True)")
    
    try:
        start_time = datetime.now()
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{BASE_URL}/api/chat",
                json=payload
            )
            data = response.json()
            duration = (datetime.now() - start_time).total_seconds()
            
            print(f"\nResponse: {data.get('response', 'No response')}")
            print(f"Duration: {duration:.2f}s")
            
            if data.get("success") and duration < 2.0:
                print_colored(f"✅ PASSED: Voice mode fast enough ({duration:.2f}s)", "green")
                return True
            else:
                print_colored("❌ FAILED: Too slow or unsuccessful", "red")
                return False
    except Exception as e:
        print_colored(f"❌ FAILED: {e}", "red")
        return False


async def test_models():
    """Test available models"""
    print_test("Available Models")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/models")
            data = response.json()
            
            print("Models:")
            for model in data.get("models", []):
                print(f"  • {model['name']}")
            
            # Check for required models
            model_names = [m["name"] for m in data.get("models", [])]
            has_qwen = any("qwen" in name.lower() for name in model_names)
            has_llama = any("llama" in name.lower() for name in model_names)
            
            if has_qwen and has_llama:
                print_colored("✅ PASSED: Required models found", "green")
                return True
            else:
                print_colored("⚠️  WARNING: Some models missing", "yellow")
                return False
    except Exception as e:
        print_colored(f"❌ FAILED: {e}", "red")
        return False


async def main():
    """Run all tests"""
    print_colored("\n" + "="*60, "blue")
    print_colored("     VAANI AI BACKEND TEST SUITE", "blue")
    print_colored("="*60 + "\n", "blue")
    
    print_colored(f"Testing backend at: {BASE_URL}", "yellow")
    print_colored(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n", "yellow")
    
    tests = [
        ("Health Check", test_health),
        ("Models Check", test_models),
        ("English Chat", test_english_chat),
        ("Hindi Chat", test_hindi_chat),
        ("FAQ Agent", test_faq),
        ("Voice Mode", test_voice_mode),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print_colored(f"❌ ERROR in {name}: {e}", "red")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print_colored("TEST SUMMARY", "blue")
    print("="*60 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        color = "green" if result else "red"
        print_colored(f"{status} - {name}", color)
    
    print("\n" + "-"*60)
    percentage = (passed / total) * 100
    print_colored(f"Results: {passed}/{total} tests passed ({percentage:.1f}%)", 
                 "green" if passed == total else "yellow")
    
    if passed == total:
        print_colored("\n🎉 All tests passed! Your AI backend is working perfectly!", "green")
    elif passed >= total * 0.5:
        print_colored("\n⚠️  Some tests failed. Check the logs above.", "yellow")
    else:
        print_colored("\n❌ Many tests failed. Please check your setup:", "red")
        print("  1. Is Ollama running? (ollama serve)")
        print("  2. Are models downloaded? (ollama list)")
        print("  3. Is AI backend running? (python main.py)")
        print("  4. Check logs in: logs/ai_backend.log")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
