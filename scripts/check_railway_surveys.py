#!/usr/bin/env python3
"""
Check Railway Surveys Data
=========================

This script checks if surveys data exists in Railway.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Railway Database Configuration
RAILWAY_DB_CONFIG = {
    'host': 'nozomi.proxy.rlwy.net',
    'database': 'railway',
    'user': 'postgres',
    'password': 'irUsikIqAifdrCMNOlGtApioMQJDjDfE',
    'port': 49967
}

def check_railway_surveys():
    """Check Railway surveys data"""
    try:
        print("🔌 Connecting to Railway database...")
        conn = psycopg2.connect(**RAILWAY_DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database successfully")
        print("=" * 60)
        
        # Check if customer_satisfaction_surveys table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'customer_satisfaction_surveys'
            )
        """)
        surveys_table_exists = cursor.fetchone()[0]
        
        if surveys_table_exists:
            print("✅ customer_satisfaction_surveys table exists")
            
            # Check surveys data
            cursor.execute("SELECT COUNT(*) FROM customer_satisfaction_surveys WHERE organization_id = 1")
            surveys_count = cursor.fetchone()[0]
            print(f"📊 Surveys for organization 1: {surveys_count}")
            
            if surveys_count > 0:
                cursor.execute("""
                    SELECT id, customer_name, satisfaction_score, feedback, created_at 
                    FROM customer_satisfaction_surveys 
                    WHERE organization_id = 1 
                    ORDER BY created_at DESC 
                    LIMIT 3
                """)
                recent_surveys = cursor.fetchall()
                
                print("\n📋 Recent Surveys:")
                for survey in recent_surveys:
                    print(f"  - ID {survey[0]}: {survey[1]} (Score: {survey[2]}/10)")
                    print(f"    Feedback: {survey[3][:50]}..." if survey[3] else "    No feedback")
                    print(f"    Date: {survey[4]}")
            else:
                print("❌ No surveys found for organization 1")
        else:
            print("❌ customer_satisfaction_surveys table does not exist")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking surveys: {e}")

if __name__ == "__main__":
    check_railway_surveys()
