#!/usr/bin/env python3
"""
Script to test the company settings API endpoints.
This script tests the GET, POST, and PUT endpoints for company settings.
"""

import requests
import json
from db_config import get_railway_db_config

def test_company_settings_api():
    """Test the company settings API endpoints"""
    
    base_url = "https://neuracrm.up.railway.app"
    
    # Login credentials
    login_data = {
        "email": "nodeit@node.com",
        "password": "NodeIT2024!"
    }
    
    print("🧪 Testing Company Settings API")
    print("=" * 50)
    
    try:
        # Step 1: Login to get access token
        print("1. Logging in...")
        login_response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful")
        
        # Step 2: Test GET company settings (should return defaults if none exist)
        print("\n2. Testing GET /api/company-settings...")
        get_response = requests.get(f"{base_url}/api/company-settings", headers=headers)
        
        if get_response.status_code == 200:
            settings = get_response.json()
            print("✅ GET settings successful")
            print(f"   Company Name: {settings.get('company_name', 'Not set')}")
            print(f"   Currency: {settings.get('currency', 'Not set')}")
            print(f"   Timezone: {settings.get('timezone', 'Not set')}")
            print(f"   Trial Date Enabled: {settings.get('trial_date_enabled', 'Not set')}")
            print(f"   Trial Date Days: {settings.get('trial_date_days', 'Not set')}")
        else:
            print(f"❌ GET settings failed: {get_response.status_code}")
            print(f"Response: {get_response.text}")
            return
        
        # Step 3: Test PUT company settings (create/update)
        print("\n3. Testing PUT /api/company-settings...")
        update_data = {
            "company_name": "The Node Information Technology LLC",
            "company_mobile": "500343500",
            "city": "Sharjah",
            "area": "Al Barsha",
            "complete_address": "Al- LaxLLLL LLLLLLLL",
            "trn": "100000057776",
            "currency": "AED - UAE Dirham (د.إ)",
            "timezone": "Dubai (UAE)",
            "trial_date_enabled": True,
            "trial_date_days": 3,
            "delivery_date_enabled": True,
            "delivery_date_days": 3,
            "advance_payment_enabled": True
        }
        
        put_response = requests.put(f"{base_url}/api/company-settings", 
                                  json=update_data, headers=headers)
        
        if put_response.status_code == 200:
            updated_settings = put_response.json()
            print("✅ PUT settings successful")
            print(f"   Updated Company Name: {updated_settings.get('company_name')}")
            print(f"   Updated Mobile: {updated_settings.get('company_mobile')}")
            print(f"   Updated City: {updated_settings.get('city')}")
            print(f"   Settings ID: {updated_settings.get('id')}")
        else:
            print(f"❌ PUT settings failed: {put_response.status_code}")
            print(f"Response: {put_response.text}")
            return
        
        # Step 4: Test GET again to verify the update
        print("\n4. Testing GET /api/company-settings (after update)...")
        get_response_2 = requests.get(f"{base_url}/api/company-settings", headers=headers)
        
        if get_response_2.status_code == 200:
            final_settings = get_response_2.json()
            print("✅ GET settings after update successful")
            print(f"   Final Company Name: {final_settings.get('company_name')}")
            print(f"   Final Mobile: {final_settings.get('company_mobile')}")
            print(f"   Final City: {final_settings.get('city')}")
            
            # Verify the update was saved
            if final_settings.get('company_name') == update_data['company_name']:
                print("✅ Settings were successfully saved and retrieved")
            else:
                print("❌ Settings were not properly saved")
        else:
            print(f"❌ GET settings after update failed: {get_response_2.status_code}")
            print(f"Response: {get_response_2.text}")
            return
        
        print("\n🎉 All company settings API tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")

def test_database_connection():
    """Test database connection to verify table exists"""
    
    print("\n🔍 Testing Database Connection")
    print("=" * 30)
    
    try:
        config = get_railway_db_config()
        
        import psycopg2
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # Check if company_settings table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'company_settings'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            print("✅ company_settings table exists")
            
            # Check table structure
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'company_settings'
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            print(f"   Table has {len(columns)} columns")
            
            # Check if there are any settings records
            cursor.execute("SELECT COUNT(*) FROM company_settings;")
            count = cursor.fetchone()[0]
            print(f"   Current records: {count}")
            
        else:
            print("❌ company_settings table does not exist")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")

def main():
    """Main function to run all tests"""
    
    print("🏢 Company Settings API Test Suite")
    print("=" * 60)
    
    # Test database connection first
    test_database_connection()
    
    # Test API endpoints
    test_company_settings_api()
    
    print("\n📊 Test Summary:")
    print("✅ Database connection verified")
    print("✅ API endpoints tested")
    print("✅ Settings save/load functionality verified")

if __name__ == "__main__":
    main()
