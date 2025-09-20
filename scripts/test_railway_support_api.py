#!/usr/bin/env python3
"""
Test Railway Support API
========================

This script tests the Railway support API endpoints directly to identify the issue.
"""

import requests
import json

import sys
import os

# Add the scripts directory to the path to import db_config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from db_config import get_railway_db_config, validate_config
from datetime import datetime

# Railway API Configuration
RAILWAY_API_BASE = "https://neuracrm.up.railway.app"

def get_auth_token():
    """Get authentication token for Railway"""
    login_data = {
        "email": "nodeit@node.com",
        "password": "NodeIT2024!"
    }
    
    try:
        response = requests.post(f"{RAILWAY_API_BASE}/api/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get("access_token")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_support_endpoints():
    """Test support API endpoints"""
    token = get_auth_token()
    if not token:
        print("❌ Cannot get authentication token")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("🔐 Authentication successful")
    print("=" * 60)
    
    # Test endpoints
    endpoints_to_test = [
        ("/api/support/tickets", "Support Tickets"),
        ("/api/support/knowledge-base", "Knowledge Base"),
        ("/api/support/surveys", "Surveys"),
        ("/api/support/analytics/dashboard", "Support Analytics"),
        ("/api/auth/me", "Current User Info")
    ]
    
    for endpoint, name in endpoints_to_test:
        try:
            print(f"\n📡 Testing {name} ({endpoint}):")
            response = requests.get(f"{RAILWAY_API_BASE}{endpoint}", headers=headers)
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"  ✅ Returns {len(data)} items")
                        if len(data) > 0:
                            print(f"  Sample item keys: {list(data[0].keys()) if data[0] else 'Empty'}")
                    elif isinstance(data, dict):
                        print(f"  ✅ Returns object with keys: {list(data.keys())}")
                        if 'ticket_count' in data:
                            print(f"  Ticket count: {data['ticket_count']}")
                        if 'total_tickets' in data:
                            print(f"  Total tickets: {data['total_tickets']}")
                    else:
                        print(f"  ✅ Returns: {data}")
                except json.JSONDecodeError:
                    print(f"  ✅ Returns non-JSON data: {response.text[:100]}...")
            else:
                print(f"  ❌ Error: {response.text}")
                
        except Exception as e:
            print(f"  ❌ Request failed: {e}")

def test_direct_database_query():
    """Test direct database query to verify data exists"""
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    
    # Railway Database Configuration
    # Railway DB config now loaded from environment variables
    
    try:
        print("\n🔍 DIRECT DATABASE QUERY:")
        print("=" * 60)
        
        conn = psycopg2.connect(**get_railway_db_config())
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check user info
        cursor.execute("SELECT id, name, email, organization_id FROM users WHERE email = 'nodeit@node.com'")
        user = cursor.fetchone()
        if user:
            print(f"👤 User: {user[1]} (ID: {user[0]}) -> Organization: {user[3]}")
            org_id = user[3]
            
            # Check support tickets for this organization
            cursor.execute("SELECT COUNT(*) FROM support_tickets WHERE organization_id = %s", (org_id,))
            ticket_count = cursor.fetchone()[0]
            print(f"🎫 Support tickets for org {org_id}: {ticket_count}")
            
            # Check knowledge base for this organization
            cursor.execute("SELECT COUNT(*) FROM knowledge_base_articles WHERE organization_id = %s", (org_id,))
            kb_count = cursor.fetchone()[0]
            print(f"📚 Knowledge base articles for org {org_id}: {kb_count}")
            
            # Check surveys for this organization
            cursor.execute("SELECT COUNT(*) FROM customer_satisfaction_surveys WHERE organization_id = %s", (org_id,))
            survey_count = cursor.fetchone()[0]
            print(f"📊 Surveys for org {org_id}: {survey_count}")
            
            # Show sample tickets
            if ticket_count > 0:
                cursor.execute("""
                    SELECT id, title, status, priority, created_at 
                    FROM support_tickets 
                    WHERE organization_id = %s 
                    ORDER BY created_at DESC 
                    LIMIT 3
                """, (org_id,))
                sample_tickets = cursor.fetchall()
                print(f"\n📋 Sample tickets:")
                for ticket in sample_tickets:
                    print(f"  - ID {ticket[0]}: {ticket[1]} ({ticket[2]}, {ticket[3]}) - {ticket[4]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database query error: {e}")

if __name__ == "__main__":
    test_support_endpoints()
    test_direct_database_query()
