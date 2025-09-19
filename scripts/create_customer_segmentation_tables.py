#!/usr/bin/env python3
"""
Create Customer Segmentation Tables
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import text
from api.db import get_engine

def create_customer_segmentation_tables():
    """Create customer segmentation tables"""
    
    engine = get_engine()
    
    # SQL to create customer segmentation tables
    create_tables_sql = """
    -- Customer Segments Table
    CREATE TABLE IF NOT EXISTS customer_segments (
        id SERIAL PRIMARY KEY,
        organization_id INTEGER NOT NULL REFERENCES organizations(id),
        name VARCHAR NOT NULL,
        description TEXT,
        segment_type VARCHAR DEFAULT 'behavioral',
        criteria JSON NOT NULL,
        criteria_description TEXT,
        customer_count INTEGER DEFAULT 0,
        total_deal_value FLOAT DEFAULT 0.0,
        avg_deal_value FLOAT DEFAULT 0.0,
        conversion_rate FLOAT DEFAULT 0.0,
        insights JSON,
        recommendations JSON,
        risk_score FLOAT DEFAULT 0.0,
        opportunity_score FLOAT DEFAULT 0.0,
        is_active BOOLEAN DEFAULT TRUE,
        is_auto_updated BOOLEAN DEFAULT TRUE,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by INTEGER NOT NULL REFERENCES users(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Customer Segment Members Table
    CREATE TABLE IF NOT EXISTS customer_segment_members (
        id SERIAL PRIMARY KEY,
        segment_id INTEGER NOT NULL REFERENCES customer_segments(id),
        contact_id INTEGER NOT NULL REFERENCES contacts(id),
        membership_score FLOAT DEFAULT 1.0,
        membership_reasons JSON,
        added_by_ai BOOLEAN DEFAULT FALSE,
        segment_engagement_score FLOAT DEFAULT 0.0,
        last_activity_in_segment TIMESTAMP,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Segment Analytics Table
    CREATE TABLE IF NOT EXISTS segment_analytics (
        id SERIAL PRIMARY KEY,
        segment_id INTEGER NOT NULL REFERENCES customer_segments(id),
        organization_id INTEGER NOT NULL REFERENCES organizations(id),
        period_type VARCHAR NOT NULL,
        period_start TIMESTAMP NOT NULL,
        period_end TIMESTAMP NOT NULL,
        customer_count INTEGER DEFAULT 0,
        new_members INTEGER DEFAULT 0,
        lost_members INTEGER DEFAULT 0,
        total_revenue FLOAT DEFAULT 0.0,
        avg_revenue_per_customer FLOAT DEFAULT 0.0,
        revenue_growth_rate FLOAT DEFAULT 0.0,
        avg_engagement_score FLOAT DEFAULT 0.0,
        active_customers INTEGER DEFAULT 0,
        churn_rate FLOAT DEFAULT 0.0,
        total_deals INTEGER DEFAULT 0,
        closed_deals INTEGER DEFAULT 0,
        avg_deal_size FLOAT DEFAULT 0.0,
        conversion_rate FLOAT DEFAULT 0.0,
        trends JSON,
        predictions JSON,
        recommendations JSON,
        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Add indexes for better performance
    CREATE INDEX IF NOT EXISTS idx_customer_segments_org_id ON customer_segments(organization_id);
    CREATE INDEX IF NOT EXISTS idx_customer_segments_active ON customer_segments(is_active);
    CREATE INDEX IF NOT EXISTS idx_segment_members_segment_id ON customer_segment_members(segment_id);
    CREATE INDEX IF NOT EXISTS idx_segment_members_contact_id ON customer_segment_members(contact_id);
    CREATE INDEX IF NOT EXISTS idx_segment_analytics_segment_id ON segment_analytics(segment_id);
    CREATE INDEX IF NOT EXISTS idx_segment_analytics_period ON segment_analytics(period_start, period_end);
    """
    
    try:
        with engine.connect() as connection:
            # Execute the SQL
            connection.execute(text(create_tables_sql))
            connection.commit()
            print("✓ Customer segmentation tables created successfully")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise

if __name__ == "__main__":
    print("🚀 Creating Customer Segmentation Tables...")
    print("=" * 50)
    
    create_customer_segmentation_tables()
    
    print("=" * 50)
    print("✅ Tables created successfully!")
    print("You can now run the seed script to populate data.")
