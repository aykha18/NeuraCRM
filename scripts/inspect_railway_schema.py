#!/usr/bin/env python3
"""
Railway Database Schema Inspector
===============================

This script inspects the Railway database schema to understand
the actual table structures for proper data seeding.
"""

import psycopg2

import sys
import os

# Add the scripts directory to the path to import db_config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from db_config import get_railway_db_config, validate_config
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Railway Database Configuration
# Railway DB config now loaded from environment variables

def inspect_schema():
    """Inspect the Railway database schema"""
    try:
        conn = psycopg2.connect(**get_railway_db_config())
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("🔍 Inspecting Railway Database Schema...")
        print("=" * 50)
        
        # Get all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"📊 Found {len(tables)} tables:")
        
        for table in tables:
            table_name = table[0]
            print(f"\n📋 Table: {table_name}")
            
            # Get column information
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY ordinal_position;
            """, (table_name,))
            
            columns = cursor.fetchall()
            print("   Columns:")
            for col_name, data_type, nullable, default in columns:
                nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
                default_str = f" DEFAULT {default}" if default else ""
                print(f"     - {col_name}: {data_type} {nullable_str}{default_str}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Schema inspection completed!")
        
    except Exception as e:
        print(f"❌ Error inspecting schema: {e}")

if __name__ == "__main__":
    inspect_schema()
