#!/usr/bin/env python3
"""
Apply closure workflow migration to Railway database
Adds new columns for ticket closure workflow
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def apply_closure_migration():
    """Apply closure workflow migration"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ Migration failed: DATABASE_URL environment variable is not set.")
        return False
    
    print(f"Using DATABASE_URL: {database_url}")
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Add closure workflow columns to support_tickets table
        closure_columns = [
            "ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS closure_reason VARCHAR",
            "ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS closure_category VARCHAR",
            "ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS follow_up_required BOOLEAN DEFAULT FALSE",
            "ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS follow_up_date TIMESTAMP",
            "ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS follow_up_notes TEXT",
            "ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS customer_satisfied BOOLEAN",
            "ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS internal_notes TEXT"
        ]
        
        for column_sql in closure_columns:
            try:
                cursor.execute(column_sql)
                print(f"✅ Applied: {column_sql}")
            except psycopg2.Error as e:
                if "already exists" in str(e):
                    print(f"⚠️  Column already exists: {column_sql}")
                else:
                    print(f"❌ Error applying {column_sql}: {e}")
                    raise
        
        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_support_tickets_closure_reason ON support_tickets(closure_reason)",
            "CREATE INDEX IF NOT EXISTS idx_support_tickets_follow_up_date ON support_tickets(follow_up_date)",
            "CREATE INDEX IF NOT EXISTS idx_support_tickets_customer_satisfied ON support_tickets(customer_satisfied)",
            "CREATE INDEX IF NOT EXISTS idx_support_tickets_resolved_at ON support_tickets(resolved_at)",
            "CREATE INDEX IF NOT EXISTS idx_support_tickets_closed_at ON support_tickets(closed_at)"
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
                print(f"✅ Created index: {index_sql}")
            except psycopg2.Error as e:
                if "already exists" in str(e):
                    print(f"⚠️  Index already exists: {index_sql}")
                else:
                    print(f"❌ Error creating index {index_sql}: {e}")
                    raise
        
        cursor.close()
        conn.close()
        
        print("✅ Support ticket closure migration applied successfully.")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    apply_closure_migration()
