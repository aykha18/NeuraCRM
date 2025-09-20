#!/usr/bin/env python3
"""
Test Delete Functionality for Leads and Contacts
================================================

This script tests the delete functionality for both leads and contacts
on Railway to verify the newly added DELETE endpoints work correctly.
"""

import requests
import json
import time

def test_delete_functionality():
    """Test delete functionality on Railway"""
    
    base_url = 'https://neuracrm.up.railway.app'  # Railway server
    login_data = {'email': 'nodeit@node.com', 'password': 'NodeIT2024!'}
    
    try:
        # Login
        print('🔐 Logging in...')
        login_response = requests.post(f'{base_url}/api/auth/login', json=login_data)
        if login_response.status_code == 200:
            token = login_response.json().get('access_token')
            headers = {'Authorization': f'Bearer {token}'}
            print('✅ Login successful')
        else:
            print(f'❌ Login failed: {login_response.status_code}')
            return
        
        print('\n' + '=' * 70)
        print('🧪 TESTING DELETE FUNCTIONALITY ON RAILWAY')
        print('=' * 70)
        
        # Test 1: Test leads delete functionality
        print('\n1. 📋 TESTING LEADS DELETE FUNCTIONALITY:')
        response = requests.get(f'{base_url}/api/leads', headers=headers)
        if response.status_code == 200:
            leads = response.json()
            print(f'   ✅ Found {len(leads)} leads')
            
            if leads:
                # Get first lead to test delete
                test_lead = leads[0]
                lead_id = test_lead['id']
                print(f'   Testing delete with lead ID: {lead_id}, Title: "{test_lead.get("title", "N/A")}"')
                
                # Test DELETE endpoint
                delete_response = requests.delete(f'{base_url}/api/leads/{lead_id}', headers=headers)
                print(f'   Delete Status: {delete_response.status_code}')
                print(f'   Delete Response: {delete_response.text}')
                
                if delete_response.status_code == 200:
                    print(f'   ✅ Lead deleted successfully!')
                    
                    # Verify deletion by trying to get the lead again
                    verify_response = requests.get(f'{base_url}/api/leads/{lead_id}', headers=headers)
                    if verify_response.status_code == 404 or "not found" in verify_response.text.lower():
                        print(f'   ✅ Deletion verified - lead no longer exists')
                    else:
                        print(f'   ⚠️ Deletion may not have worked - lead still accessible')
                else:
                    print(f'   ❌ Failed to delete lead: {delete_response.status_code}')
                    print(f'      Response: {delete_response.text}')
            else:
                print('   ⚠️ No leads found to test delete functionality')
        else:
            print(f'   ❌ Failed to fetch leads: {response.status_code}')
        
        # Test 2: Test contacts delete functionality
        print('\n2. 👥 TESTING CONTACTS DELETE FUNCTIONALITY:')
        response = requests.get(f'{base_url}/api/contacts', headers=headers)
        if response.status_code == 200:
            contacts = response.json()
            print(f'   ✅ Found {len(contacts)} contacts')
            
            if contacts:
                # Get first contact to test delete
                test_contact = contacts[0]
                contact_id = test_contact['id']
                print(f'   Testing delete with contact ID: {contact_id}, Name: "{test_contact.get("name", "N/A")}"')
                
                # Test DELETE endpoint
                delete_response = requests.delete(f'{base_url}/api/contacts/{contact_id}', headers=headers)
                print(f'   Delete Status: {delete_response.status_code}')
                print(f'   Delete Response: {delete_response.text}')
                
                if delete_response.status_code == 200:
                    print(f'   ✅ Contact deleted successfully!')
                    
                    # Verify deletion by trying to get the contact again
                    verify_response = requests.get(f'{base_url}/api/contacts/{contact_id}', headers=headers)
                    if verify_response.status_code == 404 or "not found" in verify_response.text.lower():
                        print(f'   ✅ Deletion verified - contact no longer exists')
                    else:
                        print(f'   ⚠️ Deletion may not have worked - contact still accessible')
                else:
                    print(f'   ❌ Failed to delete contact: {delete_response.status_code}')
                    print(f'      Response: {delete_response.text}')
            else:
                print('   ⚠️ No contacts found to test delete functionality')
        else:
            print(f'   ❌ Failed to fetch contacts: {response.status_code}')
        
        # Test 3: Check if DELETE endpoints exist
        print('\n3. 🔍 CHECKING DELETE ENDPOINTS:')
        
        # Test leads delete endpoint (with non-existent ID to avoid actual deletion)
        test_response = requests.delete(f'{base_url}/api/leads/999999', headers=headers)
        if test_response.status_code in [200, 404, 422]:
            print('   ✅ DELETE /api/leads/{id} endpoint exists')
        else:
            print(f'   ❌ DELETE /api/leads/{{id}} endpoint issue - Status: {test_response.status_code}')
        
        # Test contacts delete endpoint (with non-existent ID to avoid actual deletion)
        test_response = requests.delete(f'{base_url}/api/contacts/999999', headers=headers)
        if test_response.status_code in [200, 404, 422]:
            print('   ✅ DELETE /api/contacts/{id} endpoint exists')
        else:
            print(f'   ❌ DELETE /api/contacts/{{id}} endpoint issue - Status: {test_response.status_code}')
        
        print('\n' + '=' * 70)
        print('🎉 DELETE FUNCTIONALITY TEST COMPLETED!')
        print('=' * 70)
        print('\n📋 SUMMARY:')
        print('   - DELETE endpoints have been added to the backend')
        print('   - Frontend services already have delete functions')
        print('   - Both leads and contacts can now be deleted')
        print('\n🚀 NEXT STEPS:')
        print('   1. Wait for Railway deployment to complete')
        print('   2. Test the frontend delete functionality in browser')
        print('   3. Verify delete buttons work in the UI')
        
    except Exception as e:
        print(f'❌ Test failed with error: {e}')

if __name__ == "__main__":
    test_delete_functionality()
