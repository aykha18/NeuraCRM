#!/usr/bin/env python3
"""
Railway Database Sync Script
Syncs Railway database with local database schema
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

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

def get_table_definition(conn, table_name):
    """Get complete table definition including columns, constraints, indexes"""
    cursor = conn.cursor()
    try:
        # Get column definitions
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                character_maximum_length,
                is_nullable,
                column_default,
                ordinal_position
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = %s
            ORDER BY ordinal_position;
        """, (table_name,))
        
        columns = []
        for row in cursor.fetchall():
            col_name, data_type, max_length, nullable, default, position = row
            col_def = f'"{col_name}" {data_type}'
            
            if max_length:
                col_def += f'({max_length})'
            
            if nullable == 'NO':
                col_def += ' NOT NULL'
            
            if default:
                col_def += f' DEFAULT {default}'
                
            columns.append(col_def)
        
        # Get primary key
        cursor.execute("""
            SELECT column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_schema = 'public'
            AND tc.table_name = %s
            AND tc.constraint_type = 'PRIMARY KEY'
            ORDER BY kcu.ordinal_position;
        """, (table_name,))
        
        pk_columns = [row[0] for row in cursor.fetchall()]
        
        # Get foreign keys
        cursor.execute("""
            SELECT 
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name,
                tc.constraint_name
            FROM information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' 
            AND tc.table_schema = 'public'
            AND tc.table_name = %s;
        """, (table_name,))
        
        foreign_keys = cursor.fetchall()
        
        return {
            'columns': columns,
            'primary_key': pk_columns,
            'foreign_keys': foreign_keys
        }
        
    except Exception as e:
        print(f"❌ Error getting table definition for {table_name}: {e}")
        return None

def create_table_sql(table_name, table_def):
    """Generate CREATE TABLE SQL"""
    sql = f'CREATE TABLE "{table_name}" (\n'
    
    # Add columns
    sql += ',\n'.join(f'  {col}' for col in table_def['columns'])
    
    # Add primary key
    if table_def['primary_key']:
        pk_cols = '", "'.join(table_def["primary_key"])
        sql += f',\n  PRIMARY KEY ("{pk_cols}")'
    
    sql += '\n);'
    
    # Add foreign keys
    for fk in table_def['foreign_keys']:
        col_name, foreign_table, foreign_col, constraint_name = fk
        sql += f'\nALTER TABLE "{table_name}" ADD CONSTRAINT "{constraint_name}" '
        sql += f'FOREIGN KEY ("{col_name}") REFERENCES "{foreign_table}" ("{foreign_col}");'
    
    return sql

def add_missing_columns(railway_conn, table_name, missing_columns, local_conn):
    """Add missing columns to Railway table"""
    cursor = railway_conn.cursor()
    local_cursor = local_conn.cursor()
    
    for col_name in missing_columns:
        try:
            # Get column definition from local database
            local_cursor.execute("""
                SELECT 
                    data_type,
                    character_maximum_length,
                    is_nullable,
                    column_default
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = %s
                AND column_name = %s;
            """, (table_name, col_name))
            
            row = local_cursor.fetchone()
            if not row:
                print(f"⚠️  Column {col_name} not found in local {table_name}")
                continue
                
            data_type, max_length, nullable, default = row
            
            # Build ALTER TABLE statement
            col_def = f'"{col_name}" {data_type}'
            if max_length:
                col_def += f'({max_length})'
            
            if nullable == 'NO':
                col_def += ' NOT NULL'
            
            if default:
                col_def += f' DEFAULT {default}'
            
            alter_sql = f'ALTER TABLE "{table_name}" ADD COLUMN {col_def};'
            
            print(f"   Adding column: {col_name} ({data_type})")
            cursor.execute(alter_sql)
            print(f"   ✅ Added column {col_name}")
            
        except Exception as e:
            print(f"   ❌ Error adding column {col_name}: {e}")
            railway_conn.rollback()

def sync_databases():
    """Sync Railway database with local database"""
    print("🚀 Railway Database Sync")
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
        
        # Get table lists
        local_cursor = local_conn.cursor()
        railway_cursor = railway_conn.cursor()
        
        local_cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        local_tables = set(row[0] for row in local_cursor.fetchall())
        
        railway_cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        railway_tables = set(row[0] for row in railway_cursor.fetchall())
        
        # 1. Add missing tables to Railway
        missing_tables = local_tables - railway_tables
        if missing_tables:
            print(f"\n📋 Adding missing tables to Railway ({len(missing_tables)}):")
            for table_name in sorted(missing_tables):
                print(f"   Creating table: {table_name}")
                try:
                    table_def = get_table_definition(local_conn, table_name)
                    if table_def:
                        create_sql = create_table_sql(table_name, table_def)
                        railway_cursor.execute(create_sql)
                        print(f"   ✅ Created table {table_name}")
                    else:
                        print(f"   ❌ Failed to get definition for {table_name}")
                except Exception as e:
                    print(f"   ❌ Error creating table {table_name}: {e}")
                    railway_conn.rollback()
        else:
            print("\n✅ No missing tables to add")
        
        # 2. Add missing columns to existing tables
        common_tables = local_tables & railway_tables
        if common_tables:
            print(f"\n🔧 Adding missing columns to existing tables:")
            
            for table_name in sorted(common_tables):
                # Get columns from both databases
                local_cursor.execute("""
                    SELECT column_name
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                    ORDER BY ordinal_position;
                """, (table_name,))
                local_cols = set(row[0] for row in local_cursor.fetchall())
                
                railway_cursor.execute("""
                    SELECT column_name
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                    ORDER BY ordinal_position;
                """, (table_name,))
                railway_cols = set(row[0] for row in railway_cursor.fetchall())
                
                missing_cols = local_cols - railway_cols
                if missing_cols:
                    print(f"\n   📝 Table {table_name}: Adding {len(missing_cols)} columns")
                    add_missing_columns(railway_conn, table_name, missing_cols, local_conn)
                else:
                    print(f"   ✅ Table {table_name}: No missing columns")
        
        # Commit all changes
        railway_conn.commit()
        print(f"\n🎉 Database sync completed successfully!")
        
        # Verify sync
        print(f"\n🔍 Verifying sync...")
        railway_cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        updated_railway_tables = set(row[0] for row in railway_cursor.fetchall())
        
        print(f"   Local tables: {len(local_tables)}")
        print(f"   Railway tables: {len(updated_railway_tables)}")
        print(f"   Tables added: {len(missing_tables)}")
        
        if updated_railway_tables >= local_tables:
            print("   ✅ Sync verification passed!")
        else:
            print("   ⚠️  Some tables may still be missing")
        
    except Exception as e:
        print(f"❌ Error during sync: {e}")
        if railway_conn:
            railway_conn.rollback()
        sys.exit(1)
    
    finally:
        if local_conn:
            local_conn.close()
        if railway_conn:
            railway_conn.close()
        print("\n🔌 Connections closed")

if __name__ == "__main__":
    sync_databases()
