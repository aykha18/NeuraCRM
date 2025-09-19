#!/usr/bin/env python3
"""
Test Railway Telephony Module
============================

This script tests the telephony module deployment on Railway database.

Usage:
    python scripts/test_railway_telephony.py
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import requests
import json

# Railway Database Configuration
RAILWAY_DB_CONFIG = {
    'host': 'nozomi.proxy.rlwy.net',
    'database': 'railway',
    'user': 'postgres',
    'password': 'xxxxxxxx',
    'port': 49967
}

# Local API Configuration
API_BASE_URL = "http://127.0.0.1:8000"

def test_database_connection():
    """Test Railway database connection and telephony tables"""
    print("🔍 Testing Railway Database Connection...")
    
    try:
        conn = psycopg2.connect(**RAILWAY_DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check telephony tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND (table_name LIKE '%call%' OR table_name LIKE '%pbx%')
            ORDER BY table_name
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        print(f"✅ Found {len(tables)} telephony tables:")
        for table in tables:
            print(f"   📋 {table}")
        
        # Check table structures
        print("\n🔍 Checking table structures...")
        for table in tables:
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = '{table}'
                ORDER BY ordinal_position
                LIMIT 5
            """)
            columns = cursor.fetchall()
            print(f"   📊 {table}: {len(columns)} columns (showing first 5)")
            for col in columns:
                print(f"      - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_api_endpoints():
    """Test telephony API endpoints"""
    print("\n🌐 Testing Telephony API Endpoints...")
    
    # Test credentials
    login_data = {
        "email": "nodeit@node.com",
        "password": "NodeIT2024!"
    }
    
    try:
        # Login to get token
        print("🔐 Authenticating...")
        login_response = requests.post(f"{API_BASE_URL}/api/auth/login", json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
        
        token = login_response.json().get('access_token')
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Authentication successful")
        
        # Test telephony endpoints
        endpoints = [
            ("/api/telephony/dashboard", "GET", "Call Center Dashboard"),
            ("/api/telephony/providers", "GET", "PBX Providers"),
        ]
        
        for endpoint, method, description in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{API_BASE_URL}{endpoint}", headers=headers)
                else:
                    response = requests.post(f"{API_BASE_URL}{endpoint}", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {description}: OK")
                    if isinstance(data, dict):
                        print(f"   📊 Response keys: {list(data.keys())}")
                    elif isinstance(data, list):
                        print(f"   📊 Response items: {len(data)}")
                else:
                    print(f"❌ {description}: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"❌ {description}: Error - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_telephony_functionality():
    """Test basic telephony functionality"""
    print("\n📞 Testing Telephony Functionality...")
    
    try:
        conn = psycopg2.connect(**RAILWAY_DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Test inserting sample data
        print("📝 Testing data insertion...")
        
        # Get first organization and user
        cursor.execute("SELECT id FROM organizations LIMIT 1")
        org_result = cursor.fetchone()
        if not org_result:
            print("❌ No organizations found in database")
            return False
        
        org_id = org_result[0]
        
        cursor.execute("SELECT id FROM users WHERE organization_id = %s LIMIT 1", (org_id,))
        user_result = cursor.fetchone()
        if not user_result:
            print("❌ No users found for organization")
            return False
        
        user_id = user_result[0]
        
        # Insert sample PBX provider
        cursor.execute("""
            INSERT INTO pbx_providers (organization_id, created_by, name, provider_type, display_name, host, port, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (org_id, user_id, "Test PBX", "asterisk", "Test Asterisk Server", "192.168.1.100", 8088, True))
        
        provider_id = cursor.fetchone()[0]
        print(f"✅ Created test PBX provider (ID: {provider_id})")
        
        # Insert sample call queue
        cursor.execute("""
            INSERT INTO call_queues (organization_id, provider_id, name, queue_number, strategy, timeout)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (org_id, provider_id, "Sales Queue", "100", "ringall", 30))
        
        queue_id = cursor.fetchone()[0]
        print(f"✅ Created test call queue (ID: {queue_id})")
        
        # Insert sample call
        cursor.execute("""
            INSERT INTO calls (organization_id, provider_id, caller_id, called_number, direction, status, duration)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (org_id, provider_id, "+1234567890", "+0987654321", "inbound", "completed", 120))
        
        call_id = cursor.fetchone()[0]
        print(f"✅ Created test call (ID: {call_id})")
        
        # Test data retrieval
        cursor.execute("SELECT COUNT(*) FROM pbx_providers WHERE organization_id = %s", (org_id,))
        provider_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM call_queues WHERE organization_id = %s", (org_id,))
        queue_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM calls WHERE organization_id = %s", (org_id,))
        call_count = cursor.fetchone()[0]
        
        print(f"📊 Database contains:")
        print(f"   - {provider_count} PBX providers")
        print(f"   - {queue_count} call queues")
        print(f"   - {call_count} calls")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def main():
    print("🧪 Railway Telephony Module Test Suite")
    print("=" * 50)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("API Endpoints", test_api_endpoints),
        ("Telephony Functionality", test_telephony_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📈 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Telephony module is ready for production!")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
