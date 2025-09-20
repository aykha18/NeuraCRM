#!/usr/bin/env python3
"""
Seed Railway Surveys Data
========================

Creates customer satisfaction surveys for Railway organization 1.
"""

import psycopg2

import sys
import os

# Add the scripts directory to the path to import db_config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from db_config import get_railway_db_config, validate_config
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime, timedelta
import random

# Railway Database Configuration
# Railway DB config now loaded from environment variables

def seed_railway_surveys():
    """Create customer satisfaction surveys for Railway"""
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
        
        # Check if surveys already exist
        cursor.execute("SELECT COUNT(*) FROM customer_satisfaction_surveys WHERE organization_id = 1")
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0:
            print(f"✓ Surveys already exist ({existing_count} surveys)")
            return True
        
        # Get some support tickets to link surveys to
        cursor.execute("SELECT id FROM support_tickets WHERE organization_id = 1 LIMIT 15")
        ticket_ids = [row[0] for row in cursor.fetchall()]
        
        if not ticket_ids:
            print("❌ No support tickets found to link surveys to")
            return False
        
        # Create customer satisfaction surveys with correct schema
        surveys_data = [
            {
                "customer_name": "Ahmed Al-Rashid",
                "customer_email": "ahmed@techflow.com",
                "rating": 9,
                "nps_score": 9,
                "overall_satisfaction": 9,
                "response_time_rating": 8,
                "resolution_quality_rating": 10,
                "agent_knowledge_rating": 9,
                "communication_rating": 9,
                "what_went_well": "Excellent service and quick response time. The technical team was very professional.",
                "what_could_improve": "Could provide more detailed status updates during resolution process."
            },
            {
                "customer_name": "Sarah Johnson",
                "customer_email": "sarah@innovatecorp.com",
                "rating": 8,
                "nps_score": 8,
                "overall_satisfaction": 8,
                "response_time_rating": 7,
                "resolution_quality_rating": 9,
                "agent_knowledge_rating": 8,
                "communication_rating": 8,
                "what_went_well": "Good overall experience. Minor issue with response time but resolved quickly.",
                "what_could_improve": "Initial response time could be faster."
            },
            {
                "customer_name": "Mohammed Hassan",
                "customer_email": "mohammed@digitalplus.com",
                "rating": 10,
                "nps_score": 10,
                "overall_satisfaction": 10,
                "response_time_rating": 9,
                "resolution_quality_rating": 10,
                "agent_knowledge_rating": 10,
                "communication_rating": 10,
                "what_went_well": "Outstanding support! The team went above and beyond to solve our complex technical issues.",
                "what_could_improve": "Nothing to improve - perfect service!"
            },
            {
                "customer_name": "Fatima Al-Zahra",
                "customer_email": "fatima@cloudtech.com",
                "rating": 7,
                "nps_score": 7,
                "overall_satisfaction": 7,
                "response_time_rating": 6,
                "resolution_quality_rating": 8,
                "agent_knowledge_rating": 8,
                "communication_rating": 7,
                "what_went_well": "Satisfied with the service. Quality of resolution was good.",
                "what_could_improve": "Improve on initial response time."
            },
            {
                "customer_name": "David Chen",
                "customer_email": "david@nexusenterprise.com",
                "rating": 9,
                "nps_score": 9,
                "overall_satisfaction": 9,
                "response_time_rating": 9,
                "resolution_quality_rating": 9,
                "agent_knowledge_rating": 9,
                "communication_rating": 9,
                "what_went_well": "Very professional team. Quick resolution and excellent communication throughout the process.",
                "what_could_improve": "Keep up the great work!"
            },
            {
                "customer_name": "Aisha Mohammed",
                "customer_email": "aisha@smartbusiness.com",
                "rating": 8,
                "nps_score": 8,
                "overall_satisfaction": 8,
                "response_time_rating": 8,
                "resolution_quality_rating": 8,
                "agent_knowledge_rating": 8,
                "communication_rating": 8,
                "what_went_well": "Good service overall. The support agent was knowledgeable and helpful.",
                "what_could_improve": "Could provide more proactive updates."
            },
            {
                "customer_name": "Omar Al-Mansouri",
                "customer_email": "omar@techsolutions.com",
                "rating": 6,
                "nps_score": 6,
                "overall_satisfaction": 6,
                "response_time_rating": 5,
                "resolution_quality_rating": 7,
                "agent_knowledge_rating": 7,
                "communication_rating": 6,
                "what_went_well": "Service was okay but took longer than expected to resolve.",
                "what_could_improve": "Faster resolution times needed."
            },
            {
                "customer_name": "Lisa Wang",
                "customer_email": "lisa@innovatehub.com",
                "rating": 10,
                "nps_score": 10,
                "overall_satisfaction": 10,
                "response_time_rating": 10,
                "resolution_quality_rating": 10,
                "agent_knowledge_rating": 10,
                "communication_rating": 10,
                "what_went_well": "Exceptional service! The team provided excellent support and exceeded our expectations.",
                "what_could_improve": "Nothing - perfect service!"
            },
            {
                "customer_name": "Khalid Al-Suwaidi",
                "customer_email": "khalid@digitalworks.com",
                "rating": 8,
                "nps_score": 8,
                "overall_satisfaction": 8,
                "response_time_rating": 8,
                "resolution_quality_rating": 8,
                "agent_knowledge_rating": 8,
                "communication_rating": 8,
                "what_went_well": "Good experience with the support team. Professional and efficient service.",
                "what_could_improve": "Minor improvements in follow-up communication."
            },
            {
                "customer_name": "Emily Rodriguez",
                "customer_email": "emily@cloudsystems.com",
                "rating": 9,
                "nps_score": 9,
                "overall_satisfaction": 9,
                "response_time_rating": 9,
                "resolution_quality_rating": 9,
                "agent_knowledge_rating": 9,
                "communication_rating": 9,
                "what_went_well": "Very satisfied with the support provided. Quick response and effective solution.",
                "what_could_improve": "Continue the excellent service!"
            }
        ]
        
        created_count = 0
        for i, survey_data in enumerate(surveys_data):
            # Random date within last 30 days
            submitted_date = datetime.now() - timedelta(days=random.randint(1, 30))
            
            cursor.execute("""
                INSERT INTO customer_satisfaction_surveys (
                    ticket_id, organization_id, survey_type, rating,
                    nps_score, overall_satisfaction, response_time_rating,
                    resolution_quality_rating, agent_knowledge_rating,
                    communication_rating, what_went_well, what_could_improve,
                    additional_comments, follow_up_required, submitted_at,
                    customer_email, customer_name
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                ticket_ids[i % len(ticket_ids)],  # ticket_id
                1,  # organization_id
                "post_support",  # survey_type
                survey_data["rating"],
                survey_data["nps_score"],
                survey_data["overall_satisfaction"],
                survey_data["response_time_rating"],
                survey_data["resolution_quality_rating"],
                survey_data["agent_knowledge_rating"],
                survey_data["communication_rating"],
                survey_data["what_went_well"],
                survey_data["what_could_improve"],
                f"Additional feedback for {survey_data['customer_name']}",  # additional_comments
                random.choice([True, False]),  # follow_up_required
                submitted_date,
                survey_data["customer_email"],
                survey_data["customer_name"]
            ))
            created_count += 1
        
        print(f"✓ Created {created_count} customer satisfaction surveys")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating surveys: {e}")
        return False

if __name__ == "__main__":
    seed_railway_surveys()