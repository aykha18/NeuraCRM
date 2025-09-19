#!/usr/bin/env python3
"""
Inspect PBX Extensions Schema
============================

This script inspects the actual schema of pbx_extensions table.
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

def inspect_pbx_extensions_schema():
    """Inspect the schema of pbx_extensions table"""
    try:
        print("🔌 Connecting to Railway database...")
        conn = psycopg2.connect(**RAILWAY_DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database successfully")
        print("=" * 60)
        
        print("\n📋 PBX_EXTENSIONS TABLE SCHEMA:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'pbx_extensions'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        if columns:
            for col in columns:
                print(f"  - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
        else:
            print("  ❌ Table pbx_extensions does not exist")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error inspecting schema: {e}")

if __name__ == "__main__":
    inspect_pbx_extensions_schema()
