#!/usr/bin/env python3
"""
Fix Railway Knowledge Base
=========================

This script fixes the knowledge base articles data to ensure all date fields have proper values.
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

def fix_knowledge_base_data():
    """Fix knowledge base articles data to ensure all date fields have proper values"""
    try:
        print("🔌 Connecting to Railway database...")
        conn = psycopg2.connect(**RAILWAY_DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database successfully")
        print("=" * 60)
        
        # Check for knowledge base articles with NULL dates
        cursor.execute("""
            SELECT COUNT(*) FROM knowledge_base_articles 
            WHERE organization_id = 1 
            AND (created_at IS NULL OR updated_at IS NULL)
        """)
        null_date_count = cursor.fetchone()[0]
        
        print(f"📊 Knowledge base articles with NULL dates: {null_date_count}")
        
        if null_date_count > 0:
            print("🔧 Fixing NULL date fields...")
            
            # Update articles with NULL created_at
            cursor.execute("""
                UPDATE knowledge_base_articles 
                SET created_at = NOW() 
                WHERE organization_id = 1 
                AND created_at IS NULL
            """)
            created_at_fixed = cursor.rowcount
            print(f"  ✅ Fixed {created_at_fixed} articles with NULL created_at")
            
            # Update articles with NULL updated_at
            cursor.execute("""
                UPDATE knowledge_base_articles 
                SET updated_at = NOW() 
                WHERE organization_id = 1 
                AND updated_at IS NULL
            """)
            updated_at_fixed = cursor.rowcount
            print(f"  ✅ Fixed {updated_at_fixed} articles with NULL updated_at")
        
        # Check final status
        cursor.execute("""
            SELECT COUNT(*) FROM knowledge_base_articles 
            WHERE organization_id = 1
        """)
        total_articles = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM knowledge_base_articles 
            WHERE organization_id = 1 
            AND (created_at IS NULL OR updated_at IS NULL)
        """)
        remaining_null_dates = cursor.fetchone()[0]
        
        print(f"\n📊 FINAL STATUS:")
        print(f"  Total knowledge base articles: {total_articles}")
        print(f"  Articles with NULL dates: {remaining_null_dates}")
        
        if remaining_null_dates == 0:
            print("✅ All knowledge base date fields fixed successfully!")
        else:
            print("⚠️  Some knowledge base date fields still need attention")
        
        # Show sample articles
        if total_articles > 0:
            print(f"\n📋 Sample Knowledge Base Articles:")
            cursor.execute("""
                SELECT id, title, status, created_at, updated_at 
                FROM knowledge_base_articles 
                WHERE organization_id = 1 
                ORDER BY created_at DESC 
                LIMIT 3
            """)
            sample_articles = cursor.fetchall()
            for article in sample_articles:
                print(f"  - ID {article[0]}: {article[1]} ({article[2]}) - {article[3]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error fixing knowledge base: {e}")

if __name__ == "__main__":
    fix_knowledge_base_data()
