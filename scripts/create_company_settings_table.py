#!/usr/bin/env python3
"""
Script to create the company_settings table in the database.
This script can be used for both local and Railway databases.
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from db_config import get_railway_db_config, get_local_db_config, validate_config

def create_company_settings_table(db_config, db_name="Local"):
    """Create the company_settings table"""
    
    # SQL to create the company_settings table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS company_settings (
        id SERIAL PRIMARY KEY,
        organization_id INTEGER NOT NULL UNIQUE,
        company_name VARCHAR NOT NULL,
        company_mobile VARCHAR,
        city VARCHAR,
        area VARCHAR,
        complete_address TEXT,
        trn VARCHAR,
        currency VARCHAR DEFAULT 'AED - UAE Dirham (د.إ)',
        timezone VARCHAR DEFAULT 'Dubai (UAE)',
        trial_date_enabled BOOLEAN DEFAULT TRUE,
        trial_date_days INTEGER DEFAULT 3,
        delivery_date_enabled BOOLEAN DEFAULT TRUE,
        delivery_date_days INTEGER DEFAULT 3,
        advance_payment_enabled BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by INTEGER NOT NULL,
        FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
        FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
    );
    """
    
    # SQL to create an index on organization_id for faster lookups
    create_index_sql = """
    CREATE INDEX IF NOT EXISTS idx_company_settings_organization_id 
    ON company_settings(organization_id);
    """
    
    # SQL to create a trigger to update the updated_at timestamp
    create_trigger_sql = """
    CREATE OR REPLACE FUNCTION update_company_settings_updated_at()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    
    DROP TRIGGER IF EXISTS trigger_update_company_settings_updated_at ON company_settings;
    CREATE TRIGGER trigger_update_company_settings_updated_at
        BEFORE UPDATE ON company_settings
        FOR EACH ROW
        EXECUTE FUNCTION update_company_settings_updated_at();
    """
    
    try:
        print(f"Connecting to {db_name} database...")
        conn = psycopg2.connect(**db_config)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print(f"Creating company_settings table in {db_name} database...")
        cursor.execute(create_table_sql)
        print("✅ company_settings table created successfully")
        
        print(f"Creating index on organization_id...")
        cursor.execute(create_index_sql)
        print("✅ Index created successfully")
        
        print(f"Creating trigger for updated_at...")
        cursor.execute(create_trigger_sql)
        print("✅ Trigger created successfully")
        
        # Verify the table was created
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'company_settings'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print(f"\n📋 Table 'company_settings' structure:")
        print("-" * 60)
        for col in columns:
            print(f"{col[0]:<25} {col[1]:<15} {'NULL' if col[2] == 'YES' else 'NOT NULL':<10} {col[3] or 'None'}")
        
        cursor.close()
        conn.close()
        
        print(f"\n✅ Successfully created company_settings table in {db_name} database!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating company_settings table in {db_name} database: {str(e)}")
        return False

def main():
    """Main function to create company_settings table in both databases"""
    
    print("🏢 Company Settings Table Creation Script")
    print("=" * 50)
    
    try:
        validate_config()
        print("✅ Environment variables validated")
    except Exception as e:
        print(f"❌ Configuration error: {str(e)}")
        return
    
    success_count = 0
    
    # Create table in Railway database
    try:
        railway_config = get_railway_db_config()
        print(f"\n🚀 Creating table in Railway database...")
        if create_company_settings_table(railway_config, "Railway"):
            success_count += 1
    except Exception as e:
        print(f"❌ Failed to create table in Railway database: {str(e)}")
    
    # Create table in local database
    try:
        local_config = get_local_db_config()
        print(f"\n💻 Creating table in local database...")
        if create_company_settings_table(local_config, "Local"):
            success_count += 1
    except Exception as e:
        print(f"❌ Failed to create table in local database: {str(e)}")
    
    print(f"\n📊 Summary: {success_count}/2 databases updated successfully")
    
    if success_count > 0:
        print("\n🎉 Company settings table is ready!")
        print("You can now use the company settings endpoints:")
        print("- GET /api/company-settings")
        print("- PUT /api/company-settings")
        print("- POST /api/company-settings")
    else:
        print("\n❌ No databases were updated. Please check your configuration.")

if __name__ == "__main__":
    main()
