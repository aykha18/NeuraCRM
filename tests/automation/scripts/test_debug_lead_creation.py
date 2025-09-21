#!/usr/bin/env python3
"""
Debug script to understand why lead creation is failing
"""

import requests
import json

def debug_lead_creation():
    """Debug lead creation issues"""
    
    print("🔍 Debugging Lead Creation Issues")
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
            
            # Check if there are any contacts
            print("\n📋 Checking contacts...")
            contacts_url = "http://127.0.0.1:8000/api/contacts"
            contacts_response = requests.get(contacts_url, headers=headers, timeout=10)
            
            if contacts_response.status_code == 200:
                contacts_data = contacts_response.json()
                if isinstance(contacts_data, list):
                    print(f"📊 Found {len(contacts_data)} contacts")
                    if len(contacts_data) > 0:
                        print("📋 Contacts:")
                        for i, contact in enumerate(contacts_data[:3]):
                            print(f"   {i+1}. ID: {contact.get('id')}, Name: {contact.get('name')}, Company: {contact.get('company')}")
                    else:
                        print("❌ No contacts found - this might be the issue!")
                else:
                    print(f"⚠️ Unexpected contacts response: {contacts_data}")
            else:
                print(f"❌ Failed to get contacts: {contacts_response.status_code}")
            
            # Check if there are any users
            print("\n👥 Checking users...")
            users_url = "http://127.0.0.1:8000/api/users"
            users_response = requests.get(users_url, headers=headers, timeout=10)
            
            if users_response.status_code == 200:
                users_data = users_response.json()
                if isinstance(users_data, list):
                    print(f"📊 Found {len(users_data)} users")
                    if len(users_data) > 0:
                        print("👥 Users:")
                        for i, user in enumerate(users_data[:3]):
                            print(f"   {i+1}. ID: {user.get('id')}, Name: {user.get('name')}, Email: {user.get('email')}")
                    else:
                        print("❌ No users found!")
                else:
                    print(f"⚠️ Unexpected users response: {users_data}")
            else:
                print(f"❌ Failed to get users: {users_response.status_code}")
            
            # Try creating a lead with explicit contact_id
            print("\n🧪 Testing lead creation with explicit contact_id...")
            import time
            
            # First, try to create a contact if none exist
            if isinstance(contacts_data, list) and len(contacts_data) == 0:
                print("📝 Creating a contact first...")
                contact_data = {
                    "name": f"Test Contact {int(time.time())}",
                    "email": f"testcontact{int(time.time())}@example.com",
                    "company": "Test Company",
                    "phone": "+1-555-TEST"
                }
                
                create_contact_response = requests.post(contacts_url, json=contact_data, headers=headers, timeout=10)
                if create_contact_response.status_code == 200:
                    new_contact = create_contact_response.json()
                    contact_id = new_contact.get("id")
                    print(f"✅ Created contact with ID: {contact_id}")
                else:
                    print(f"❌ Failed to create contact: {create_contact_response.status_code}")
                    print(f"Response: {create_contact_response.text}")
                    contact_id = None
            else:
                contact_id = contacts_data[0].get("id") if contacts_data else None
                print(f"📋 Using existing contact ID: {contact_id}")
            
            # Now try creating a lead
            if contact_id:
                lead_data = {
                    "title": f"Debug Test Lead {int(time.time())}",
                    "status": "new",
                    "source": "manual",
                    "contact_id": contact_id
                }
                
                leads_url = "http://127.0.0.1:8000/api/leads"
                print(f"📡 Creating lead with data: {lead_data}")
                
                create_lead_response = requests.post(leads_url, json=lead_data, headers=headers, timeout=10)
                
                print(f"📊 Lead creation response status: {create_lead_response.status_code}")
                print(f"📋 Lead creation response: {create_lead_response.text}")
                
                if create_lead_response.status_code == 200:
                    print("✅ Lead created successfully!")
                    created_lead = create_lead_response.json()
                    print(f"📋 Created lead: {created_lead}")
                else:
                    print("❌ Lead creation failed")
            else:
                print("❌ No contact ID available for lead creation")
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_lead_creation()

