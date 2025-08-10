from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from api.crud.kanban import (
    get_kanban_board,
    get_stage, get_stages, create_stage, update_stage, delete_stage,
    get_deal, create_deal, update_deal, delete_deal, move_deal
)
from api.schemas.kanban import (
    StageBase, StageCreate, StageUpdate, StageOut,
    DealBase, DealCreate, DealUpdate, DealOut,
    DealMoveRequest, KanbanBoard
)
from api.dependencies import get_db
from api.models import Deal, User

router = APIRouter(
    prefix="/api/kanban",
    tags=["kanban"],
    responses={404: {"description": "Not found"}},
)

@router.get("/board", response_model=KanbanBoard)
def get_board(db: Session = Depends(get_db)):
    """
    Get the complete Kanban board with all stages and deals
    """
    board = get_kanban_board(db)
    return board

# Stage endpoints
@router.post("/stages/", response_model=StageOut)
def create_stage(stage: StageCreate, db: Session = Depends(get_db)):
    """
    Create a new stage in the Kanban board
    """
    return create_stage(db=db, stage=stage)

@router.get("/stages/", response_model=List[StageOut])
def read_stages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> list[StageOut]:
    """
    Retrieve all stages, ordered by their position
    """
    stages = get_stages(db, skip=skip, limit=limit)
    return stages

@router.get("/stages/{stage_id}", response_model=StageOut)
def read_stage(stage_id: int, db: Session = Depends(get_db)) -> StageOut:
    """
    Get a specific stage by ID
    """
    db_stage = get_stage(db, stage_id=stage_id)
    if db_stage is None:
        raise HTTPException(status_code=404, detail="Stage not found")
    return db_stage

@router.put("/stages/{stage_id}", response_model=StageOut)
def update_stage(
    stage_id: int, stage: StageUpdate, db: Session = Depends(get_db)
) -> StageOut:
    """
    Update a stage
    """
    db_stage = update_stage(db=db, stage_id=stage_id, stage=stage)
    if db_stage is None:
        raise HTTPException(status_code=404, detail="Stage not found")
    return db_stage

@router.delete("/stages/{stage_id}", response_model=dict)
def delete_stage(stage_id: int, db: Session = Depends(get_db)):
    """
    Delete a stage. Any deals in this stage will have their stage_id set to NULL.
    """
    if not delete_stage(db=db, stage_id=stage_id):
        raise HTTPException(status_code=404, detail="Stage not found")
    return {"status": "success", "message": "Stage deleted successfully"}

# Deal endpoints
@router.post("/deals/", response_model=DealOut)
def create_deal(deal: DealCreate, db: Session = Depends(get_db)) -> DealOut:
    """
    Create a new deal in the Kanban board
    """
    return create_deal(db=db, deal=deal)

@router.get("/deals/{deal_id}", response_model=DealOut)
def read_deal(deal_id: int, db: Session = Depends(get_db)) -> DealOut:
    """
    Get a specific deal by ID
    """
    db_deal = get_deal(db, deal_id=deal_id)
    if not db_deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    # Convert the result to a dictionary and handle the unpacked fields
    deal_data = db_deal[0].__dict__
    deal_data["contact_name"] = db_deal[1]
    deal_data["owner_name"] = db_deal[2]
    deal_data["stage_name"] = db_deal[3]
    
    return deal_data

@router.put("/deals/{deal_id}", response_model=DealOut)
def update_deal(
    deal_id: int, deal: DealUpdate, db: Session = Depends(get_db)
) -> DealOut:
    """
    Update a deal's details
    """
    db_deal = update_deal(db=db, deal_id=deal_id, deal=deal)
    if db_deal is None:
        raise HTTPException(status_code=404, detail="Deal not found")
    return db_deal

@router.delete("/deals/{deal_id}", response_model=dict)
def delete_deal(deal_id: int, db: Session = Depends(get_db)):
    """
    Delete a deal
    """
    if not delete_deal(db=db, deal_id=deal_id):
        raise HTTPException(status_code=404, detail="Deal not found")
    return {"status": "success", "message": "Deal deleted successfully"}

@router.post("/deals/{deal_id}/move", response_model=DealOut)
def move_deal_to_stage(
    deal_id: int, 
    move_request: DealMoveRequest,
    db: Session = Depends(get_db)
) -> DealOut:
    """
    Move a deal to a different stage and optionally specify its position
    """
    db_deal = move_deal(
        db=db, 
        deal_id=deal_id, 
        new_stage_id=move_request.to_stage_id, 
        new_position=move_request.position
    )
    if db_deal is None:
        raise HTTPException(status_code=404, detail="Deal not found")
    return db_deal

@router.post("/deals/{deal_id}/watch", response_model=DealOut)
def add_watcher(deal_id: int, db: Session = Depends(get_db)):
    user_id = 5  # Imran Patel
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    user = db.query(User).filter(User.id == user_id).first()
    if not deal or not user:
        raise HTTPException(status_code=404, detail="Deal or user not found")
    if user not in deal.watchers:
        deal.watchers.append(user)
        db.commit()
        db.refresh(deal)
    
    # Convert to proper format for response
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
        "contact_name": None,
        "owner_name": None,
        "stage_name": None,
        "watchers": [user.name for user in deal.watchers]
    }
    return deal_dict

@router.delete("/deals/{deal_id}/watch", response_model=DealOut)
def remove_watcher(deal_id: int, db: Session = Depends(get_db)):
    user_id = 5  # Imran Patel
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    user = db.query(User).filter(User.id == user_id).first()
    if not deal or not user:
        raise HTTPException(status_code=404, detail="Deal or user not found")
    if user in deal.watchers:
        deal.watchers.remove(user)
        db.commit()
        db.refresh(deal)
    
    # Convert to proper format for response
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
        "contact_name": None,
        "owner_name": None,
        "stage_name": None,
        "watchers": [user.name for user in deal.watchers]
    }
    return deal_dict
