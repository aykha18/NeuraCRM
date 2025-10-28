from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.api.db import get_db
from backend.api.models import User, ChatRoom, ChatMessage, ChatParticipant, Organization
from backend.api.dependencies import get_current_user
from backend.api.schemas.chat import (
    ChatRoomCreate, ChatRoomResponse, ChatMessageCreate,
    ChatMessageResponse, ChatParticipantResponse, ChatRoomList
)

router = APIRouter(prefix="/chat", tags=["chat"])

@router.get("/rooms", response_model=List[ChatRoomResponse])
async def get_user_rooms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all chat rooms for the current user"""
    rooms = db.query(ChatRoom).join(ChatParticipant).filter(
        ChatParticipant.user_id == current_user.id,
        ChatParticipant.is_active == True,
        ChatRoom.is_active == True
    ).all()
    
    return rooms

@router.post("/rooms", response_model=ChatRoomResponse)
async def create_room(
    room_data: ChatRoomCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new chat room"""
    # Check if user has permission to create rooms in this organization
    if current_user.organization_id != room_data.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create room in different organization"
        )
    
    # Create the room
    room = ChatRoom(
        name=room_data.name,
        description=room_data.description,
        room_type=room_data.room_type,
        organization_id=room_data.organization_id,
        created_by_id=current_user.id
    )
    db.add(room)
    db.flush()  # Get the room ID
    
    # Add creator as admin participant
    creator_participant = ChatParticipant(
        room_id=room.id,
        user_id=current_user.id,
        role="admin"
    )
    db.add(creator_participant)
    
    # Add other participants
    for user_id in room_data.participant_ids:
        if user_id != current_user.id:  # Don't add creator twice
            participant = ChatParticipant(
                room_id=room.id,
                user_id=user_id,
                role="member"
            )
            db.add(participant)
    
    db.commit()
    db.refresh(room)
    
    return room

@router.get("/rooms/{room_id}", response_model=ChatRoomResponse)
async def get_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific chat room"""
    # Check if user is a participant
    participant = db.query(ChatParticipant).filter(
        ChatParticipant.room_id == room_id,
        ChatParticipant.user_id == current_user.id,
        ChatParticipant.is_active == True
    ).first()
    
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found or access denied"
        )
    
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    return room

@router.get("/rooms/{room_id}/messages", response_model=List[ChatMessageResponse])
async def get_room_messages(
    room_id: int,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages for a specific room"""
    # Check if user is a participant
    participant = db.query(ChatParticipant).filter(
        ChatParticipant.room_id == room_id,
        ChatParticipant.user_id == current_user.id,
        ChatParticipant.is_active == True
    ).first()
    
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found or access denied"
        )
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.room_id == room_id,
        ChatMessage.deleted_at.is_(None)
    ).order_by(ChatMessage.created_at.desc()).offset(offset).limit(limit).all()
    
    # Update last read timestamp
    participant.last_read_at = datetime.utcnow()
    db.commit()
    
    return messages

@router.post("/rooms/{room_id}/messages", response_model=ChatMessageResponse)
async def send_message(
    room_id: int,
    message_data: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message to a room"""
    # Check if user is a participant
    participant = db.query(ChatParticipant).filter(
        ChatParticipant.room_id == room_id,
        ChatParticipant.user_id == current_user.id,
        ChatParticipant.is_active == True
    ).first()
    
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found or access denied"
        )
    
    # Create the message
    message = ChatMessage(
        room_id=room_id,
        sender_id=current_user.id,
        content=message_data.content,
        message_type=message_data.message_type or "text",
        reply_to_id=message_data.reply_to_id
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    
    return message

@router.get("/rooms/{room_id}/participants", response_model=List[ChatParticipantResponse])
async def get_room_participants(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get participants of a room"""
    # Check if user is a participant
    participant = db.query(ChatParticipant).filter(
        ChatParticipant.room_id == room_id,
        ChatParticipant.user_id == current_user.id,
        ChatParticipant.is_active == True
    ).first()
    
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found or access denied"
        )
    
    participants = db.query(ChatParticipant).filter(
        ChatParticipant.room_id == room_id,
        ChatParticipant.is_active == True
    ).all()
    
    return participants

@router.post("/rooms/{room_id}/participants")
async def add_participant(
    room_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a participant to a room"""
    # Check if current user is admin of the room
    admin_participant = db.query(ChatParticipant).filter(
        ChatParticipant.room_id == room_id,
        ChatParticipant.user_id == current_user.id,
        ChatParticipant.role == "admin",
        ChatParticipant.is_active == True
    ).first()
    
    if not admin_participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only room admins can add participants"
        )
    
    # Check if user exists and is in the same organization
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found or not in same organization"
        )
    
    # Check if user is already a participant
    existing_participant = db.query(ChatParticipant).filter(
        ChatParticipant.room_id == room_id,
        ChatParticipant.user_id == user_id
    ).first()
    
    if existing_participant:
        if existing_participant.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a participant"
            )
        else:
            # Reactivate participant
            existing_participant.is_active = True
            existing_participant.joined_at = datetime.utcnow()
    else:
        # Create new participant
        participant = ChatParticipant(
            room_id=room_id,
            user_id=user_id,
            role="member"
        )
        db.add(participant)
    
    db.commit()
    
    return {"message": "Participant added successfully"}

@router.delete("/rooms/{room_id}/participants/{user_id}")
async def remove_participant(
    room_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a participant from a room"""
    # Check if current user is admin or removing themselves
    if user_id != current_user.id:
        admin_participant = db.query(ChatParticipant).filter(
            ChatParticipant.room_id == room_id,
            ChatParticipant.user_id == current_user.id,
            ChatParticipant.role == "admin",
            ChatParticipant.is_active == True
        ).first()
        
        if not admin_participant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only room admins can remove other participants"
            )
    
    # Find and deactivate participant
    participant = db.query(ChatParticipant).filter(
        ChatParticipant.room_id == room_id,
        ChatParticipant.user_id == user_id,
        ChatParticipant.is_active == True
    ).first()
    
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )
    
    participant.is_active = False
    db.commit()
    
    return {"message": "Participant removed successfully"}

@router.get("/organizations/{org_id}/users", response_model=List[dict])
async def get_organization_users(
    org_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all users in an organization for adding to chat rooms"""
    # Check if user is in the same organization
    if current_user.organization_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to organization users"
        )
    
    users = db.query(User).filter(User.organization_id == org_id).all()
    
    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "avatar_url": user.avatar_url
        }
        for user in users
    ]
