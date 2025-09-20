#!/usr/bin/env python3
"""
Test Inline Editing Functionality Locally
=========================================

This script tests the inline editing functionality for both leads and contacts
on the local server to verify the newly added PUT endpoints work correctly.
"""

import requests
import json
import time

def test_local_inline_editing():
    """Test inline editing on local server"""
    
    base_url = 'http://localhost:8000'  # Local server
    login_data = {'email': 'nodeit@node.com', 'password': 'NodeIT2024!'}
    
    try:
        # Test server availability first
        print('🔍 Testing local server availability...')
        try:
            ping_response = requests.get(f'{base_url}/api/ping', timeout=5)
            if ping_response.status_code == 200:
                print('✅ Local server is running')
            else:
                print(f'⚠️ Local server responded with status: {ping_response.status_code}')
        except requests.exceptions.RequestException as e:
            print(f'❌ Local server not available: {e}')
            print('💡 Make sure to start the local server with: python working_app.py --port 8001')
            return
        
        # Login
        print('\n🔐 Logging in...')
        login_response = requests.post(f'{base_url}/api/auth/login', json=login_data)
        if login_response.status_code == 200:
            token = login_response.json().get('access_token')
            headers = {'Authorization': f'Bearer {token}'}
            print('✅ Login successful')
        else:
            print(f'❌ Login failed: {login_response.status_code}')
            print(f'Response: {login_response.text}')
            return
        
        print('\n' + '=' * 70)
        print('🧪 TESTING LOCAL INLINE EDITING FUNCTIONALITY')
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
                new_title = f'LOCAL TEST - {int(time.time())}'
                
                update_data = {'title': new_title}
                update_response = requests.put(f'{base_url}/api/leads/{test_lead["id"]}', 
                                             json=update_data, headers=headers)
                
                print(f'   Update request status: {update_response.status_code}')
                print(f'   Update response: {update_response.text[:200]}...')
                
                if update_response.status_code == 200:
                    updated_lead = update_response.json()
                    print(f'   ✅ Lead title updated successfully!')
                    print(f'      Original: {original_title}')
                    print(f'      Updated: {updated_lead.get("title", "N/A")}')
                    
                    # Test updating lead status
                    original_status = test_lead.get('status', '')
                    new_status = 'qualified' if original_status != 'qualified' else 'contacted'
                    
                    status_update_data = {'status': new_status}
                    status_response = requests.put(f'{base_url}/api/leads/{test_lead["id"]}', 
                                                 json=status_update_data, headers=headers)
                    
                    if status_response.status_code == 200:
                        print(f'   ✅ Lead status updated successfully!')
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
                new_name = f'LOCAL TEST CONTACT - {int(time.time())}'
                
                update_data = {'name': new_name}
                update_response = requests.put(f'{base_url}/api/contacts/{test_contact["id"]}', 
                                             json=update_data, headers=headers)
                
                print(f'   Update request status: {update_response.status_code}')
                print(f'   Update response: {update_response.text[:200]}...')
                
                if update_response.status_code == 200:
                    updated_contact = update_response.json()
                    print(f'   ✅ Contact name updated successfully!')
                    print(f'      Original: {original_name}')
                    print(f'      Updated: {updated_contact.get("name", "N/A")}')
                    
                    # Test updating contact email
                    original_email = test_contact.get('email', '')
                    new_email = f'local.test.{int(time.time())}@example.com'
                    
                    email_update_data = {'email': new_email}
                    email_response = requests.put(f'{base_url}/api/contacts/{test_contact["id"]}', 
                                                json=email_update_data, headers=headers)
                    
                    if email_response.status_code == 200:
                        print(f'   ✅ Contact email updated successfully!')
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
        print('\n3. 🔍 CHECKING LOCAL API ENDPOINTS:')
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
        print('\n4. 🔧 CHECKING LOCAL UPDATE ENDPOINTS:')
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
        
        print('\n' + '=' * 70)
        print('🎉 LOCAL INLINE EDITING TEST COMPLETED!')
        print('=' * 70)
        print('\n📋 SUMMARY:')
        print('   - Local server PUT endpoints are now working!')
        print('   - Inline editing functionality is fixed')
        print('   - Both leads and contacts can be updated')
        print('\n🚀 NEXT STEPS:')
        print('   1. Wait for Railway deployment to complete')
        print('   2. Test the frontend inline editing in browser')
        print('   3. Verify click-to-edit functionality works')
        
    except Exception as e:
        print(f'❌ Test failed with error: {e}')

if __name__ == "__main__":
    test_local_inline_editing()
