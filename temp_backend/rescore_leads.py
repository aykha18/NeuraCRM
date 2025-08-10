#!/usr/bin/env python3
"""
Rescore all leads with the new improved scoring algorithm
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.db import SessionLocal
from api.models import Lead
from api.lead_scoring import lead_scoring_service
from datetime import datetime

def rescore_all_leads():
    """Rescore all leads in the database with the new algorithm"""
    db = SessionLocal()
    
    try:
        print("🔄 Rescoring all leads with improved algorithm...")
        
        # Get all leads
        leads = db.query(Lead).all()
        print(f"📊 Found {len(leads)} leads to rescore")
        
        hot_leads = 0
        warm_leads = 0
        lukewarm_leads = 0
        cold_leads = 0
        
        for i, lead in enumerate(leads, 1):
            # Calculate new score
            scoring_result = lead_scoring_service.calculate_lead_score(lead, db)
            
            # Update lead with new score
            lead.score = scoring_result["score"]
            lead.score_updated_at = datetime.now()
            lead.score_factors = str(scoring_result["factors"])
            lead.score_confidence = scoring_result["confidence"]
            
            # Count by category
            category = scoring_result["category"]
            if category == "Hot Lead":
                hot_leads += 1
            elif category == "Warm Lead":
                warm_leads += 1
            elif category == "Lukewarm Lead":
                lukewarm_leads += 1
            else:
                cold_leads += 1
            
            # Progress indicator
            if i % 100 == 0:
                print(f"✅ Processed {i}/{len(leads)} leads...")
        
        # Commit all changes
        db.commit()
        
        print("\n🎉 Lead rescoring completed!")
        print(f"📈 Score Distribution:")
        print(f"   🔥 Hot Leads: {hot_leads}")
        print(f"   🔶 Warm Leads: {warm_leads}")
        print(f"   🔸 Lukewarm Leads: {lukewarm_leads}")
        print(f"   ❄️ Cold Leads: {cold_leads}")
        print(f"   📊 Total: {len(leads)}")
        
        # Calculate percentages
        total = len(leads)
        if total > 0:
            print(f"\n📊 Percentages:")
            print(f"   🔥 Hot: {hot_leads/total*100:.1f}%")
            print(f"   🔶 Warm: {warm_leads/total*100:.1f}%")
            print(f"   🔸 Lukewarm: {lukewarm_leads/total*100:.1f}%")
            print(f"   ❄️ Cold: {cold_leads/total*100:.1f}%")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error rescoring leads: {e}")
        db.rollback()
        db.close()
        return False

if __name__ == "__main__":
    print("🚀 Starting lead rescoring process...")
    success = rescore_all_leads()
    
    if success:
        print("\n✅ All leads have been successfully rescored!")
        print("🔄 Refresh your browser to see the updated scores.")
    else:
        print("\n❌ Lead rescoring failed. Check the error above.") 