#!/usr/bin/env python3
"""
Complete CRUD operations test for Contacts
Tests CREATE, READ, UPDATE, DELETE operations for contacts
"""

import requests
import json
import time

def test_contacts_crud_complete():
    """Complete CRUD operations test for contacts"""
    
    print("🚀 NeuraCRM Contacts CRUD Operations Test")
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
            
            # ===== CREATE OPERATION =====
            print("\n🆕 === CREATE CONTACT ===")
            demo_contact_name = f"CRUD Demo Contact {int(time.time())}"
            contact_data = {
                "name": demo_contact_name,
                "email": f"cruddemo{int(time.time())}@example.com",
                "phone": "+1-555-CRUD-DEMO",
                "company": "CRUD Demo Company"
            }
            
            contacts_url = "http://127.0.0.1:8000/api/contacts"
            print(f"📝 Creating contact: {demo_contact_name}")
            
            create_response = requests.post(contacts_url, json=contact_data, headers=headers, timeout=10)
            
            if create_response.status_code == 200:
                created_contact = create_response.json()
                if "error" not in created_contact:
                    contact_id = created_contact.get("id")
                    print(f"✅ Contact created successfully!")
                    print(f"   ID: {contact_id}")
                    print(f"   Name: {created_contact.get('name')}")
                    print(f"   Email: {created_contact.get('email')}")
                    print(f"   Company: {created_contact.get('company')}")
                else:
                    print(f"❌ Contact creation failed: {created_contact['error']}")
                    return False
            else:
                print(f"❌ Contact creation failed with status: {create_response.status_code}")
                print(f"Response: {create_response.text}")
                return False
            
            # ===== READ OPERATION =====
            print("\n📖 === READ CONTACT ===")
            print("📋 Reading all contacts...")
            
            read_response = requests.get(contacts_url, headers=headers, timeout=10)
            
            if read_response.status_code == 200:
                contacts_data = read_response.json()
                if isinstance(contacts_data, list):
                    print(f"✅ Found {len(contacts_data)} contacts in database")
                    
                    # Find our created contact
                    our_contact = None
                    for contact in contacts_data:
                        if contact.get("id") == contact_id:
                            our_contact = contact
                            break
                    
                    if our_contact:
                        print(f"✅ Our contact found in database:")
                        print(f"   ID: {our_contact.get('id')}")
                        print(f"   Name: {our_contact.get('name')}")
                        print(f"   Email: {our_contact.get('email')}")
                        print(f"   Company: {our_contact.get('company')}")
                    else:
                        print("❌ Our created contact not found in database")
                        return False
                else:
                    print(f"⚠️ Unexpected response format: {type(contacts_data)}")
                    return False
            else:
                print(f"❌ Failed to read contacts: {read_response.status_code}")
                return False
            
            # ===== UPDATE OPERATION =====
            print("\n✏️ === UPDATE CONTACT ===")
            updated_name = f"Updated {demo_contact_name}"
            updated_email = f"updated{int(time.time())}@example.com"
            update_data = {
                "name": updated_name,
                "email": updated_email,
                "phone": "+1-555-UPDATED",
                "company": "Updated Demo Company"
            }
            
            update_url = f"{contacts_url}/{contact_id}"
            print(f"📝 Updating contact {contact_id}...")
            print(f"   New name: {updated_name}")
            print(f"   New email: {updated_email}")
            
            update_response = requests.put(update_url, json=update_data, headers=headers, timeout=10)
            
            if update_response.status_code == 200:
                updated_contact = update_response.json()
                if "error" not in updated_contact:
                    print(f"✅ Contact updated successfully!")
                    print(f"   ID: {updated_contact.get('id')}")
                    print(f"   Name: {updated_contact.get('name')}")
                    print(f"   Email: {updated_contact.get('email')}")
                    print(f"   Company: {updated_contact.get('company')}")
                else:
                    print(f"❌ Contact update failed: {updated_contact['error']}")
                    return False
            else:
                print(f"❌ Contact update failed with status: {update_response.status_code}")
                print(f"Response: {update_response.text}")
                return False
            
            # ===== CONVERT TO LEAD OPERATION =====
            print("\n🔄 === CONVERT CONTACT TO LEAD ===")
            print(f"🔄 Converting contact {contact_id} to lead...")
            
            convert_url = f"{contacts_url}/{contact_id}/convert-to-lead"
            convert_data = {
                "title": f"Lead from {updated_name}",
                "status": "new",
                "source": "contact_conversion"
            }
            
            convert_response = requests.post(convert_url, json=convert_data, headers=headers, timeout=10)
            
            if convert_response.status_code == 200:
                converted_result = convert_response.json()
                if "error" not in converted_result:
                    lead_id = converted_result.get("lead_id")
                    print(f"✅ Contact converted to lead successfully!")
                    print(f"   Lead ID: {lead_id}")
                    print(f"   Contact ID: {converted_result.get('contact_id')}")
                    print(f"   Message: {converted_result.get('message')}")
                else:
                    print(f"❌ Contact conversion failed: {converted_result['error']}")
                    return False
            else:
                print(f"❌ Contact conversion failed with status: {convert_response.status_code}")
                print(f"Response: {convert_response.text}")
                return False
            
            # ===== DELETE OPERATION =====
            print("\n🗑️ === DELETE CONTACT ===")
            print(f"🗑️ Deleting contact {contact_id}...")
            
            delete_url = f"{contacts_url}/{contact_id}"
            delete_response = requests.delete(delete_url, headers=headers, timeout=10)
            
            if delete_response.status_code == 200:
                delete_result = delete_response.json()
                if "error" not in delete_result:
                    print(f"✅ Contact deleted successfully!")
                    print(f"   Deleted ID: {delete_result.get('deleted_id', contact_id)}")
                    
                    # Verify deletion
                    print("🔍 Verifying deletion...")
                    verify_response = requests.get(contacts_url, headers=headers, timeout=10)
                    
                    if verify_response.status_code == 200:
                        remaining_contacts = verify_response.json()
                        if isinstance(remaining_contacts, list):
                            contact_found = False
                            for contact in remaining_contacts:
                                if contact.get("id") == contact_id:
                                    contact_found = True
                                    break
                            
                            if not contact_found:
                                print(f"✅ Contact {contact_id} successfully removed from database")
                            else:
                                print(f"❌ Contact {contact_id} still exists in database")
                                return False
                        else:
                            print(f"⚠️ Unexpected response format: {type(remaining_contacts)}")
                            return False
                    else:
                        print(f"❌ Failed to verify deletion: {verify_response.status_code}")
                        return False
                else:
                    print(f"❌ Contact deletion failed: {delete_result['error']}")
                    return False
            else:
                print(f"❌ Contact deletion failed with status: {delete_response.status_code}")
                print(f"Response: {delete_response.text}")
                return False
            
            # ===== SUMMARY =====
            print("\n🎉 === CONTACTS CRUD OPERATIONS SUMMARY ===")
            print("✅ CREATE: Contact created successfully")
            print("✅ READ: Contact retrieved from database")
            print("✅ UPDATE: Contact information updated")
            print("✅ CONVERT: Contact converted to lead")
            print("✅ DELETE: Contact removed from database")
            print("\n🎯 All Contacts CRUD operations completed successfully!")
            print("   The NeuraCRM system is fully functional for contact management.")
            
            return True
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_contacts_crud_complete()
    if success:
        print("\n🎉 Complete Contacts CRUD test successful!")
        print("   NeuraCRM contact management is working perfectly.")
    else:
        print("\n❌ Contacts CRUD test failed.")
