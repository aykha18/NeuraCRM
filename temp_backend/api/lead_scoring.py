"""
Lead Scoring Service
AI-powered lead scoring system for Smart CRM
"""
import json
from datetime import datetime
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from api.models import Lead, Contact, User, Activity, Message

class LeadScoringService:
    """AI-powered lead scoring service"""
    
    def __init__(self):
        # Scoring weights for different factors - adjusted for higher scores
        self.weights = {
            "company_size": 0.20,      # Increased from 0.15
            "industry": 0.15,           # Increased from 0.10
            "engagement_level": 0.30,   # Increased from 0.25
            "decision_maker": 0.15,     # Decreased from 0.20
            "urgency": 0.10,            # Decreased from 0.15
            "timeline": 0.05,           # Decreased from 0.10
            "source_quality": 0.05      # Same
        }
        
        # Industry scoring (higher = better) - increased scores
        self.industry_scores = {
            "technology": 35,           # Increased from 20
            "healthcare": 32,           # Increased from 18
            "finance": 30,              # Increased from 16
            "manufacturing": 28,        # Increased from 14
            "retail": 25,               # Increased from 12
            "education": 22,            # Increased from 10
            "government": 20,           # Increased from 8
            "non_profit": 18           # Increased from 6
        }
        
        # Source quality scoring - increased scores
        self.source_scores = {
            "referral": 35,             # Increased from 20
            "website": 30,              # Increased from 15
            "social_media": 25,         # Increased from 12
            "email_campaign": 22,       # Increased from 10
            "cold_outreach": 15,        # Increased from 5
            "manual": 20                # Increased from 8
        }
    
    def calculate_lead_score(self, lead: Lead, db: Session) -> Dict[str, Any]:
        """Calculate comprehensive lead score with AI analysis"""
        
        # Get lead context
        contact = db.query(Contact).filter(Contact.id == lead.contact_id).first()
        owner = db.query(User).filter(User.id == lead.owner_id).first()
        
        # Calculate individual factor scores
        scores = {}
        
        # 1. Company/Contact Analysis
        scores["company_size"] = self._score_company_size(contact)
        scores["industry"] = self._score_industry(contact)
        
        # 2. Engagement Analysis
        scores["engagement_level"] = self._score_engagement(lead, db)
        
        # 3. Decision Making Power
        scores["decision_maker"] = self._score_decision_maker(lead, contact)
        
        # 4. Urgency Analysis
        scores["urgency"] = self._score_urgency(lead, db)
        
        # 5. Timeline Analysis
        scores["timeline"] = self._score_timeline(lead)
        
        # 6. Source Quality
        scores["source_quality"] = self._score_source(lead)
        
        # Calculate weighted total score
        total_score = 0
        for factor, score in scores.items():
            total_score += score * self.weights[factor]
        
        # Cap at 100
        total_score = min(int(total_score), 100)
        
        # Determine confidence level
        confidence = self._calculate_confidence(scores)
        
        # Generate scoring factors explanation
        factors_explanation = self._generate_factors_explanation(scores)
        
        return {
            "score": total_score,
            "confidence": confidence,
            "factors": scores,
            "explanation": factors_explanation,
            "category": self._get_score_category(total_score),
            "recommendations": self._get_recommendations(total_score, scores)
        }
    
    def _score_company_size(self, contact: Contact) -> int:
        """Score based on company size (estimated from contact data)"""
        if not contact or not contact.company:
            return 50  # Much higher default score
        
        company = contact.company.lower()
        
        # Simple heuristic based on company name patterns - much higher scores
        if any(word in company for word in ["inc", "corp", "ltd", "llc"]):
            return 60
        elif any(word in company for word in ["enterprises", "group", "holdings"]):
            return 65
        elif any(word in company for word in ["startup", "small", "local"]):
            return 45
        else:
            return 55
    
    def _score_industry(self, contact: Contact) -> int:
        """Score based on industry"""
        if not contact or not contact.company:
            return 40  # Much higher default score
        
        company = contact.company.lower()
        
        # Industry detection based on company name/keywords
        for industry, score in self.industry_scores.items():
            if industry in company:
                return score
        
        return 40  # Much higher default score
    
    def _score_engagement(self, lead: Lead, db: Session) -> int:
        """Score based on engagement level"""
        score = 0
        
        # Base engagement from lead age - much higher scores
        days_since_created = (datetime.now() - lead.created_at).days
        if days_since_created <= 7:
            score += 60  # Recent lead - much higher
        elif days_since_created <= 30:
            score += 55  # Much higher
        elif days_since_created <= 90:
            score += 50  # Much higher
        else:
            score += 45  # Much higher
        
        # Engagement from activities (if we had activity tracking)
        # For now, use status as engagement indicator - much higher scores
        status_engagement = {
            "new": 50,          # Much higher
            "contacted": 60,     # Much higher
            "qualified": 70,     # Much higher
            "proposal": 75,      # Much higher
            "negotiation": 80,   # Much higher
            "won": 85,           # Much higher
            "lost": 40           # Much higher
        }
        
        score += status_engagement.get(lead.status.lower(), 55)  # Much higher default
        
        return min(score, 100)  # Much higher cap
    
    def _score_decision_maker(self, lead: Lead, contact: Contact) -> int:
        """Score based on decision-making power"""
        if not contact:
            return 20  # Increased default score
        
        # Simple heuristic based on title/name - increased scores
        name = contact.name.lower()
        title_indicators = {
            "ceo": 40,           # Increased from 25
            "cto": 35,           # Increased from 20
            "cfo": 35,           # Increased from 20
            "director": 30,      # Increased from 18
            "manager": 25,       # Increased from 15
            "vp": 35,            # Increased from 22
            "president": 40,     # Increased from 25
            "founder": 35,       # Increased from 20
            "owner": 30          # Increased from 18
        }
        
        for title, score in title_indicators.items():
            if title in name:
                return score
        
        return 20  # Increased default score
    
    def _score_urgency(self, lead: Lead, db: Session) -> int:
        """Score based on urgency indicators"""
        score = 20  # Increased base score from 10
        
        # Status-based urgency - increased scores
        urgent_statuses = ["qualified", "proposal", "negotiation"]
        if lead.status.lower() in urgent_statuses:
            score += 20  # Increased from 10
        
        # Lead age urgency (newer = more urgent) - increased scores
        days_since_created = (datetime.now() - lead.created_at).days
        if days_since_created <= 3:
            score += 15  # Increased from 5
        elif days_since_created <= 7:
            score += 10  # Increased from 3
        
        return min(score, 35)  # Increased cap from 15 to 35
    
    def _score_timeline(self, lead: Lead) -> int:
        """Score based on timeline fit"""
        # For now, use source as timeline indicator - increased scores
        timeline_scores = {
            "referral": 25,      # Increased from 12
            "website": 20,       # Increased from 10
            "social_media": 18,  # Increased from 8
            "email_campaign": 22, # Increased from 9
            "cold_outreach": 15, # Increased from 6
            "manual": 18         # Increased from 8
        }
        
        return timeline_scores.get(lead.source.lower(), 18)  # Increased default
    
    def _score_source(self, lead: Lead) -> int:
        """Score based on lead source quality"""
        return self.source_scores.get(lead.source.lower(), 8)
    
    def _calculate_confidence(self, scores: Dict[str, int]) -> float:
        """Calculate confidence level in the scoring"""
        # Higher confidence when we have more data points
        non_zero_scores = sum(1 for score in scores.values() if score > 0)
        base_confidence = min(non_zero_scores / len(scores), 1.0)
        
        # Adjust confidence based on score consistency
        score_variance = sum((score - sum(scores.values()) / len(scores)) ** 2 for score in scores.values())
        variance_factor = max(0.1, 1 - (score_variance / 1000))
        
        return min(base_confidence * variance_factor, 1.0)
    
    def _generate_factors_explanation(self, scores: Dict[str, int]) -> List[str]:
        """Generate human-readable explanation of scoring factors"""
        explanations = []
        
        if scores["company_size"] > 15:
            explanations.append("Large company size indicates higher potential value")
        
        if scores["industry"] > 15:
            explanations.append("Industry alignment suggests good market fit")
        
        if scores["engagement_level"] > 20:
            explanations.append("High engagement level shows strong interest")
        
        if scores["decision_maker"] > 15:
            explanations.append("Decision maker identified - faster sales cycle likely")
        
        if scores["urgency"] > 12:
            explanations.append("Urgency indicators suggest immediate opportunity")
        
        if scores["source_quality"] > 15:
            explanations.append("High-quality lead source increases conversion probability")
        
        if not explanations:
            explanations.append("Standard lead profile - requires nurturing")
        
        return explanations
    
    def _get_score_category(self, score: int) -> str:
        """Get score category label - extremely aggressive thresholds"""
        if score >= 30:  # Much lower threshold for Hot Leads
            return "Hot Lead"
        elif score >= 20:  # Lowered threshold for Warm Leads
            return "Warm Lead"
        elif score >= 10:  # Lowered threshold for Lukewarm Leads
            return "Lukewarm Lead"
        else:
            return "Cold Lead"
    
    def _get_recommendations(self, score: int, factors: Dict[str, int]) -> List[str]:
        """Get actionable recommendations based on score - extremely aggressive thresholds"""
        recommendations = []
        
        if score >= 30:  # Much lower threshold for Hot Leads
            recommendations.extend([
                "Immediate follow-up required",
                "Prepare proposal/demo",
                "Engage decision maker directly",
                "Set up contract discussion"
            ])
        elif score >= 20:  # Lowered threshold for Warm Leads
            recommendations.extend([
                "Schedule discovery call",
                "Send relevant case studies",
                "Build relationship with key stakeholders",
                "Qualify budget and timeline"
            ])
        elif score >= 10:  # Lowered threshold for Lukewarm Leads
            recommendations.extend([
                "Send educational content",
                "Nurture with value propositions",
                "Identify pain points",
                "Build awareness of solution benefits"
            ])
        else:
            recommendations.extend([
                "Add to nurture campaign",
                "Send awareness content",
                "Monitor for engagement signals",
                "Consider re-engagement campaign"
            ])
        
        return recommendations[:3]  # Limit to top 3 recommendations

# Global instance
lead_scoring_service = LeadScoringService() 