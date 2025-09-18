"""
Comprehensive Data Access Layer for AI Sales Assistant
Provides structured access to all CRM data with intelligent caching and filtering
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, and_, or_
from api.models import (
    User, Organization, Contact, Lead, Deal, Stage, Activity, 
    EmailTemplate, EmailCampaign, EmailLog, ChatMessage, ChatRoom,
    Subscription, SubscriptionPlan, SupportTicket, SupportComment,
    KnowledgeBaseArticle, SupportSLA, CustomerSatisfactionSurvey,
    SupportAnalytics, SupportQueue
)

class CRMDataAccess:
    """Comprehensive data access for AI sales assistant"""
    
    def __init__(self, db: Session, user_id: int, organization_id: int):
        self.db = db
        self.user_id = user_id
        self.organization_id = organization_id
    
    def get_user_context(self) -> Dict[str, Any]:
        """Get comprehensive user context"""
        user = self.db.query(User).filter(User.id == self.user_id).first()
        if not user:
            return {}
        
        # Get user's performance metrics
        deals_count = self.db.query(Deal).filter(Deal.owner_id == self.user_id).count()
        total_value = self.db.query(func.sum(Deal.value)).filter(Deal.owner_id == self.user_id).scalar() or 0
        closed_deals = self.db.query(Deal).filter(
            and_(Deal.owner_id == self.user_id, Deal.closed_at.isnot(None))
        ).count()
        
        # Recent activity
        recent_activities = self.db.query(Activity).filter(
            Activity.user_id == self.user_id
        ).order_by(desc(Activity.timestamp)).limit(5).all()
        
        return {
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "avatar_url": user.avatar_url
            },
            "performance": {
                "total_deals": deals_count,
                "total_value": total_value,
                "closed_deals": closed_deals,
                "win_rate": (closed_deals / deals_count * 100) if deals_count > 0 else 0
            },
            "recent_activities": [
                {
                    "type": activity.type,
                    "message": activity.message,
                    "timestamp": activity.timestamp.isoformat() if activity.timestamp else None
                }
                for activity in recent_activities
            ]
        }
    
    def get_organization_context(self) -> Dict[str, Any]:
        """Get organization-wide context"""
        org = self.db.query(Organization).filter(Organization.id == self.organization_id).first()
        if not org:
            return {}
        
        # Organization metrics
        total_users = self.db.query(User).filter(User.organization_id == self.organization_id).count()
        total_contacts = self.db.query(Contact).filter(Contact.organization_id == self.organization_id).count()
        total_leads = self.db.query(Lead).filter(Lead.organization_id == self.organization_id).count()
        total_deals = self.db.query(Deal).filter(Deal.organization_id == self.organization_id).count()
        
        # Pipeline value
        pipeline_value = self.db.query(func.sum(Deal.value)).filter(
            and_(Deal.organization_id == self.organization_id, Deal.closed_at.is_(None))
        ).scalar() or 0
        
        # Subscription info
        subscription = self.db.query(Subscription).filter(
            Subscription.organization_id == self.organization_id
        ).first()
        
        return {
            "organization": {
                "id": org.id,
                "name": org.name,
                "domain": org.domain,
                "settings": org.settings
            },
            "metrics": {
                "total_users": total_users,
                "total_contacts": total_contacts,
                "total_leads": total_leads,
                "total_deals": total_deals,
                "pipeline_value": pipeline_value
            },
            "subscription": {
                "plan": subscription.plan if subscription else "free",
                "status": subscription.status if subscription else "active",
                "user_limit": subscription.user_limit if subscription else 5
            } if subscription else None
        }
    
    def get_lead_context(self, lead_id: int) -> Dict[str, Any]:
        """Get comprehensive lead context"""
        lead = self.db.query(Lead).options(
            joinedload(Lead.contact),
            joinedload(Lead.owner)
        ).filter(Lead.id == lead_id).first()
        
        if not lead:
            return {}
        
        # Get related deals
        related_deals = self.db.query(Deal).filter(
            and_(Deal.contact_id == lead.contact_id, Deal.organization_id == self.organization_id)
        ).all()
        
        # Get lead activities
        activities = self.db.query(Activity).filter(
            Activity.deal_id.in_([deal.id for deal in related_deals])
        ).order_by(desc(Activity.timestamp)).limit(10).all()
        
        return {
            "lead": {
                "id": lead.id,
                "title": lead.title,
                "status": lead.status,
                "source": lead.source,
                "score": lead.score,
                "score_confidence": lead.score_confidence,
                "score_factors": lead.score_factors,
                "created_at": lead.created_at.isoformat() if lead.created_at else None
            },
            "contact": {
                "id": lead.contact.id if lead.contact else None,
                "name": lead.contact.name if lead.contact else None,
                "email": lead.contact.email if lead.contact else None,
                "phone": lead.contact.phone if lead.contact else None,
                "company": lead.contact.company if lead.contact else None
            } if lead.contact else None,
            "owner": {
                "id": lead.owner.id if lead.owner else None,
                "name": lead.owner.name if lead.owner else None,
                "email": lead.owner.email if lead.owner else None
            } if lead.owner else None,
            "related_deals": [
                {
                    "id": deal.id,
                    "title": deal.title,
                    "value": deal.value,
                    "stage": deal.stage.name if deal.stage else None,
                    "status": "closed" if deal.closed_at else "open"
                }
                for deal in related_deals
            ],
            "activities": [
                {
                    "type": activity.type,
                    "message": activity.message,
                    "timestamp": activity.timestamp.isoformat() if activity.timestamp else None
                }
                for activity in activities
            ]
        }
    
    def get_deal_context(self, deal_id: int) -> Dict[str, Any]:
        """Get comprehensive deal context"""
        deal = self.db.query(Deal).options(
            joinedload(Deal.contact),
            joinedload(Deal.owner),
            joinedload(Deal.stage),
            joinedload(Deal.activities),
            joinedload(Deal.attachments)
        ).filter(Deal.id == deal_id).first()
        
        if not deal:
            return {}
        
        # Get deal timeline
        activities = sorted(deal.activities, key=lambda x: x.timestamp or datetime.min)
        
        # Get similar deals for comparison
        similar_deals = self.db.query(Deal).filter(
            and_(
                Deal.organization_id == self.organization_id,
                Deal.stage_id == deal.stage_id,
                Deal.id != deal_id
            )
        ).limit(5).all()
        
        return {
            "deal": {
                "id": deal.id,
                "title": deal.title,
                "value": deal.value,
                "description": deal.description,
                "created_at": deal.created_at.isoformat() if deal.created_at else None,
                "closed_at": deal.closed_at.isoformat() if deal.closed_at else None,
                "reminder_date": deal.reminder_date.isoformat() if deal.reminder_date else None
            },
            "stage": {
                "id": deal.stage.id if deal.stage else None,
                "name": deal.stage.name if deal.stage else None,
                "order": deal.stage.order if deal.stage else None
            } if deal.stage else None,
            "contact": {
                "id": deal.contact.id if deal.contact else None,
                "name": deal.contact.name if deal.contact else None,
                "email": deal.contact.email if deal.contact else None,
                "phone": deal.contact.phone if deal.contact else None,
                "company": deal.contact.company if deal.contact else None
            } if deal.contact else None,
            "owner": {
                "id": deal.owner.id if deal.owner else None,
                "name": deal.owner.name if deal.owner else None,
                "email": deal.owner.email if deal.owner else None
            } if deal.owner else None,
            "timeline": [
                {
                    "type": activity.type,
                    "message": activity.message,
                    "timestamp": activity.timestamp.isoformat() if activity.timestamp else None
                }
                for activity in activities
            ],
            "attachments": [
                {
                    "id": att.id,
                    "filename": att.filename,
                    "url": att.url,
                    "uploaded_at": att.uploaded_at.isoformat() if att.uploaded_at else None
                }
                for att in deal.attachments
            ],
            "similar_deals": [
                {
                    "id": similar.id,
                    "title": similar.title,
                    "value": similar.value,
                    "status": "closed" if similar.closed_at else "open"
                }
                for similar in similar_deals
            ]
        }
    
    def get_contact_context(self, contact_id: int) -> Dict[str, Any]:
        """Get comprehensive contact context"""
        contact = self.db.query(Contact).options(
            joinedload(Contact.leads),
            joinedload(Contact.deals)
        ).filter(Contact.id == contact_id).first()
        
        if not contact:
            return {}
        
        # Get contact's interaction history
        all_deals = contact.deals
        all_leads = contact.leads
        
        # Calculate contact value
        total_deal_value = sum(deal.value or 0 for deal in all_deals)
        closed_deal_value = sum(deal.value or 0 for deal in all_deals if deal.closed_at)
        
        # Get recent activities across all deals
        deal_ids = [deal.id for deal in all_deals]
        recent_activities = []
        if deal_ids:
            recent_activities = self.db.query(Activity).filter(
                Activity.deal_id.in_(deal_ids)
            ).order_by(desc(Activity.timestamp)).limit(10).all()
        
        return {
            "contact": {
                "id": contact.id,
                "name": contact.name,
                "email": contact.email,
                "phone": contact.phone,
                "company": contact.company,
                "created_at": contact.created_at.isoformat() if contact.created_at else None
            },
            "owner": {
                "id": contact.owner.id if contact.owner else None,
                "name": contact.owner.name if contact.owner else None,
                "email": contact.owner.email if contact.owner else None
            } if contact.owner else None,
            "interaction_summary": {
                "total_leads": len(all_leads),
                "total_deals": len(all_deals),
                "total_deal_value": total_deal_value,
                "closed_deal_value": closed_deal_value,
                "active_deals": len([deal for deal in all_deals if not deal.closed_at])
            },
            "leads": [
                {
                    "id": lead.id,
                    "title": lead.title,
                    "status": lead.status,
                    "source": lead.source,
                    "score": lead.score,
                    "created_at": lead.created_at.isoformat() if lead.created_at else None
                }
                for lead in all_leads
            ],
            "deals": [
                {
                    "id": deal.id,
                    "title": deal.title,
                    "value": deal.value,
                    "stage": deal.stage.name if deal.stage else None,
                    "status": "closed" if deal.closed_at else "open",
                    "created_at": deal.created_at.isoformat() if deal.created_at else None
                }
                for deal in all_deals
            ],
            "recent_activities": [
                {
                    "type": activity.type,
                    "message": activity.message,
                    "timestamp": activity.timestamp.isoformat() if activity.timestamp else None
                }
                for activity in recent_activities
            ]
        }
    
    def get_pipeline_summary(self) -> Dict[str, Any]:
        """Get pipeline summary for the organization"""
        # Get all stages with deal counts and values
        stages = self.db.query(Stage).order_by(Stage.order).all()
        stage_summary = []
        
        for stage in stages:
            deals = self.db.query(Deal).filter(
                and_(Deal.stage_id == stage.id, Deal.organization_id == self.organization_id)
            ).all()
            
            total_value = sum(deal.value or 0 for deal in deals)
            stage_summary.append({
                "stage": {
                    "id": stage.id,
                    "name": stage.name,
                    "order": stage.order
                },
                "deal_count": len(deals),
                "total_value": total_value,
                "avg_deal_size": total_value / len(deals) if deals else 0
            })
        
        # Get recent activity
        recent_activities = self.db.query(Activity).join(Deal).filter(
            Deal.organization_id == self.organization_id
        ).order_by(desc(Activity.timestamp)).limit(20).all()
        
        return {
            "stages": stage_summary,
            "recent_activities": [
                {
                    "type": activity.type,
                    "message": activity.message,
                    "timestamp": activity.timestamp.isoformat() if activity.timestamp else None,
                    "deal_id": activity.deal_id
                }
                for activity in recent_activities
            ]
        }
    
    def get_email_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get available email templates"""
        query = self.db.query(EmailTemplate).filter(EmailTemplate.is_active == True)
        
        if category:
            query = query.filter(EmailTemplate.category == category)
        
        templates = query.all()
        
        return [
            {
                "id": template.id,
                "name": template.name,
                "category": template.category,
                "subject": template.subject,
                "body": template.body,
                "created_at": template.created_at.isoformat() if template.created_at else None
            }
            for template in templates
        ]
    
    def get_recent_communications(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get recent email communications"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        email_logs = self.db.query(EmailLog).filter(
            EmailLog.sent_at >= cutoff_date
        ).order_by(desc(EmailLog.sent_at)).limit(50).all()
        
        return [
            {
                "id": log.id,
                "recipient_email": log.recipient_email,
                "recipient_name": log.recipient_name,
                "subject": log.subject,
                "status": log.status,
                "sent_at": log.sent_at.isoformat() if log.sent_at else None,
                "opened_at": log.opened_at.isoformat() if log.opened_at else None,
                "clicked_at": log.clicked_at.isoformat() if log.clicked_at else None
            }
            for log in email_logs
        ]
    
    def search_entities(self, query: str, entity_types: List[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Search across multiple entity types"""
        if entity_types is None:
            entity_types = ["contacts", "leads", "deals"]
        
        results = {}
        
        if "contacts" in entity_types:
            contacts = self.db.query(Contact).filter(
                and_(
                    Contact.organization_id == self.organization_id,
                    or_(
                        Contact.name.ilike(f"%{query}%"),
                        Contact.email.ilike(f"%{query}%"),
                        Contact.company.ilike(f"%{query}%")
                    )
                )
            ).limit(10).all()
            
            results["contacts"] = [
                {
                    "id": contact.id,
                    "name": contact.name,
                    "email": contact.email,
                    "company": contact.company,
                    "type": "contact"
                }
                for contact in contacts
            ]
        
        if "leads" in entity_types:
            leads = self.db.query(Lead).filter(
                and_(
                    Lead.organization_id == self.organization_id,
                    Lead.title.ilike(f"%{query}%")
                )
            ).limit(10).all()
            
            results["leads"] = [
                {
                    "id": lead.id,
                    "title": lead.title,
                    "status": lead.status,
                    "score": lead.score,
                    "type": "lead"
                }
                for lead in leads
            ]
        
        if "deals" in entity_types:
            deals = self.db.query(Deal).filter(
                and_(
                    Deal.organization_id == self.organization_id,
                    Deal.title.ilike(f"%{query}%")
                )
            ).limit(10).all()
            
            results["deals"] = [
                {
                    "id": deal.id,
                    "title": deal.title,
                    "value": deal.value,
                    "stage": deal.stage.name if deal.stage else None,
                    "type": "deal"
                }
                for deal in deals
            ]
        
        return results
    
    def get_support_context(self) -> Dict[str, Any]:
        """Get support and customer service context"""
        # Support tickets
        total_tickets = self.db.query(SupportTicket).filter(
            SupportTicket.organization_id == self.organization_id
        ).count()
        
        open_tickets = self.db.query(SupportTicket).filter(
            and_(
                SupportTicket.organization_id == self.organization_id,
                SupportTicket.status.in_(['open', 'in_progress', 'pending_customer'])
            )
        ).count()
        
        # Knowledge base articles
        total_articles = self.db.query(KnowledgeBaseArticle).filter(
            KnowledgeBaseArticle.organization_id == self.organization_id
        ).count()
        
        published_articles = self.db.query(KnowledgeBaseArticle).filter(
            and_(
                KnowledgeBaseArticle.organization_id == self.organization_id,
                KnowledgeBaseArticle.status == 'published'
            )
        ).count()
        
        # Recent tickets
        recent_tickets = self.db.query(SupportTicket).filter(
            SupportTicket.organization_id == self.organization_id
        ).order_by(desc(SupportTicket.created_at)).limit(5).all()
        
        return {
            "support_metrics": {
                "total_tickets": total_tickets,
                "open_tickets": open_tickets,
                "resolved_tickets": total_tickets - open_tickets,
                "total_articles": total_articles,
                "published_articles": published_articles
            },
            "recent_tickets": [
                {
                    "id": ticket.id,
                    "ticket_number": ticket.ticket_number,
                    "title": ticket.title,
                    "status": ticket.status,
                    "priority": ticket.priority,
                    "customer_name": ticket.customer_name,
                    "created_at": ticket.created_at.isoformat() if ticket.created_at else None
                }
                for ticket in recent_tickets
            ]
        }
    
    def get_knowledge_base_context(self, query: str = None) -> Dict[str, Any]:
        """Get knowledge base context for AI responses"""
        base_query = self.db.query(KnowledgeBaseArticle).filter(
            and_(
                KnowledgeBaseArticle.organization_id == self.organization_id,
                KnowledgeBaseArticle.status == 'published'
            )
        )
        
        if query:
            articles = base_query.filter(
                or_(
                    KnowledgeBaseArticle.title.ilike(f"%{query}%"),
                    KnowledgeBaseArticle.content.ilike(f"%{query}%"),
                    KnowledgeBaseArticle.summary.ilike(f"%{query}%")
                )
            ).limit(10).all()
        else:
            articles = base_query.order_by(desc(KnowledgeBaseArticle.view_count)).limit(10).all()
        
        return {
            "articles": [
                {
                    "id": article.id,
                    "title": article.title,
                    "summary": article.summary,
                    "category": article.category,
                    "subcategory": article.subcategory,
                    "view_count": article.view_count,
                    "helpful_count": article.helpful_count,
                    "created_at": article.created_at.isoformat() if article.created_at else None
                }
                for article in articles
            ]
        }
