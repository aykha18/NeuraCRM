#!/usr/bin/env python3
"""
Test Local Telephony Data
========================

This script tests the local telephony database to see if there's data available.
"""

import requests
import json

def test_local_telephony_data():
    """Test local telephony database data"""
    
    base_url = 'http://127.0.0.1:8000'
    login_data = {'email': 'nodeit@node.com', 'password': 'NodeIT2024!'}
    
    try:
        # Login
        login_response = requests.post(f'{base_url}/api/auth/login', json=login_data)
        token = login_response.json().get('access_token')
        headers = {'Authorization': f'Bearer {token}'}
        
        print('🔍 Testing LOCAL Database Data')
        print('=' * 40)
        
        # Test dashboard to see if there's any data
        print('\n1. 📊 Dashboard:')
        response = requests.get(f'{base_url}/api/telephony/dashboard', headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f'   Active calls: {data.get("active_calls", 0)}')
            print(f'   Available agents: {data.get("available_agents", 0)}')
            print(f'   Recent calls: {len(data.get("recent_calls", []))}')
            print(f'   Agent status: {len(data.get("agent_status", []))}')
        else:
            print(f'   ❌ Dashboard error: {response.status_code}')
        
        # Test providers
        print('\n2. 🔧 Providers:')
        response = requests.get(f'{base_url}/api/telephony/providers', headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f'   Providers count: {len(data)}')
            if len(data) > 0:
                print(f'   First provider: {data[0].get("name", "Unknown")}')
        else:
            print(f'   ❌ Providers error: {response.status_code}')
        
        # Test calls
        print('\n3. 📞 Calls:')
        response = requests.get(f'{base_url}/api/telephony/calls?limit=5', headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f'   Calls count: {len(data)}')
        else:
            print(f'   ❌ Calls error: {response.status_code}')
        
        # Test queues
        print('\n4. 🎧 Queues:')
        response = requests.get(f'{base_url}/api/telephony/queues', headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f'   Queues count: {len(data)}')
        else:
            print(f'   ❌ Queues error: {response.status_code}')
        
        # Test queue members
        print('\n5. 👥 Queue Members:')
        response = requests.get(f'{base_url}/api/telephony/queue-members', headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f'   Queue members count: {len(data)}')
        else:
            print(f'   ❌ Queue members error: {response.status_code}')
        
        print('\n' + '=' * 40)
        print('🎯 SUMMARY:')
        print('   If all counts are 0, the local database needs telephony data')
        print('   If API endpoints work (return arrays), the fix is successful')
        
    except Exception as e:
        print(f'❌ Test failed: {e}')
        print('Make sure the local server is running on port 8000')

if __name__ == "__main__":
    test_local_telephony_data()
