#!/usr/bin/env python3
"""
Test database connection and Lead model directly
"""

import requests
import json
import time

def test_database_connection():
    """Test if the database connection is working"""
    
    print("🔍 Testing Database Connection")
    print("=" * 50)
    
    # Login to get token
    login_url = "http://127.0.0.1:8000/api/auth/login"
    login_data = {
        "email": "nodeit@node.com",
        "password": "NodeIT2024!"
    }
    
    try:
        print("🔐 Logging in...")
        login_response = requests.post(login_url, json=login_data, timeout=10)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            print("✅ Login successful")
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Test different endpoints to see what's working
            endpoints = [
                ("/api/contacts", "Contacts"),
                ("/api/users", "Users"),
                ("/api/organizations", "Organizations"),
                ("/api/leads", "Leads")
            ]
            
            for endpoint, name in endpoints:
                try:
                    response = requests.get(f"http://127.0.0.1:8000{endpoint}", headers=headers, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, list):
                            print(f"✅ {name}: {len(data)} records")
                        else:
                            print(f"✅ {name}: {type(data)}")
                    else:
                        print(f"❌ {name}: Status {response.status_code}")
                except Exception as e:
                    print(f"❌ {name}: Error {e}")
            
            # Test creating a contact to see if database writes work
            print("\n🧪 Testing Contact Creation (to verify database writes work)...")
            contact_data = {
                "name": f"Test Contact {int(time.time())}",
                "email": f"testcontact{int(time.time())}@example.com",
                "company": "Test Company",
                "phone": "+1-555-TEST"
            }
            
            create_contact_response = requests.post("http://127.0.0.1:8000/api/contacts", json=contact_data, headers=headers, timeout=10)
            print(f"📊 Contact creation response status: {create_contact_response.status_code}")
            print(f"📋 Contact creation response: {create_contact_response.text}")
            
            if create_contact_response.status_code == 200:
                created_contact = create_contact_response.json()
                if "error" not in created_contact:
                    print("✅ Contact creation successful - database writes work!")
                    return True
                else:
                    print(f"❌ Contact creation failed: {created_contact['error']}")
                    return False
            else:
                print(f"❌ Contact creation failed with status: {create_contact_response.status_code}")
                return False
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_lead_model_fields():
    """Test what fields the Lead model actually expects"""
    
    print("\n🔍 Testing Lead Model Fields")
    print("=" * 50)
    
    # Login to get token
    login_url = "http://127.0.0.1:8000/api/auth/login"
    login_data = {
        "email": "nodeit@node.com",
        "password": "NodeIT2024!"
    }
    
    try:
        print("🔐 Logging in...")
        login_response = requests.post(login_url, json=login_data, timeout=10)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            print("✅ Login successful")
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Get a contact ID
            contacts_response = requests.get("http://127.0.0.1:8000/api/contacts", headers=headers, timeout=10)
            if contacts_response.status_code == 200:
                contacts_data = contacts_response.json()
                if isinstance(contacts_data, list) and len(contacts_data) > 0:
                    contact_id = contacts_data[0].get("id")
                    print(f"✅ Using contact ID: {contact_id}")
                else:
                    print("❌ No contacts found")
                    return False
            else:
                print(f"❌ Failed to get contacts: {contacts_response.status_code}")
                return False
            
            # Test different lead data formats
            test_cases = [
                {
                    "name": "Minimal Lead",
                    "data": {
                        "title": f"Minimal Lead {int(time.time())}",
                        "contact_id": contact_id
                    }
                },
                {
                    "name": "Full Lead",
                    "data": {
                        "title": f"Full Lead {int(time.time())}",
                        "status": "new",
                        "source": "manual",
                        "contact_id": contact_id,
                        "owner_id": 23  # From our user data
                    }
                },
                {
                    "name": "Lead with Score",
                    "data": {
                        "title": f"Scored Lead {int(time.time())}",
                        "status": "new",
                        "source": "manual",
                        "contact_id": contact_id,
                        "score": 75,
                        "score_confidence": 0.8
                    }
                }
            ]
            
            for test_case in test_cases:
                print(f"\n🧪 Testing {test_case['name']}...")
                print(f"📝 Data: {test_case['data']}")
                
                response = requests.post("http://127.0.0.1:8000/api/leads", json=test_case['data'], headers=headers, timeout=10)
                print(f"📊 Response status: {response.status_code}")
                print(f"📋 Response: {response.text}")
                
                if response.status_code == 200:
                    result = response.json()
                    if "error" not in result:
                        print(f"✅ {test_case['name']} successful!")
                        return True
                    else:
                        print(f"❌ {test_case['name']} failed: {result['error']}")
                else:
                    print(f"❌ {test_case['name']} failed with status: {response.status_code}")
            
            return False
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_database_connection()
    test_lead_model_fields()

