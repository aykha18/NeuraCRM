#!/usr/bin/env python3
"""
Check Railway Customer Segmentation Data
=======================================

This script checks if customer segmentation data exists in the Railway database.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json
import sys
import os

# Add the scripts directory to the path to import db_config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from db_config import get_railway_db_config, validate_config

def check_customer_segments():
    """Check customer segmentation data in Railway database"""
    try:
        # Validate environment configuration
        validate_config()
        
        # Get Railway database configuration from environment variables
        railway_config = get_railway_db_config()
        
        print("🔌 Connecting to Railway database...")
        conn = psycopg2.connect(**railway_config)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database successfully")
        
        # Check customer_segments table
        cursor.execute("SELECT COUNT(*) FROM customer_segments WHERE organization_id = 1")
        segments_count = cursor.fetchone()[0]
        print(f"📊 Customer segments count for org 1: {segments_count}")
        
        if segments_count > 0:
            cursor.execute("""
                SELECT id, name, segment_type, customer_count, total_deal_value, is_active 
                FROM customer_segments 
                WHERE organization_id = 1 
                ORDER BY created_at DESC
            """)
            segments = cursor.fetchall()
            
            print("\n📋 Customer Segments:")
            for segment in segments:
                print(f"  - ID: {segment[0]}, Name: {segment[1]}, Type: {segment[2]}")
                print(f"    Count: {segment[3]}, Value: ${segment[4]:,.2f}, Active: {segment[5]}")
        else:
            print("❌ No customer segments found for organization 1")
        
        # Check customer_segment_members table
        cursor.execute("SELECT COUNT(*) FROM customer_segment_members")
        members_count = cursor.fetchone()[0]
        print(f"\n👥 Segment members count: {members_count}")
        
        # Check segment_analytics table
        cursor.execute("SELECT COUNT(*) FROM segment_analytics WHERE organization_id = 1")
        analytics_count = cursor.fetchone()[0]
        print(f"📈 Segment analytics count for org 1: {analytics_count}")
        
        # Check if we have contacts and deals to create segments from
        cursor.execute("SELECT COUNT(*) FROM contacts WHERE organization_id = 1")
        contacts_count = cursor.fetchone()[0]
        print(f"\n📞 Contacts count for org 1: {contacts_count}")
        
        cursor.execute("SELECT COUNT(*) FROM deals WHERE organization_id = 1")
        deals_count = cursor.fetchone()[0]
        print(f"💼 Deals count for org 1: {deals_count}")
        
        cursor.close()
        conn.close()
        
        if segments_count == 0:
            print("\n💡 Recommendation: Run the customer segmentation seeding script:")
            print("   python scripts/seed_customer_segmentation.py")
        
        return segments_count > 0
        
    except Exception as e:
        print(f"❌ Error checking customer segments: {e}")
        return False

if __name__ == "__main__":
    check_customer_segments()
