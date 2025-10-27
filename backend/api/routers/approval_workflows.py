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
class ApprovalWorkflowBase(BaseModel):
    workflow_name: str
    workflow_description: Optional[str] = None
    entity_type: str
    trigger_conditions: dict
    approval_steps: List[dict]
    is_active: bool = True
    auto_approve_conditions: Optional[dict] = None

class ApprovalWorkflowCreate(ApprovalWorkflowBase):
    pass

class ApprovalWorkflowUpdate(ApprovalWorkflowBase):
    pass

class ApprovalWorkflow(ApprovalWorkflowBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int

    class Config:
        from_attributes = True

class ApprovalRequestBase(BaseModel):
    entity_type: str
    entity_id: int
    request_reason: str
    priority: str = "medium"

class ApprovalRequestCreate(ApprovalRequestBase):
    pass

class ApprovalRequest(ApprovalRequestBase):
    id: int
    status: str
    current_step: int
    total_steps: int
    requested_at: datetime
    requester_id: int

    class Config:
        from_attributes = True

# In-memory storage for demo (replace with database table later)
workflows = []
requests = []
workflow_id_counter = 1
request_id_counter = 1

@router.get("/approval-workflows", response_model=List[ApprovalWorkflow])
async def get_approval_workflows(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all approval workflows for the organization"""
    # Return demo data for now
    return [
        {
            "id": 1,
            "workflow_name": "Deal Approval Workflow",
            "workflow_description": "Multi-step approval process for deals over $50,000",
            "entity_type": "deal",
            "trigger_conditions": {"amount": {"gt": 50000}},
            "approval_steps": [
                {"step_number": 1, "approver_role": "sales_manager", "required": True},
                {"step_number": 2, "approver_role": "finance_manager", "required": True}
            ],
            "is_active": True,
            "auto_approve_conditions": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_by": 1,
            "updated_by": 1
        },
        {
            "id": 2,
            "workflow_name": "Expense Approval Workflow",
            "workflow_description": "Approval process for business expenses",
            "entity_type": "expense",
            "trigger_conditions": {"amount": {"gt": 1000}},
            "approval_steps": [
                {"step_number": 1, "approver_role": "department_head", "required": True},
                {"step_number": 2, "approver_role": "finance_manager", "required": False}
            ],
            "is_active": True,
            "auto_approve_conditions": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_by": 1,
            "updated_by": 1
        }
    ]

@router.post("/approval-workflows", response_model=ApprovalWorkflow)
async def create_approval_workflow(
    workflow: ApprovalWorkflowCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new approval workflow"""
    global workflow_id_counter

    new_workflow = {
        "id": workflow_id_counter,
        "workflow_name": workflow.workflow_name,
        "workflow_description": workflow.workflow_description,
        "entity_type": workflow.entity_type,
        "trigger_conditions": workflow.trigger_conditions,
        "approval_steps": workflow.approval_steps,
        "is_active": workflow.is_active,
        "auto_approve_conditions": workflow.auto_approve_conditions,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "created_by": 1,
        "updated_by": 1
    }

    workflows.append(new_workflow)
    workflow_id_counter += 1

    return new_workflow

@router.post("/approval-workflows/create-samples")
async def create_sample_workflows(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create sample approval workflows"""
    global workflow_id_counter

    samples = [
        {
            "id": workflow_id_counter,
            "workflow_name": "High-Value Deal Approval",
            "workflow_description": "Approval workflow for deals over $100,000",
            "entity_type": "deal",
            "trigger_conditions": {"amount": {"gt": 100000}},
            "approval_steps": [
                {"step_number": 1, "approver_role": "sales_director", "required": True},
                {"step_number": 2, "approver_role": "ceo", "required": True}
            ],
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_by": 1,
            "updated_by": 1
        },
        {
            "id": workflow_id_counter + 1,
            "workflow_name": "Task Approval Workflow",
            "workflow_description": "Approval process for critical tasks",
            "entity_type": "task",
            "trigger_conditions": {"priority": "high"},
            "approval_steps": [
                {"step_number": 1, "approver_role": "project_manager", "required": True}
            ],
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_by": 1,
            "updated_by": 1
        }
    ]

    workflows.extend(samples)
    workflow_id_counter += len(samples)

    return {"workflows": samples, "already_exists": False}

@router.get("/approval-requests", response_model=List[ApprovalRequest])
async def get_approval_requests(
    status: Optional[str] = None,
    entity_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all approval requests"""
    # Return demo data for now
    return [
        {
            "id": 1,
            "entity_type": "deal",
            "entity_id": 1,
            "request_reason": "Large deal approval required",
            "priority": "high",
            "status": "pending",
            "current_step": 1,
            "total_steps": 2,
            "requested_at": datetime.utcnow(),
            "requester_id": current_user.id
        },
        {
            "id": 2,
            "entity_type": "expense",
            "entity_id": 1,
            "request_reason": "Business expense reimbursement",
            "priority": "medium",
            "status": "approved",
            "current_step": 2,
            "total_steps": 2,
            "requested_at": datetime.utcnow(),
            "requester_id": current_user.id
        }
    ]

@router.get("/approval-requests/my-pending", response_model=List[ApprovalRequest])
async def get_my_pending_approvals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get pending approval requests for current user"""
    # Return demo data for now
    return [
        {
            "id": 1,
            "entity_type": "deal",
            "entity_id": 1,
            "request_reason": "Large deal approval required",
            "priority": "high",
            "status": "pending",
            "current_step": 1,
            "total_steps": 2,
            "requested_at": datetime.utcnow(),
            "requester_id": current_user.id
        }
    ]

@router.get("/approval-requests/{request_id}/steps")
async def get_approval_request_steps(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get approval steps for a specific request"""
    # Return demo data for now
    return [
        {
            "id": 1,
            "step_number": 1,
            "approver_id": current_user.id,
            "approver_name": current_user.name,
            "status": "pending",
            "comments": None,
            "approved_at": None,
            "due_date": None
        },
        {
            "id": 2,
            "step_number": 2,
            "approver_id": current_user.id + 1,
            "approver_name": "Finance Manager",
            "status": "pending",
            "comments": None,
            "approved_at": None,
            "due_date": None
        }
    ]

@router.post("/approval-requests/{request_id}/action")
async def handle_approval_action(
    request_id: int,
    action: str,  # approve, reject, delegate
    comments: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Handle approval action (approve/reject/delegate)"""
    # Demo implementation - just return success
    return {
        "message": f"Request {action}d successfully",
        "request_id": request_id,
        "action": action,
        "approved_by": current_user.id,
        "comments": comments
    }