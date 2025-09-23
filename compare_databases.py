#!/usr/bin/env python3
"""
Simple Database Comparison Script
Compare local vs Railway database schemas
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Database configurations
LOCAL_CONFIG = {
    'host': 'localhost',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'aykha123',
    'port': 5432
}

RAILWAY_CONFIG = {
    'host': 'nozomi.proxy.rlwy.net',
    'database': 'railway',
    'user': 'postgres',
    'password': 'irUsikIqAifdrCMNOlGtApioMQJDjDfE',
    'port': 49967
}

def get_tables(conn, db_name):
    """Get list of tables from database"""
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 {db_name}: Found {len(tables)} tables")
        return set(tables)
    except Exception as e:
        print(f"❌ Error getting tables from {db_name}: {e}")
        return set()

def get_table_columns(conn, table_name, db_name):
    """Get columns for a specific table"""
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = %s
            ORDER BY ordinal_position;
        """, (table_name,))
        columns = {row[0]: f"{row[1]}({'NULL' if row[2] == 'YES' else 'NOT NULL'})" 
                  for row in cursor.fetchall()}
        return columns
    except Exception as e:
        print(f"❌ Error getting columns for {table_name} in {db_name}: {e}")
        return {}

def compare_databases():
    """Compare local and Railway databases"""
    print("🚀 Database Schema Comparison")
    print("=" * 50)
    
    local_conn = None
    railway_conn = None
    
    try:
        # Connect to databases
        print("🔌 Connecting to local database...")
        local_conn = psycopg2.connect(**LOCAL_CONFIG)
        local_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        print("✅ Local database connected")
        
        print("🔌 Connecting to Railway database...")
        railway_conn = psycopg2.connect(**RAILWAY_CONFIG)
        railway_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        print("✅ Railway database connected")
        
        # Get tables
        local_tables = get_tables(local_conn, "Local")
        railway_tables = get_tables(railway_conn, "Railway")
        
        print(f"\n📊 COMPARISON RESULTS:")
        print("=" * 50)
        
        # Tables only in local
        only_local = local_tables - railway_tables
        if only_local:
            print(f"\n❌ Tables only in LOCAL ({len(only_local)}):")
            for table in sorted(only_local):
                print(f"   - {table}")
        else:
            print("\n✅ All local tables exist in Railway")
        
        # Tables only in Railway
        only_railway = railway_tables - local_tables
        if only_railway:
            print(f"\n🆕 Tables only in RAILWAY ({len(only_railway)}):")
            for table in sorted(only_railway):
                print(f"   - {table}")
        else:
            print("\n✅ No extra tables in Railway")
        
        # Common tables - check for column differences
        common_tables = local_tables & railway_tables
        if common_tables:
            print(f"\n🔍 Checking columns in common tables ({len(common_tables)}):")
            column_differences = {}
            
            for table in sorted(common_tables):
                local_cols = get_table_columns(local_conn, table, "Local")
                railway_cols = get_table_columns(railway_conn, table, "Railway")
                
                if local_cols != railway_cols:
                    missing_in_railway = set(local_cols.keys()) - set(railway_cols.keys())
                    missing_in_local = set(railway_cols.keys()) - set(local_cols.keys())
                    
                    if missing_in_railway or missing_in_local:
                        column_differences[table] = {
                            'missing_in_railway': missing_in_railway,
                            'missing_in_local': missing_in_local
                        }
            
            if column_differences:
                print("\n❌ Column differences found:")
                for table, diffs in column_differences.items():
                    if diffs['missing_in_railway']:
                        print(f"   - {table}: Missing in Railway: {', '.join(diffs['missing_in_railway'])}")
                    if diffs['missing_in_local']:
                        print(f"   - {table}: Missing in Local: {', '.join(diffs['missing_in_local'])}")
            else:
                print("✅ All common tables have matching columns")
        
        # Summary
        print(f"\n📈 SUMMARY:")
        print(f"   Local tables: {len(local_tables)}")
        print(f"   Railway tables: {len(railway_tables)}")
        print(f"   Common tables: {len(common_tables)}")
        print(f"   Missing in Railway: {len(only_local)}")
        print(f"   Extra in Railway: {len(only_railway)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        if local_conn:
            local_conn.close()
        if railway_conn:
            railway_conn.close()
        print("\n🔌 Connections closed")

if __name__ == "__main__":
    compare_databases()
