#!/usr/bin/env python3
"""
Check Current Stages in Railway
==============================

This script checks the current stages in the Railway database
to understand the pipeline structure.
"""

import requests
import json

def check_current_stages():
    """Check current stages in Railway"""
    
    base_url = 'https://neuracrm.up.railway.app'
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
        
        # Get stages
        print('\n📋 Getting current stages...')
        stages_response = requests.get(f'{base_url}/api/kanban/columns', headers=headers)
        if stages_response.status_code == 200:
            stages = stages_response.json()
            print(f'\n🎯 Current Stages ({len(stages)} total):')
            print('=' * 50)
            for stage in stages:
                order = stage.get('order', '?')
                name = stage.get('name', 'Unknown')
                deal_count = stage.get('deal_count', 0)
                print(f'  {order}. {name} ({deal_count} deals)')
            
            print('\n💡 Analysis:')
            if len(stages) > 6:
                print('  ⚠️  Many stages detected - horizontal scrolling will be required')
                print('  💭 Consider implementing stage management alternatives')
            else:
                print('  ✅ Manageable number of stages')
                
        else:
            print(f'❌ Error getting stages: {stages_response.status_code}')
            print(f'Response: {stages_response.text}')
            
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    check_current_stages()
