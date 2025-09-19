#!/usr/bin/env python3
"""
Check Support Tickets Schema
===========================

This script checks the support tickets schema in Railway to identify missing fields.
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

def check_support_tickets_schema():
    """Check the schema of support_tickets table"""
    try:
        print("🔌 Connecting to Railway database...")
        conn = psycopg2.connect(**RAILWAY_DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database successfully")
        print("=" * 60)
        
        print("\n📋 SUPPORT_TICKETS TABLE SCHEMA:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'support_tickets'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        if columns:
            for col in columns:
                print(f"  - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
        else:
            print("  ❌ Table support_tickets does not exist")
        
        print(f"\n📊 SAMPLE SUPPORT TICKET DATA:")
        cursor.execute("SELECT * FROM support_tickets WHERE organization_id = 1 LIMIT 1")
        sample_ticket = cursor.fetchone()
        
        if sample_ticket:
            print(f"  Sample ticket found")
            # Get column names
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'support_tickets' 
                ORDER BY ordinal_position
            """)
            column_names = [row[0] for row in cursor.fetchall()]
            
            # Print sample data
            for i, value in enumerate(sample_ticket):
                col_name = column_names[i] if i < len(column_names) else f"col_{i}"
                print(f"    {col_name}: {value}")
        else:
            print("  ❌ No sample tickets found")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking schema: {e}")

if __name__ == "__main__":
    check_support_tickets_schema()
