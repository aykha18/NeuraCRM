from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

# Pydantic models for Kanban board
class StageBase(BaseModel):
    name: str
    order: int
    wip_limit: Optional[int] = None

class StageCreate(StageBase):
    pass

class StageUpdate(StageBase):
    name: Optional[str] = None
    order: Optional[int] = None
    wip_limit: Optional[int] = None

class StageOut(StageBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class DealBase(BaseModel):
    title: str
    description: Optional[str] = None
    value: Optional[float] = None
    contact_id: Optional[int] = None
    owner_id: Optional[int] = None
    stage_id: Optional[int] = None
    reminder_date: Optional[datetime] = None

class DealCreate(DealBase):
    pass

class DealUpdate(DealBase):
    title: Optional[str] = None
    stage_id: Optional[int] = None

class DealOut(DealBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    contact_name: Optional[str] = None
    owner_name: Optional[str] = None
    stage_name: Optional[str] = None
    watchers: Optional[List[str]] = []
    
    class Config:
        from_attributes = True

class DealMoveRequest(BaseModel):
    to_stage_id: int
    position: Optional[int] = None

class KanbanBoard(BaseModel):
    stages: List[StageOut]
    deals: List[DealOut]
