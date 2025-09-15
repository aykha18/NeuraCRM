from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from datetime import datetime, timedelta
from typing import List, Dict, Any
from api.dependencies import get_db, get_current_user
from api.models import Deal, Lead, Contact, User, Activity, Stage
from api.schemas.dashboard import (
    DashboardMetrics,
    PerformanceData,
    LeadQualityData,
    ActivityFeedItem,
    DashboardData
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/metrics", response_model=DashboardMetrics)
def get_dashboard_metrics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get dashboard metrics including active leads, closed deals, revenue, and AI score"""
    try:
        # Active leads count (case-insensitive and includes more statuses)
        try:
            active_leads = db.query(Lead).filter(
                Lead.status.in_(['new', 'New', 'contacted', 'Contacted', 'qualified', 'Qualified', 'Proposal Sent', 'Negotiation']),
                Lead.organization_id == current_user.organization_id
            ).count()
        except Exception as e:
            logger.warning(f"active_leads query failed: {e}")
            active_leads = 0
        
        # Closed deals count (deals with closed_at date)
        try:
            closed_deals = db.query(Deal).filter(
                Deal.closed_at.isnot(None),
                Deal.organization_id == current_user.organization_id
            ).count()
        except Exception as e:
            logger.warning(f"closed_deals query failed: {e}")
            closed_deals = 0
        
        # Total revenue from closed deals
        try:
            total_revenue = db.query(func.sum(Deal.value)).filter(
                Deal.closed_at.isnot(None),
                Deal.organization_id == current_user.organization_id
            ).scalar() or 0
        except Exception as e:
            logger.warning(f"total_revenue query failed: {e}")
            total_revenue = 0
        
        # Calculate AI score based on various factors
        try:
            total_deals = db.query(Deal).filter(Deal.organization_id == current_user.organization_id).count()
        except Exception as e:
            logger.warning(f"total_deals query failed: {e}")
            total_deals = 0
        try:
            deals_with_activities = db.query(Deal).join(Activity, isouter=True).filter(
                Deal.organization_id == current_user.organization_id,
                Activity.id.isnot(None)
            ).distinct().count()
        except Exception as e:
            logger.warning(f"deals_with_activities query failed: {e}")
            deals_with_activities = 0
        try:
            deals_with_reminders = db.query(Deal).filter(
                Deal.reminder_date.isnot(None),
                Deal.organization_id == current_user.organization_id
            ).count()
        except Exception as e:
            logger.warning(f"deals_with_reminders query failed: {e}")
            deals_with_reminders = 0
        
        ai_score = 0
        if total_deals > 0:
            activity_score = (deals_with_activities / total_deals) * 40
            reminder_score = (deals_with_reminders / total_deals) * 30
            revenue_score = min((total_revenue / 1000000) * 30, 30)  # Cap at 30 points
            ai_score = min(int(activity_score + reminder_score + revenue_score), 100)
        
        # Calculate quality score for leads
        try:
            qualified_leads = db.query(Lead).filter(
                Lead.status == 'qualified',
                Lead.organization_id == current_user.organization_id
            ).count()
        except Exception as e:
            logger.warning(f"qualified_leads query failed: {e}")
            qualified_leads = 0
        lead_quality_score = (qualified_leads / max(active_leads, 1)) * 10
        
        # Calculate conversion rate
        conversion_rate = (closed_deals / max(active_leads + closed_deals, 1)) * 100
        
        # Calculate revenue target achievement
        revenue_target = 1000000  # $1M target
        target_achievement = (total_revenue / max(revenue_target, 1)) * 100
        
        return DashboardMetrics(
            active_leads=active_leads,
            closed_deals=closed_deals,
            total_revenue=int(total_revenue),
            ai_score=int(ai_score),
            lead_quality_score=round(lead_quality_score, 1),
            conversion_rate=round(conversion_rate, 1),
            target_achievement=round(target_achievement, 1)
        )
    except Exception as e:
        logger.error(f"Error fetching dashboard metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard metrics: {str(e)}")

@router.get("/performance", response_model=List[PerformanceData])
def get_performance_data(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get performance data for the last 6 months"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)
        
        performance_data = []
        current_date = start_date
        
        for i in range(6):
            month_start = current_date.replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            try:
                leads_count = db.query(Lead).filter(
                    and_(
                        Lead.created_at >= month_start,
                        Lead.created_at <= month_end,
                        Lead.organization_id == current_user.organization_id
                    )
                ).count()
            except Exception as e:
                logger.warning(f"leads_count month {i} failed: {e}")
                leads_count = 0
            try:
                deals_count = db.query(Deal).filter(
                    and_(
                        Deal.created_at >= month_start,
                        Deal.created_at <= month_end,
                        Deal.organization_id == current_user.organization_id
                    )
                ).count()
            except Exception as e:
                logger.warning(f"deals_count month {i} failed: {e}")
                deals_count = 0
            try:
                revenue = db.query(func.sum(Deal.value)).filter(
                    and_(
                        Deal.closed_at.isnot(None),
                        Deal.closed_at >= month_start,
                        Deal.closed_at <= month_end,
                        Deal.organization_id == current_user.organization_id
                    )
                ).scalar() or 0
            except Exception as e:
                logger.warning(f"revenue month {i} failed: {e}")
                revenue = 0
            performance_data.append(PerformanceData(
                month=month_start.strftime("%b"),
                leads=leads_count,
                deals=deals_count,
                revenue=int(revenue)
            ))
            current_date = (current_date + timedelta(days=32)).replace(day=1)
        
        return performance_data
    except Exception as e:
        logger.error(f"Error fetching performance data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching performance data: {str(e)}")

@router.get("/lead-quality", response_model=List[LeadQualityData])
def get_lead_quality_data(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get lead quality distribution data"""
    try:
        try:
            qualified_count = db.query(Lead).filter(
                Lead.status.in_(['qualified', 'Qualified', 'Proposal Sent']),
                Lead.organization_id == current_user.organization_id
            ).count()
        except Exception as e:
            logger.warning(f"qualified_count failed: {e}")
            qualified_count = 0
        try:
            nurturing_count = db.query(Lead).filter(
                Lead.status.in_(['contacted', 'Contacted', 'Negotiation']),
                Lead.organization_id == current_user.organization_id
            ).count()
        except Exception as e:
            logger.warning(f"nurturing_count failed: {e}")
            nurturing_count = 0
        try:
            cold_count = db.query(Lead).filter(
                Lead.status.in_(['new', 'New']),
                Lead.organization_id == current_user.organization_id
            ).count()
        except Exception as e:
            logger.warning(f"cold_count failed: {e}")
            cold_count = 0
        try:
            hot_count = db.query(Lead).filter(
                Lead.status.in_(['hot', 'Hot', 'Won']),
                Lead.organization_id == current_user.organization_id
            ).count()
        except Exception as e:
            logger.warning(f"hot_count failed: {e}")
            hot_count = 0
        
        total_leads = qualified_count + nurturing_count + cold_count + hot_count
        if total_leads == 0:
            return [
                LeadQualityData(name="Qualified", value=0, color="#22c55e"),
                LeadQualityData(name="Nurturing", value=0, color="#fbbf24"),
                LeadQualityData(name="Cold", value=0, color="#64748b"),
                LeadQualityData(name="Hot", value=0, color="#a21caf")
            ]
        
        return [
            LeadQualityData(name="Qualified", value=int((qualified_count / total_leads) * 100), color="#22c55e"),
            LeadQualityData(name="Nurturing", value=int((nurturing_count / total_leads) * 100), color="#fbbf24"),
            LeadQualityData(name="Cold", value=int((cold_count / total_leads) * 100), color="#64748b"),
            LeadQualityData(name="Hot", value=int((hot_count / total_leads) * 100), color="#a21caf")
        ]
    except Exception as e:
        logger.error(f"Error fetching lead quality data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching lead quality data: {str(e)}")

@router.get("/activity-feed", response_model=List[ActivityFeedItem])
def get_activity_feed(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get recent activity feed for dashboard"""
    try:
        activities = db.query(Activity).join(Deal, isouter=True).filter(
            Deal.organization_id == current_user.organization_id
        ).order_by(
            Activity.timestamp.desc().nullslast()
        ).limit(10).all()
        
        activity_feed = []
        for activity in activities:
            icon_map = {
                'deal_moved': 'CheckCircle',
                'deal_created': 'Plus',
                'deal_closed': 'CheckCircle',
                'lead_created': 'UserPlus',
                'contact_added': 'UserPlus',
                'reminder_set': 'Clock',
                'note_added': 'MessageCircle',
                'ai_insight': 'Zap'
            }
            color_map = {
                'deal_moved': 'yellow',
                'deal_created': 'green',
                'deal_closed': 'green',
                'lead_created': 'blue',
                'contact_added': 'blue',
                'reminder_set': 'orange',
                'note_added': 'blue',
                'ai_insight': 'pink'
            }
            icon = icon_map.get(getattr(activity, 'type', '') or '', 'MessageCircle')
            color = color_map.get(getattr(activity, 'type', '') or '', 'blue')
            ts = getattr(activity, 'timestamp', None)
            if ts is None:
                time_ago = "just now"
            else:
                try:
                    time_diff = datetime.now() - ts
                    if time_diff.days > 0:
                        time_ago = f"{time_diff.days} day{'s' if time_diff.days > 1 else ''} ago"
                    elif time_diff.seconds > 3600:
                        hours = time_diff.seconds // 3600
                        time_ago = f"{hours} hour{'s' if hours > 1 else ''} ago"
                    else:
                        minutes = max(1, time_diff.seconds // 60)
                        time_ago = f"{minutes} min ago"
                except Exception:
                    time_ago = "just now"
            title = getattr(activity, 'message', None) or 'Activity'
            activity_feed.append(ActivityFeedItem(
                icon=icon,
                color=f"bg-{color}-100",
                title=title,
                time=time_ago
            ))
        return activity_feed
    except Exception as e:
        logger.error(f"Error fetching activity feed: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching activity feed: {str(e)}")

@router.get("/", response_model=DashboardData)
def get_dashboard_data(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all dashboard data in one endpoint"""
    try:
        metrics = get_dashboard_metrics(current_user, db)
        performance = get_performance_data(current_user, db)
        lead_quality = get_lead_quality_data(current_user, db)
        activity_feed = get_activity_feed(current_user, db)
        return DashboardData(
            metrics=metrics,
            performance=performance,
            lead_quality=lead_quality,
            activity_feed=activity_feed
        )
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard data: {str(e)}") 