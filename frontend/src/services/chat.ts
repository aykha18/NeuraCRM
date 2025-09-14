import { apiRequest } from '../utils/api';

export interface ChatRoom {
  id: number;
  name: string;
  description?: string;
  room_type: 'direct' | 'group' | 'channel';
  organization_id: number;
  created_by_id: number;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

export interface ChatMessage {
  id: number;
  room_id: number;
  sender_id: number;
  sender_name?: string;
  sender_avatar?: string;
  content: string;
  message_type: 'text' | 'image' | 'file' | 'system';
  reply_to_id?: number;
  edited_at?: string;
  deleted_at?: string;
  created_at: string;
}

export interface ChatParticipant {
  id: number;
  room_id: number;
  user_id: number;
  user_name?: string;
  user_email?: string;
  user_avatar?: string;
  role: 'admin' | 'moderator' | 'member';
  joined_at: string;
  last_read_at?: string;
  is_active: boolean;
}

export interface CreateRoomRequest {
  name: string;
  description?: string;
  room_type: 'direct' | 'group' | 'channel';
  organization_id: number;
  participant_ids: number[];
}

export interface SendMessageRequest {
  content: string;
  message_type?: 'text' | 'image' | 'file' | 'system';
  reply_to_id?: number;
}

export interface OrganizationUser {
  id: number;
  name: string;
  email: string;
  avatar_url?: string;
}

export const chatService = {
  // Get all chat rooms for the current user
  async getRooms(): Promise<ChatRoom[]> {
    return apiRequest<ChatRoom[]>('/chat/rooms', 'GET');
  },

  // Create a new chat room
  async createRoom(roomData: CreateRoomRequest): Promise<ChatRoom> {
    return apiRequest<ChatRoom>('/chat/rooms', 'POST', roomData);
  },

  // Get a specific chat room
  async getRoom(roomId: number): Promise<ChatRoom> {
    return apiRequest<ChatRoom>(`/chat/rooms/${roomId}`, 'GET');
  },

  // Get messages for a room
  async getMessages(roomId: number, limit: number = 50, offset: number = 0): Promise<ChatMessage[]> {
    return apiRequest<ChatMessage[]>(`/chat/rooms/${roomId}/messages?limit=${limit}&offset=${offset}`, 'GET');
  },

  // Send a message to a room
  async sendMessage(roomId: number, messageData: SendMessageRequest): Promise<ChatMessage> {
    return apiRequest<ChatMessage>(`/chat/rooms/${roomId}/messages`, 'POST', messageData);
  },

  // Get participants of a room
  async getParticipants(roomId: number): Promise<ChatParticipant[]> {
    return apiRequest<ChatParticipant[]>(`/chat/rooms/${roomId}/participants`, 'GET');
  },

  // Add a participant to a room
  async addParticipant(roomId: number, userId: number): Promise<void> {
    return apiRequest<void>(`/chat/rooms/${roomId}/participants`, 'POST', { user_id: userId });
  },

  // Remove a participant from a room
  async removeParticipant(roomId: number, userId: number): Promise<void> {
    return apiRequest<void>(`/chat/rooms/${roomId}/participants/${userId}`, 'DELETE');
  },

  // Get organization users for adding to chat rooms
  async getOrganizationUsers(orgId: number): Promise<OrganizationUser[]> {
    return apiRequest<OrganizationUser[]>(`/chat/organizations/${orgId}/users`, 'GET');
  }
};
