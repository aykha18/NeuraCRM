from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..models import Deal, Stage, Contact, User
from ..schemas.kanban import DealCreate, DealUpdate, StageCreate, StageUpdate

def get_kanban_board(db: Session, organization_id: int):
    """
    Get all stages with their associated deals for the Kanban board
    """
    stages = db.query(Stage).order_by(Stage.order).all()
    
    # Get all deals with related data
    deals = (
        db.query(
            Deal,
            Contact.name.label("contact_name"),
            User.name.label("owner_name"),
            Stage.name.label("stage_name")
        )
        .join(Contact, Deal.contact_id == Contact.id, isouter=True)
        .join(User, Deal.owner_id == User.id, isouter=True)
        .join(Stage, Deal.stage_id == Stage.id, isouter=True)
        .filter(Deal.organization_id == organization_id)
        .all()
    )
    
    # Convert to list of dicts for easier processing
    deal_list = []
    for deal, contact_name, owner_name, stage_name in deals:
        # Create a clean dict without SQLAlchemy internal attributes
        deal_dict = {
            "id": deal.id,
            "title": deal.title,
            "description": deal.description,
            "value": deal.value,
            "contact_id": deal.contact_id,
            "owner_id": deal.owner_id,
            "stage_id": deal.stage_id,
            "reminder_date": deal.reminder_date,
            "created_at": deal.created_at,
            "contact_name": contact_name,
            "owner_name": owner_name,
            "stage_name": stage_name,
        }
        
        # Get watchers for this deal
        deal_dict["watchers"] = [user.name for user in deal.watchers]
        
        deal_list.append(deal_dict)
    
    return {"stages": stages, "deals": deal_list}

def get_stage(db: Session, stage_id: int):
    """Get a single stage by ID"""
    return db.query(Stage).filter(Stage.id == stage_id).first()

def get_stages(db: Session, skip: int = 0, limit: int = 100):
    """Get all stages, ordered by their position"""
    return db.query(Stage).order_by(Stage.order).offset(skip).limit(limit).all()

def create_stage(db: Session, stage: StageCreate):
    """Create a new stage"""
    db_stage = Stage(**stage.dict())
    db.add(db_stage)
    db.commit()
    db.refresh(db_stage)
    return db_stage

def update_stage(db: Session, stage_id: int, stage: StageUpdate):
    """Update a stage"""
    db_stage = get_stage(db, stage_id)
    if not db_stage:
        return None
    
    update_data = stage.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_stage, field, value)
    
    db.add(db_stage)
    db.commit()
    db.refresh(db_stage)
    return db_stage

def delete_stage(db: Session, stage_id: int):
    """Delete a stage"""
    # First, move all deals in this stage to another stage or set stage_id to None
    db.query(Deal).filter(Deal.stage_id == stage_id).update({Deal.stage_id: None})
    
    # Then delete the stage
    db_stage = get_stage(db, stage_id)
    if db_stage:
        db.delete(db_stage)
        db.commit()
        return True
    return False

def get_deal(db: Session, deal_id: int):
    """Get a single deal with related data"""
    return (
        db.query(
            Deal,
            Contact.name.label("contact_name"),
            User.name.label("owner_name"),
            Stage.name.label("stage_name")
        )
        .join(Contact, Deal.contact_id == Contact.id, isouter=True)
        .join(User, Deal.owner_id == User.id, isouter=True)
        .join(Stage, Deal.stage_id == Stage.id, isouter=True)
        .filter(Deal.id == deal_id)
        .first()
    )

def create_deal(db: Session, deal: DealCreate):
    """Create a new deal"""
    db_deal = Deal(**deal.dict())
    db.add(db_deal)
    db.commit()
    db.refresh(db_deal)
    return db_deal

def update_deal(db: Session, deal_id: int, deal: DealUpdate):
    """Update a deal, including moving it between stages"""
    db_deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not db_deal:
        return None
    
    update_data = deal.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_deal, field, value)
    
    db.add(db_deal)
    db.commit()
    db.refresh(db_deal)
    return db_deal

def delete_deal(db: Session, deal_id: int):
    """Delete a deal"""
    db_deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if db_deal:
        db.delete(db_deal)
        db.commit()
        return True
    return False

def move_deal(db: Session, deal_id: int, new_stage_id: int, new_position: Optional[int] = None):
    """
    Move a deal to a new stage and optionally reorder it within that stage
    """
    db_deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not db_deal:
        return None
    
    # Update the stage
    db_deal.stage_id = new_stage_id
    
    # If a new position is provided, you might want to update an 'order' field in the Deal model
    # For now, we'll just update the stage_id
    
    db.add(db_deal)
    db.commit()
    db.refresh(db_deal)
    return db_deal
