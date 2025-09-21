#!/usr/bin/env python3
"""
Script to check leads via API to see if they're being saved to the database
"""

import requests
import json

def test_api_leads_check():
    """Check leads via API"""
    
    print("🔍 NeuraCRM API Leads Check")
    print("=" * 50)
    
    # Login to get token
    login_url = "http://127.0.0.1:8000/api/auth/login"
    login_data = {
        "email": "nodeit@node.com",
        "password": "NodeIT2024!"
    }
    
    try:
        print("🔐 Logging in to get API token...")
        login_response = requests.post(login_url, json=login_data, timeout=10)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            print("✅ Login successful, got API token")
            
            # Check leads via API
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            leads_url = "http://127.0.0.1:8000/api/leads"
            print(f"📡 Checking leads API: {leads_url}")
            
            leads_response = requests.get(leads_url, headers=headers, timeout=10)
            
            if leads_response.status_code == 200:
                leads_data = leads_response.json()
                print("✅ API call successful")
                
                if isinstance(leads_data, list):
                    print(f"📊 Found {len(leads_data)} leads in database")
                    
                    if len(leads_data) > 0:
                        print("\n📋 Leads in database:")
                        for i, lead in enumerate(leads_data[:5]):  # Show first 5 leads
                            lead_name = lead.get("name", "Unknown")
                            lead_email = lead.get("email", "No email")
                            lead_company = lead.get("company", "No company")
                            lead_status = lead.get("status", "No status")
                            print(f"   {i+1}. {lead_name} ({lead_email}) - {lead_company} - {lead_status}")
                    else:
                        print("📭 No leads found in database")
                else:
                    print(f"⚠️ Unexpected API response format: {type(leads_data)}")
                    print(f"Response: {leads_data}")
            else:
                print(f"❌ API call failed with status: {leads_response.status_code}")
                print(f"Response: {leads_response.text}")
        else:
            print(f"❌ Login failed with status: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API - is the server running?")
    except requests.exceptions.Timeout:
        print("❌ API request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_create_lead_via_api():
    """Test creating a lead via API"""
    
    print("\n🧪 Testing Lead Creation via API")
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
            
            # Create a lead via API
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            import time
            lead_data = {
                "name": f"API Test Lead {int(time.time())}",
                "email": f"apitest{int(time.time())}@example.com",
                "company": "API Test Company",
                "phone": "+1-555-API-TEST",
                "status": "new",
                "source": "manual"
            }
            
            create_url = "http://127.0.0.1:8000/api/leads"
            print(f"📡 Creating lead via API: {create_url}")
            print(f"📝 Lead data: {lead_data}")
            
            create_response = requests.post(create_url, json=lead_data, headers=headers, timeout=10)
            
            if create_response.status_code == 200 or create_response.status_code == 201:
                print("✅ Lead created successfully via API")
                created_lead = create_response.json()
                print(f"📋 Created lead: {created_lead}")
                
                # Check if it appears in the list
                print("\n🔍 Checking if lead appears in API list...")
                leads_response = requests.get(create_url, headers=headers, timeout=10)
                
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
            else:
                print(f"❌ Lead creation failed with status: {create_response.status_code}")
                print(f"Response: {create_response.text}")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api_leads_check()
    test_create_lead_via_api()

