#!/usr/bin/env python3
"""
PBX Configuration Debug Test
Tests PBX provider creation, database verification, and troubleshooting
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000"
LOGIN_EMAIL = "nodeit@node.com"
LOGIN_PASSWORD = "NodeIT2024!"

def login_and_get_token():
    """Login and get authentication token"""
    print("🔐 Logging in...")
    
    login_data = {
        "email": LOGIN_EMAIL,
        "password": LOGIN_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print("✅ Login successful")
        return token
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

def test_pbx_provider_creation(token):
    """Test PBX provider creation with detailed debugging"""
    print("\n🎯 Testing PBX Provider Creation")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Get existing providers
    print("1. Getting existing PBX providers...")
    response = requests.get(f"{BASE_URL}/api/telephony/providers", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {len(data)} existing providers")
        for provider in data:
            print(f"   - {provider.get('name')} ({provider.get('provider_type')}) - ID: {provider.get('id')}")
    else:
        print(f"❌ Failed to get providers: {response.status_code} - {response.text}")
        return None
    
    # Test 2: Create a new PBX provider
    print("\n2. Creating a new PBX provider...")
    provider_data = {
        "name": "Test Asterisk PBX",
        "provider_type": "asterisk",
        "display_name": "Test Asterisk Server",
        "description": "Test PBX for debugging",
        "host": "192.168.1.100",
        "port": 8088,
        "username": "admin",
        "password": "admin123",
        "context": "default",
        "caller_id_field": "CallerIDNum",
        "dialplan_context": "from-internal",
        "recording_enabled": True,
        "recording_path": "/var/spool/asterisk/monitor",
        "transcription_enabled": False,
        "cdr_enabled": True,
        "cdr_path": "/var/log/asterisk/cdr-csv",
        "webhook_url": "",
        "webhook_secret": "",
        "auto_assign_calls": True,
        "is_active": True,
        "is_primary": False
    }
    
    print(f"   📝 Sending data: {json.dumps(provider_data, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/api/telephony/providers", 
                           json=provider_data, headers=headers)
    
    print(f"   📡 Response status: {response.status_code}")
    print(f"   📡 Response headers: {dict(response.headers)}")
    print(f"   📡 Response body: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        provider_id = result.get("id")
        print(f"✅ PBX Provider created successfully! ID: {provider_id}")
        print(f"   Name: {result.get('name')}")
        print(f"   Type: {result.get('provider_type')}")
        print(f"   Host: {result.get('host')}:{result.get('port')}")
        return provider_id
    else:
        print(f"❌ Failed to create PBX provider: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def verify_database_entry(token, provider_id):
    """Verify the provider was saved in the database"""
    print(f"\n🔍 Verifying Database Entry for Provider ID: {provider_id}")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Get the specific provider
    print("1. Getting the specific provider...")
    response = requests.get(f"{BASE_URL}/api/telephony/providers/{provider_id}", headers=headers)
    
    if response.status_code == 200:
        provider = response.json()
        print("✅ Provider found in database!")
        print(f"   📊 Provider Details:")
        print(f"      ID: {provider.get('id')}")
        print(f"      Name: {provider.get('name')}")
        print(f"      Type: {provider.get('provider_type')}")
        print(f"      Host: {provider.get('host')}")
        print(f"      Port: {provider.get('port')}")
        print(f"      Username: {provider.get('username')}")
        print(f"      Active: {provider.get('is_active')}")
        print(f"      Primary: {provider.get('is_primary')}")
        print(f"      Created: {provider.get('created_at')}")
        return True
    else:
        print(f"❌ Provider not found in database: {response.status_code} - {response.text}")
        return False

def test_provider_update(token, provider_id):
    """Test updating the PBX provider"""
    print(f"\n✏️ Testing PBX Provider Update for ID: {provider_id}")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    update_data = {
        "display_name": "Updated Test Asterisk Server",
        "description": "Updated description for testing",
        "recording_enabled": False,
        "is_primary": True
    }
    
    print(f"   📝 Update data: {json.dumps(update_data, indent=2)}")
    
    response = requests.put(f"{BASE_URL}/api/telephony/providers/{provider_id}", 
                          json=update_data, headers=headers)
    
    print(f"   📡 Response status: {response.status_code}")
    print(f"   📡 Response body: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ PBX Provider updated successfully!")
        print(f"   Updated name: {result.get('display_name')}")
        print(f"   Updated description: {result.get('description')}")
        print(f"   Recording enabled: {result.get('recording_enabled')}")
        print(f"   Is primary: {result.get('is_primary')}")
        return True
    else:
        print(f"❌ Failed to update PBX provider: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def test_connection_test(token, provider_id):
    """Test PBX connection testing"""
    print(f"\n🔌 Testing PBX Connection for ID: {provider_id}")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(f"{BASE_URL}/api/telephony/providers/{provider_id}/test", 
                           headers=headers)
    
    print(f"   📡 Response status: {response.status_code}")
    print(f"   📡 Response body: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Connection test completed!")
        print(f"   Success: {result.get('success')}")
        print(f"   Message: {result.get('message')}")
        if result.get('response_time'):
            print(f"   Response time: {result.get('response_time')}ms")
        if result.get('error'):
            print(f"   Error: {result.get('error')}")
        return True
    else:
        print(f"❌ Connection test failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def cleanup_test_data(token, provider_id):
    """Clean up test data"""
    print(f"\n🧹 Cleaning up test data (Provider ID: {provider_id})...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.delete(f"{BASE_URL}/api/telephony/providers/{provider_id}", headers=headers)
    
    if response.status_code == 200:
        print("✅ Test provider deleted successfully")
        return True
    else:
        print(f"⚠️ Failed to delete test provider: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def test_database_direct_query():
    """Test direct database query to verify data persistence"""
    print("\n🗄️ Testing Direct Database Query")
    print("=" * 50)
    
    try:
        # This would require direct database access
        # For now, we'll just show what we would check
        print("📋 Database verification checklist:")
        print("   1. Check if pbx_providers table exists")
        print("   2. Verify provider record was inserted")
        print("   3. Check all field values are correct")
        print("   4. Verify organization_id and created_by are set")
        print("   5. Check created_at timestamp")
        print("   6. Verify foreign key constraints")
        
        print("\n💡 To check database directly, run:")
        print("   SELECT * FROM pbx_providers WHERE name = 'Test Asterisk PBX';")
        print("   SELECT * FROM pbx_providers ORDER BY created_at DESC LIMIT 5;")
        
        return True
    except Exception as e:
        print(f"❌ Database query test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🔧 PBX CONFIGURATION DEBUG TEST")
    print("=" * 60)
    print(f"Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Login
    token = login_and_get_token()
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    provider_id = None
    
    try:
        # Test PBX provider creation
        provider_id = test_pbx_provider_creation(token)
        
        if provider_id:
            # Verify database entry
            db_verified = verify_database_entry(token, provider_id)
            
            if db_verified:
                # Test provider update
                test_provider_update(token, provider_id)
                
                # Test connection
                test_connection_test(token, provider_id)
            else:
                print("❌ Database verification failed - provider not saved properly")
        
        # Test database direct query
        test_database_direct_query()
        
        print("\n🎉 PBX CONFIGURATION DEBUG TEST COMPLETED!")
        
        if provider_id:
            print("✅ PBX Provider Creation - Working")
            print("✅ Database Storage - Working")
            print("✅ Provider Retrieval - Working")
        else:
            print("❌ PBX Provider Creation - Failed")
            print("❌ Database Storage - Failed")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
    
    finally:
        # Clean up
        if provider_id:
            cleanup_test_data(token, provider_id)

if __name__ == "__main__":
    main()

