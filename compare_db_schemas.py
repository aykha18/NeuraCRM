#!/usr/bin/env python3
"""
Compare database schemas between local and Railway
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from api.models import Base

def get_local_db_info():
    """Get local database schema info"""
    try:
        # Use local database URL
        local_url = "postgresql://postgres:password@localhost:5432/crm_db"
        engine = create_engine(local_url)
        inspector = inspect(engine)
        
        print("🏠 LOCAL DATABASE SCHEMA")
        print("="*60)
        
        # Get all tables
        tables = inspector.get_table_names()
        print(f"📊 Total tables: {len(tables)}")
        
        for table in sorted(tables):
            print(f"\n📋 Table: {table}")
            
            # Get columns
            columns = inspector.get_columns(table)
            print(f"  Columns ({len(columns)}):")
            for col in columns:
                print(f"    - {col['name']}: {col['type']} {'(nullable)' if col['nullable'] else '(not null)'}")
            
            # Get row count
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"  Rows: {count}")
        
        return tables, inspector
        
    except Exception as e:
        print(f"❌ Error accessing local database: {e}")
        return [], None

def get_railway_db_info():
    """Get Railway database schema info"""
    try:
        railway_url = "postgresql://postgres:irUsikIqAifdrCMNOlGtApioMQJDjDfE@nozomi.proxy.rlwy.net:49967/railway"
        
        # Fix Railway URL format
        if railway_url.startswith("postgres://"):
            railway_url = railway_url.replace("postgres://", "postgresql://", 1)
        
        engine = create_engine(railway_url)
        inspector = inspect(engine)
        
        print("\n🚀 RAILWAY DATABASE SCHEMA")
        print("="*60)
        
        # Get all tables
        tables = inspector.get_table_names()
        print(f"📊 Total tables: {len(tables)}")
        
        for table in sorted(tables):
            print(f"\n📋 Table: {table}")
            
            # Get columns
            columns = inspector.get_columns(table)
            print(f"  Columns ({len(columns)}):")
            for col in columns:
                print(f"    - {col['name']}: {col['type']} {'(nullable)' if col['nullable'] else '(not null)'}")
            
            # Get row count
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"  Rows: {count}")
        
        return tables, inspector
        
    except Exception as e:
        print(f"❌ Error accessing Railway database: {e}")
        return [], None

def compare_schemas(local_tables, local_inspector, railway_tables, railway_inspector):
    """Compare the two database schemas"""
    print("\n🔍 SCHEMA COMPARISON")
    print("="*60)
    
    # Compare tables
    local_set = set(local_tables)
    railway_set = set(railway_tables)
    
    missing_in_railway = local_set - railway_set
    missing_in_local = railway_set - local_set
    common_tables = local_set & railway_set
    
    print(f"📊 Table Comparison:")
    print(f"  Common tables: {len(common_tables)}")
    print(f"  Missing in Railway: {len(missing_in_railway)}")
    print(f"  Missing in Local: {len(missing_in_local)}")
    
    if missing_in_railway:
        print(f"\n❌ Tables missing in Railway: {sorted(missing_in_railway)}")
    
    if missing_in_local:
        print(f"\n❌ Tables missing in Local: {sorted(missing_in_local)}")
    
    # Compare columns for common tables
    print(f"\n🔍 Column Comparison for Common Tables:")
    for table in sorted(common_tables):
        local_cols = {col['name']: col for col in local_inspector.get_columns(table)}
        railway_cols = {col['name']: col for col in railway_inspector.get_columns(table)}
        
        local_col_names = set(local_cols.keys())
        railway_col_names = set(railway_cols.keys())
        
        missing_in_railway_cols = local_col_names - railway_col_names
        missing_in_local_cols = railway_col_names - local_col_names
        
        if missing_in_railway_cols or missing_in_local_cols:
            print(f"\n  📋 Table: {table}")
            if missing_in_railway_cols:
                print(f"    ❌ Columns missing in Railway: {sorted(missing_in_railway_cols)}")
            if missing_in_local_cols:
                print(f"    ❌ Columns missing in Local: {sorted(missing_in_local_cols)}")
        
        # Check for type differences
        for col_name in local_col_names & railway_col_names:
            local_type = str(local_cols[col_name]['type'])
            railway_type = str(railway_cols[col_name]['type'])
            if local_type != railway_type:
                print(f"    ⚠️  Column {col_name} type differs: Local={local_type}, Railway={railway_type}")

def main():
    print("🔍 COMPARING LOCAL vs RAILWAY DATABASE SCHEMAS")
    print("="*80)
    
    # Get local database info
    local_tables, local_inspector = get_local_db_info()
    
    # Get Railway database info
    railway_tables, railway_inspector = get_railway_db_info()
    
    # Compare schemas
    if local_inspector and railway_inspector:
        compare_schemas(local_tables, local_inspector, railway_tables, railway_inspector)
    
    print("\n" + "="*80)
    print("📋 SUMMARY")
    print("="*80)
    
    if not local_tables:
        print("❌ Could not access local database")
    if not railway_tables:
        print("❌ Could not access Railway database")
    
    if local_tables and railway_tables:
        if set(local_tables) == set(railway_tables):
            print("✅ Database schemas appear to be identical")
        else:
            print("❌ Database schemas differ - this could cause frontend issues")
            print("💡 Consider running migrations on Railway to sync schemas")

if __name__ == "__main__":
    main()
