from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from api.db import get_db
from api.dependencies import get_current_user
from api.models import User

router = APIRouter()

# Pydantic models
class CampaignBase(BaseModel):
    campaign_name: str
    campaign_description: Optional[str] = None
    campaign_type: str
    target_segment: Optional[str] = None
    is_active: bool = True
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(CampaignBase):
    pass

class Campaign(CampaignBase):
    id: int
    total_leads: int
    active_leads: int
    converted_leads: int
    conversion_rate: float
    created_at: str
    updated_at: str
    created_by: int

    class Config:
        from_attributes = True

class NurturingStepBase(BaseModel):
    step_name: str
    step_type: str
    step_order: int
    delay_days: int = 0
    delay_hours: int = 0
    step_data: dict = {}
    trigger_conditions: Optional[dict] = None
    is_active: bool = True

class NurturingStepCreate(NurturingStepBase):
    pass

class NurturingStep(NurturingStepBase):
    id: int
    campaign_id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

class CampaignEnrollmentBase(BaseModel):
    lead_id: int
    campaign_id: int
    enrollment_reason: Optional[str] = None

class CampaignEnrollment(CampaignEnrollmentBase):
    id: int
    current_step: int
    status: str
    enrolled_at: str
    last_activity: Optional[str] = None
    completed_at: Optional[str] = None

    class Config:
        from_attributes = True

# In-memory storage for demo (replace with database table later)
campaigns = []
steps = []
enrollments = []
campaign_id_counter = 1
step_id_counter = 1
enrollment_id_counter = 1

@router.get("/lead-nurturing-campaigns", response_model=List[Campaign])
async def get_campaigns(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all lead nurturing campaigns for the organization"""
    # Return demo data for now
    return [
        {
            "id": 1,
            "campaign_name": "Welcome Series",
            "campaign_description": "Automated welcome emails for new leads",
            "campaign_type": "drip",
            "target_segment": "new_leads",
            "is_active": True,
            "start_date": "2024-01-01",
            "end_date": None,
            "total_leads": 150,
            "active_leads": 120,
            "converted_leads": 45,
            "conversion_rate": 30.0,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-15T00:00:00Z",
            "created_by": current_user.id
        },
        {
            "id": 2,
            "campaign_name": "Re-engagement Campaign",
            "campaign_description": "Re-engage inactive leads with special offers",
            "campaign_type": "behavioral",
            "target_segment": "inactive_leads",
            "is_active": True,
            "start_date": "2024-02-01",
            "end_date": "2024-12-31",
            "total_leads": 200,
            "active_leads": 80,
            "converted_leads": 25,
            "conversion_rate": 12.5,
            "created_at": "2024-02-01T00:00:00Z",
            "updated_at": "2024-02-10T00:00:00Z",
            "created_by": current_user.id
        }
    ]

@router.post("/lead-nurturing-campaigns", response_model=Campaign)
async def create_campaign(
    campaign: CampaignCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new lead nurturing campaign"""
    global campaign_id_counter

    new_campaign = {
        "id": campaign_id_counter,
        "campaign_name": campaign.campaign_name,
        "campaign_description": campaign.campaign_description,
        "campaign_type": campaign.campaign_type,
        "target_segment": campaign.target_segment,
        "is_active": campaign.is_active,
        "start_date": campaign.start_date,
        "end_date": campaign.end_date,
        "total_leads": 0,
        "active_leads": 0,
        "converted_leads": 0,
        "conversion_rate": 0.0,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "created_by": current_user.id
    }

    campaigns.append(new_campaign)
    campaign_id_counter += 1

    return new_campaign

@router.get("/lead-nurturing-campaigns/{campaign_id}/steps", response_model=List[NurturingStep])
async def get_campaign_steps(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all steps for a specific campaign"""
    # Return demo data for now
    return [
        {
            "id": 1,
            "campaign_id": campaign_id,
            "step_name": "Welcome Email",
            "step_type": "email",
            "step_order": 1,
            "delay_days": 0,
            "delay_hours": 1,
            "step_data": {"subject": "Welcome to our platform!", "content": "Welcome email content..."},
            "trigger_conditions": None,
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        },
        {
            "id": 2,
            "campaign_id": campaign_id,
            "step_name": "Follow-up Call",
            "step_type": "call",
            "step_order": 2,
            "delay_days": 3,
            "delay_hours": 0,
            "step_data": {"script": "Follow-up call script..."},
            "trigger_conditions": None,
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    ]

@router.post("/lead-nurturing-campaigns/{campaign_id}/steps", response_model=NurturingStep)
async def create_campaign_step(
    campaign_id: int,
    step: NurturingStepCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new step for a campaign"""
    global step_id_counter

    new_step = {
        "id": step_id_counter,
        "campaign_id": campaign_id,
        "step_name": step.step_name,
        "step_type": step.step_type,
        "step_order": step.step_order,
        "delay_days": step.delay_days,
        "delay_hours": step.delay_hours,
        "step_data": step.step_data,
        "trigger_conditions": step.trigger_conditions,
        "is_active": step.is_active,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z"
    }

    steps.append(new_step)
    step_id_counter += 1

    return new_step

@router.get("/lead-nurturing-campaigns/{campaign_id}/enrollments", response_model=List[CampaignEnrollment])
async def get_campaign_enrollments(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all enrollments for a specific campaign"""
    # Return demo data for now
    return [
        {
            "id": 1,
            "lead_id": 101,
            "campaign_id": campaign_id,
            "enrollment_reason": "New lead signup",
            "current_step": 1,
            "status": "active",
            "enrolled_at": "2024-01-15T10:00:00Z",
            "last_activity": "2024-01-15T10:30:00Z",
            "completed_at": None
        },
        {
            "id": 2,
            "lead_id": 102,
            "campaign_id": campaign_id,
            "enrollment_reason": "Lead reactivation",
            "current_step": 2,
            "status": "active",
            "enrolled_at": "2024-01-14T14:00:00Z",
            "last_activity": "2024-01-16T09:00:00Z",
            "completed_at": None
        }
    ]