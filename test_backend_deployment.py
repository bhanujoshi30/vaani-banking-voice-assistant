#!/usr/bin/env python3
"""
Test script to verify backend deployment and login flow
Tests both sunnationalbank.online and tech-tonic-ai.com backends
"""
import requests
import json
import sys
from typing import Optional, Dict, Any

# Test credentials (first user)
TEST_EMAIL = "john.doe@example.com"
TEST_PASSWORD = "SecurePass123!"

# Backend URLs to test
BACKEND_URLS = {
    "sunbank": "https://api.sunnationalbank.online",
    "techtonic": "https://api.tech-tonic-ai.com"
}

def test_health_check(url: str) -> tuple[bool, Optional[str]]:
    """Test health check endpoint"""
    try:
        response = requests.get(f"{url}/health", timeout=10)
        if response.status_code == 200:
            return True, response.json()
        return False, f"Status {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def test_root_endpoint(url: str) -> tuple[bool, Optional[str]]:
    """Test root endpoint"""
    try:
        response = requests.get(f"{url}/", timeout=10)
        if response.status_code == 200:
            return True, response.json()
        return False, f"Status {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def test_login(url: str, email: str, password: str) -> tuple[bool, Optional[Dict[str, Any]]]:
    """Test login endpoint"""
    try:
        login_data = {
            "email": email,
            "password": password
        }
        
        response = requests.post(
            f"{url}/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, {
                "status_code": response.status_code,
                "response": response.text,
                "headers": dict(response.headers)
            }
    except Exception as e:
        return False, {"error": str(e)}

def test_cors_preflight(url: str, origin: str) -> tuple[bool, Optional[str]]:
    """Test CORS preflight request"""
    try:
        response = requests.options(
            f"{url}/api/v1/auth/login",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type"
            },
            timeout=10
        )
        
        if response.status_code in [200, 204]:
            cors_headers = {
                "access-control-allow-origin": response.headers.get("access-control-allow-origin"),
                "access-control-allow-methods": response.headers.get("access-control-allow-methods"),
                "access-control-allow-credentials": response.headers.get("access-control-allow-credentials")
            }
            return True, json.dumps(cors_headers, indent=2)
        return False, f"Status {response.status_code}"
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 80)
    print("Backend Deployment Test Suite")
    print("=" * 80)
    print()
    
    results = {}
    
    for name, base_url in BACKEND_URLS.items():
        print(f"\n{'='*80}")
        print(f"Testing: {name.upper()} ({base_url})")
        print(f"{'='*80}\n")
        
        results[name] = {}
        
        # Test 1: Health Check
        print("1. Testing /health endpoint...")
        success, result = test_health_check(base_url)
        if success:
            print(f"   ✅ Health check passed: {json.dumps(result, indent=2)}")
            results[name]["health"] = "PASS"
        else:
            print(f"   ❌ Health check failed: {result}")
            results[name]["health"] = f"FAIL: {result}"
        
        # Test 2: Root Endpoint
        print("\n2. Testing / endpoint...")
        success, result = test_root_endpoint(base_url)
        if success:
            print(f"   ✅ Root endpoint passed: {json.dumps(result, indent=2)}")
            results[name]["root"] = "PASS"
        else:
            print(f"   ❌ Root endpoint failed: {result}")
            results[name]["root"] = f"FAIL: {result}"
        
        # Test 3: CORS Preflight
        print("\n3. Testing CORS preflight...")
        test_origins = [
            "https://sunnationalbank.online",
            "https://tech-tonic-ai.com"
        ]
        cors_passed = False
        for origin in test_origins:
            success, result = test_cors_preflight(base_url, origin)
            if success:
                print(f"   ✅ CORS preflight passed for {origin}")
                print(f"      {result}")
                cors_passed = True
                break
        if not cors_passed:
            print(f"   ❌ CORS preflight failed for all origins")
            results[name]["cors"] = "FAIL"
        else:
            results[name]["cors"] = "PASS"
        
        # Test 4: Login
        print("\n4. Testing login endpoint...")
        success, result = test_login(base_url, TEST_EMAIL, TEST_PASSWORD)
        if success:
            print(f"   ✅ Login successful!")
            print(f"      Response: {json.dumps(result, indent=2)}")
            results[name]["login"] = "PASS"
        else:
            print(f"   ❌ Login failed:")
            print(f"      {json.dumps(result, indent=2)}")
            results[name]["login"] = f"FAIL: {json.dumps(result)}"
        
        print()
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for name, test_results in results.items():
        print(f"\n{name.upper()}:")
        for test_name, result in test_results.items():
            status = "✅" if result == "PASS" else "❌"
            print(f"  {status} {test_name}: {result}")
            if result != "PASS":
                all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL TESTS PASSED")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())

