from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatRoomCreate(BaseModel):
    name: str
    description: Optional[str] = None
    room_type: str = "group"  # "direct", "group", "channel"
    organization_id: int
    participant_ids: List[int] = []

class ChatRoomResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    room_type: str
    organization_id: int
    created_by_id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

class ChatMessageCreate(BaseModel):
    content: str
    message_type: str = "text"  # "text", "image", "file", "system"
    reply_to_id: Optional[int] = None

class ChatMessageResponse(BaseModel):
    id: int
    room_id: int
    sender_id: int
    content: str
    message_type: str
    reply_to_id: Optional[int]
    edited_at: Optional[datetime]
    deleted_at: Optional[datetime]
    created_at: datetime
    
    # Include sender information
    sender_name: Optional[str] = None
    sender_avatar: Optional[str] = None
    
    class Config:
        from_attributes = True

class ChatParticipantResponse(BaseModel):
    id: int
    room_id: int
    user_id: int
    role: str
    joined_at: datetime
    last_read_at: Optional[datetime]
    is_active: bool
    
    # Include user information
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    user_avatar: Optional[str] = None
    
    class Config:
        from_attributes = True

class ChatRoomList(BaseModel):
    rooms: List[ChatRoomResponse]
    total: int

class TypingIndicator(BaseModel):
    user_id: int
    user_name: str
    is_typing: bool
    timestamp: datetime

class WebSocketMessage(BaseModel):
    type: str  # "message", "typing", "join_room", "leave_room"
    content: Optional[str] = None
    room_id: Optional[int] = None
    is_typing: Optional[bool] = None
    message_type: Optional[str] = "text"
    reply_to_id: Optional[int] = None
