#!/usr/bin/env python3
"""
Test the backend API directly (not working_app.py) to see if it works
"""

import requests
import json
import time

def test_backend_api_direct():
    """Test the backend API directly"""
    
    print("🧪 Testing Backend API Directly")
    print("=" * 50)
    
    # Try the backend API endpoint directly
    backend_url = "http://127.0.0.1:8000"
    
    # Login to get token
    login_url = f"{backend_url}/api/auth/login"
    login_data = {
        "email": "nodeit@node.com",
        "password": "NodeIT2024!"
    }
    
    try:
        print("🔐 Logging in to backend API...")
        login_response = requests.post(login_url, json=login_data, timeout=10)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            print("✅ Backend login successful")
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Check if backend API has leads endpoint
            print("📡 Testing backend API leads endpoint...")
            leads_url = f"{backend_url}/api/leads"
            
            # First, check if we can get leads
            get_response = requests.get(leads_url, headers=headers, timeout=10)
            print(f"📊 GET leads response status: {get_response.status_code}")
            print(f"📋 GET leads response: {get_response.text[:200]}...")
            
            if get_response.status_code == 200:
                leads_data = get_response.json()
                if isinstance(leads_data, list):
                    print(f"✅ Backend API working - found {len(leads_data)} leads")
                else:
                    print(f"⚠️ Backend API response format: {type(leads_data)}")
            
            # Now try to create a lead using backend API format
            print("\n📝 Testing lead creation with backend API format...")
            
            # Get a contact ID first
            contacts_url = f"{backend_url}/api/contacts"
            contacts_response = requests.get(contacts_url, headers=headers, timeout=10)
            
            contact_id = None
            if contacts_response.status_code == 200:
                contacts_data = contacts_response.json()
                if isinstance(contacts_data, list) and len(contacts_data) > 0:
                    contact_id = contacts_data[0].get("id")
                    print(f"✅ Using contact ID: {contact_id}")
                else:
                    print("❌ No contacts found")
            else:
                print(f"❌ Failed to get contacts: {contacts_response.status_code}")
            
            if contact_id:
                # Try creating lead with backend API format (using LeadUpdate schema)
                lead_data = {
                    "title": f"Backend API Lead {int(time.time())}",
                    "status": "new",
                    "source": "manual",
                    "contact_id": contact_id
                }
                
                print(f"📡 Creating lead with backend API...")
                print(f"📝 Lead data: {lead_data}")
                
                create_response = requests.post(leads_url, json=lead_data, headers=headers, timeout=10)
                
                print(f"📊 Backend API response status: {create_response.status_code}")
                print(f"📋 Backend API response: {create_response.text}")
                
                if create_response.status_code == 200:
                    created_lead = create_response.json()
                    if "error" not in created_lead:
                        print("✅ Backend API lead creation successful!")
                        print(f"📋 Created lead: {created_lead}")
                        return True
                    else:
                        print(f"❌ Backend API lead creation failed: {created_lead['error']}")
                        return False
                else:
                    print(f"❌ Backend API lead creation failed with status: {create_response.status_code}")
                    return False
            else:
                print("❌ No contact ID available")
                return False
                
        else:
            print(f"❌ Backend login failed: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_which_api_is_running():
    """Test which API is actually running"""
    
    print("\n🔍 Testing Which API is Running")
    print("=" * 50)
    
    # Test different endpoints to see which one responds
    endpoints_to_test = [
        "http://127.0.0.1:8000/api/leads",
        "http://127.0.0.1:8000/api/contacts", 
        "http://127.0.0.1:8000/api/auth/login",
        "http://127.0.0.1:8000/health",
        "http://127.0.0.1:8000/docs"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(endpoint, timeout=5)
            print(f"✅ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

if __name__ == "__main__":
    test_which_api_is_running()
    test_backend_api_direct()

