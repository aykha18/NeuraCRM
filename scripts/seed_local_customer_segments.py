#!/usr/bin/env python3
"""
Seed Local Customer Segmentation Data
====================================

Creates realistic customer segments and data for the local database.
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

def seed_local_customer_segments():
    """Create realistic customer segments for the local organization"""
    
    # Get database session
    db_session = get_session_local()()
    
    try:
        print("🚀 Seeding Local Customer Segmentation Data...")
        print("=" * 50)
        
        # Find the organization (should be ID 18 for local)
        org = db_session.query(Organization).filter(Organization.id == 18).first()
        if not org:
            print("❌ Organization 18 not found. Please run essential demo data first.")
            return False
        
        print(f"✓ Found organization: {org.name}")
        
        # Check if we have the necessary data
        contacts_count = db_session.query(Contact).filter(Contact.organization_id == 18).count()
        deals_count = db_session.query(Deal).filter(Deal.organization_id == 18).count()
        
        print(f"✓ Found {contacts_count} contacts")
        print(f"✓ Found {deals_count} deals")
        
        if contacts_count == 0 or deals_count == 0:
            print("❌ Not enough data to create customer segments")
            return False
        
        # Clear existing segments for organization 18
        db_session.query(CustomerSegmentMember).filter(
            CustomerSegmentMember.segment_id.in_(
                db_session.query(CustomerSegment.id).filter(CustomerSegment.organization_id == 18)
            )
        ).delete(synchronize_session=False)
        
        db_session.query(CustomerSegment).filter(CustomerSegment.organization_id == 18).delete()
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
        segment_objects = []
        for segment_data in segments_data:
            segment = CustomerSegment(
                organization_id=18,
                name=segment_data["name"],
                description=segment_data["description"],
                segment_type=segment_data["segment_type"],
                criteria=segment_data["criteria"],
                criteria_description=segment_data["criteria_description"],
                customer_count=0,
                total_deal_value=0,
                avg_deal_value=0,
                conversion_rate=0,
                insights={"ai_generated": True, "confidence": 0.85},
                recommendations=["Focus on retention", "Increase engagement"],
                risk_score=0.5,
                opportunity_score=0.5,
                is_active=True,
                is_auto_updated=True,
                last_updated=datetime.now(),
                created_by=23,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db_session.add(segment)
            segment_objects.append(segment)
        
        db_session.commit()
        print(f"✓ Created {len(segments_data)} customer segments")
        
        # Populate segment members based on criteria
        for segment in segment_objects:
            criteria = segment.criteria
            members_added = 0
            
            if segment.name == "High-Value Customers":
                # Find contacts with high-value won deals
                high_value_contacts = db_session.query(Contact).join(Deal).filter(
                    Contact.organization_id == 18,
                    Deal.organization_id == 18,
                    Deal.value >= criteria["min_deal_value"],
                    Deal.status == "won"
                ).distinct().limit(20).all()
                
                for contact in high_value_contacts:
                    member = CustomerSegmentMember(
                        segment_id=segment.id,
                        contact_id=contact.id,
                        membership_score=0.9,
                        membership_reasons={"high_deal_value": True, "won_deals": True},
                        added_by_ai=True,
                        segment_engagement_score=0.85,
                        last_activity_in_segment=datetime.now(),
                        added_at=datetime.now(),
                        last_updated=datetime.now()
                    )
                    db_session.add(member)
                    members_added += 1
            
            elif segment.name == "Active Prospects":
                # Find recent contacts
                recent_contacts = db_session.query(Contact).filter(
                    Contact.organization_id == 18,
                    Contact.created_at >= datetime.now() - timedelta(days=criteria["days_since_last_activity"])
                ).limit(15).all()
                
                for contact in recent_contacts:
                    member = CustomerSegmentMember(
                        segment_id=segment.id,
                        contact_id=contact.id,
                        membership_score=0.75,
                        membership_reasons={"recent_activity": True, "high_engagement": True},
                        added_by_ai=True,
                        segment_engagement_score=0.8,
                        last_activity_in_segment=datetime.now(),
                        added_at=datetime.now(),
                        last_updated=datetime.now()
                    )
                    db_session.add(member)
                    members_added += 1
            
            elif segment.name == "Enterprise Customers":
                # Find contacts from large companies with multiple deals
                enterprise_contacts = db_session.query(Contact).filter(
                    Contact.organization_id == 18,
                    Contact.company.isnot(None),
                    db_session.query(Deal).filter(
                        Deal.contact_id == Contact.id,
                        Deal.organization_id == 18
                    ).count() >= criteria["min_deal_count"]
                ).limit(10).all()
                
                for contact in enterprise_contacts:
                    deal_count = db_session.query(Deal).filter(
                        Deal.contact_id == contact.id,
                        Deal.organization_id == 18
                    ).count()
                    
                    member = CustomerSegmentMember(
                        segment_id=segment.id,
                        contact_id=contact.id,
                        membership_score=0.85,
                        membership_reasons={"enterprise_company": True, "multiple_deals": deal_count},
                        added_by_ai=True,
                        segment_engagement_score=0.75,
                        last_activity_in_segment=datetime.now(),
                        added_at=datetime.now(),
                        last_updated=datetime.now()
                    )
                    db_session.add(member)
                    members_added += 1
            
            elif segment.name == "At-Risk Customers":
                # Find customers with old open deals
                at_risk_contacts = db_session.query(Contact).join(Deal).filter(
                    Contact.organization_id == 18,
                    Deal.organization_id == 18,
                    Deal.status == "open",
                    Deal.created_at <= datetime.now() - timedelta(days=criteria["days_since_last_activity"])
                ).distinct().limit(10).all()
                
                for contact in at_risk_contacts:
                    member = CustomerSegmentMember(
                        segment_id=segment.id,
                        contact_id=contact.id,
                        membership_score=0.6,
                        membership_reasons={"declining_engagement": True, "old_open_deals": True},
                        added_by_ai=True,
                        segment_engagement_score=0.4,
                        last_activity_in_segment=datetime.now(),
                        added_at=datetime.now(),
                        last_updated=datetime.now()
                    )
                    db_session.add(member)
                    members_added += 1
            
            elif segment.name == "SMB Customers":
                # Find contacts with smaller deals
                smb_contacts = db_session.query(Contact).join(Deal).filter(
                    Contact.organization_id == 18,
                    Deal.organization_id == 18,
                    Deal.value <= criteria["max_deal_value"]
                ).distinct().limit(15).all()
                
                for contact in smb_contacts:
                    member = CustomerSegmentMember(
                        segment_id=segment.id,
                        contact_id=contact.id,
                        membership_score=0.7,
                        membership_reasons={"smb_company": True, "smaller_deals": True},
                        added_by_ai=True,
                        segment_engagement_score=0.65,
                        last_activity_in_segment=datetime.now(),
                        added_at=datetime.now(),
                        last_updated=datetime.now()
                    )
                    db_session.add(member)
                    members_added += 1
            
            print(f"✓ Added {members_added} members to segment: {segment.name}")
            
            # Update segment statistics
            segment.customer_count = members_added
            segment.last_updated = datetime.now()
            
        # Commit all segment members first
        db_session.commit()
        print("💾 Committed segment members to database")
        
        # Now calculate financial statistics for each segment
        for segment in segment_objects:
            print(f"\n🔄 Calculating financials for: {segment.name}")
            
            # Calculate financial statistics for this segment
            member_contact_ids = db_session.query(CustomerSegmentMember.contact_id).filter(
                CustomerSegmentMember.segment_id == segment.id
            ).all()
            member_contact_ids = [row[0] for row in member_contact_ids]
            
            print(f"  🔍 Found {len(member_contact_ids)} member contacts for {segment.name}")
            
            if member_contact_ids:
                if segment.name == "High-Value Customers":
                    deals = db_session.query(Deal).filter(
                        Deal.contact_id.in_(member_contact_ids),
                        Deal.organization_id == 18,
                        Deal.value >= 50000
                    ).all()
                elif segment.name == "Active Prospects":
                    deals = db_session.query(Deal).filter(
                        Deal.contact_id.in_(member_contact_ids),
                        Deal.organization_id == 18,
                        Deal.created_at >= datetime.now() - timedelta(days=30)
                    ).all()
                elif segment.name == "Enterprise Customers":
                    deals = db_session.query(Deal).filter(
                        Deal.contact_id.in_(member_contact_ids),
                        Deal.organization_id == 18,
                        Deal.value >= 25000
                    ).all()
                elif segment.name == "At-Risk Customers":
                    deals = db_session.query(Deal).filter(
                        Deal.contact_id.in_(member_contact_ids),
                        Deal.organization_id == 18,
                        Deal.status == "open",
                        Deal.created_at <= datetime.now() - timedelta(days=90)
                    ).all()
                elif segment.name == "SMB Customers":
                    deals = db_session.query(Deal).filter(
                        Deal.contact_id.in_(member_contact_ids),
                        Deal.organization_id == 18,
                        Deal.value <= 25000
                    ).all()
                else:
                    deals = db_session.query(Deal).filter(
                        Deal.contact_id.in_(member_contact_ids),
                        Deal.organization_id == 18
                    ).all()
                
                print(f"  🔍 Found {len(deals)} deals for {segment.name}")
                
                if deals:
                    total_value = sum(deal.value or 0 for deal in deals)
                    avg_value = total_value / len(deals) if deals else 0
                    won_deals = [deal for deal in deals if deal.status == "won"]
                    conversion_rate = (len(won_deals) / len(deals) * 100) if deals else 0
                    
                    segment.total_deal_value = total_value
                    segment.avg_deal_value = avg_value
                    segment.conversion_rate = conversion_rate
                    
                    print(f"  📊 {segment.name}: ${total_value:,.2f} total, ${avg_value:,.2f} avg, {conversion_rate:.1f}% conversion")
                else:
                    print(f"  ⚠️  No deals found for {segment.name}")
        
        # Final commit with all financial data
        db_session.commit()
        
        print("=" * 50)
        print("✅ Local customer segmentation seeding completed!")
        print("\nYou can now:")
        print("1. Refresh the Customer Segmentation page")
        print("2. See proper financial metrics and statistics")
        print("3. View realistic customer segment data")
        
        return True
        
    except Exception as e:
        db_session.rollback()
        print(f"❌ Error seeding customer segments: {e}")
        return False
    finally:
        db_session.close()

if __name__ == "__main__":
    seed_local_customer_segments()
