#!/usr/bin/env python3
"""
Fix Railway Support API
======================

This script creates a patch to fix the isoformat error in the support tickets API.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime

# Railway Database Configuration
RAILWAY_DB_CONFIG = {
    'host': 'nozomi.proxy.rlwy.net',
    'database': 'railway',
    'user': 'postgres',
    'password': 'irUsikIqAifdrCMNOlGtApioMQJDjDfE',
    'port': 49967
}

def fix_support_tickets_data():
    """Fix support tickets data to ensure all date fields have proper values"""
    try:
        print("🔌 Connecting to Railway database...")
        conn = psycopg2.connect(**RAILWAY_DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database successfully")
        print("=" * 60)
        
        # Check for tickets with NULL created_at or updated_at
        cursor.execute("""
            SELECT COUNT(*) FROM support_tickets 
            WHERE organization_id = 1 
            AND (created_at IS NULL OR updated_at IS NULL)
        """)
        null_date_count = cursor.fetchone()[0]
        
        print(f"📊 Tickets with NULL dates: {null_date_count}")
        
        if null_date_count > 0:
            print("🔧 Fixing NULL date fields...")
            
            # Update tickets with NULL created_at
            cursor.execute("""
                UPDATE support_tickets 
                SET created_at = NOW() 
                WHERE organization_id = 1 
                AND created_at IS NULL
            """)
            created_at_fixed = cursor.rowcount
            print(f"  ✅ Fixed {created_at_fixed} tickets with NULL created_at")
            
            # Update tickets with NULL updated_at
            cursor.execute("""
                UPDATE support_tickets 
                SET updated_at = NOW() 
                WHERE organization_id = 1 
                AND updated_at IS NULL
            """)
            updated_at_fixed = cursor.rowcount
            print(f"  ✅ Fixed {updated_at_fixed} tickets with NULL updated_at")
            
            # Update tickets with NULL sla_deadline (set to 24 hours from created_at)
            cursor.execute("""
                UPDATE support_tickets 
                SET sla_deadline = created_at + INTERVAL '24 hours'
                WHERE organization_id = 1 
                AND sla_deadline IS NULL
                AND created_at IS NOT NULL
            """)
            sla_fixed = cursor.rowcount
            print(f"  ✅ Fixed {sla_fixed} tickets with NULL sla_deadline")
            
            # Update tickets with NULL resolution_deadline (set to 48 hours from created_at)
            cursor.execute("""
                UPDATE support_tickets 
                SET resolution_deadline = created_at + INTERVAL '48 hours'
                WHERE organization_id = 1 
                AND resolution_deadline IS NULL
                AND created_at IS NOT NULL
            """)
            resolution_fixed = cursor.rowcount
            print(f"  ✅ Fixed {resolution_fixed} tickets with NULL resolution_deadline")
        
        # Check final status
        cursor.execute("""
            SELECT COUNT(*) FROM support_tickets 
            WHERE organization_id = 1
        """)
        total_tickets = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM support_tickets 
            WHERE organization_id = 1 
            AND (created_at IS NULL OR updated_at IS NULL)
        """)
        remaining_null_dates = cursor.fetchone()[0]
        
        print(f"\n📊 FINAL STATUS:")
        print(f"  Total tickets: {total_tickets}")
        print(f"  Tickets with NULL dates: {remaining_null_dates}")
        
        if remaining_null_dates == 0:
            print("✅ All date fields fixed successfully!")
        else:
            print("⚠️  Some date fields still need attention")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error fixing support tickets: {e}")

if __name__ == "__main__":
    fix_support_tickets_data()
