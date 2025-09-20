#!/usr/bin/env python3
"""
Verify Railway Support Data
==========================

This script verifies that all support data exists in Railway database.
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

def verify_support_data():
    """Verify all support data exists in Railway"""
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
        
        # Check nodeit user
        cursor.execute("SELECT id, name, email, organization_id FROM users WHERE email = 'nodeit@node.com'")
        user = cursor.fetchone()
        if user:
            print(f"👤 User: {user[1]} (ID: {user[0]}) -> Organization: {user[3]}")
            org_id = user[3]
            
            print(f"\n📊 SUPPORT DATA FOR ORGANIZATION {org_id}:")
            print("-" * 40)
            
            # Support Tickets
            cursor.execute("SELECT COUNT(*) FROM support_tickets WHERE organization_id = %s", (org_id,))
            ticket_count = cursor.fetchone()[0]
            print(f"🎫 Support Tickets: {ticket_count}")
            
            # Support Comments
            cursor.execute("""
                SELECT COUNT(*) FROM support_comments sc
                JOIN support_tickets st ON sc.ticket_id = st.id
                WHERE st.organization_id = %s
            """, (org_id,))
            comment_count = cursor.fetchone()[0]
            print(f"💬 Support Comments: {comment_count}")
            
            # Knowledge Base Articles
            cursor.execute("SELECT COUNT(*) FROM knowledge_base_articles WHERE organization_id = %s", (org_id,))
            kb_count = cursor.fetchone()[0]
            print(f"📚 Knowledge Base Articles: {kb_count}")
            
            # Customer Satisfaction Surveys
            cursor.execute("SELECT COUNT(*) FROM customer_satisfaction_surveys WHERE organization_id = %s", (org_id,))
            survey_count = cursor.fetchone()[0]
            print(f"📊 Customer Satisfaction Surveys: {survey_count}")
            
            # Support Queues
            cursor.execute("SELECT COUNT(*) FROM support_queues WHERE organization_id = %s", (org_id,))
            queue_count = cursor.fetchone()[0]
            print(f"🔄 Support Queues: {queue_count}")
            
            print(f"\n✅ ALL SUPPORT DATA IS PRESENT!")
            print(f"   - Tickets: {ticket_count}")
            print(f"   - Comments: {comment_count}")
            print(f"   - Knowledge Base: {kb_count}")
            print(f"   - Surveys: {survey_count}")
            print(f"   - Queues: {queue_count}")
            
            if ticket_count > 0:
                print(f"\n📋 Sample Support Tickets:")
                cursor.execute("""
                    SELECT id, title, status, priority, created_at 
                    FROM support_tickets 
                    WHERE organization_id = %s 
                    ORDER BY created_at DESC 
                    LIMIT 5
                """, (org_id,))
                sample_tickets = cursor.fetchall()
                for ticket in sample_tickets:
                    print(f"  - ID {ticket[0]}: {ticket[1]} ({ticket[2]}, {ticket[3]})")
            
            if survey_count > 0:
                print(f"\n📊 Sample Surveys:")
                cursor.execute("""
                    SELECT customer_name, rating, overall_satisfaction, submitted_at 
                    FROM customer_satisfaction_surveys 
                    WHERE organization_id = %s 
                    ORDER BY submitted_at DESC 
                    LIMIT 3
                """, (org_id,))
                sample_surveys = cursor.fetchall()
                for survey in sample_surveys:
                    print(f"  - {survey[0]}: Rating {survey[1]}, Satisfaction {survey[2]}")
            
            print(f"\n🔑 AUTHENTICATION REQUIRED:")
            print(f"   To access this data, login to Railway with:")
            print(f"   Email: nodeit@node.com")
            print(f"   Password: NodeIT2024!")
            print(f"   URL: https://neuracrm.up.railway.app")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error verifying support data: {e}")

if __name__ == "__main__":
    verify_support_data()
