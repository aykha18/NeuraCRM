#!/usr/bin/env python3
"""
Test Railway Watchers Functionality
==================================

This script tests the watchers functionality in the Railway database
to ensure it's working correctly.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json

# Railway Database Configuration
RAILWAY_DB_CONFIG = {
    'host': 'nozomi.proxy.rlwy.net',
    'database': 'railway',
    'user': 'postgres',
    'password': 'irUsikIqAifdrCMNOlGtApioMQJDjDfE',
    'port': 49967
}

def test_railway_watchers():
    """Test watchers functionality in Railway database"""
    try:
        print("🔌 Connecting to Railway database...")
        conn = psycopg2.connect(**RAILWAY_DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database successfully")
        
        # Check if watcher table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'watcher'
            );
        """)
        
        watcher_table_exists = cursor.fetchone()[0]
        print(f"📋 Watcher table exists: {watcher_table_exists}")
        
        if not watcher_table_exists:
            print("❌ Watcher table does not exist in Railway database!")
            return False
        
        # Get some deals
        cursor.execute("SELECT id, title FROM deals WHERE organization_id = 1 LIMIT 5")
        deals = cursor.fetchall()
        print(f"📊 Found {len(deals)} deals in organization 1")
        
        if not deals:
            print("❌ No deals found in organization 1")
            return False
        
        # Get a user
        cursor.execute("SELECT id, name, email FROM users WHERE organization_id = 1 LIMIT 1")
        user = cursor.fetchone()
        
        if not user:
            print("❌ No users found in organization 1")
            return False
        
        user_id, user_name, user_email = user
        print(f"👤 Using user: {user_name} ({user_email}) - ID: {user_id}")
        
        # Test with first deal
        deal_id, deal_title = deals[0]
        print(f"🎯 Testing with deal: {deal_title} (ID: {deal_id})")
        
        # Check current watchers for this deal
        cursor.execute("SELECT user_id FROM watcher WHERE deal_id = %s", (deal_id,))
        current_watchers = cursor.fetchall()
        watcher_ids = [row[0] for row in current_watchers]
        print(f"👀 Current watchers for deal {deal_id}: {watcher_ids}")
        
        # Test adding user as watcher
        if user_id not in watcher_ids:
            print("➕ Adding user as watcher...")
            cursor.execute("INSERT INTO watcher (deal_id, user_id) VALUES (%s, %s)", (deal_id, user_id))
            print("✅ User added as watcher")
        else:
            print("ℹ️ User is already watching this deal")
        
        # Check watchers again
        cursor.execute("SELECT user_id FROM watcher WHERE deal_id = %s", (deal_id,))
        updated_watchers = cursor.fetchall()
        updated_watcher_ids = [row[0] for row in updated_watchers]
        print(f"👀 Updated watchers for deal {deal_id}: {updated_watcher_ids}")
        
        # Test removing user as watcher
        if user_id in updated_watcher_ids:
            print("➖ Removing user as watcher...")
            cursor.execute("DELETE FROM watcher WHERE deal_id = %s AND user_id = %s", (deal_id, user_id))
            print("✅ User removed as watcher")
        
        # Final check
        cursor.execute("SELECT user_id FROM watcher WHERE deal_id = %s", (deal_id,))
        final_watchers = cursor.fetchall()
        final_watcher_ids = [row[0] for row in final_watchers]
        print(f"👀 Final watchers for deal {deal_id}: {final_watcher_ids}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Railway watchers functionality test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Railway watchers: {e}")
        return False

if __name__ == "__main__":
    test_railway_watchers()
