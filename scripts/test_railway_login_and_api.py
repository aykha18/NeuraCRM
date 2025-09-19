#!/usr/bin/env python3
"""
Test Railway Login and API
=========================

This script tests Railway login and API endpoints to identify the issue.
"""

import requests
import json
from datetime import datetime

# Railway API Configuration
RAILWAY_API_BASE = "https://neuracrm.up.railway.app"

def test_railway_login_and_api():
    """Test Railway login and API endpoints"""
    print("🔐 Testing Railway Login and API")
    print("=" * 60)
    
    # Step 1: Login
    login_data = {
        "email": "nodeit@node.com",
        "password": "NodeIT2024!"
    }
    
    print(f"📡 Attempting login to {RAILWAY_API_BASE}/api/auth/login")
    try:
        login_response = requests.post(f"{RAILWAY_API_BASE}/api/auth/login", json=login_data)
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get("access_token")
            print(f"✅ Login successful!")
            print(f"Token type: {token_data.get('token_type')}")
            print(f"Token preview: {token[:50]}..." if token else "No token")
            
            # Step 2: Test authenticated endpoints
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            print(f"\n📊 Testing Support API Endpoints:")
            print("-" * 40)
            
            # Test user info
            print(f"\n👤 Testing /api/auth/me:")
            me_response = requests.get(f"{RAILWAY_API_BASE}/api/auth/me", headers=headers)
            print(f"  Status: {me_response.status_code}")
            if me_response.status_code == 200:
                me_data = me_response.json()
                print(f"  User: {me_data.get('name')} ({me_data.get('email')})")
                print(f"  Organization ID: {me_data.get('organization_id')}")
                org_id = me_data.get('organization_id')
            else:
                print(f"  Error: {me_response.text}")
                return
            
            # Test support tickets
            print(f"\n🎫 Testing /api/support/tickets:")
            tickets_response = requests.get(f"{RAILWAY_API_BASE}/api/support/tickets", headers=headers)
            print(f"  Status: {tickets_response.status_code}")
            if tickets_response.status_code == 200:
                tickets_data = tickets_response.json()
                if isinstance(tickets_data, list):
                    print(f"  ✅ Returns {len(tickets_data)} tickets")
                    if len(tickets_data) > 0:
                        print(f"  Sample ticket: {tickets_data[0].get('title', 'No title')} ({tickets_data[0].get('status', 'No status')})")
                elif isinstance(tickets_data, dict):
                    print(f"  ✅ Returns object with keys: {list(tickets_data.keys())}")
                else:
                    print(f"  ✅ Returns: {tickets_data}")
            else:
                print(f"  ❌ Error: {tickets_response.text}")
            
            # Test knowledge base
            print(f"\n📚 Testing /api/support/knowledge-base:")
            kb_response = requests.get(f"{RAILWAY_API_BASE}/api/support/knowledge-base", headers=headers)
            print(f"  Status: {kb_response.status_code}")
            if kb_response.status_code == 200:
                kb_data = kb_response.json()
                if isinstance(kb_data, list):
                    print(f"  ✅ Returns {len(kb_data)} articles")
                    if len(kb_data) > 0:
                        print(f"  Sample article: {kb_data[0].get('title', 'No title')}")
                elif isinstance(kb_data, dict):
                    print(f"  ✅ Returns object with keys: {list(kb_data.keys())}")
                else:
                    print(f"  ✅ Returns: {kb_data}")
            else:
                print(f"  ❌ Error: {kb_response.text}")
            
            # Test surveys
            print(f"\n📊 Testing /api/support/surveys:")
            surveys_response = requests.get(f"{RAILWAY_API_BASE}/api/support/surveys", headers=headers)
            print(f"  Status: {surveys_response.status_code}")
            if surveys_response.status_code == 200:
                surveys_data = surveys_response.json()
                if isinstance(surveys_data, list):
                    print(f"  ✅ Returns {len(surveys_data)} surveys")
                    if len(surveys_data) > 0:
                        print(f"  Sample survey: {surveys_data[0].get('customer_name', 'No name')} - Rating {surveys_data[0].get('rating', 'No rating')}")
                elif isinstance(surveys_data, dict):
                    print(f"  ✅ Returns object with keys: {list(surveys_data.keys())}")
                else:
                    print(f"  ✅ Returns: {surveys_data}")
            else:
                print(f"  ❌ Error: {surveys_response.text}")
            
            # Test support analytics
            print(f"\n📈 Testing /api/support/analytics/dashboard:")
            analytics_response = requests.get(f"{RAILWAY_API_BASE}/api/support/analytics/dashboard", headers=headers)
            print(f"  Status: {analytics_response.status_code}")
            if analytics_response.status_code == 200:
                analytics_data = analytics_response.json()
                if isinstance(analytics_data, dict):
                    print(f"  ✅ Returns analytics with keys: {list(analytics_data.keys())}")
                    if 'total_tickets' in analytics_data:
                        print(f"  Total tickets: {analytics_data['total_tickets']}")
                    if 'open_tickets' in analytics_data:
                        print(f"  Open tickets: {analytics_data['open_tickets']}")
                else:
                    print(f"  ✅ Returns: {analytics_data}")
            else:
                print(f"  ❌ Error: {analytics_response.text}")
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_railway_login_and_api()
