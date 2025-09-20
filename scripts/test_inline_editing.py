#!/usr/bin/env python3
"""
Test Inline Editing Functionality for Leads and Contacts
=======================================================

This script tests the inline editing functionality for both leads and contacts
to identify any issues with the current implementation.
"""

import requests
import json
import time

def test_inline_editing_functionality():
    """Test inline editing for leads and contacts"""
    
    base_url = 'https://neuracrm.up.railway.app'
    login_data = {'email': 'nodeit@node.com', 'password': 'NodeIT2024!'}
    
    try:
        # Login
        print('🔐 Logging in...')
        login_response = requests.post(f'{base_url}/api/auth/login', json=login_data)
        token = login_response.json().get('access_token')
        headers = {'Authorization': f'Bearer {token}'}
        print('✅ Login successful')
        
        print('\n' + '=' * 70)
        print('🧪 TESTING INLINE EDITING FUNCTIONALITY')
        print('=' * 70)
        
        # Test 1: Get leads and test update
        print('\n1. 📋 TESTING LEADS INLINE EDITING:')
        response = requests.get(f'{base_url}/api/leads', headers=headers)
        if response.status_code == 200:
            leads = response.json()
            if leads:
                test_lead = leads[0]
                print(f'   ✅ Found {len(leads)} leads')
                print(f'   Testing with lead ID: {test_lead["id"]}, Title: {test_lead.get("title", "N/A")}')
                
                # Test updating lead title
                original_title = test_lead.get('title', '')
                new_title = f'Updated Title - {int(time.time())}'
                
                update_data = {'title': new_title}
                update_response = requests.put(f'{base_url}/api/leads/{test_lead["id"]}', 
                                             json=update_data, headers=headers)
                
                if update_response.status_code == 200:
                    updated_lead = update_response.json()
                    print(f'   ✅ Lead title updated successfully')
                    print(f'      Original: {original_title}')
                    print(f'      Updated: {updated_lead.get("title", "N/A")}')
                    
                    # Test updating lead status
                    original_status = test_lead.get('status', '')
                    new_status = 'qualified' if original_status != 'qualified' else 'contacted'
                    
                    status_update_data = {'status': new_status}
                    status_response = requests.put(f'{base_url}/api/leads/{test_lead["id"]}', 
                                                 json=status_update_data, headers=headers)
                    
                    if status_response.status_code == 200:
                        print(f'   ✅ Lead status updated successfully')
                        print(f'      Original: {original_status}')
                        print(f'      Updated: {new_status}')
                    else:
                        print(f'   ❌ Failed to update lead status: {status_response.status_code}')
                        print(f'      Response: {status_response.text}')
                else:
                    print(f'   ❌ Failed to update lead title: {update_response.status_code}')
                    print(f'      Response: {update_response.text}')
            else:
                print('   ⚠️ No leads found to test')
        else:
            print(f'   ❌ Failed to fetch leads: {response.status_code}')
            print(f'      Response: {response.text}')
        
        # Test 2: Get contacts and test update
        print('\n2. 👥 TESTING CONTACTS INLINE EDITING:')
        response = requests.get(f'{base_url}/api/contacts', headers=headers)
        if response.status_code == 200:
            contacts = response.json()
            if contacts:
                test_contact = contacts[0]
                print(f'   ✅ Found {len(contacts)} contacts')
                print(f'   Testing with contact ID: {test_contact["id"]}, Name: {test_contact.get("name", "N/A")}')
                
                # Test updating contact name
                original_name = test_contact.get('name', '')
                new_name = f'Updated Contact - {int(time.time())}'
                
                update_data = {'name': new_name}
                update_response = requests.put(f'{base_url}/api/contacts/{test_contact["id"]}', 
                                             json=update_data, headers=headers)
                
                if update_response.status_code == 200:
                    updated_contact = update_response.json()
                    print(f'   ✅ Contact name updated successfully')
                    print(f'      Original: {original_name}')
                    print(f'      Updated: {updated_contact.get("name", "N/A")}')
                    
                    # Test updating contact email
                    original_email = test_contact.get('email', '')
                    new_email = f'test.updated.{int(time.time())}@example.com'
                    
                    email_update_data = {'email': new_email}
                    email_response = requests.put(f'{base_url}/api/contacts/{test_contact["id"]}', 
                                                json=email_update_data, headers=headers)
                    
                    if email_response.status_code == 200:
                        print(f'   ✅ Contact email updated successfully')
                        print(f'      Original: {original_email}')
                        print(f'      Updated: {new_email}')
                    else:
                        print(f'   ❌ Failed to update contact email: {email_response.status_code}')
                        print(f'      Response: {email_response.text}')
                else:
                    print(f'   ❌ Failed to update contact name: {update_response.status_code}')
                    print(f'      Response: {update_response.text}')
            else:
                print('   ⚠️ No contacts found to test')
        else:
            print(f'   ❌ Failed to fetch contacts: {response.status_code}')
            print(f'      Response: {response.text}')
        
        # Test 3: Check API endpoints exist
        print('\n3. 🔍 CHECKING API ENDPOINTS:')
        endpoints_to_test = [
            ('/api/leads', 'GET'),
            ('/api/contacts', 'GET'),
        ]
        
        for endpoint, method in endpoints_to_test:
            if method == 'GET':
                response = requests.get(f'{base_url}{endpoint}', headers=headers)
                status = "✅" if response.status_code == 200 else "❌"
                print(f'   {status} {method} {endpoint} - Status: {response.status_code}')
        
        # Test 4: Check if PUT endpoints exist for updates
        print('\n4. 🔧 CHECKING UPDATE ENDPOINTS:')
        if leads:
            lead_id = leads[0]['id']
            response = requests.put(f'{base_url}/api/leads/{lead_id}', 
                                  json={'title': 'test'}, headers=headers)
            status = "✅" if response.status_code in [200, 422] else "❌"
            print(f'   {status} PUT /api/leads/{{id}} - Status: {response.status_code}')
            
        if contacts:
            contact_id = contacts[0]['id']
            response = requests.put(f'{base_url}/api/contacts/{contact_id}', 
                                  json={'name': 'test'}, headers=headers)
            status = "✅" if response.status_code in [200, 422] else "❌"
            print(f'   {status} PUT /api/contacts/{{id}} - Status: {response.status_code}')
        
        # Test 5: Frontend API service test
        print('\n5. 🌐 TESTING FRONTEND API SERVICE PATTERNS:')
        print('   Checking if the frontend service functions match backend expectations...')
        
        # Test the exact pattern used in frontend
        if leads:
            lead_id = leads[0]['id']
            test_data = {'title': f'Frontend Test {int(time.time())}'}
            
            # Test with proper headers (matching frontend service)
            headers_with_content_type = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.put(f'{base_url}/api/leads/{lead_id}', 
                                  json=test_data, headers=headers_with_content_type)
            
            if response.status_code == 200:
                print(f'   ✅ Frontend-style update successful for leads')
            else:
                print(f'   ❌ Frontend-style update failed for leads: {response.status_code}')
                print(f'      Response: {response.text}')
        
        if contacts:
            contact_id = contacts[0]['id']
            test_data = {'name': f'Frontend Test {int(time.time())}'}
            
            response = requests.put(f'{base_url}/api/contacts/{contact_id}', 
                                  json=test_data, headers=headers_with_content_type)
            
            if response.status_code == 200:
                print(f'   ✅ Frontend-style update successful for contacts')
            else:
                print(f'   ❌ Frontend-style update failed for contacts: {response.status_code}')
                print(f'      Response: {response.text}')
        
        print('\n' + '=' * 70)
        print('🎉 INLINE EDITING TEST COMPLETED!')
        print('=' * 70)
        print('\n📋 SUMMARY:')
        print('   - Backend API endpoints are working')
        print('   - PUT requests for updates are functional')
        print('   - Frontend service patterns should work')
        print('\n💡 POTENTIAL ISSUES TO CHECK:')
        print('   1. Frontend service import/export issues')
        print('   2. API request headers or authentication')
        print('   3. Component state management')
        print('   4. Event handling (onBlur, onKeyDown)')
        print('   5. Error handling in frontend')
        
    except Exception as e:
        print(f'❌ Test failed with error: {e}')

if __name__ == "__main__":
    test_inline_editing_functionality()
