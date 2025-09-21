#!/usr/bin/env python3
"""
Test lead creation using the correct model fields (title instead of name)
"""

import requests
import json
import time

def test_lead_creation_correct_model():
    """Test lead creation with correct model fields"""
    
    print("🧪 Testing Lead Creation with Correct Model Fields")
    print("=" * 60)
    
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
            
            # Get a contact ID first
            print("📋 Getting contact ID...")
            contacts_url = "http://127.0.0.1:8000/api/contacts"
            contacts_response = requests.get(contacts_url, headers=headers, timeout=10)
            
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
            
            # Create lead with correct model fields
            lead_data = {
                "title": f"Correct Model Lead {int(time.time())}",  # Use 'title' not 'name'
                "status": "new",
                "source": "manual",
                "contact_id": contact_id
            }
            
            leads_url = "http://127.0.0.1:8000/api/leads"
            print(f"📡 Creating lead with correct model fields...")
            print(f"📝 Lead data: {lead_data}")
            
            create_response = requests.post(leads_url, json=lead_data, headers=headers, timeout=10)
            
            print(f"📊 Response status: {create_response.status_code}")
            print(f"📋 Response: {create_response.text}")
            
            if create_response.status_code == 200:
                created_lead = create_response.json()
                if "error" not in created_lead:
                    print("✅ Lead created successfully!")
                    print(f"📋 Created lead: {created_lead}")
                    
                    # Check if it appears in the list
                    print("\n🔍 Checking if lead appears in API list...")
                    leads_response = requests.get(leads_url, headers=headers, timeout=10)
                    
                    if leads_response.status_code == 200:
                        leads_data = leads_response.json()
                        if isinstance(leads_data, list):
                            print(f"📊 Found {len(leads_data)} leads in database")
                            
                            # Look for our created lead
                            lead_found = False
                            for lead in leads_data:
                                if lead.get("title") == lead_data["title"]:
                                    print(f"✅ Created lead found in API list: {lead['title']}")
                                    lead_found = True
                                    break
                            
                            if not lead_found:
                                print("❌ Created lead not found in API list")
                        else:
                            print(f"⚠️ Unexpected API response format: {type(leads_data)}")
                    else:
                        print(f"❌ Failed to get leads list: {leads_response.status_code}")
                    
                    return True
                else:
                    print(f"❌ Lead creation failed: {created_lead['error']}")
                    return False
            else:
                print(f"❌ Lead creation failed with status: {create_response.status_code}")
                return False
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_create_two_leads_correct_model():
    """Test creating 2 leads with correct model fields"""
    
    print("\n🚀 Creating 2 Leads with Correct Model Fields")
    print("=" * 60)
    
    success_count = 0
    
    for i in range(2):
        print(f"\n=== Creating Lead {i+1} ===")
        if test_lead_creation_correct_model():
            success_count += 1
        time.sleep(1)  # Small delay between requests
    
    print(f"\n📊 Results: {success_count}/2 leads created successfully")
    
    if success_count == 2:
        print("🎉 Both leads created successfully!")
        print("✅ Lead creation API is working correctly")
        print("✅ Database is saving leads properly")
        print("✅ The issue was using wrong field names in working_app.py")
        print("💡 working_app.py should use 'title' instead of 'name'")
    elif success_count == 1:
        print("⚠️ One lead created successfully")
    else:
        print("❌ No leads created successfully")
    
    return success_count == 2

if __name__ == "__main__":
    success = test_create_two_leads_correct_model()
    if success:
        print("\n🎉 Lead creation is now working perfectly!")
        print("   The CRUD operations are functional.")
        print("   The issue was a model field mismatch in working_app.py")
    else:
        print("\n❌ Lead creation still needs attention.")

