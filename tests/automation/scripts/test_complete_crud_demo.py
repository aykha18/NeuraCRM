#!/usr/bin/env python3
"""
Complete CRUD operations demonstration for NeuraCRM
Shows CREATE, READ, UPDATE, DELETE, and CONVERT operations
"""

import requests
import json
import time

def test_complete_crud_demo():
    """Complete CRUD operations demonstration"""
    
    print("🚀 NeuraCRM Complete CRUD Operations Demo")
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
            
            # Get a contact ID for lead creation
            print("\n📋 Getting contact for lead creation...")
            contacts_url = "http://127.0.0.1:8000/api/contacts"
            contacts_response = requests.get(contacts_url, headers=headers, timeout=10)
            
            contact_id = None
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
            
            # ===== CREATE OPERATION =====
            print("\n🆕 === CREATE OPERATION ===")
            demo_lead_title = f"CRUD Demo Lead {int(time.time())}"
            lead_data = {
                "title": demo_lead_title,
                "status": "new",
                "source": "demo",
                "contact_id": contact_id
            }
            
            leads_url = "http://127.0.0.1:8000/api/leads"
            print(f"📝 Creating lead: {demo_lead_title}")
            
            create_response = requests.post(leads_url, json=lead_data, headers=headers, timeout=10)
            
            if create_response.status_code == 200:
                created_lead = create_response.json()
                if "error" not in created_lead:
                    lead_id = created_lead.get("id")
                    print(f"✅ Lead created successfully!")
                    print(f"   ID: {lead_id}")
                    print(f"   Title: {created_lead.get('title')}")
                    print(f"   Status: {created_lead.get('status')}")
                else:
                    print(f"❌ Lead creation failed: {created_lead['error']}")
                    return False
            else:
                print(f"❌ Lead creation failed with status: {create_response.status_code}")
                return False
            
            # ===== READ OPERATION =====
            print("\n📖 === READ OPERATION ===")
            print("📋 Reading all leads...")
            
            read_response = requests.get(leads_url, headers=headers, timeout=10)
            
            if read_response.status_code == 200:
                leads_data = read_response.json()
                if isinstance(leads_data, list):
                    print(f"✅ Found {len(leads_data)} leads in database")
                    
                    # Find our created lead
                    our_lead = None
                    for lead in leads_data:
                        if lead.get("id") == lead_id:
                            our_lead = lead
                            break
                    
                    if our_lead:
                        print(f"✅ Our lead found in database:")
                        print(f"   ID: {our_lead.get('id')}")
                        print(f"   Title: {our_lead.get('title')}")
                        print(f"   Status: {our_lead.get('status')}")
                        print(f"   Source: {our_lead.get('source')}")
                    else:
                        print("❌ Our created lead not found in database")
                        return False
                else:
                    print(f"⚠️ Unexpected response format: {type(leads_data)}")
                    return False
            else:
                print(f"❌ Failed to read leads: {read_response.status_code}")
                return False
            
            # ===== UPDATE OPERATION =====
            print("\n✏️ === UPDATE OPERATION ===")
            updated_title = f"Updated {demo_lead_title}"
            update_data = {
                "title": updated_title,
                "status": "contacted",
                "source": "updated_demo"
            }
            
            update_url = f"{leads_url}/{lead_id}"
            print(f"📝 Updating lead {lead_id}...")
            print(f"   New title: {updated_title}")
            print(f"   New status: contacted")
            
            update_response = requests.put(update_url, json=update_data, headers=headers, timeout=10)
            
            if update_response.status_code == 200:
                updated_lead = update_response.json()
                if "error" not in updated_lead:
                    print(f"✅ Lead updated successfully!")
                    print(f"   ID: {updated_lead.get('id')}")
                    print(f"   Title: {updated_lead.get('title')}")
                    print(f"   Status: {updated_lead.get('status')}")
                else:
                    print(f"❌ Lead update failed: {updated_lead['error']}")
                    return False
            else:
                print(f"❌ Lead update failed with status: {update_response.status_code}")
                return False
            
            # ===== CONVERT OPERATION =====
            print("\n🔄 === CONVERT OPERATION ===")
            print(f"🔄 Converting lead {lead_id} to deal...")
            
            convert_url = f"{leads_url}/{lead_id}/convert-to-deal"
            convert_data = {
                "title": f"Deal from {updated_title}",
                "description": f"Converted from lead: {updated_title}",
                "value": 75000
            }
            
            convert_response = requests.post(convert_url, json=convert_data, headers=headers, timeout=10)
            
            if convert_response.status_code == 200:
                converted_result = convert_response.json()
                if "error" not in converted_result:
                    deal_id = converted_result.get("deal_id")
                    print(f"✅ Lead converted to deal successfully!")
                    print(f"   Deal ID: {deal_id}")
                    print(f"   Lead ID: {converted_result.get('lead_id')}")
                    print(f"   Stage ID: {converted_result.get('stage_id')}")
                else:
                    print(f"❌ Lead conversion failed: {converted_result['error']}")
                    return False
            else:
                print(f"❌ Lead conversion failed with status: {convert_response.status_code}")
                return False
            
            # ===== DELETE OPERATION =====
            print("\n🗑️ === DELETE OPERATION ===")
            print(f"🗑️ Deleting lead {lead_id}...")
            
            delete_url = f"{leads_url}/{lead_id}"
            delete_response = requests.delete(delete_url, headers=headers, timeout=10)
            
            if delete_response.status_code == 200:
                delete_result = delete_response.json()
                if "error" not in delete_result:
                    print(f"✅ Lead deleted successfully!")
                    print(f"   Deleted ID: {delete_result.get('deleted_id')}")
                    
                    # Verify deletion
                    print("🔍 Verifying deletion...")
                    verify_response = requests.get(leads_url, headers=headers, timeout=10)
                    
                    if verify_response.status_code == 200:
                        remaining_leads = verify_response.json()
                        if isinstance(remaining_leads, list):
                            lead_found = False
                            for lead in remaining_leads:
                                if lead.get("id") == lead_id:
                                    lead_found = True
                                    break
                            
                            if not lead_found:
                                print(f"✅ Lead {lead_id} successfully removed from database")
                            else:
                                print(f"❌ Lead {lead_id} still exists in database")
                                return False
                        else:
                            print(f"⚠️ Unexpected response format: {type(remaining_leads)}")
                            return False
                    else:
                        print(f"❌ Failed to verify deletion: {verify_response.status_code}")
                        return False
                else:
                    print(f"❌ Lead deletion failed: {delete_result['error']}")
                    return False
            else:
                print(f"❌ Lead deletion failed with status: {delete_response.status_code}")
                return False
            
            # ===== SUMMARY =====
            print("\n🎉 === CRUD OPERATIONS SUMMARY ===")
            print("✅ CREATE: Lead created successfully")
            print("✅ READ: Lead retrieved from database")
            print("✅ UPDATE: Lead information updated")
            print("✅ CONVERT: Lead converted to deal")
            print("✅ DELETE: Lead removed from database")
            print("\n🎯 All CRUD operations completed successfully!")
            print("   The NeuraCRM system is fully functional for lead management.")
            
            return True
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_complete_crud_demo()
    if success:
        print("\n🎉 Complete CRUD demonstration successful!")
        print("   NeuraCRM lead management is working perfectly.")
    else:
        print("\n❌ CRUD demonstration failed.")

