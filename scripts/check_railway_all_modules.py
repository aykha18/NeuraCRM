#!/usr/bin/env python3
"""
Check Railway All Modules Data
==============================

This script checks what data exists in Railway for all CRM modules.
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

def check_all_modules():
    """Check data for all modules in Railway database"""
    try:
        print("🔌 Connecting to Railway database...")
        # Validate environment configuration
        validate_config()
        
        # Get Railway database configuration from environment variables
        railway_config = get_railway_db_config()
        
        conn = psycopg2.connect(**railway_config)(**get_railway_db_config())
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database successfully")
        print("=" * 60)
        
        # First, let's check what tables exist and their structure
        print("\n🔍 CHECKING TABLE STRUCTURES:")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN (
                'customer_accounts', 'invoices', 'payments', 'revenue', 'financial_reports',
                'support_tickets', 'support_comments', 'knowledge_base_articles', 'support_queues',
                'pbx_providers', 'calls', 'call_queues', 'call_queue_members',
                'customer_segments', 'forecasting_models', 'deals', 'contacts', 'users'
            )
            ORDER BY table_name
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]
        print(f"  Existing tables: {existing_tables}")
        
        # Check Customer Accounts
        print("\n📊 CUSTOMER ACCOUNTS MODULE:")
        if 'customer_accounts' in existing_tables:
            # Check the structure first
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'customer_accounts'
                ORDER BY ordinal_position
            """)
            columns = [row[0] for row in cursor.fetchall()]
            print(f"  Customer Accounts columns: {columns}")
            
            # Try different column names for organization
            if 'organization_id' in columns:
                cursor.execute("SELECT COUNT(*) FROM customer_accounts WHERE organization_id = 1")
            elif 'org_id' in columns:
                cursor.execute("SELECT COUNT(*) FROM customer_accounts WHERE org_id = 1")
            else:
                cursor.execute("SELECT COUNT(*) FROM customer_accounts")
            accounts_count = cursor.fetchone()[0]
            print(f"  Customer Accounts: {accounts_count}")
        else:
            print("  ❌ customer_accounts table does not exist")
        
        # Check Financial Management
        print("\n💰 FINANCIAL MANAGEMENT MODULE:")
        financial_tables = ['invoices', 'payments', 'revenue', 'financial_reports']
        for table in financial_tables:
            if table in existing_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {table.title()}: {count}")
            else:
                print(f"  ❌ {table} table does not exist")
        
        # Check Customer Support
        print("\n🎧 CUSTOMER SUPPORT MODULE:")
        support_tables = ['support_tickets', 'support_comments', 'knowledge_base_articles', 'support_queues']
        for table in support_tables:
            if table in existing_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {table.replace('_', ' ').title()}: {count}")
            else:
                print(f"  ❌ {table} table does not exist")
        
        # Check Call Center (Telephony)
        print("\n📞 CALL CENTER MODULE:")
        telephony_tables = ['pbx_providers', 'calls', 'call_queues', 'call_queue_members']
        for table in telephony_tables:
            if table in existing_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {table.replace('_', ' ').title()}: {count}")
            else:
                print(f"  ❌ {table} table does not exist")
        
        # Check Customer Segmentation (we know this works)
        print("\n📈 CUSTOMER SEGMENTATION MODULE:")
        if 'customer_segments' in existing_tables:
            cursor.execute("SELECT COUNT(*) FROM customer_segments WHERE organization_id = 1")
            segments_count = cursor.fetchone()[0]
            print(f"  Customer Segments: {segments_count}")
        
        # Check Forecasting (we know this works)
        print("\n🔮 ADVANCED FORECASTING MODULE:")
        if 'forecasting_models' in existing_tables:
            cursor.execute("SELECT COUNT(*) FROM forecasting_models WHERE organization_id = 1")
            models_count = cursor.fetchone()[0]
            print(f"  Forecasting Models: {models_count}")
        
        # Check core CRM data
        print("\n🏢 CORE CRM DATA:")
        core_tables = ['deals', 'contacts', 'users']
        for table in core_tables:
            if table in existing_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {table.title()}: {count}")
            else:
                print(f"  ❌ {table} table does not exist")
        
        print("\n" + "=" * 60)
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking modules: {e}")
        return False

if __name__ == "__main__":
    check_all_modules()