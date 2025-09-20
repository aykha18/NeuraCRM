#!/usr/bin/env python3
"""
Test API Fixes
=============

This script tests the fixed APIs to ensure they work correctly.
"""

import requests

def test_api_fixes():
    """Test the fixed APIs"""
    base_url = 'https://neuracrm.up.railway.app'
    
    print("🚀 Testing Fixed APIs")
    print("=" * 50)
    
    # Login
    login_data = {'email': 'nodeit@node.com', 'password': 'NodeIT2024!'}
    login_response = requests.post(f'{base_url}/api/auth/login', json=login_data)
    token = login_response.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    
    print("1. 🔍 Testing Leads API...")
    response = requests.get(f'{base_url}/api/leads', headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Leads returned: {len(data)} (type: {type(data)})")
        if data and isinstance(data, list):
            print(f"   ✅ First lead title: {data[0].get('title', 'N/A')}")
    else:
        print(f"   ❌ Error: {response.status_code} - {response.text}")
    
    print("\n2. 🔢 Testing Leads Count Stats API...")
    response = requests.get(f'{base_url}/api/stats/leads-count', headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Total leads: {data.get('total_count', 'N/A')}")
    else:
        print(f"   ❌ Error: {response.status_code} - {response.text}")
    
    print("\n3. 👥 Testing Contacts API...")
    response = requests.get(f'{base_url}/api/contacts', headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Contacts returned: {len(data)} (type: {type(data)})")
        if data and isinstance(data, list):
            print(f"   ✅ First contact name: {data[0].get('name', 'N/A')}")
    else:
        print(f"   ❌ Error: {response.status_code} - {response.text}")
    
    print("\n4. 🔢 Testing Contacts Count Stats API...")
    response = requests.get(f'{base_url}/api/stats/contacts-count', headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Total contacts: {data.get('total_count', 'N/A')}")
    else:
        print(f"   ❌ Error: {response.status_code} - {response.text}")
    
    print("\n" + "=" * 50)
    print("🎉 API Testing Complete!")

if __name__ == "__main__":
    test_api_fixes()
