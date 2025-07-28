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
        # Scoring weights for different factors
        self.weights = {
            "company_size": 0.15,
            "industry": 0.10,
            "engagement_level": 0.25,
            "decision_maker": 0.20,
            "urgency": 0.15,
            "timeline": 0.10,
            "source_quality": 0.05
        }
        
        # Industry scoring (higher = better)
        self.industry_scores = {
            "technology": 20,
            "healthcare": 18,
            "finance": 16,
            "manufacturing": 14,
            "retail": 12,
            "education": 10,
            "government": 8,
            "non_profit": 6
        }
        
        # Source quality scoring
        self.source_scores = {
            "referral": 20,
            "website": 15,
            "social_media": 12,
            "email_campaign": 10,
            "cold_outreach": 5,
            "manual": 8
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
            return 10  # Default score
        
        company = contact.company.lower()
        
        # Simple heuristic based on company name patterns
        if any(word in company for word in ["inc", "corp", "ltd", "llc"]):
            return 15
        elif any(word in company for word in ["enterprises", "group", "holdings"]):
            return 18
        elif any(word in company for word in ["startup", "small", "local"]):
            return 8
        else:
            return 12
    
    def _score_industry(self, contact: Contact) -> int:
        """Score based on industry"""
        if not contact or not contact.company:
            return 10
        
        company = contact.company.lower()
        
        # Industry detection based on company name/keywords
        for industry, score in self.industry_scores.items():
            if industry in company:
                return score
        
        return 10  # Default score
    
    def _score_engagement(self, lead: Lead, db: Session) -> int:
        """Score based on engagement level"""
        score = 0
        
        # Base engagement from lead age
        days_since_created = (datetime.now() - lead.created_at).days
        if days_since_created <= 7:
            score += 15  # Recent lead
        elif days_since_created <= 30:
            score += 10
        elif days_since_created <= 90:
            score += 5
        else:
            score += 2
        
        # Engagement from activities (if we had activity tracking)
        # For now, use status as engagement indicator
        status_engagement = {
            "new": 5,
            "contacted": 15,
            "qualified": 25,
            "proposal": 30,
            "negotiation": 35,
            "won": 40,
            "lost": 0
        }
        
        score += status_engagement.get(lead.status.lower(), 10)
        
        return min(score, 25)  # Cap at 25
    
    def _score_decision_maker(self, lead: Lead, contact: Contact) -> int:
        """Score based on decision-making power"""
        if not contact:
            return 10
        
        # Simple heuristic based on title/name
        name = contact.name.lower()
        title_indicators = {
            "ceo": 25,
            "cto": 20,
            "cfo": 20,
            "director": 18,
            "manager": 15,
            "vp": 22,
            "president": 25,
            "founder": 20,
            "owner": 18
        }
        
        for title, score in title_indicators.items():
            if title in name:
                return score
        
        return 10  # Default score
    
    def _score_urgency(self, lead: Lead, db: Session) -> int:
        """Score based on urgency indicators"""
        score = 10  # Base score
        
        # Status-based urgency
        urgent_statuses = ["qualified", "proposal", "negotiation"]
        if lead.status.lower() in urgent_statuses:
            score += 10
        
        # Lead age urgency (newer = more urgent)
        days_since_created = (datetime.now() - lead.created_at).days
        if days_since_created <= 3:
            score += 5
        elif days_since_created <= 7:
            score += 3
        
        return min(score, 15)
    
    def _score_timeline(self, lead: Lead) -> int:
        """Score based on timeline fit"""
        # For now, use source as timeline indicator
        timeline_scores = {
            "referral": 12,
            "website": 10,
            "social_media": 8,
            "email_campaign": 9,
            "cold_outreach": 6,
            "manual": 8
        }
        
        return timeline_scores.get(lead.source.lower(), 8)
    
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
        """Get score category label"""
        if score >= 80:
            return "Hot Lead"
        elif score >= 60:
            return "Warm Lead"
        elif score >= 40:
            return "Lukewarm Lead"
        else:
            return "Cold Lead"
    
    def _get_recommendations(self, score: int, factors: Dict[str, int]) -> List[str]:
        """Get actionable recommendations based on score"""
        recommendations = []
        
        if score >= 80:
            recommendations.extend([
                "Immediate follow-up required",
                "Prepare proposal/demo",
                "Engage decision maker directly",
                "Set up contract discussion"
            ])
        elif score >= 60:
            recommendations.extend([
                "Schedule discovery call",
                "Send relevant case studies",
                "Build relationship with key stakeholders",
                "Qualify budget and timeline"
            ])
        elif score >= 40:
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