#!/usr/bin/env python3
"""
PBX Database Schema Fix
Identifies and fixes database schema mismatches for PBX tables
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

def test_pbx_provider_operations(token):
    """Test all PBX provider operations to identify issues"""
    print("\n🔧 Testing PBX Provider Operations")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {token}"}
    provider_id = None
    
    try:
        # Test 1: Create provider
        print("1. Creating PBX provider...")
        provider_data = {
            "name": "Schema Test PBX",
            "provider_type": "asterisk",
            "display_name": "Schema Test Server",
            "description": "Testing database schema",
            "host": "192.168.1.200",
            "port": 8088,
            "username": "testuser",
            "password": "testpass",
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
        
        response = requests.post(f"{BASE_URL}/api/telephony/providers", 
                               json=provider_data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            provider_id = result.get("id")
            print(f"✅ Provider created successfully! ID: {provider_id}")
        else:
            print(f"❌ Provider creation failed: {response.status_code} - {response.text}")
            return False
        
        # Test 2: Get provider
        print("\n2. Getting provider...")
        response = requests.get(f"{BASE_URL}/api/telephony/providers/{provider_id}", headers=headers)
        
        if response.status_code == 200:
            provider = response.json()
            print(f"✅ Provider retrieved successfully!")
            print(f"   Name: {provider.get('name')}")
            print(f"   Host: {provider.get('host')}:{provider.get('port')}")
        else:
            print(f"❌ Provider retrieval failed: {response.status_code} - {response.text}")
        
        # Test 3: Update provider
        print("\n3. Updating provider...")
        update_data = {
            "display_name": "Updated Schema Test Server",
            "description": "Updated description for schema testing"
        }
        
        response = requests.put(f"{BASE_URL}/api/telephony/providers/{provider_id}", 
                              json=update_data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Provider updated successfully!")
            print(f"   Updated name: {result.get('display_name')}")
        else:
            print(f"❌ Provider update failed: {response.status_code} - {response.text}")
        
        # Test 4: Test connection
        print("\n4. Testing connection...")
        response = requests.post(f"{BASE_URL}/api/telephony/providers/{provider_id}/test", 
                               headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Connection test successful!")
            print(f"   Success: {result.get('success')}")
            print(f"   Message: {result.get('message')}")
        else:
            print(f"❌ Connection test failed: {response.status_code} - {response.text}")
        
        # Test 5: Delete provider (this is where the error occurs)
        print("\n5. Deleting provider...")
        response = requests.delete(f"{BASE_URL}/api/telephony/providers/{provider_id}", headers=headers)
        
        if response.status_code == 200:
            print("✅ Provider deleted successfully!")
            return True
        else:
            print(f"❌ Provider deletion failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
            # Parse the error to understand the schema issue
            try:
                error_data = response.json()
                error_detail = error_data.get("detail", "")
                print(f"\n🔍 Error Analysis:")
                print(f"   Error: {error_detail}")
                
                if "extension_name does not exist" in error_detail:
                    print(f"\n💡 SCHEMA ISSUE IDENTIFIED:")
                    print(f"   The pbx_extensions table is missing the 'extension_name' column")
                    print(f"   This suggests the database schema is out of sync with the model")
                    print(f"\n🔧 SOLUTION:")
                    print(f"   1. Check the pbx_extensions table structure")
                    print(f"   2. Add missing columns or recreate the table")
                    print(f"   3. Ensure all required columns exist")
                    
            except:
                print(f"   Could not parse error details")
            
            return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def check_database_schema_requirements():
    """Check what the database schema should look like"""
    print("\n📋 Database Schema Requirements")
    print("=" * 50)
    
    print("🔍 Required pbx_providers table columns:")
    required_provider_columns = [
        "id", "organization_id", "created_by", "name", "provider_type", 
        "display_name", "description", "host", "port", "username", "password", 
        "api_key", "context", "caller_id_field", "dialplan_context", 
        "recording_enabled", "recording_path", "transcription_enabled", 
        "cdr_enabled", "cdr_path", "webhook_url", "webhook_secret", 
        "is_active", "is_primary", "auto_assign_calls", "created_at", 
        "updated_at", "last_sync"
    ]
    
    for col in required_provider_columns:
        print(f"   ✅ {col}")
    
    print("\n🔍 Required pbx_extensions table columns:")
    required_extension_columns = [
        "id", "provider_id", "organization_id", "user_id", "extension_number", 
        "extension_name", "extension_type", "device_type", "device_config", 
        "voicemail_enabled", "voicemail_password", "ring_timeout", 
        "max_ring_timeout", "call_forward_enabled", "call_forward_number", 
        "call_forward_conditions", "presence_status", "dnd_enabled", 
        "auto_answer", "queue_strategy", "queue_timeout", "queue_retry", 
        "queue_wrapup_time", "is_active", "is_registered", "last_registered", 
        "created_at", "updated_at"
    ]
    
    for col in required_extension_columns:
        print(f"   ✅ {col}")
    
    print(f"\n💡 To check your database schema, run these SQL queries:")
    print(f"   \\d pbx_providers")
    print(f"   \\d pbx_extensions")
    print(f"   SELECT column_name FROM information_schema.columns WHERE table_name = 'pbx_providers';")
    print(f"   SELECT column_name FROM information_schema.columns WHERE table_name = 'pbx_extensions';")

def provide_schema_fix_sql():
    """Provide SQL to fix the schema issues"""
    print("\n🔧 Schema Fix SQL Commands")
    print("=" * 50)
    
    print("📝 If pbx_extensions table is missing columns, run:")
    print("""
-- Add missing extension_name column
ALTER TABLE pbx_extensions ADD COLUMN IF NOT EXISTS extension_name VARCHAR(255);

-- Add other potentially missing columns
ALTER TABLE pbx_extensions ADD COLUMN IF NOT EXISTS extension_type VARCHAR(50) DEFAULT 'user';
ALTER TABLE pbx_extensions ADD COLUMN IF NOT EXISTS device_type VARCHAR(50);
ALTER TABLE pbx_extensions ADD COLUMN IF NOT EXISTS device_config JSON;
ALTER TABLE pbx_extensions ADD COLUMN IF NOT EXISTS voicemail_enabled BOOLEAN DEFAULT TRUE;
ALTER TABLE pbx_extensions ADD COLUMN IF NOT EXISTS voicemail_password VARCHAR(255);
ALTER TABLE pbx_extensions ADD COLUMN IF NOT EXISTS ring_timeout INTEGER DEFAULT 30;
ALTER TABLE pbx_extensions ADD COLUMN IF NOT EXISTS max_ring_timeout INTEGER DEFAULT 60;
ALTER TABLE pbx_extensions ADD COLUMN IF NOT EXISTS call_forward_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE pbx_extensions ADD COLUMN IF NOT EXISTS call_forward_number VARCHAR(255);
ALTER TABLE pbx_extensions ADD COLUMN IF NOT EXISTS call_forward_conditions JSON;
ALTER TABLE pbx_extensions ADD COLUMN IF NOT EXISTS presence_status VARCHAR(50) DEFAULT 'available';
ALTER TABLE pbx_extensions ADD COLUMN IF NOT EXISTS dnd_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE pbx_extensions ADD COLUMN IF NOT EXISTS auto_answer BOOLEAN DEFAULT FALSE;
ALTER TABLE pbx_extensions ADD COLUMN IF NOT EXISTS queue_strategy VARCHAR(50) DEFAULT 'ringall';
ALTER TABLE pbx_extensions ADD COLUMN IF NOT EXISTS queue_timeout INTEGER DEFAULT 30;
ALTER TABLE pbx_extensions ADD COLUMN IF NOT EXISTS queue_retry INTEGER DEFAULT 5;
ALTER TABLE pbx_extensions ADD COLUMN IF NOT EXISTS queue_wrapup_time INTEGER DEFAULT 30;
ALTER TABLE pbx_extensions ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
ALTER TABLE pbx_extensions ADD COLUMN IF NOT EXISTS is_registered BOOLEAN DEFAULT FALSE;
ALTER TABLE pbx_extensions ADD COLUMN IF NOT EXISTS last_registered TIMESTAMP;
ALTER TABLE pbx_extensions ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
""")
    
    print("\n📝 If you need to recreate the pbx_extensions table completely:")
    print("""
-- Drop and recreate pbx_extensions table
DROP TABLE IF EXISTS pbx_extensions CASCADE;

CREATE TABLE pbx_extensions (
    id SERIAL PRIMARY KEY,
    provider_id INTEGER NOT NULL REFERENCES pbx_providers(id) ON DELETE CASCADE,
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    extension_number VARCHAR(255) NOT NULL,
    extension_name VARCHAR(255) NOT NULL,
    extension_type VARCHAR(50) DEFAULT 'user',
    device_type VARCHAR(50),
    device_config JSON,
    voicemail_enabled BOOLEAN DEFAULT TRUE,
    voicemail_password VARCHAR(255),
    ring_timeout INTEGER DEFAULT 30,
    max_ring_timeout INTEGER DEFAULT 60,
    call_forward_enabled BOOLEAN DEFAULT FALSE,
    call_forward_number VARCHAR(255),
    call_forward_conditions JSON,
    presence_status VARCHAR(50) DEFAULT 'available',
    dnd_enabled BOOLEAN DEFAULT FALSE,
    auto_answer BOOLEAN DEFAULT FALSE,
    queue_strategy VARCHAR(50) DEFAULT 'ringall',
    queue_timeout INTEGER DEFAULT 30,
    queue_retry INTEGER DEFAULT 5,
    queue_wrapup_time INTEGER DEFAULT 30,
    is_active BOOLEAN DEFAULT TRUE,
    is_registered BOOLEAN DEFAULT FALSE,
    last_registered TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

def main():
    """Main test function"""
    print("🔧 PBX DATABASE SCHEMA FIX TEST")
    print("=" * 60)
    print(f"Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Login
    token = login_and_get_token()
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    try:
        # Test PBX operations
        success = test_pbx_provider_operations(token)
        
        # Check schema requirements
        check_database_schema_requirements()
        
        # Provide fix SQL
        provide_schema_fix_sql()
        
        print("\n🎉 PBX DATABASE SCHEMA ANALYSIS COMPLETED!")
        
        if success:
            print("✅ All PBX operations working correctly")
        else:
            print("❌ PBX operations have issues - schema fix required")
            print("\n💡 NEXT STEPS:")
            print("   1. Check your database schema using the SQL queries above")
            print("   2. Run the schema fix SQL commands")
            print("   3. Restart the application")
            print("   4. Test PBX operations again")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()

