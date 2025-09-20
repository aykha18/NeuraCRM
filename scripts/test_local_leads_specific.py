#!/usr/bin/env python3
"""
Test Leads Inline Editing Specifically
=====================================

This script tests the leads inline editing functionality specifically
to debug why no leads were found in the previous test.
"""

import requests
import json
import time

def test_local_leads_specific():
    """Test leads inline editing specifically"""
    
    base_url = 'http://localhost:8000'  # Local server
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
        print('🧪 TESTING LEADS INLINE EDITING SPECIFICALLY')
        print('=' * 70)
        
        # Test 1: Get leads with detailed response
        print('\n1. 📋 TESTING LEADS ENDPOINT:')
        response = requests.get(f'{base_url}/api/leads', headers=headers)
        print(f'   Status Code: {response.status_code}')
        print(f'   Response Length: {len(response.text)}')
        
        if response.status_code == 200:
            leads = response.json()
            print(f'   ✅ Found {len(leads)} leads')
            
            if leads:
                # Show first few leads
                for i, lead in enumerate(leads[:3]):
                    print(f'   Lead {i+1}: ID={lead.get("id")}, Title="{lead.get("title", "N/A")}", Status="{lead.get("status", "N/A")}"')
                
                # Test updating the first lead
                test_lead = leads[0]
                print(f'\n   Testing update with lead ID: {test_lead["id"]}')
                
                # Test updating lead title
                original_title = test_lead.get('title', '')
                new_title = f'LOCAL LEADS TEST - {int(time.time())}'
                
                update_data = {'title': new_title}
                update_response = requests.put(f'{base_url}/api/leads/{test_lead["id"]}', 
                                             json=update_data, headers=headers)
                
                print(f'   Update Status: {update_response.status_code}')
                print(f'   Update Response: {update_response.text[:300]}...')
                
                if update_response.status_code == 200:
                    updated_lead = update_response.json()
                    print(f'   ✅ Lead title updated successfully!')
                    print(f'      Original: {original_title}')
                    print(f'      Updated: {updated_lead.get("title", "N/A")}')
                else:
                    print(f'   ❌ Failed to update lead title')
            else:
                print('   ⚠️ No leads found in database')
        else:
            print(f'   ❌ Failed to fetch leads: {response.status_code}')
            print(f'   Response: {response.text[:500]}')
        
        # Test 2: Check leads paginated endpoint
        print('\n2. 📄 TESTING LEADS PAGINATED ENDPOINT:')
        response = requests.get(f'{base_url}/api/leads/paginated', headers=headers)
        print(f'   Status Code: {response.status_code}')
        
        if response.status_code == 200:
            paginated_data = response.json()
            leads_count = paginated_data.get('total', 0)
            leads_list = paginated_data.get('data', [])
            print(f'   ✅ Paginated endpoint shows {leads_count} total leads')
            print(f'   ✅ First page has {len(leads_list)} leads')
        else:
            print(f'   ❌ Failed to fetch paginated leads: {response.status_code}')
        
        # Test 3: Check leads count endpoint
        print('\n3. 📊 TESTING LEADS COUNT ENDPOINT:')
        response = requests.get(f'{base_url}/api/stats/leads-count', headers=headers)
        print(f'   Status Code: {response.status_code}')
        
        if response.status_code == 200:
            count_data = response.json()
            print(f'   ✅ Count endpoint response: {count_data}')
        else:
            print(f'   ❌ Failed to fetch leads count: {response.status_code}')
        
        print('\n' + '=' * 70)
        print('🎉 LEADS SPECIFIC TEST COMPLETED!')
        print('=' * 70)
        
    except Exception as e:
        print(f'❌ Test failed with error: {e}')

if __name__ == "__main__":
    test_local_leads_specific()
