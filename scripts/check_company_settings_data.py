#!/usr/bin/env python3
"""
Script to check what company settings data exists in the database.
"""

import psycopg2
from db_config import get_railway_db_config

def check_company_settings_data():
    """Check what company settings data exists in the database"""
    
    print("🔍 Checking Company Settings Data in Database")
    print("=" * 50)
    
    try:
        config = get_railway_db_config()
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # Check if there are any settings records
        cursor.execute("SELECT COUNT(*) FROM company_settings;")
        count = cursor.fetchone()[0]
        print(f"📊 Total company_settings records: {count}")
        
        if count > 0:
            # Get all settings records
            cursor.execute("""
                SELECT id, organization_id, company_name, company_mobile, city, 
                       area, complete_address, trn, currency, timezone,
                       trial_date_enabled, trial_date_days, delivery_date_enabled, 
                       delivery_date_days, advance_payment_enabled,
                       created_at, updated_at, created_by
                FROM company_settings
                ORDER BY created_at DESC;
            """)
            
            records = cursor.fetchall()
            
            print(f"\n📋 Found {len(records)} settings records:")
            print("-" * 80)
            
            for i, record in enumerate(records, 1):
                print(f"\nRecord {i}:")
                print(f"  ID: {record[0]}")
                print(f"  Organization ID: {record[1]}")
                print(f"  Company Name: {record[2] or 'Not set'}")
                print(f"  Company Mobile: {record[3] or 'Not set'}")
                print(f"  City: {record[4] or 'Not set'}")
                print(f"  Area: {record[5] or 'Not set'}")
                print(f"  Complete Address: {record[6] or 'Not set'}")
                print(f"  TRN: {record[7] or 'Not set'}")
                print(f"  Currency: {record[8] or 'Not set'}")
                print(f"  Timezone: {record[9] or 'Not set'}")
                print(f"  Trial Date Enabled: {record[10]}")
                print(f"  Trial Date Days: {record[11]}")
                print(f"  Delivery Date Enabled: {record[12]}")
                print(f"  Delivery Date Days: {record[13]}")
                print(f"  Advance Payment Enabled: {record[14]}")
                print(f"  Created At: {record[15]}")
                print(f"  Updated At: {record[16]}")
                print(f"  Created By: {record[17]}")
        
        # Check organization info
        cursor.execute("""
            SELECT id, name, domain 
            FROM organizations 
            WHERE id = 1;
        """)
        
        org = cursor.fetchone()
        if org:
            print(f"\n🏢 Organization Info:")
            print(f"  ID: {org[0]}")
            print(f"  Name: {org[1]}")
            print(f"  Domain: {org[2] or 'Not set'}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking data: {str(e)}")

if __name__ == "__main__":
    check_company_settings_data()
