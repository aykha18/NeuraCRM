#!/usr/bin/env python3
"""
Script to test if the company settings endpoints exist and are accessible.
"""

import requests
import json

def test_endpoints_exist():
    """Test if the company settings endpoints exist"""
    
    base_url = "https://neuracrm.up.railway.app"
    
    # Login credentials
    login_data = {
        "email": "nodeit@node.com",
        "password": "NodeIT2024!"
    }
    
    print("🧪 Testing Company Settings Endpoints")
    print("=" * 50)
    
    try:
        # Step 1: Login to get access token
        print("1. Logging in...")
        login_response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful")
        
        # Step 2: Test GET endpoint
        print("\n2. Testing GET /api/company-settings...")
        get_response = requests.get(f"{base_url}/api/company-settings", headers=headers)
        print(f"   Status Code: {get_response.status_code}")
        
        if get_response.status_code == 200:
            print("✅ GET endpoint exists and works")
            settings = get_response.json()
            print(f"   Response keys: {list(settings.keys())}")
        elif get_response.status_code == 404:
            print("❌ GET endpoint not found (404)")
        elif get_response.status_code == 405:
            print("❌ GET endpoint exists but method not allowed (405)")
        else:
            print(f"❌ GET endpoint returned: {get_response.status_code}")
            print(f"   Response: {get_response.text}")
        
        # Step 3: Test PUT endpoint
        print("\n3. Testing PUT /api/company-settings...")
        test_data = {
            "company_name": "Test Company",
            "currency": "AED - UAE Dirham (د.إ)",
            "timezone": "Dubai (UAE)"
        }
        
        put_response = requests.put(f"{base_url}/api/company-settings", 
                                  json=test_data, headers=headers)
        print(f"   Status Code: {put_response.status_code}")
        
        if put_response.status_code == 200:
            print("✅ PUT endpoint exists and works")
            result = put_response.json()
            print(f"   Created/Updated ID: {result.get('id')}")
        elif put_response.status_code == 404:
            print("❌ PUT endpoint not found (404)")
        elif put_response.status_code == 405:
            print("❌ PUT endpoint exists but method not allowed (405)")
            print("   This suggests the endpoint isn't properly registered")
        else:
            print(f"❌ PUT endpoint returned: {put_response.status_code}")
            print(f"   Response: {put_response.text}")
        
        # Step 4: Test POST endpoint
        print("\n4. Testing POST /api/company-settings...")
        post_response = requests.post(f"{base_url}/api/company-settings", 
                                    json=test_data, headers=headers)
        print(f"   Status Code: {post_response.status_code}")
        
        if post_response.status_code == 200:
            print("✅ POST endpoint exists and works")
        elif post_response.status_code == 404:
            print("❌ POST endpoint not found (404)")
        elif post_response.status_code == 405:
            print("❌ POST endpoint exists but method not allowed (405)")
        else:
            print(f"❌ POST endpoint returned: {post_response.status_code}")
            print(f"   Response: {post_response.text}")
        
        # Step 5: Test with OPTIONS to see what methods are allowed
        print("\n5. Testing OPTIONS /api/company-settings...")
        options_response = requests.options(f"{base_url}/api/company-settings", headers=headers)
        print(f"   Status Code: {options_response.status_code}")
        print(f"   Allow header: {options_response.headers.get('Allow', 'Not set')}")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")

if __name__ == "__main__":
    test_endpoints_exist()
