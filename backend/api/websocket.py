from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
import json
import asyncio
from datetime import datetime

from .db import get_db
from .models import User, ChatRoom, ChatMessage, ChatParticipant
from .dependencies import get_current_user

class ConnectionManager:
    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # Store room connections by room_id
        self.room_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int, room_id: Optional[int] = None):
        await websocket.accept()
        
        # Add to user connections
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        
        # Add to room connections if room_id provided
        if room_id:
            if room_id not in self.room_connections:
                self.room_connections[room_id] = []
            self.room_connections[room_id].append(websocket)
            
            # Send user joined notification
            await self.broadcast_to_room(room_id, {
                "type": "user_joined",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }, exclude_user=user_id)

    def disconnect(self, websocket: WebSocket, user_id: int, room_id: Optional[int] = None):
        # Remove from user connections
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        # Remove from room connections
        if room_id and room_id in self.room_connections:
            if websocket in self.room_connections[room_id]:
                self.room_connections[room_id].remove(websocket)
            if not self.room_connections[room_id]:
                del self.room_connections[room_id]

    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    # Remove broken connections
                    self.active_connections[user_id].remove(connection)

    async def broadcast_to_room(self, room_id: int, message: dict, exclude_user: Optional[int] = None):
        if room_id in self.room_connections:
            for connection in self.room_connections[room_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    # Remove broken connections
                    self.room_connections[room_id].remove(connection)

    async def broadcast_to_organization(self, organization_id: int, message: dict, exclude_user: Optional[int] = None):
        # This would require additional logic to get all users in an organization
        # For now, we'll implement a simpler version
        for user_id, connections in self.active_connections.items():
            if exclude_user and user_id == exclude_user:
                continue
            for connection in connections:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    # Remove broken connections
                    if connection in connections:
                        connections.remove(connection)

manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket, room_id: Optional[int] = None, token: Optional[str] = None):
    user = None
    current_room_id = room_id
    
    try:
        # Authenticate user from token
        if not token:
            await websocket.close(code=1008, reason="Authentication required")
            return
            
        # Here you would validate the JWT token and get the user
        # For now, we'll use a simple approach
        db = next(get_db())
        try:
            # This is a simplified authentication - in production, use proper JWT validation
            user = db.query(User).filter(User.id == 1).first()  # Demo user
            if not user:
                await websocket.close(code=1008, reason="Invalid token")
                return
        except Exception as e:
            await websocket.close(code=1008, reason="Authentication failed")
            return
        finally:
            db.close()
        
        # Check if user has access to the room
        if current_room_id:
            db = next(get_db())
            try:
                participant = db.query(ChatParticipant).filter(
                    ChatParticipant.room_id == current_room_id,
                    ChatParticipant.user_id == user.id,
                    ChatParticipant.is_active == True
                ).first()
                if not participant:
                    await websocket.close(code=1008, reason="Access denied to room")
                    return
            except Exception as e:
                await websocket.close(code=1008, reason="Room access check failed")
                return
            finally:
                db.close()
        
        # Connect to the room
        await manager.connect(websocket, user.id, current_room_id)
        
        # Send connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "user_id": user.id,
            "room_id": current_room_id,
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        # Listen for messages
        while True:
            try:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                if message_data.get("type") == "message":
                    await handle_message(websocket, user, current_room_id, message_data)
                elif message_data.get("type") == "typing":
                    await handle_typing(websocket, user, current_room_id, message_data)
                elif message_data.get("type") == "join_room":
                    await handle_join_room(websocket, user, message_data)
                elif message_data.get("type") == "leave_room":
                    await handle_leave_room(websocket, user, message_data)
                    
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
            except Exception as e:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "An error occurred"
                }))
                
    except WebSocketDisconnect:
        pass
    finally:
        if user:
            manager.disconnect(websocket, user.id, current_room_id)

async def handle_message(websocket: WebSocket, user: User, room_id: int, message_data: dict):
    """Handle incoming chat messages"""
    content = message_data.get("content", "").strip()
    if not content:
        return
    
    db = next(get_db())
    try:
        # Create the message
        message = ChatMessage(
            room_id=room_id,
            sender_id=user.id,
            content=content,
            message_type=message_data.get("message_type", "text")
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        
        # Update last read timestamp for sender
        participant = db.query(ChatParticipant).filter(
            ChatParticipant.room_id == room_id,
            ChatParticipant.user_id == user.id
        ).first()
        if participant:
            participant.last_read_at = datetime.utcnow()
            db.commit()
        
        # Broadcast message to room
        message_response = {
            "type": "new_message",
            "message": {
                "id": message.id,
                "room_id": message.room_id,
                "sender_id": message.sender_id,
                "sender_name": user.name,
                "content": message.content,
                "message_type": message.message_type,
                "created_at": message.created_at.isoformat(),
                "reply_to_id": message.reply_to_id
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await manager.broadcast_to_room(room_id, message_response)
        
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": "Failed to send message"
        }))
    finally:
        db.close()

async def handle_typing(websocket: WebSocket, user: User, room_id: int, message_data: dict):
    """Handle typing indicators"""
    is_typing = message_data.get("is_typing", False)
    
    typing_response = {
        "type": "typing",
        "user_id": user.id,
        "user_name": user.name,
        "is_typing": is_typing,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.broadcast_to_room(room_id, typing_response, exclude_user=user.id)

async def handle_join_room(websocket: WebSocket, user: User, message_data: dict):
    """Handle joining a new room"""
    room_id = message_data.get("room_id")
    if not room_id:
        return
    
    db = next(get_db())
    try:
        # Check if user has access to the room
        participant = db.query(ChatParticipant).filter(
            ChatParticipant.room_id == room_id,
            ChatParticipant.user_id == user.id,
            ChatParticipant.is_active == True
        ).first()
        
        if participant:
            # Disconnect from current room and connect to new room
            manager.disconnect(websocket, user.id)
            await manager.connect(websocket, user.id, room_id)
            
            await websocket.send_text(json.dumps({
                "type": "room_joined",
                "room_id": room_id,
                "timestamp": datetime.utcnow().isoformat()
            }))
        else:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Access denied to room"
            }))
            
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": "Failed to join room"
        }))
    finally:
        db.close()

async def handle_leave_room(websocket: WebSocket, user: User, message_data: dict):
    """Handle leaving a room"""
    room_id = message_data.get("room_id")
    if room_id:
        manager.disconnect(websocket, user.id, room_id)
        
        # Send user left notification
        await manager.broadcast_to_room(room_id, {
            "type": "user_left",
            "user_id": user.id,
            "timestamp": datetime.utcnow().isoformat()
        }, exclude_user=user.id)
