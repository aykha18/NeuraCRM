#!/usr/bin/env python3
"""
Quick script to verify login credentials work with the NeuraCRM system
"""

import requests
import json
import sys

def test_login_credentials():
    """Test the provided login credentials"""
    
    print("🔐 Testing NeuraCRM Login Credentials")
    print("=" * 50)
    
    # Test credentials
    credentials = {
        "email": "nodeit@node.com",
        "password": "NodeIT2024!"
    }
    
    # Test backend health first
    print("1. Testing backend health...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend is running")
        else:
            print(f"   ❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Backend not accessible: {e}")
        print("   💡 Make sure to start the backend with: python main.py")
        return False
    
    # Test login endpoint
    print("2. Testing login endpoint...")
    try:
        response = requests.post(
            "http://localhost:8000/api/auth/login",
            json=credentials,
            timeout=10
        )
        
        if response.status_code == 200:
            print("   ✅ Login successful!")
            data = response.json()
            if 'access_token' in data:
                print("   ✅ Access token received")
                print(f"   📝 Token type: {data.get('token_type', 'Bearer')}")
            else:
                print("   ⚠️ Login successful but no access token in response")
            return True
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   📝 Error details: {error_data}")
            except:
                print(f"   📝 Response text: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Login request failed: {e}")
        return False

def test_frontend_access():
    """Test if frontend is accessible"""
    print("\n3. Testing frontend access...")
    try:
        response = requests.get("http://127.0.0.1:8000", timeout=5)
        if response.status_code == 200:
            print("   ✅ Frontend is accessible")
            return True
        else:
            print(f"   ⚠️ Frontend returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Frontend not accessible: {e}")
        print("   💡 Make sure to start the backend with: python main.py")
        return False

def main():
    """Main function"""
    print("🧪 NeuraCRM Credential Verification")
    print("=" * 50)
    print(f"Email: nodeit@node.com")
    print(f"Password: NodeIT2024!")
    print("=" * 50)
    
    # Test login
    login_success = test_login_credentials()
    
    # Test frontend
    frontend_success = test_frontend_access()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)
    
    if login_success and frontend_success:
        print("🎉 All tests passed! Credentials are working correctly.")
        print("✅ You can now run the regression tests:")
        print("   python tests/run_regression_tests.py")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the issues above.")
        if not login_success:
            print("🔧 Fix login issues before running regression tests.")
        if not frontend_success:
            print("🔧 Fix frontend issues before running regression tests.")
        sys.exit(1)

if __name__ == "__main__":
    main()
