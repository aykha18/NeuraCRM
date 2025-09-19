from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import logging

from ..db import get_db
from ..dependencies import get_current_user
from ..models import (
    User, Organization, PBXProvider, PBXExtension, Call, CallActivity, 
    CallQueue, CallQueueMember, CallCampaign, CampaignCall, CallAnalytics,
    Contact, Lead, Deal
)
from ..schemas.telephony import (
    PBXProviderCreate, PBXProviderUpdate, PBXProviderResponse,
    PBXExtensionCreate, PBXExtensionUpdate, PBXExtensionResponse,
    CallCreate, CallUpdate, CallResponse,
    CallQueueCreate, CallQueueUpdate, CallQueueResponse,
    CallQueueMemberCreate, CallQueueMemberUpdate, CallQueueMemberResponse,
    CallCampaignCreate, CallCampaignUpdate, CallCampaignResponse,
    CallAnalyticsResponse, CallCenterDashboard, RealTimeCallUpdate,
    CallTransferRequest, CallHoldRequest, CallMuteRequest, 
    CallRecordingRequest, CallConferenceRequest
)

router = APIRouter(prefix="/api/telephony", tags=["telephony"])
logger = logging.getLogger(__name__)

# PBX Provider Management
@router.get("/providers", response_model=List[PBXProviderResponse])
def get_pbx_providers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all PBX providers for the organization"""
    try:
        providers = db.query(PBXProvider).filter(
            PBXProvider.organization_id == current_user.organization_id
        ).all()
        
        return providers
    except Exception as e:
        logger.error(f"Error fetching PBX providers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch PBX providers: {str(e)}")

@router.post("/providers", response_model=PBXProviderResponse)
def create_pbx_provider(
    provider_data: PBXProviderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new PBX provider"""
    try:
        # Check if this is the first provider (make it primary)
        existing_providers = db.query(PBXProvider).filter(
            PBXProvider.organization_id == current_user.organization_id
        ).count()
        
        is_primary = existing_providers == 0 or provider_data.is_primary
        
        # If setting as primary, unset other primary providers
        if is_primary:
            db.query(PBXProvider).filter(
                and_(
                    PBXProvider.organization_id == current_user.organization_id,
                    PBXProvider.is_primary == True
                )
            ).update({"is_primary": False})
        
        provider = PBXProvider(
            organization_id=current_user.organization_id,
            created_by=current_user.id,
            is_primary=is_primary,
            **provider_data.dict()
        )
        
        db.add(provider)
        db.commit()
        db.refresh(provider)
        
        return provider
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating PBX provider: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create PBX provider: {str(e)}")

@router.get("/providers/{provider_id}", response_model=PBXProviderResponse)
def get_pbx_provider(
    provider_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific PBX provider"""
    try:
        provider = db.query(PBXProvider).filter(
            and_(
                PBXProvider.id == provider_id,
                PBXProvider.organization_id == current_user.organization_id
            )
        ).first()
        
        if not provider:
            raise HTTPException(status_code=404, detail="PBX provider not found")
        
        return provider
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching PBX provider: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch PBX provider: {str(e)}")

@router.put("/providers/{provider_id}", response_model=PBXProviderResponse)
def update_pbx_provider(
    provider_id: int,
    provider_data: PBXProviderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a PBX provider"""
    try:
        provider = db.query(PBXProvider).filter(
            and_(
                PBXProvider.id == provider_id,
                PBXProvider.organization_id == current_user.organization_id
            )
        ).first()
        
        if not provider:
            raise HTTPException(status_code=404, detail="PBX provider not found")
        
        # Handle primary provider logic
        if provider_data.is_primary and not provider.is_primary:
            db.query(PBXProvider).filter(
                and_(
                    PBXProvider.organization_id == current_user.organization_id,
                    PBXProvider.is_primary == True
                )
            ).update({"is_primary": False})
        
        # Update provider fields
        update_data = provider_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(provider, field, value)
        
        provider.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(provider)
        
        return provider
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating PBX provider: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update PBX provider: {str(e)}")

@router.delete("/providers/{provider_id}")
def delete_pbx_provider(
    provider_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a PBX provider"""
    try:
        provider = db.query(PBXProvider).filter(
            and_(
                PBXProvider.id == provider_id,
                PBXProvider.organization_id == current_user.organization_id
            )
        ).first()
        
        if not provider:
            raise HTTPException(status_code=404, detail="PBX provider not found")
        
        # Check if there are active calls or extensions
        active_calls = db.query(Call).filter(
            and_(
                Call.provider_id == provider_id,
                Call.status.in_(["ringing", "answered"])
            )
        ).count()
        
        if active_calls > 0:
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete provider with active calls"
            )
        
        extensions_count = db.query(PBXExtension).filter(
            PBXExtension.provider_id == provider_id
        ).count()
        
        if extensions_count > 0:
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete provider with active extensions"
            )
        
        db.delete(provider)
        db.commit()
        
        return {"message": "PBX provider deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting PBX provider: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete PBX provider: {str(e)}")

@router.post("/providers/{provider_id}/test-connection")
def test_pbx_connection(
    provider_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test connection to PBX provider"""
    try:
        provider = db.query(PBXProvider).filter(
            and_(
                PBXProvider.id == provider_id,
                PBXProvider.organization_id == current_user.organization_id
            )
        ).first()
        
        if not provider:
            raise HTTPException(status_code=404, detail="PBX provider not found")
        
        # Here you would implement the actual connection test
        # This is a placeholder implementation
        connection_status = {
            "connected": True,
            "response_time": 150,  # milliseconds
            "version": "Asterisk 18.0.0",
            "uptime": "15 days, 3 hours",
            "extensions_count": 25,
            "active_channels": 8,
            "tested_at": datetime.utcnow().isoformat()
        }
        
        # Update last sync time
        provider.last_sync = datetime.utcnow()
        db.commit()
        
        return connection_status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing PBX connection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to test PBX connection: {str(e)}")

# PBX Extension Management
@router.get("/extensions", response_model=List[PBXExtensionResponse])
def get_pbx_extensions(
    provider_id: Optional[int] = Query(None, description="Filter by provider ID"),
    extension_type: Optional[str] = Query(None, description="Filter by extension type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get PBX extensions for the organization"""
    try:
        query = db.query(PBXExtension).filter(
            PBXExtension.organization_id == current_user.organization_id
        )
        
        if provider_id:
            query = query.filter(PBXExtension.provider_id == provider_id)
        
        if extension_type:
            query = query.filter(PBXExtension.extension_type == extension_type)
        
        extensions = query.all()
        return extensions
    except Exception as e:
        logger.error(f"Error fetching PBX extensions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch PBX extensions: {str(e)}")

@router.post("/extensions", response_model=PBXExtensionResponse)
def create_pbx_extension(
    extension_data: PBXExtensionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new PBX extension"""
    try:
        # Verify provider exists and belongs to organization
        provider = db.query(PBXProvider).filter(
            and_(
                PBXProvider.id == extension_data.provider_id,
                PBXProvider.organization_id == current_user.organization_id
            )
        ).first()
        
        if not provider:
            raise HTTPException(status_code=404, detail="PBX provider not found")
        
        # Check if extension number already exists for this provider
        existing_extension = db.query(PBXExtension).filter(
            and_(
                PBXExtension.provider_id == extension_data.provider_id,
                PBXExtension.extension_number == extension_data.extension_number
            )
        ).first()
        
        if existing_extension:
            raise HTTPException(
                status_code=400, 
                detail="Extension number already exists for this provider"
            )
        
        extension = PBXExtension(
            organization_id=current_user.organization_id,
            **extension_data.dict()
        )
        
        db.add(extension)
        db.commit()
        db.refresh(extension)
        
        return extension
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating PBX extension: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create PBX extension: {str(e)}")

@router.put("/extensions/{extension_id}", response_model=PBXExtensionResponse)
def update_pbx_extension(
    extension_id: int,
    extension_data: PBXExtensionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a PBX extension"""
    try:
        extension = db.query(PBXExtension).filter(
            and_(
                PBXExtension.id == extension_id,
                PBXExtension.organization_id == current_user.organization_id
            )
        ).first()
        
        if not extension:
            raise HTTPException(status_code=404, detail="PBX extension not found")
        
        # Update extension fields
        update_data = extension_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(extension, field, value)
        
        extension.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(extension)
        
        return extension
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating PBX extension: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update PBX extension: {str(e)}")

@router.delete("/extensions/{extension_id}")
def delete_pbx_extension(
    extension_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a PBX extension"""
    try:
        extension = db.query(PBXExtension).filter(
            and_(
                PBXExtension.id == extension_id,
                PBXExtension.organization_id == current_user.organization_id
            )
        ).first()
        
        if not extension:
            raise HTTPException(status_code=404, detail="PBX extension not found")
        
        # Check for active calls
        active_calls = db.query(Call).filter(
            and_(
                Call.extension_id == extension_id,
                Call.status.in_(["ringing", "answered"])
            )
        ).count()
        
        if active_calls > 0:
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete extension with active calls"
            )
        
        db.delete(extension)
        db.commit()
        
        return {"message": "PBX extension deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting PBX extension: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete PBX extension: {str(e)}")

# Call Management
@router.get("/calls", response_model=List[CallResponse])
def get_calls(
    provider_id: Optional[int] = Query(None, description="Filter by provider ID"),
    agent_id: Optional[int] = Query(None, description="Filter by agent ID"),
    status: Optional[str] = Query(None, description="Filter by call status"),
    direction: Optional[str] = Query(None, description="Filter by call direction"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    limit: int = Query(100, description="Number of calls to return"),
    offset: int = Query(0, description="Number of calls to skip"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get calls for the organization with optional filters"""
    try:
        query = db.query(Call).filter(
            Call.organization_id == current_user.organization_id
        )
        
        if provider_id:
            query = query.filter(Call.provider_id == provider_id)
        
        if agent_id:
            query = query.filter(Call.agent_id == agent_id)
        
        if status:
            query = query.filter(Call.status == status)
        
        if direction:
            query = query.filter(Call.direction == direction)
        
        if start_date:
            query = query.filter(Call.start_time >= start_date)
        
        if end_date:
            query = query.filter(Call.start_time <= end_date)
        
        calls = query.order_by(desc(Call.start_time)).offset(offset).limit(limit).all()
        
        return calls
    except Exception as e:
        logger.error(f"Error fetching calls: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch calls: {str(e)}")

@router.get("/calls/{call_id}", response_model=CallResponse)
def get_call(
    call_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific call"""
    try:
        call = db.query(Call).filter(
            and_(
                Call.id == call_id,
                Call.organization_id == current_user.organization_id
            )
        ).first()
        
        if not call:
            raise HTTPException(status_code=404, detail="Call not found")
        
        return call
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching call: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch call: {str(e)}")

@router.put("/calls/{call_id}", response_model=CallResponse)
def update_call(
    call_id: int,
    call_data: CallUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a call record"""
    try:
        call = db.query(Call).filter(
            and_(
                Call.id == call_id,
                Call.organization_id == current_user.organization_id
            )
        ).first()
        
        if not call:
            raise HTTPException(status_code=404, detail="Call not found")
        
        # Update call fields
        update_data = call_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(call, field, value)
        
        call.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(call)
        
        return call
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating call: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update call: {str(e)}")

# Call Queue Management
@router.get("/queues", response_model=List[CallQueueResponse])
def get_call_queues(
    provider_id: Optional[int] = Query(None, description="Filter by provider ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get call queues for the organization"""
    try:
        query = db.query(CallQueue).filter(
            CallQueue.organization_id == current_user.organization_id
        )
        
        if provider_id:
            query = query.filter(CallQueue.provider_id == provider_id)
        
        queues = query.all()
        return queues
    except Exception as e:
        logger.error(f"Error fetching call queues: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch call queues: {str(e)}")

@router.post("/queues", response_model=CallQueueResponse)
def create_call_queue(
    queue_data: CallQueueCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new call queue"""
    try:
        # Verify provider exists
        provider = db.query(PBXProvider).filter(
            and_(
                PBXProvider.id == queue_data.provider_id,
                PBXProvider.organization_id == current_user.organization_id
            )
        ).first()
        
        if not provider:
            raise HTTPException(status_code=404, detail="PBX provider not found")
        
        # Check if queue number already exists
        existing_queue = db.query(CallQueue).filter(
            and_(
                CallQueue.provider_id == queue_data.provider_id,
                CallQueue.queue_number == queue_data.queue_number
            )
        ).first()
        
        if existing_queue:
            raise HTTPException(
                status_code=400, 
                detail="Queue number already exists for this provider"
            )
        
        queue = CallQueue(
            organization_id=current_user.organization_id,
            **queue_data.dict()
        )
        
        db.add(queue)
        db.commit()
        db.refresh(queue)
        
        return queue
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating call queue: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create call queue: {str(e)}")

@router.put("/queues/{queue_id}", response_model=CallQueueResponse)
def update_call_queue(
    queue_id: int,
    queue_data: CallQueueUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a call queue"""
    try:
        queue = db.query(CallQueue).filter(
            and_(
                CallQueue.id == queue_id,
                CallQueue.organization_id == current_user.organization_id
            )
        ).first()
        
        if not queue:
            raise HTTPException(status_code=404, detail="Call queue not found")
        
        # Update queue fields
        update_data = queue_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(queue, field, value)
        
        queue.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(queue)
        
        return queue
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating call queue: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update call queue: {str(e)}")

@router.delete("/queues/{queue_id}")
def delete_call_queue(
    queue_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a call queue"""
    try:
        queue = db.query(CallQueue).filter(
            and_(
                CallQueue.id == queue_id,
                CallQueue.organization_id == current_user.organization_id
            )
        ).first()
        
        if not queue:
            raise HTTPException(status_code=404, detail="Call queue not found")
        
        # Check for active calls
        active_calls = db.query(Call).filter(
            and_(
                Call.queue_id == queue_id,
                Call.status.in_(["ringing", "answered"])
            )
        ).count()
        
        if active_calls > 0:
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete queue with active calls"
            )
        
        db.delete(queue)
        db.commit()
        
        return {"message": "Call queue deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting call queue: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete call queue: {str(e)}")

# Call Queue Member Management
@router.get("/queues/{queue_id}/members", response_model=List[CallQueueMemberResponse])
def get_queue_members(
    queue_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get members of a call queue"""
    try:
        # Verify queue exists and belongs to organization
        queue = db.query(CallQueue).filter(
            and_(
                CallQueue.id == queue_id,
                CallQueue.organization_id == current_user.organization_id
            )
        ).first()
        
        if not queue:
            raise HTTPException(status_code=404, detail="Call queue not found")
        
        members = db.query(CallQueueMember).filter(
            CallQueueMember.queue_id == queue_id
        ).all()
        
        return members
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching queue members: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch queue members: {str(e)}")

@router.post("/queues/{queue_id}/members", response_model=CallQueueMemberResponse)
def add_queue_member(
    queue_id: int,
    member_data: CallQueueMemberCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a member to a call queue"""
    try:
        # Verify queue exists and belongs to organization
        queue = db.query(CallQueue).filter(
            and_(
                CallQueue.id == queue_id,
                CallQueue.organization_id == current_user.organization_id
            )
        ).first()
        
        if not queue:
            raise HTTPException(status_code=404, detail="Call queue not found")
        
        # Verify user exists and belongs to organization
        user = db.query(User).filter(
            and_(
                User.id == member_data.user_id,
                User.organization_id == current_user.organization_id
            )
        ).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if user is already a member of this queue
        existing_member = db.query(CallQueueMember).filter(
            and_(
                CallQueueMember.queue_id == queue_id,
                CallQueueMember.user_id == member_data.user_id
            )
        ).first()
        
        if existing_member:
            raise HTTPException(
                status_code=400, 
                detail="User is already a member of this queue"
            )
        
        member = CallQueueMember(
            queue_id=queue_id,
            **member_data.dict()
        )
        
        db.add(member)
        
        # Update queue agent count
        queue.current_agents = db.query(CallQueueMember).filter(
            and_(
                CallQueueMember.queue_id == queue_id,
                CallQueueMember.status == "logged_in"
            )
        ).count()
        
        db.commit()
        db.refresh(member)
        
        return member
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding queue member: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add queue member: {str(e)}")

@router.put("/queues/{queue_id}/members/{member_id}", response_model=CallQueueMemberResponse)
def update_queue_member(
    queue_id: int,
    member_id: int,
    member_data: CallQueueMemberUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a queue member"""
    try:
        # Verify queue exists and belongs to organization
        queue = db.query(CallQueue).filter(
            and_(
                CallQueue.id == queue_id,
                CallQueue.organization_id == current_user.organization_id
            )
        ).first()
        
        if not queue:
            raise HTTPException(status_code=404, detail="Call queue not found")
        
        member = db.query(CallQueueMember).filter(
            and_(
                CallQueueMember.id == member_id,
                CallQueueMember.queue_id == queue_id
            )
        ).first()
        
        if not member:
            raise HTTPException(status_code=404, detail="Queue member not found")
        
        # Update member fields
        update_data = member_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(member, field, value)
        
        if 'status' in update_data:
            member.last_status_change = datetime.utcnow()
        
        member.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(member)
        
        return member
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating queue member: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update queue member: {str(e)}")

@router.delete("/queues/{queue_id}/members/{member_id}")
def remove_queue_member(
    queue_id: int,
    member_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a member from a call queue"""
    try:
        # Verify queue exists and belongs to organization
        queue = db.query(CallQueue).filter(
            and_(
                CallQueue.id == queue_id,
                CallQueue.organization_id == current_user.organization_id
            )
        ).first()
        
        if not queue:
            raise HTTPException(status_code=404, detail="Call queue not found")
        
        member = db.query(CallQueueMember).filter(
            and_(
                CallQueueMember.id == member_id,
                CallQueueMember.queue_id == queue_id
            )
        ).first()
        
        if not member:
            raise HTTPException(status_code=404, detail="Queue member not found")
        
        # Check for active calls for this agent
        active_calls = db.query(Call).filter(
            and_(
                Call.agent_id == member.user_id,
                Call.queue_id == queue_id,
                Call.status.in_(["ringing", "answered"])
            )
        ).count()
        
        if active_calls > 0:
            raise HTTPException(
                status_code=400, 
                detail="Cannot remove member with active calls"
            )
        
        db.delete(member)
        
        # Update queue agent count
        queue.current_agents = db.query(CallQueueMember).filter(
            and_(
                CallQueueMember.queue_id == queue_id,
                CallQueueMember.status == "logged_in"
            )
        ).count()
        
        db.commit()
        
        return {"message": "Queue member removed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error removing queue member: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to remove queue member: {str(e)}")

# Call Center Dashboard
@router.get("/dashboard", response_model=CallCenterDashboard)
def get_call_center_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get call center dashboard data"""
    try:
        # Active calls
        active_calls = db.query(Call).filter(
            and_(
                Call.organization_id == current_user.organization_id,
                Call.status.in_(["ringing", "answered"])
            )
        ).count()
        
        # Queued calls
        queued_calls = db.query(Call).filter(
            and_(
                Call.organization_id == current_user.organization_id,
                Call.status == "ringing",
                Call.queue_id.isnot(None)
            )
        ).count()
        
        # Agent status counts
        available_agents = db.query(CallQueueMember).filter(
            and_(
                CallQueueMember.status == "logged_in",
                CallQueueMember.queue.has(
                    CallQueue.organization_id == current_user.organization_id
                )
            )
        ).count()
        
        busy_agents = db.query(Call).filter(
            and_(
                Call.organization_id == current_user.organization_id,
                Call.status == "answered",
                Call.agent_id.isnot(None)
            )
        ).distinct(Call.agent_id).count()
        
        offline_agents = db.query(CallQueueMember).filter(
            and_(
                CallQueueMember.status.in_(["logged_out", "offline"]),
                CallQueueMember.queue.has(
                    CallQueue.organization_id == current_user.organization_id
                )
            )
        ).count()
        
        # Current queue status
        queues = db.query(CallQueue).filter(
            CallQueue.organization_id == current_user.organization_id
        ).all()
        
        queue_status = []
        for queue in queues:
            queue_calls = db.query(Call).filter(
                and_(
                    Call.queue_id == queue.id,
                    Call.status == "ringing"
                )
            ).count()
            
            queue_status.append({
                "id": queue.id,
                "name": queue.name,
                "queue_number": queue.queue_number,
                "current_calls": queue_calls,
                "current_agents": queue.current_agents,
                "wait_time": queue.avg_wait_time
            })
        
        # Recent calls (last 10)
        recent_calls = db.query(Call).filter(
            Call.organization_id == current_user.organization_id
        ).order_by(desc(Call.start_time)).limit(10).all()
        
        # Agent status
        agent_status = []
        agents = db.query(User).filter(
            User.organization_id == current_user.organization_id
        ).all()
        
        for agent in agents:
            agent_calls = db.query(Call).filter(
                and_(
                    Call.agent_id == agent.id,
                    Call.status.in_(["ringing", "answered"])
                )
            ).count()
            
            queue_memberships = db.query(CallQueueMember).filter(
                CallQueueMember.user_id == agent.id
            ).all()
            
            status = "offline"
            if queue_memberships:
                for membership in queue_memberships:
                    if membership.status == "logged_in":
                        status = "available"
                        break
                    elif membership.status == "busy":
                        status = "busy"
            
            agent_status.append({
                "id": agent.id,
                "name": agent.name,
                "email": agent.email,
                "status": status,
                "active_calls": agent_calls,
                "queues": [m.queue.name for m in queue_memberships]
            })
        
        # Queue metrics
        queue_metrics = []
        for queue in queues:
            today = datetime.utcnow().date()
            today_calls = db.query(Call).filter(
                and_(
                    Call.queue_id == queue.id,
                    func.date(Call.start_time) == today
                )
            ).count()
            
            answered_today = db.query(Call).filter(
                and_(
                    Call.queue_id == queue.id,
                    func.date(Call.start_time) == today,
                    Call.status == "answered"
                )
            ).count()
            
            queue_metrics.append({
                "id": queue.id,
                "name": queue.name,
                "calls_today": today_calls,
                "answered_today": answered_today,
                "answer_rate": (answered_today / today_calls * 100) if today_calls > 0 else 0,
                "avg_wait_time": queue.avg_wait_time,
                "service_level": queue.service_level
            })
        
        # Hourly stats for today
        hourly_stats = {}
        for hour in range(24):
            hour_calls = db.query(Call).filter(
                and_(
                    Call.organization_id == current_user.organization_id,
                    func.date(Call.start_time) == datetime.utcnow().date(),
                    func.extract('hour', Call.start_time) == hour
                )
            ).count()
            hourly_stats[str(hour)] = hour_calls
        
        # Daily stats for last 7 days
        daily_stats = {}
        for i in range(7):
            date = (datetime.utcnow() - timedelta(days=i)).date()
            day_calls = db.query(Call).filter(
                and_(
                    Call.organization_id == current_user.organization_id,
                    func.date(Call.start_time) == date
                )
            ).count()
            daily_stats[date.isoformat()] = day_calls
        
        # Alerts (placeholder)
        alerts = []
        if queued_calls > 10:
            alerts.append({
                "type": "warning",
                "message": f"High queue volume: {queued_calls} calls waiting"
            })
        
        if available_agents == 0:
            alerts.append({
                "type": "error",
                "message": "No agents available"
            })
        
        return CallCenterDashboard(
            active_calls=active_calls,
            queued_calls=queued_calls,
            available_agents=available_agents,
            busy_agents=busy_agents,
            offline_agents=offline_agents,
            current_queue_status=queue_status,
            recent_calls=recent_calls,
            agent_status=agent_status,
            queue_metrics=queue_metrics,
            hourly_stats=hourly_stats,
            daily_stats=daily_stats,
            alerts=alerts
        )
    except Exception as e:
        logger.error(f"Error fetching call center dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard: {str(e)}")

# Call Actions (Hold, Transfer, Mute, etc.)
@router.post("/calls/{call_id}/hold")
def hold_call(
    call_id: int,
    hold_data: CallHoldRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Hold or unhold a call"""
    try:
        call = db.query(Call).filter(
            and_(
                Call.id == call_id,
                Call.organization_id == current_user.organization_id
            )
        ).first()
        
        if not call:
            raise HTTPException(status_code=404, detail="Call not found")
        
        if call.status != "answered":
            raise HTTPException(status_code=400, detail="Call must be answered to hold/unhold")
        
        # Here you would implement the actual PBX hold command
        # This is a placeholder
        
        # Log the activity
        activity = CallActivity(
            call_id=call_id,
            user_id=current_user.id,
            activity_type="hold" if hold_data.hold else "unhold",
            activity_data={"reason": hold_data.reason},
            timestamp=datetime.utcnow()
        )
        
        db.add(activity)
        db.commit()
        
        return {"message": f"Call {'held' if hold_data.hold else 'unheld'} successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error holding call: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to hold call: {str(e)}")

@router.post("/calls/{call_id}/transfer")
def transfer_call(
    call_id: int,
    transfer_data: CallTransferRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Transfer a call"""
    try:
        call = db.query(Call).filter(
            and_(
                Call.id == call_id,
                Call.organization_id == current_user.organization_id
            )
        ).first()
        
        if not call:
            raise HTTPException(status_code=404, detail="Call not found")
        
        if call.status != "answered":
            raise HTTPException(status_code=400, detail="Call must be answered to transfer")
        
        # Here you would implement the actual PBX transfer command
        # This is a placeholder
        
        # Log the activity
        activity = CallActivity(
            call_id=call_id,
            user_id=current_user.id,
            activity_type="transfer",
            activity_data={
                "target_extension": transfer_data.target_extension,
                "target_type": transfer_data.target_type,
                "transfer_type": transfer_data.transfer_type,
                "notes": transfer_data.notes
            },
            timestamp=datetime.utcnow()
        )
        
        db.add(activity)
        db.commit()
        
        return {"message": "Call transfer initiated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error transferring call: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to transfer call: {str(e)}")

@router.post("/calls/{call_id}/mute")
def mute_call(
    call_id: int,
    mute_data: CallMuteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mute or unmute a call"""
    try:
        call = db.query(Call).filter(
            and_(
                Call.id == call_id,
                Call.organization_id == current_user.organization_id
            )
        ).first()
        
        if not call:
            raise HTTPException(status_code=404, detail="Call not found")
        
        if call.status != "answered":
            raise HTTPException(status_code=400, detail="Call must be answered to mute/unmute")
        
        # Here you would implement the actual PBX mute command
        # This is a placeholder
        
        # Log the activity
        activity = CallActivity(
            call_id=call_id,
            user_id=current_user.id,
            activity_type="mute" if mute_data.mute else "unmute",
            timestamp=datetime.utcnow()
        )
        
        db.add(activity)
        db.commit()
        
        return {"message": f"Call {'muted' if mute_data.mute else 'unmuted'} successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error muting call: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to mute call: {str(e)}")

@router.post("/calls/{call_id}/recording")
def control_call_recording(
    call_id: int,
    recording_data: CallRecordingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start or stop call recording"""
    try:
        call = db.query(Call).filter(
            and_(
                Call.id == call_id,
                Call.organization_id == current_user.organization_id
            )
        ).first()
        
        if not call:
            raise HTTPException(status_code=404, detail="Call not found")
        
        if call.status not in ["answered", "ringing"]:
            raise HTTPException(status_code=400, detail="Call must be active to record")
        
        # Here you would implement the actual PBX recording command
        # This is a placeholder
        
        # Log the activity
        activity = CallActivity(
            call_id=call_id,
            user_id=current_user.id,
            activity_type="start_recording" if recording_data.start_recording else "stop_recording",
            activity_data={"format": recording_data.format},
            timestamp=datetime.utcnow()
        )
        
        db.add(activity)
        db.commit()
        
        return {"message": f"Call recording {'started' if recording_data.start_recording else 'stopped'} successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error controlling call recording: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to control call recording: {str(e)}")

# Call Analytics
@router.get("/analytics", response_model=List[CallAnalyticsResponse])
def get_call_analytics(
    period_type: str = Query("daily", description="Analytics period type"),
    start_date: Optional[datetime] = Query(None, description="Start date for analytics"),
    end_date: Optional[datetime] = Query(None, description="End date for analytics"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get call analytics for the organization"""
    try:
        query = db.query(CallAnalytics).filter(
            and_(
                CallAnalytics.organization_id == current_user.organization_id,
                CallAnalytics.period_type == period_type
            )
        )
        
        if start_date:
            query = query.filter(CallAnalytics.period_start >= start_date)
        
        if end_date:
            query = query.filter(CallAnalytics.period_end <= end_date)
        
        analytics = query.order_by(desc(CallAnalytics.period_start)).all()
        
        return analytics
    except Exception as e:
        logger.error(f"Error fetching call analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch call analytics: {str(e)}")

# Webhook endpoint for PBX events
@router.post("/webhook/{provider_id}")
def pbx_webhook(
    provider_id: int,
    webhook_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Webhook endpoint for PBX events"""
    try:
        # Verify provider exists
        provider = db.query(PBXProvider).filter(
            PBXProvider.id == provider_id
        ).first()
        
        if not provider:
            raise HTTPException(status_code=404, detail="PBX provider not found")
        
        # Here you would process the webhook data and update call records
        # This is a placeholder implementation
        
        logger.info(f"Received webhook for provider {provider_id}: {webhook_data}")
        
        return {"status": "received", "provider_id": provider_id}
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process webhook: {str(e)}")
