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
class LeadAssignmentRuleBase(BaseModel):
    rule_name: str
    rule_description: Optional[str] = None
    criteria: dict
    assignment_type: str  # 'user', 'round_robin', 'team'
    assigned_user_id: Optional[int] = None
    assigned_team_id: Optional[int] = None
    priority: int = 1
    is_active: bool = True

class LeadAssignmentRuleCreate(LeadAssignmentRuleBase):
    pass

class LeadAssignmentRuleUpdate(LeadAssignmentRuleBase):
    pass

class LeadAssignmentRule(LeadAssignmentRuleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: int

    class Config:
        from_attributes = True

# In-memory storage for demo (replace with database table later)
assignment_rules = []
rule_id_counter = 1

@router.get("/lead-assignment-rules", response_model=List[LeadAssignmentRule])
async def get_lead_assignment_rules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all lead assignment rules for the organization"""
    # Return demo data for now
    return [
        {
            "id": 1,
            "rule_name": "High Priority Enterprise Leads",
            "rule_description": "Automatically assign high-priority enterprise leads to senior sales reps",
            "criteria": {
                "source": "website",
                "priority": "high",
                "industry": "Technology"
            },
            "assignment_type": "user",
            "assigned_user_id": current_user.id,
            "assigned_team_id": None,
            "priority": 1,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_by": current_user.id
        },
        {
            "id": 2,
            "rule_name": "Round Robin General Leads",
            "rule_description": "Distribute general leads evenly among sales team",
            "criteria": {
                "source": "referral",
                "priority": "medium"
            },
            "assignment_type": "round_robin",
            "assigned_user_id": None,
            "assigned_team_id": None,
            "priority": 2,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_by": current_user.id
        }
    ]

@router.post("/lead-assignment-rules", response_model=LeadAssignmentRule)
async def create_lead_assignment_rule(
    rule: LeadAssignmentRuleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new lead assignment rule"""
    global rule_id_counter

    new_rule = {
        "id": rule_id_counter,
        "rule_name": rule.rule_name,
        "rule_description": rule.rule_description,
        "criteria": rule.criteria,
        "assignment_type": rule.assignment_type,
        "assigned_user_id": rule.assigned_user_id,
        "assigned_team_id": rule.assigned_team_id,
        "priority": rule.priority,
        "is_active": rule.is_active,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "created_by": current_user.id
    }

    assignment_rules.append(new_rule)
    rule_id_counter += 1

    return new_rule

@router.put("/lead-assignment-rules/{rule_id}", response_model=LeadAssignmentRule)
async def update_lead_assignment_rule(
    rule_id: int,
    rule_update: LeadAssignmentRuleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a lead assignment rule"""
    # Find the rule
    rule_index = None
    for i, rule in enumerate(assignment_rules):
        if rule["id"] == rule_id:
            rule_index = i
            break

    if rule_index is None:
        raise HTTPException(status_code=404, detail="Rule not found")

    # Update the rule
    updated_rule = {
        **assignment_rules[rule_index],
        "rule_name": rule_update.rule_name,
        "rule_description": rule_update.rule_description,
        "criteria": rule_update.criteria,
        "assignment_type": rule_update.assignment_type,
        "assigned_user_id": rule_update.assigned_user_id,
        "assigned_team_id": rule_update.assigned_team_id,
        "priority": rule_update.priority,
        "is_active": rule_update.is_active,
        "updated_at": datetime.utcnow()
    }

    assignment_rules[rule_index] = updated_rule
    return updated_rule

@router.delete("/lead-assignment-rules/{rule_id}")
async def delete_lead_assignment_rule(
    rule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a lead assignment rule"""
    global assignment_rules

    # Find and remove the rule
    rule_index = None
    for i, rule in enumerate(assignment_rules):
        if rule["id"] == rule_id:
            rule_index = i
            break

    if rule_index is None:
        raise HTTPException(status_code=404, detail="Rule not found")

    assignment_rules.pop(rule_index)
    return {"message": "Rule deleted successfully"}