#!/usr/bin/env python3
"""
Check Local Deals Data
=====================

Check what deals exist in the local database and their values.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy.orm import Session
from api.db import get_session_local
from api.models import Deal, Contact, Organization

def check_local_deals():
    """Check deals in local database"""
    
    # Get database session
    db_session = get_session_local()()
    
    try:
        print("🔍 Checking Local Database Deals...")
        print("=" * 50)
        
        # Check organization
        org = db_session.query(Organization).filter(Organization.id == 18).first()
        if org:
            print(f"✓ Organization: {org.name} (ID: {org.id})")
        else:
            print("❌ Organization 18 not found")
            return
        
        # Check contacts
        contacts_count = db_session.query(Contact).filter(Contact.organization_id == 18).count()
        print(f"📞 Contacts: {contacts_count}")
        
        # Check deals
        deals_count = db_session.query(Deal).filter(Deal.organization_id == 18).count()
        print(f"💼 Total deals: {deals_count}")
        
        # Check deals with values
        deals_with_values = db_session.query(Deal).filter(
            Deal.organization_id == 18,
            Deal.value.isnot(None),
            Deal.value > 0
        ).all()
        
        print(f"💰 Deals with values: {len(deals_with_values)}")
        
        if deals_with_values:
            print("\n📊 Sample deals with values:")
            for deal in deals_with_values[:5]:
                print(f"  - Deal {deal.id}: ${deal.value:,.2f} ({deal.status}) - Contact: {deal.contact_id}")
        
        # Check deal statuses
        status_counts = {}
        for deal in db_session.query(Deal).filter(Deal.organization_id == 18).all():
            status = deal.status or 'unknown'
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"\n📈 Deal status breakdown:")
        for status, count in status_counts.items():
            print(f"  - {status}: {count}")
        
        # Check high-value deals
        high_value_deals = db_session.query(Deal).filter(
            Deal.organization_id == 18,
            Deal.value >= 50000
        ).count()
        print(f"\n🎯 High-value deals (≥$50K): {high_value_deals}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking deals: {e}")
        return False
    finally:
        db_session.close()

if __name__ == "__main__":
    check_local_deals()
