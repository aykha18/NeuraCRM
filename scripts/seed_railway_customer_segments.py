#!/usr/bin/env python3
"""
Seed Customer Segmentation Data for Railway Database
==================================================

Creates realistic customer segments and data for organization ID 1 in Railway.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json
from datetime import datetime, timedelta

# Railway Database Configuration
RAILWAY_DB_CONFIG = {
    'host': 'nozomi.proxy.rlwy.net',
    'database': 'railway',
    'user': 'postgres',
    'password': 'irUsikIqAifdrCMNOlGtApioMQJDjDfE',
    'port': 49967
}

def seed_customer_segments():
    """Create realistic customer segments for Railway organization 1"""
    try:
        print("🔌 Connecting to Railway database...")
        conn = psycopg2.connect(**RAILWAY_DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database successfully")
        
        # Check if we have the necessary data
        cursor.execute("SELECT COUNT(*) FROM contacts WHERE organization_id = 1")
        contacts_count = cursor.fetchone()[0]
        print(f"📞 Found {contacts_count} contacts for organization 1")
        
        cursor.execute("SELECT COUNT(*) FROM deals WHERE organization_id = 1")
        deals_count = cursor.fetchone()[0]
        print(f"💼 Found {deals_count} deals for organization 1")
        
        if contacts_count == 0 or deals_count == 0:
            print("❌ Not enough data to create customer segments")
            return False
        
        # Clear existing segments for organization 1
        cursor.execute("DELETE FROM customer_segment_members WHERE segment_id IN (SELECT id FROM customer_segments WHERE organization_id = 1)")
        cursor.execute("DELETE FROM segment_analytics WHERE organization_id = 1")
        cursor.execute("DELETE FROM customer_segments WHERE organization_id = 1")
        print("🧹 Cleared existing customer segments")
        
        # Create customer segments
        segments_data = [
            {
                "name": "High-Value Customers",
                "description": "Customers with deal values over $50,000",
                "segment_type": "transactional",
                "criteria": {
                    "min_deal_value": 50000,
                    "deal_status": "won"
                },
                "criteria_description": "Customers who have won deals worth $50,000 or more"
            },
            {
                "name": "Active Prospects", 
                "description": "Recent leads with high engagement",
                "segment_type": "behavioral",
                "criteria": {
                    "days_since_last_activity": 30,
                    "lead_score_min": 70
                },
                "criteria_description": "Leads with activity in the last 30 days and score 70+"
            },
            {
                "name": "Enterprise Customers",
                "description": "Large companies with multiple deals",
                "segment_type": "demographic", 
                "criteria": {
                    "company_size": "enterprise",
                    "min_deal_count": 3
                },
                "criteria_description": "Enterprise companies with 3+ deals"
            },
            {
                "name": "At-Risk Customers",
                "description": "Customers with declining engagement",
                "segment_type": "predictive",
                "criteria": {
                    "days_since_last_activity": 90,
                    "deal_status": "open"
                },
                "criteria_description": "Customers with open deals but no activity in 90+ days"
            },
            {
                "name": "SMB Customers",
                "description": "Small and medium business customers",
                "segment_type": "demographic",
                "criteria": {
                    "company_size": "smb",
                    "max_deal_value": 25000
                },
                "criteria_description": "SMB companies with deals under $25,000"
            }
        ]
        
        # Insert segments
        segment_ids = []
        for i, segment_data in enumerate(segments_data, 1):
            cursor.execute("""
                INSERT INTO customer_segments (
                    organization_id, name, description, segment_type, criteria, 
                    criteria_description, customer_count, total_deal_value, 
                    avg_deal_value, conversion_rate, insights, recommendations,
                    risk_score, opportunity_score, is_active, is_auto_updated,
                    last_updated, created_by, created_at, updated_at
                ) VALUES (
                    1, %s, %s, %s, %s, %s, 0, 0, 0, 0, %s, %s, 0.5, 0.5, 
                    true, true, %s, 16, %s, %s
                ) RETURNING id
            """, (
                segment_data["name"],
                segment_data["description"], 
                segment_data["segment_type"],
                json.dumps(segment_data["criteria"]),
                segment_data["criteria_description"],
                json.dumps({"ai_generated": True, "confidence": 0.85}),
                json.dumps(["Focus on retention", "Increase engagement"]),
                datetime.now(),
                datetime.now(),
                datetime.now()
            ))
            
            segment_id = cursor.fetchone()[0]
            segment_ids.append(segment_id)
            print(f"✓ Created segment: {segment_data['name']} (ID: {segment_id})")
        
        # Populate segment members based on criteria
        for segment_id, segment_data in zip(segment_ids, segments_data):
            criteria = segment_data["criteria"]
            members_added = 0
            
            if segment_data["name"] == "High-Value Customers":
                # Find contacts with high-value won deals
                cursor.execute("""
                    SELECT DISTINCT c.id, c.name, c.email, c.company
                    FROM contacts c
                    JOIN deals d ON c.id = d.contact_id
                    WHERE c.organization_id = 1 
                    AND d.organization_id = 1
                    AND d.value >= %s
                    AND d.status = 'won'
                    LIMIT 20
                """, (criteria["min_deal_value"],))
                
                for contact_id, name, email, company in cursor.fetchall():
                    cursor.execute("""
                        INSERT INTO customer_segment_members (
                            segment_id, contact_id, membership_score, membership_reasons,
                            added_by_ai, segment_engagement_score, last_activity_in_segment,
                            added_at, last_updated
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        segment_id, contact_id, 0.9,
                        json.dumps({"high_deal_value": True, "won_deals": True}),
                        True, 0.85, datetime.now(), datetime.now(), datetime.now()
                    ))
                    members_added += 1
            
            elif segment_data["name"] == "Active Prospects":
                # Find recent contacts with high activity
                cursor.execute("""
                    SELECT DISTINCT c.id, c.name, c.email, c.company
                    FROM contacts c
                    WHERE c.organization_id = 1 
                    AND c.created_at >= %s
                    LIMIT 15
                """, (datetime.now() - timedelta(days=criteria["days_since_last_activity"]),))
                
                for contact_id, name, email, company in cursor.fetchall():
                    cursor.execute("""
                        INSERT INTO customer_segment_members (
                            segment_id, contact_id, membership_score, membership_reasons,
                            added_by_ai, segment_engagement_score, last_activity_in_segment,
                            added_at, last_updated
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        segment_id, contact_id, 0.75,
                        json.dumps({"recent_activity": True, "high_engagement": True}),
                        True, 0.8, datetime.now(), datetime.now(), datetime.now()
                    ))
                    members_added += 1
            
            elif segment_data["name"] == "Enterprise Customers":
                # Find contacts from large companies with multiple deals
                cursor.execute("""
                    SELECT c.id, c.name, c.email, c.company, COUNT(d.id) as deal_count
                    FROM contacts c
                    LEFT JOIN deals d ON c.id = d.contact_id AND d.organization_id = 1
                    WHERE c.organization_id = 1 
                    AND (c.company IS NOT NULL AND LENGTH(c.company) > 10)
                    GROUP BY c.id, c.name, c.email, c.company
                    HAVING COUNT(d.id) >= %s
                    LIMIT 10
                """, (criteria["min_deal_count"],))
                
                for contact_id, name, email, company, deal_count in cursor.fetchall():
                    cursor.execute("""
                        INSERT INTO customer_segment_members (
                            segment_id, contact_id, membership_score, membership_reasons,
                            added_by_ai, segment_engagement_score, last_activity_in_segment,
                            added_at, last_updated
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        segment_id, contact_id, 0.85,
                        json.dumps({"enterprise_company": True, "multiple_deals": deal_count}),
                        True, 0.75, datetime.now(), datetime.now(), datetime.now()
                    ))
                    members_added += 1
            
            elif segment_data["name"] == "At-Risk Customers":
                # Find customers with old open deals
                cursor.execute("""
                    SELECT DISTINCT c.id, c.name, c.email, c.company
                    FROM contacts c
                    JOIN deals d ON c.id = d.contact_id
                    WHERE c.organization_id = 1 
                    AND d.organization_id = 1
                    AND d.status = 'open'
                    AND d.created_at <= %s
                    LIMIT 10
                """, (datetime.now() - timedelta(days=criteria["days_since_last_activity"]),))
                
                for contact_id, name, email, company in cursor.fetchall():
                    cursor.execute("""
                        INSERT INTO customer_segment_members (
                            segment_id, contact_id, membership_score, membership_reasons,
                            added_by_ai, segment_engagement_score, last_activity_in_segment,
                            added_at, last_updated
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        segment_id, contact_id, 0.6,
                        json.dumps({"declining_engagement": True, "old_open_deals": True}),
                        True, 0.4, datetime.now(), datetime.now(), datetime.now()
                    ))
                    members_added += 1
            
            elif segment_data["name"] == "SMB Customers":
                # Find contacts with smaller deals
                cursor.execute("""
                    SELECT DISTINCT c.id, c.name, c.email, c.company
                    FROM contacts c
                    JOIN deals d ON c.id = d.contact_id
                    WHERE c.organization_id = 1 
                    AND d.organization_id = 1
                    AND (d.value IS NULL OR d.value <= %s)
                    AND (c.company IS NULL OR LENGTH(c.company) <= 20)
                    LIMIT 15
                """, (criteria["max_deal_value"],))
                
                for contact_id, name, email, company in cursor.fetchall():
                    cursor.execute("""
                        INSERT INTO customer_segment_members (
                            segment_id, contact_id, membership_score, membership_reasons,
                            added_by_ai, segment_engagement_score, last_activity_in_segment,
                            added_at, last_updated
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        segment_id, contact_id, 0.7,
                        json.dumps({"smb_company": True, "smaller_deals": True}),
                        True, 0.65, datetime.now(), datetime.now(), datetime.now()
                    ))
                    members_added += 1
            
            print(f"✓ Added {members_added} members to segment: {segment_data['name']}")
            
            # Update segment statistics
            cursor.execute("SELECT COUNT(*) FROM customer_segment_members WHERE segment_id = %s", (segment_id,))
            member_count = cursor.fetchone()[0]
            
            cursor.execute("""
                UPDATE customer_segments 
                SET customer_count = %s, last_updated = %s
                WHERE id = %s
            """, (member_count, datetime.now(), segment_id))
        
        # Create segment analytics
        for segment_id in segment_ids:
            cursor.execute("""
                INSERT INTO segment_analytics (
                    segment_id, organization_id, period_type, period_start, period_end,
                    customer_count, new_members, lost_members, total_revenue,
                    avg_revenue_per_customer, revenue_growth_rate, avg_engagement_score,
                    active_customers, churn_rate, total_deals, closed_deals,
                    avg_deal_size, conversion_rate, trends, predictions,
                    recommendations, generated_at
                ) VALUES (
                    %s, 1, 'monthly', %s, %s, 
                    %s, 0, 0, %s, %s, 0.15, 0.75,
                    %s, 0.05, 10, 8, 15000, 0.8,
                    %s, %s, %s, %s
                )
            """, (
                segment_id,
                datetime.now() - timedelta(days=30),
                datetime.now(),
                random.randint(5, 25),
                random.randint(50000, 200000),
                random.randint(2000, 8000),
                random.randint(5, 20),
                json.dumps({"growth": "positive", "engagement": "stable"}),
                json.dumps({"next_month_revenue": "increasing", "churn_risk": "low"}),
                json.dumps(["Increase marketing spend", "Focus on retention"]),
                datetime.now()
            ))
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Customer segmentation seeding completed successfully!")
        print("\nYou can now:")
        print("1. Login with: nodeit@node.com / NodeIT2024!")
        print("2. Access the AI Features page to see Customer Segmentation")
        print("3. Use the API endpoints to manage segments")
        
        return True
        
    except Exception as e:
        print(f"❌ Error seeding customer segments: {e}")
        return False

if __name__ == "__main__":
    import random
    seed_customer_segments()
