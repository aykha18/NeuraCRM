#!/usr/bin/env python3
"""
Test Telephony API Response Format
==================================

This script tests the telephony API endpoints to check response formats
and identify why the frontend is getting filter errors.
"""

import requests
import json

def test_telephony_apis():
    """Test all telephony API endpoints for response format issues"""
    
    base_url = 'https://neuracrm.up.railway.app'
    login_data = {'email': 'nodeit@node.com', 'password': 'NodeIT2024!'}
    
    try:
        # Login
        login_response = requests.post(f'{base_url}/api/auth/login', json=login_data)
        token = login_response.json().get('access_token')
        headers = {'Authorization': f'Bearer {token}'}
        
        print('🔍 Testing Telephony API Response Formats')
        print('=' * 50)
        
        # Test dashboard
        print('\n1. 📊 Dashboard API:')
        response = requests.get(f'{base_url}/api/telephony/dashboard', headers=headers)
        print(f'   Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'   Response Type: {type(data)}')
            if isinstance(data, dict):
                print(f'   Keys: {list(data.keys())}')
                if 'recent_calls' in data:
                    recent_calls = data['recent_calls']
                    print(f'   Recent calls type: {type(recent_calls)}')
                    if isinstance(recent_calls, list):
                        print(f'   Recent calls length: {len(recent_calls)}')
                    else:
                        print(f'   ❌ Recent calls is not a list!')
                        print(f'   Recent calls value: {recent_calls}')
                if 'agent_status' in data:
                    agent_status = data['agent_status']
                    print(f'   Agent status type: {type(agent_status)}')
                    if isinstance(agent_status, list):
                        print(f'   Agent status length: {len(agent_status)}')
                    else:
                        print(f'   ❌ Agent status is not a list!')
                        print(f'   Agent status value: {agent_status}')
            else:
                print(f'   ❌ Dashboard response is not a dictionary!')
        else:
            print(f'   ❌ Error: {response.json()}')
        
        # Test calls
        print('\n2. 📞 Calls API:')
        response = requests.get(f'{base_url}/api/telephony/calls?limit=10', headers=headers)
        print(f'   Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'   Response Type: {type(data)}')
            if isinstance(data, list):
                print(f'   Calls count: {len(data)}')
                if len(data) > 0:
                    print(f'   First call keys: {list(data[0].keys())}')
            else:
                print(f'   ❌ Calls response is not a list!')
                print(f'   Calls value: {data}')
        else:
            print(f'   ❌ Error: {response.json()}')
        
        # Test queues
        print('\n3. 🎧 Queues API:')
        response = requests.get(f'{base_url}/api/telephony/queues', headers=headers)
        print(f'   Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'   Response Type: {type(data)}')
            if isinstance(data, list):
                print(f'   Queues count: {len(data)}')
            else:
                print(f'   ❌ Queues response is not a list!')
                print(f'   Queues value: {data}')
        else:
            print(f'   ❌ Error: {response.json()}')
        
        # Test queue members
        print('\n4. 👥 Queue Members API:')
        response = requests.get(f'{base_url}/api/telephony/queue-members', headers=headers)
        print(f'   Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'   Response Type: {type(data)}')
            if isinstance(data, list):
                print(f'   Members count: {len(data)}')
            else:
                print(f'   ❌ Queue members response is not a list!')
                print(f'   Queue members value: {data}')
        else:
            print(f'   ❌ Error: {response.json()}')
        
        # Test providers
        print('\n5. 🔧 Providers API:')
        response = requests.get(f'{base_url}/api/telephony/providers', headers=headers)
        print(f'   Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'   Response Type: {type(data)}')
            if isinstance(data, list):
                print(f'   Providers count: {len(data)}')
            else:
                print(f'   ❌ Providers response is not a list!')
                print(f'   Providers value: {data}')
        else:
            print(f'   ❌ Error: {response.json()}')
        
        print('\n' + '=' * 50)
        print('🎯 SUMMARY:')
        print('   Check above for any ❌ errors that indicate wrong response formats')
        print('   Frontend expects arrays but might be getting objects or other types')
        
    except Exception as e:
        print(f'❌ Test failed: {e}')

if __name__ == "__main__":
    test_telephony_apis()
