#!/usr/bin/env python3
"""
Test script to demonstrate LLM provider switching
Run this to verify both Ollama and OpenAI are working
"""
import asyncio
import sys
from pathlib import Path

# Ensure backend paths are importable after moving tests to repo-root/test
repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(repo_root / "backend" / "ai"))
sys.path.insert(0, str(repo_root / "backend"))

from services import get_llm_service, LLMProvider
from config import settings


async def test_provider(provider: LLMProvider):
    """Test a specific LLM provider"""
    print(f"\n{'='*60}")
    print(f"Testing {provider.value.upper()} Provider")
    print(f"{'='*60}")
    
    try:
        # Get LLM service
        llm = get_llm_service(provider=provider)
        print(f"✓ Service initialized: {llm.get_provider_name()}")
        
        # Test health check
        is_healthy = await llm.health_check()
        if is_healthy:
            print("✓ Health check passed")
        else:
            print("✗ Health check failed")
            return False
        
        # Test chat completion
        print("\nSending test message...")
        messages = [
            {"role": "user", "content": "Say 'Hello from Vaani AI!' in one sentence."}
        ]
        
        response = await llm.chat(messages)
        print(f"✓ Response received: {response}")
        
        # Test streaming
        print("\nTesting streaming...")
        stream_messages = [
            {"role": "user", "content": "Count to 3, one number per line."}
        ]
        
        print("Stream output: ", end="")
        async for chunk in llm.chat_stream(stream_messages):
            print(chunk, end="", flush=True)
        print("\n✓ Streaming works")
        
        print(f"\n✅ {provider.value.upper()} provider is working correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ {provider.value.upper()} provider failed: {str(e)}")
        return False


async def test_configured_provider():
    """Test the currently configured provider from .env"""
    print(f"\n{'='*60}")
    print(f"Testing CONFIGURED Provider")
    print(f"{'='*60}")
    
    provider_name = settings.llm_provider
    print(f"Current configuration: LLM_PROVIDER={provider_name}")
    
    try:
        llm = get_llm_service()
        print(f"✓ Using provider: {llm.get_provider_name()}")
        
        messages = [
            {"role": "user", "content": "What is 2+2? Answer in one word."}
        ]
        
        response = await llm.chat(messages)
        print(f"✓ Response: {response}")
        
        print(f"\n✅ Configured provider ({provider_name}) is working!")
        return True
        
    except Exception as e:
        print(f"\n❌ Configured provider failed: {str(e)}")
        return False


async def main():
    """Run all tests"""
    print("🧪 VAANI AI - LLM Provider Testing")
    print("=" * 60)
    
    # Test configured provider
    await test_configured_provider()
    
    # Test Ollama if available
    print("\n" + "="*60)
    input("Press Enter to test Ollama (make sure it's running)...")
    ollama_ok = await test_provider(LLMProvider.OLLAMA)
    
    # Test OpenAI if API key is configured
    if settings.openai_api_key and settings.openai_api_key != "your_openai_api_key_here":
        print("\n" + "="*60)
        input("Press Enter to test OpenAI (will use API credits)...")
        openai_ok = await test_provider(LLMProvider.OPENAI)
    else:
        print("\n" + "="*60)
        print("⚠️  OpenAI API key not configured, skipping OpenAI test")
        print("   Add OPENAI_API_KEY to .env to test OpenAI")
        openai_ok = None
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"Ollama:  {'✅ PASS' if ollama_ok else '❌ FAIL'}")
    if openai_ok is not None:
        print(f"OpenAI:  {'✅ PASS' if openai_ok else '❌ FAIL'}")
    else:
        print(f"OpenAI:  ⏭️  SKIPPED (no API key)")
    print("="*60)
    
    print("\n💡 To switch providers, edit .env:")
    print("   LLM_PROVIDER=ollama  # Use local Ollama")
    print("   LLM_PROVIDER=openai  # Use cloud OpenAI")
    print("\nThen restart the AI backend: cd ai && ./run.sh")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
