#!/usr/bin/env python3
"""
Inspect Surveys Schema
=====================

This script inspects the actual schema of customer_satisfaction_surveys table.
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

def inspect_surveys_schema():
    """Inspect the schema of customer_satisfaction_surveys table"""
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
        
        print("\n📋 CUSTOMER_SATISFACTION_SURVEYS TABLE SCHEMA:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'customer_satisfaction_surveys'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        if columns:
            for col in columns:
                print(f"  - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
        else:
            print("  ❌ Table customer_satisfaction_surveys does not exist")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error inspecting schema: {e}")

if __name__ == "__main__":
    inspect_surveys_schema()
