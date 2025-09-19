#!/usr/bin/env python3
"""
Check PBX Extension Constraints
==============================

This script checks the constraints on pbx_extensions table.
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

def check_pbx_extension_constraints():
    """Check constraints on pbx_extensions table"""
    try:
        print("🔌 Connecting to Railway database...")
        conn = psycopg2.connect(**RAILWAY_DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database successfully")
        print("=" * 60)
        
        # Try to insert a simple extension to see what works
        test_extensions = [
            "sip",
            "iax",
            "pjsip",
            "user",
            "peer",
            "friend",
            "extension",
            "agent",
            "queue",
            "voicemail",
            "conference",
            "meetme"
        ]
        
        print("Testing extension types:")
        for ext_type in test_extensions:
            try:
                cursor.execute("""
                    INSERT INTO pbx_extensions (
                        organization_id, provider_id, extension_number,
                        extension_type, secret, callerid, context,
                        is_active, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    1, 1, "999", ext_type, "test123", "Test", "default", True, "2025-01-01", "2025-01-01"
                ))
                print(f"  ✓ '{ext_type}' - VALID")
                cursor.execute("DELETE FROM pbx_extensions WHERE extension_number = '999'")
            except Exception as e:
                if "violates check constraint" in str(e):
                    print(f"  ❌ '{ext_type}' - INVALID")
                else:
                    print(f"  ❌ '{ext_type}' - ERROR: {e}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking constraints: {e}")

if __name__ == "__main__":
    check_pbx_extension_constraints()