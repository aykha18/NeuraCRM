#!/usr/bin/env python3
"""
Verify actual Railway deployment status
"""
import requests
import json

RAILWAY_URL = "https://neuracrm.up.railway.app"

def test_endpoint(endpoint, method="GET", data=None, headers=None):
    """Test a specific endpoint"""
    url = f"{RAILWAY_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        
        print(f"{method} {endpoint}")
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"  ✅ Success")
            try:
                if 'application/json' in response.headers.get('content-type', ''):
                    data = response.json()
                    print(f"  📋 Response: {data}")
                else:
                    content = response.text[:200]
                    print(f"  📄 Content: {content}...")
            except:
                print(f"  📄 Raw: {response.text[:100]}...")
        else:
            print(f"  ❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"  🔍 Error: {error_data}")
            except:
                print(f"  📄 Error text: {response.text[:200]}...")
        
        print()
        return response
        
    except requests.exceptions.Timeout:
        print(f"  ⏰ Timeout")
        print()
        return None
    except Exception as e:
        print(f"  ❌ Connection error: {e}")
        print()
        return None

def main():
    print("🔍 VERIFYING ACTUAL RAILWAY STATUS")
    print("="*60)
    print(f"🌐 Railway URL: {RAILWAY_URL}")
    print()
    
    # Test basic connectivity
    print("1️⃣ Testing Basic Connectivity:")
    test_endpoint("/api/ping")
    
    # Test root
    print("2️⃣ Testing Root:")
    test_endpoint("/")
    
    # Test login
    print("3️⃣ Testing Login:")
    login_data = {
        "email": "nodeit@node.com",
        "password": "NodeIT2024!"
    }
    login_response = test_endpoint("/api/auth/login", method="POST", data=login_data)
    
    # Test health
    print("4️⃣ Testing Health:")
    test_endpoint("/api/health")

if __name__ == "__main__":
    main()
