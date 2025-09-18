#!/usr/bin/env python3
"""
Fix missing columns in Railway database
"""
import os
import sys
from sqlalchemy import create_engine, text

# Railway database URL
RAILWAY_DB_URL = "postgresql://postgres:irUsikIqAifdrCMNOlGtApioMQJDjDfE@nozomi.proxy.rlwy.net:49967/railway"

def fix_missing_columns():
    """Add missing columns to Railway database tables"""
    try:
        # Create engine
        engine = create_engine(RAILWAY_DB_URL)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Connected to Railway database!")
        
        # Add missing columns to support_tickets table
        missing_columns = [
            "ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS assignment_reason VARCHAR;",
            "ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS assignment_type VARCHAR;",
            "ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS queue_id INTEGER;",
            "ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS resolution VARCHAR;",
            "ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS resolution_notes TEXT;",
            "ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS resolved_by_id INTEGER;",
            "ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS closure_reason VARCHAR;",
            "ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS closure_category VARCHAR;",
            "ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS follow_up_required BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS follow_up_date DATE;",
            "ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS follow_up_notes TEXT;",
            "ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS customer_satisfied BOOLEAN;",
            "ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS internal_notes TEXT;",
            "ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS escalated_to_id INTEGER;",
            "ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS escalation_reason TEXT;",
            "ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS satisfaction_feedback TEXT;",
            "ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS satisfaction_survey_sent BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS satisfaction_survey_sent_at TIMESTAMP;",
            "ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS created_by INTEGER;",
            "ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS customer_account_id INTEGER;",
            "ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS contact_id INTEGER;"
        ]
        
        with engine.connect() as conn:
            for sql in missing_columns:
                try:
                    conn.execute(text(sql))
                    column_name = sql.split("ADD COLUMN IF NOT EXISTS ")[1].split(" ")[0]
                    print(f"✅ Added column: {column_name}")
                except Exception as e:
                    print(f"⚠️  Column might already exist: {e}")
            
            conn.commit()
            print("✅ All missing columns added successfully!")
        
        # Add missing columns to support_comments table
        comment_columns = [
            "ALTER TABLE support_comments ADD COLUMN IF NOT EXISTS author_name VARCHAR;",
            "ALTER TABLE support_comments ADD COLUMN IF NOT EXISTS author_email VARCHAR;",
            "ALTER TABLE support_comments ADD COLUMN IF NOT EXISTS author_type VARCHAR DEFAULT 'agent';",
            "ALTER TABLE support_comments ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"
        ]
        
        with engine.connect() as conn:
            for sql in comment_columns:
                try:
                    conn.execute(text(sql))
                    column_name = sql.split("ADD COLUMN IF NOT EXISTS ")[1].split(" ")[0]
                    print(f"✅ Added comment column: {column_name}")
                except Exception as e:
                    print(f"⚠️  Comment column might already exist: {e}")
            
            conn.commit()
            print("✅ All missing comment columns added successfully!")
        
        print("🎉 Database schema fix completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database schema: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_missing_columns()
    sys.exit(0 if success else 1)
