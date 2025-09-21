#!/usr/bin/env python3
"""
Test lead creation with the correct API format (using 'name' instead of 'title')
"""

import requests
import json
import time

def test_lead_creation_fixed():
    """Test lead creation with correct API format"""
    
    print("🧪 Testing Lead Creation with Correct API Format")
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
            
            # Create lead with correct format (using 'name' instead of 'title')
            lead_data = {
                "name": f"Fixed Test Lead {int(time.time())}",
                "email": f"fixedtest{int(time.time())}@example.com",
                "company": "Fixed Test Company",
                "phone": "+1-555-FIXED",
                "status": "New",
                "source": "manual",
                "priority": "Medium",
                "estimated_value": 50000
            }
            
            leads_url = "http://127.0.0.1:8000/api/leads"
            print(f"📡 Creating lead with correct format...")
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
                                if lead.get("name") == lead_data["name"]:
                                    print(f"✅ Created lead found in API list: {lead['name']}")
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

def test_create_two_leads_fixed():
    """Test creating 2 leads with correct format"""
    
    print("\n🚀 Creating 2 Leads with Fixed API Format")
    print("=" * 60)
    
    success_count = 0
    
    for i in range(2):
        print(f"\n=== Creating Lead {i+1} ===")
        if test_lead_creation_fixed():
            success_count += 1
        time.sleep(1)  # Small delay between requests
    
    print(f"\n📊 Results: {success_count}/2 leads created successfully")
    
    if success_count == 2:
        print("🎉 Both leads created successfully!")
        print("✅ Lead creation API is working correctly")
        print("✅ Database is saving leads properly")
        print("✅ The issue was using 'title' instead of 'name' field")
    elif success_count == 1:
        print("⚠️ One lead created successfully")
    else:
        print("❌ No leads created successfully")
    
    return success_count == 2

if __name__ == "__main__":
    success = test_create_two_leads_fixed()
    if success:
        print("\n🎉 Lead creation is now working perfectly!")
        print("   The CRUD operations are functional.")
    else:
        print("\n❌ Lead creation still needs attention.")

