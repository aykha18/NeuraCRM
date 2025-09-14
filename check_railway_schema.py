#!/usr/bin/env python3
"""
Check Railway database schema
"""
import os
import sys
from sqlalchemy import create_engine, text

def check_railway_schema():
    """Check Railway database schema"""
    railway_url = "postgresql://postgres:irUsikIqAifdrCMNOlGtApioMQJDjDfE@nozomi.proxy.rlwy.net:49967/railway"
    
    try:
        # Fix Railway URL format
        if railway_url.startswith("postgres://"):
            railway_url = railway_url.replace("postgres://", "postgresql://", 1)
        
        engine = create_engine(railway_url)
        
        print("🚀 RAILWAY DATABASE SCHEMA CHECK")
        print("="*60)
        
        with engine.connect() as conn:
            # Get all tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            
            print(f"📊 Total tables: {len(tables)}")
            print(f"📋 Tables: {', '.join(tables)}")
            
            # Check specific tables
            important_tables = ['users', 'organizations', 'leads', 'contacts', 'deals', 'chat_rooms', 'subscriptions']
            
            print(f"\n🔍 Checking important tables:")
            for table in important_tables:
                if table in tables:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"  ✅ {table}: {count} rows")
                else:
                    print(f"  ❌ {table}: MISSING")
            
            # Check demo user
            print(f"\n👤 Checking demo user:")
            result = conn.execute(text("SELECT id, name, email, organization_id FROM users WHERE email = 'nodeit@node.com'"))
            user = result.fetchone()
            if user:
                print(f"  ✅ Demo user found: {user[1]} ({user[2]}) - Org ID: {user[3]}")
            else:
                print(f"  ❌ Demo user not found")
            
            # Check organization
            print(f"\n🏢 Checking organization:")
            result = conn.execute(text("SELECT id, name FROM organizations WHERE id = 1"))
            org = result.fetchone()
            if org:
                print(f"  ✅ Organization found: {org[1]} (ID: {org[0]})")
            else:
                print(f"  ❌ Organization not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking Railway database: {e}")
        return False

def main():
    success = check_railway_schema()
    
    if success:
        print(f"\n{'='*60}")
        print("📋 SUMMARY")
        print(f"{'='*60}")
        print("✅ Railway database schema check completed")
        print("💡 If any important tables are missing, that could cause frontend issues")
    else:
        print("❌ Failed to check Railway database schema")

if __name__ == "__main__":
    main()
