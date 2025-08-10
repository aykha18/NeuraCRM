from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class DashboardMetrics(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    active_leads: int
    closed_deals: int
    total_revenue: float
    ai_score: int
    lead_quality_score: float
    conversion_rate: float
    target_achievement: float

class PerformanceData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    month: str
    leads: int
    deals: int
    revenue: int

class LeadQualityData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    name: str
    value: int
    color: str

class ActivityFeedItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    icon: str
    color: str
    title: str
    time: str

class DashboardData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    metrics: DashboardMetrics
    performance: List[PerformanceData]
    lead_quality: List[LeadQualityData]
    activity_feed: List[ActivityFeedItem] 