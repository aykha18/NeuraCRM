import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, Users, Settings, Send, Paperclip, Smile } from 'lucide-react';
import { useWebSocket } from '../hooks/useWebSocket';
import { chatService, type ChatRoom, type ChatMessage, type ChatParticipant } from '../services/chat';
import { useAuth } from '../contexts/AuthContext';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import ChatSidebar from './ChatSidebar';

interface ChatWindowProps {
  roomId?: number;
  onRoomSelect?: (roomId: number) => void;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ roomId, onRoomSelect }) => {
  const { user } = useAuth();
  const [currentRoom, setCurrentRoom] = useState<ChatRoom | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [participants, setParticipants] = useState<ChatParticipant[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSidebar, setShowSidebar] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { 
    isConnected, 
    connectionError, 
    sendChatMessage, 
    sendTypingIndicator,
    joinRoom,
    leaveRoom
  } = useWebSocket({
    roomId,
    onMessage: handleWebSocketMessage,
    onError: () => setError('Connection error'),
    onOpen: () => setError(null)
  });

  function handleWebSocketMessage(message: any) {
    switch (message.type) {
      case 'new_message':
        setMessages(prev => [message.message, ...prev]);
        break;
      case 'typing':
        // Handle typing indicators
        break;
      case 'user_joined':
      case 'user_left':
        // Handle user presence
        break;
      case 'connection_established':
        setError(null);
        break;
      case 'error':
        setError(message.message);
        break;
    }
  }

  // Load room data when roomId changes
  useEffect(() => {
    if (roomId) {
      loadRoomData(roomId);
    } else {
      setCurrentRoom(null);
      setMessages([]);
      setParticipants([]);
    }
  }, [roomId]);

  const loadRoomData = async (id: number) => {
    setLoading(true);
    setError(null);
    
    try {
      const [room, roomMessages, roomParticipants] = await Promise.all([
        chatService.getRoom(id),
        chatService.getMessages(id),
        chatService.getParticipants(id)
      ]);
      
      setCurrentRoom(room);
      setMessages(roomMessages.reverse()); // Reverse to show oldest first
      setParticipants(roomParticipants);
      
      // Join the room via WebSocket
      joinRoom(id);
    } catch (err) {
      setError('Failed to load room data');
      console.error('Error loading room data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (content: string, messageType: string = 'text', replyToId?: number) => {
    if (!currentRoom || !content.trim()) return;

    try {
      // Send via WebSocket for real-time delivery
      sendChatMessage(content, messageType, replyToId);
      
      // Also send via API for persistence
      await chatService.sendMessage(currentRoom.id, {
        content,
        message_type: messageType as 'text' | 'image' | 'file' | 'system',
        reply_to_id: replyToId
      });
    } catch (err) {
      setError('Failed to send message');
      console.error('Error sending message:', err);
    }
  };

  const handleTyping = (isTyping: boolean) => {
    sendTypingIndicator(isTyping);
  };

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (!roomId) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <MessageCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Welcome to Chat</h3>
          <p className="text-gray-500">Select a conversation to start messaging</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-fuchsia-600 mx-auto mb-4"></div>
          <p className="text-gray-500">Loading conversation...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="text-red-500 mb-4">⚠️</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error</h3>
          <p className="text-gray-500 mb-4">{error}</p>
          <button
            onClick={() => roomId && loadRoomData(roomId)}
            className="px-4 py-2 bg-fuchsia-600 text-white rounded-lg hover:bg-fuchsia-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Chat Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-white">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-r from-fuchsia-600 to-pink-500 rounded-full flex items-center justify-center">
            <MessageCircle className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">{currentRoom?.name}</h2>
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <Users className="w-4 h-4" />
              <span>{participants.length} members</span>
              {!isConnected && (
                <span className="text-red-500">• Disconnected</span>
              )}
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowSidebar(!showSidebar)}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Users className="w-5 h-5" />
          </button>
          <button className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
            <Settings className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Chat Content */}
      <div className="flex-1 flex overflow-hidden min-h-0">
        {/* Messages Area */}
        <div className="flex-1 flex flex-col min-h-0">
          <MessageList 
            messages={messages}
            currentUserId={user?.id}
            onReply={(messageId) => {
              // Handle reply functionality
            }}
          />
          <div ref={messagesEndRef} />
          
          <MessageInput
            onSendMessage={handleSendMessage}
            onTyping={handleTyping}
            disabled={!isConnected}
            placeholder={`Message ${currentRoom?.name}...`}
          />
        </div>

        {/* Sidebar */}
        {showSidebar && (
          <ChatSidebar
            room={currentRoom}
            participants={participants}
            onClose={() => setShowSidebar(false)}
          />
        )}
      </div>
    </div>
  );
};

export default ChatWindow;