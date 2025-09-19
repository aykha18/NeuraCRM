#!/usr/bin/env python3
"""
Seed Customer Segmentation Data
Creates realistic customer segments and data for user ID 23, org ID 18
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy.orm import Session
from api.db import get_session_local
from api.models import (
    User, Organization, Contact, Lead, Deal, Stage, Activity,
    CustomerSegment, CustomerSegmentMember
)
from datetime import datetime, timedelta
import random
import json

def create_customer_segments():
    """Create realistic customer segments for the organization"""
    
    # Get database session
    db_session = get_session_local()()
    
    try:
        # Verify user and organization exist
        user = db_session.query(User).filter(User.id == 23).first()
        if not user:
            print("User ID 23 not found. Creating user...")
            # Create organization first if it doesn't exist
            org = db_session.query(Organization).filter(Organization.id == 18).first()
            if not org:
                org = Organization(
                    id=18,
                    name="NodeIT Solutions",
                    domain="nodeit.com",
                    settings='{"timezone": "UTC", "currency": "USD"}'
                )
                db_session.add(org)
                db_session.commit()
                print("✓ Organization created")
            
            # Create user
            user = User(
                id=23,
                name="NodeIT Admin",
                email="nodeit@node.com",
                password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6X5c5vL2WO",  # NodeIT2024!
                role="admin",
                organization_id=18
            )
            db_session.add(user)
            db_session.commit()
            print("✓ User created")
        else:
            # Update organization_id if needed
            if user.organization_id != 18:
                user.organization_id = 18
                db_session.commit()
                print("✓ Updated user organization")
        
        print(f"✓ Found user: {user.name} ({user.email})")
        
        # Create sample contacts if they don't exist
        create_sample_contacts(db_session, user.organization_id, user.id)
        
        # Create sample deals if they don't exist
        create_sample_deals(db_session, user.organization_id, user.id)
        
        # Create customer segments
        segments_data = [
            {
                "name": "High-Value Customers",
                "description": "Customers with deals over $50,000",
                "segment_type": "transactional",
                "criteria": {
                    "deal_value_range": {
                        "min_value": 50000,
                        "max_value": None
                    }
                },
                "criteria_description": "Customers who have made deals worth $50,000 or more"
            },
            {
                "name": "Active Prospects",
                "description": "Contacts with recent activity (last 30 days)",
                "segment_type": "behavioral",
                "criteria": {
                    "last_activity_days": 30
                },
                "criteria_description": "Contacts who have had activity in the last 30 days"
            },
            {
                "name": "Enterprise Customers",
                "description": "Large companies with multiple deals",
                "segment_type": "demographic",
                "criteria": {
                    "company_size": "large",
                    "deal_count": {
                        "min_count": 2
                    }
                },
                "criteria_description": "Large companies with 2 or more deals"
            },
            {
                "name": "At-Risk Customers",
                "description": "Customers with declining engagement",
                "segment_type": "predictive",
                "criteria": {
                    "engagement_score": {
                        "max_score": 30
                    },
                    "last_activity_days": 90
                },
                "criteria_description": "Customers with low engagement scores and no recent activity"
            },
            {
                "name": "SMB Customers",
                "description": "Small to medium businesses with deals under $25,000",
                "segment_type": "transactional",
                "criteria": {
                    "deal_value_range": {
                        "min_value": 0,
                        "max_value": 25000
                    }
                },
                "criteria_description": "Small to medium businesses with deals under $25,000"
            }
        ]
        
        created_segments = []
        for segment_data in segments_data:
            # Check if segment already exists
            existing_segment = db_session.query(CustomerSegment).filter(
                CustomerSegment.name == segment_data["name"],
                CustomerSegment.organization_id == user.organization_id
            ).first()
            
            if existing_segment:
                print(f"✓ Segment '{segment_data['name']}' already exists")
                created_segments.append(existing_segment)
                continue
            
            # Create new segment
            segment = CustomerSegment(
                name=segment_data["name"],
                description=segment_data["description"],
                segment_type=segment_data["segment_type"],
                criteria=segment_data["criteria"],
                criteria_description=segment_data["criteria_description"],
                organization_id=user.organization_id,
                created_by=user.id
            )
            
            db_session.add(segment)
            db_session.commit()
            db_session.refresh(segment)
            
            print(f"✓ Created segment: {segment.name}")
            created_segments.append(segment)
        
        # Apply segmentation criteria to populate segments
        for segment in created_segments:
            apply_segmentation_to_segment(segment, db_session)
            update_segment_statistics(segment.id, db_session)
            generate_segment_insights(segment.id, db_session)
        
        print(f"\n✓ Successfully created {len(created_segments)} customer segments")
        print("✓ Applied segmentation criteria and populated segments")
        print("✓ Generated segment statistics and AI insights")
        
    except Exception as e:
        print(f"❌ Error creating customer segments: {e}")
        db_session.rollback()
        raise
    finally:
        db_session.close()

def create_sample_contacts(db_session: Session, org_id: int, user_id: int):
    """Create sample contacts for testing"""
    
    # Check if contacts already exist
    existing_contacts = db_session.query(Contact).filter(
        Contact.organization_id == org_id
    ).count()
    
    if existing_contacts > 0:
        print(f"✓ Found {existing_contacts} existing contacts")
        return
    
    contacts_data = [
        {"name": "Sarah Johnson", "email": "sarah.johnson@techcorp.com", "phone": "+1-555-0101", "company": "TechCorp Inc"},
        {"name": "Michael Chen", "email": "m.chen@innovate.com", "phone": "+1-555-0102", "company": "Innovate Solutions"},
        {"name": "Emily Rodriguez", "email": "emily@startupx.com", "phone": "+1-555-0103", "company": "StartupX"},
        {"name": "David Kim", "email": "david.kim@enterprise.com", "phone": "+1-555-0104", "company": "Enterprise Systems"},
        {"name": "Lisa Wang", "email": "lisa@smbtech.com", "phone": "+1-555-0105", "company": "SMB Tech"},
        {"name": "Robert Taylor", "email": "robert@globalcorp.com", "phone": "+1-555-0106", "company": "Global Corp"},
        {"name": "Jennifer Lee", "email": "jennifer@midmarket.com", "phone": "+1-555-0107", "company": "MidMarket Solutions"},
        {"name": "James Wilson", "email": "james@smallbiz.com", "phone": "+1-555-0108", "company": "Small Biz Inc"},
        {"name": "Amanda Davis", "email": "amanda@growth.com", "phone": "+1-555-0109", "company": "Growth Technologies"},
        {"name": "Christopher Brown", "email": "chris@scaleup.com", "phone": "+1-555-0110", "company": "ScaleUp Ventures"}
    ]
    
    for contact_data in contacts_data:
        contact = Contact(
            name=contact_data["name"],
            email=contact_data["email"],
            phone=contact_data["phone"],
            company=contact_data["company"],
            owner_id=user_id,
            organization_id=org_id
        )
        db_session.add(contact)
    
    db_session.commit()
    print(f"✓ Created {len(contacts_data)} sample contacts")

def create_sample_deals(db_session: Session, org_id: int, user_id: int):
    """Create sample deals for testing"""
    
    # Check if deals already exist
    existing_deals = db_session.query(Deal).filter(
        Deal.organization_id == org_id
    ).count()
    
    if existing_deals > 0:
        print(f"✓ Found {existing_deals} existing deals")
        return
    
    # Get contacts for deals
    contacts = db_session.query(Contact).filter(
        Contact.organization_id == org_id
    ).all()
    
    if not contacts:
        print("❌ No contacts found to create deals")
        return
    
    # Create default stage if it doesn't exist
    stage = db_session.query(Stage).filter(Stage.name == "Qualification").first()
    if not stage:
        stage = Stage(
            name="Qualification",
            order=1,
            wip_limit=10
        )
        db_session.add(stage)
        db_session.commit()
        db_session.refresh(stage)
    
    deals_data = [
        {"title": "Enterprise Software License", "value": 75000, "contact": contacts[0]},
        {"title": "Cloud Migration Services", "value": 120000, "contact": contacts[1]},
        {"title": "API Integration Package", "value": 15000, "contact": contacts[2]},
        {"title": "Digital Transformation", "value": 200000, "contact": contacts[3]},
        {"title": "Website Development", "value": 8500, "contact": contacts[4]},
        {"title": "Global Infrastructure Setup", "value": 180000, "contact": contacts[5]},
        {"title": "Marketing Automation Platform", "value": 25000, "contact": contacts[6]},
        {"title": "Small Business Starter Package", "value": 5000, "contact": contacts[7]},
        {"title": "Growth Analytics Suite", "value": 35000, "contact": contacts[8]},
        {"title": "Scale-up Technology Stack", "value": 95000, "contact": contacts[9]},
        {"title": "Additional Enterprise License", "value": 45000, "contact": contacts[3]},
        {"title": "Support and Maintenance", "value": 12000, "contact": contacts[0]},
        {"title": "Custom Development", "value": 28000, "contact": contacts[6]},
        {"title": "Data Migration Services", "value": 22000, "contact": contacts[1]},
        {"title": "Training and Onboarding", "value": 8000, "contact": contacts[8]}
    ]
    
    for deal_data in deals_data:
        # Randomly set some deals as won
        status = "won" if random.random() > 0.4 else "open"
        closed_at = datetime.utcnow() - timedelta(days=random.randint(1, 90)) if status == "won" else None
        
        deal = Deal(
            title=deal_data["title"],
            value=deal_data["value"],
            owner_id=user_id,
            stage_id=stage.id,
            organization_id=org_id,
            contact_id=deal_data["contact"].id,
            status=status,
            closed_at=closed_at,
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 180))
        )
        db_session.add(deal)
    
    db_session.commit()
    print(f"✓ Created {len(deals_data)} sample deals")

def apply_segmentation_to_segment(segment: CustomerSegment, db_session: Session):
    """Apply segmentation criteria to populate a segment"""
    
    criteria = segment.criteria
    organization_id = segment.organization_id
    
    # Start with all contacts in the organization
    query = db_session.query(Contact).filter(Contact.organization_id == organization_id)
    
    # Apply criteria filters
    if criteria.get("deal_value_range"):
        value_range = criteria["deal_value_range"]
        # Join with deals to filter by deal value
        query = query.join(Deal, Contact.id == Deal.contact_id)
        if value_range.get("min_value"):
            query = query.filter(Deal.value >= value_range["min_value"])
        if value_range.get("max_value"):
            query = query.filter(Deal.value <= value_range["max_value"])
    
    if criteria.get("last_activity_days"):
        days = criteria["last_activity_days"]
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        # For simplicity, use deal creation date as activity
        query = query.join(Deal, Contact.id == Deal.contact_id)
        query = query.filter(Deal.created_at >= cutoff_date)
    
    # Get matching contacts
    matching_contacts = query.distinct().all()
    
    # Create segment members
    members_added = 0
    for contact in matching_contacts:
        # Check if member already exists
        existing_member = db_session.query(CustomerSegmentMember).filter(
            CustomerSegmentMember.segment_id == segment.id,
            CustomerSegmentMember.contact_id == contact.id
        ).first()
        
        if not existing_member:
            new_member = CustomerSegmentMember(
                segment_id=segment.id,
                contact_id=contact.id,
                membership_score=random.uniform(0.7, 1.0),
                membership_reasons={
                    "primary_reason": f"Matches {segment.name} criteria",
                    "confidence": random.uniform(0.8, 1.0)
                },
                segment_engagement_score=random.uniform(20, 90),
                added_by_ai=True
            )
            db_session.add(new_member)
            members_added += 1
    
    print(f"✓ Added {members_added} members to segment '{segment.name}'")

def update_segment_statistics(segment_id: int, db_session: Session):
    """Update segment statistics based on current members"""
    
    segment = db_session.query(CustomerSegment).filter(CustomerSegment.id == segment_id).first()
    if not segment:
        return
    
    # Count members
    member_count = db_session.query(CustomerSegmentMember).filter(
        CustomerSegmentMember.segment_id == segment_id
    ).count()
    
    # Calculate deal metrics
    from sqlalchemy import func
    deal_stats = db_session.query(
        func.count(Deal.id).label('total_deals'),
        func.sum(Deal.value).label('total_value'),
        func.avg(Deal.value).label('avg_value'),
        func.count(Deal.id).filter(Deal.status == 'won').label('closed_deals')
    ).join(Contact, Deal.contact_id == Contact.id).join(
        CustomerSegmentMember, Contact.id == CustomerSegmentMember.contact_id
    ).filter(CustomerSegmentMember.segment_id == segment_id).first()
    
    # Update segment
    segment.customer_count = member_count
    segment.total_deal_value = float(deal_stats.total_value or 0)
    segment.avg_deal_value = float(deal_stats.avg_value or 0)
    
    if deal_stats.total_deals > 0:
        segment.conversion_rate = (deal_stats.closed_deals / deal_stats.total_deals) * 100
    else:
        segment.conversion_rate = 0
    
    segment.last_updated = datetime.utcnow()

def generate_segment_insights(segment_id: int, db_session: Session):
    """Generate AI insights for a customer segment"""
    
    segment = db_session.query(CustomerSegment).filter(CustomerSegment.id == segment_id).first()
    if not segment:
        return
    
    # Generate basic insights based on segment data
    insights = {
        "segment_health": "healthy" if segment.conversion_rate > 20 else "needs_attention",
        "growth_trend": "positive" if segment.customer_count > 0 else "stable",
        "key_characteristics": [
            f"Average deal value: ${segment.avg_deal_value:,.2f}",
            f"Conversion rate: {segment.conversion_rate:.1f}%",
            f"Total customers: {segment.customer_count}"
        ]
    }
    
    recommendations = [
        "Focus on high-value customers for upselling opportunities",
        "Implement targeted marketing campaigns for this segment",
        "Monitor conversion rates and adjust sales strategies accordingly"
    ]
    
    # Calculate risk and opportunity scores
    risk_score = max(0, 100 - segment.conversion_rate * 2)  # Higher conversion = lower risk
    opportunity_score = min(100, segment.avg_deal_value / 1000 * 10)  # Higher deal value = more opportunity
    
    # Update segment with insights
    segment.insights = insights
    segment.recommendations = recommendations
    segment.risk_score = risk_score
    segment.opportunity_score = opportunity_score

if __name__ == "__main__":
    print("🚀 Seeding Customer Segmentation Data...")
    print("=" * 50)
    
    create_customer_segments()
    
    print("=" * 50)
    print("✅ Customer segmentation seeding completed!")
    print("\nYou can now:")
    print("1. Login with: nodeit@node.com / NodeIT2024!")
    print("2. Access the AI Features page to see Customer Segmentation")
    print("3. Use the API endpoints to manage segments")
    print("\nAPI Endpoints:")
    print("- GET /api/customer-segments - List all segments")
    print("- POST /api/customer-segments - Create new segment")
    print("- GET /api/customer-segments/{id}/members - Get segment members")
    print("- POST /api/customer-segments/{id}/refresh - Refresh segment")
