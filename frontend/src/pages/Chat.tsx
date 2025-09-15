import React, { useState, useEffect } from 'react';
import { MessageCircle, Plus, Search } from 'lucide-react';
import { chatService, type ChatRoom } from '../services/chat';
import { useAuth } from '../contexts/AuthContext';
import ChatWindow from '../components/ChatWindow';
import CreateRoomModal from '../components/CreateRoomModal';

const Chat: React.FC = () => {
  const { user } = useAuth();
  const [rooms, setRooms] = useState<ChatRoom[]>([]);
  const [selectedRoomId, setSelectedRoomId] = useState<number | undefined>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Load rooms on component mount
  useEffect(() => {
    loadRooms();
  }, []);

  const loadRooms = async () => {
    try {
      setLoading(true);
      const roomsData = await chatService.getRooms();
      setRooms(roomsData);
      
      // Select first room if none selected
      if (roomsData.length > 0 && !selectedRoomId) {
        setSelectedRoomId(roomsData[0].id);
      }
    } catch (err) {
      setError('Failed to load chat rooms');
      // error loading rooms
    } finally {
      setLoading(false);
    }
  };

  const handleRoomSelect = (roomId: number) => {
    setSelectedRoomId(roomId);
  };

  const handleRoomCreated = (newRoom: ChatRoom) => {
    setRooms(prev => [newRoom, ...prev]);
    setSelectedRoomId(newRoom.id);
    setShowCreateModal(false);
  };

  const filteredRooms = rooms
    .filter((room: any) => room && typeof room === 'object')
    .filter(room => (room.name || '').toLowerCase().includes((searchQuery || '').toLowerCase()));

  const getRoomIcon = (roomType: string) => {
    switch (roomType) {
      case 'direct':
        return '👤';
      case 'group':
        return '👥';
      case 'channel':
        return '📢';
      default:
        return '💬';
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-fuchsia-600 mx-auto mb-4"></div>
          <p className="text-gray-500">Loading chat rooms...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex bg-gray-50 -m-6">
      {/* Sidebar */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-xl font-semibold text-gray-900">Chat</h1>
            <button
              onClick={() => setShowCreateModal(true)}
              className="p-2 bg-gradient-to-r from-fuchsia-600 to-pink-500 text-white rounded-full hover:from-fuchsia-700 hover:to-pink-600 transition-all duration-200 transform hover:scale-105"
            >
              <Plus className="w-5 h-5" />
            </button>
          </div>

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search conversations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-fuchsia-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Rooms List */}
        <div className="flex-1 overflow-y-auto">
          {error && (
            <div className="p-4 text-center">
              <div className="text-red-500 mb-2">⚠️</div>
              <p className="text-sm text-gray-600 mb-3">{error}</p>
              <button
                onClick={loadRooms}
                className="px-3 py-1 bg-fuchsia-600 text-white text-sm rounded-lg hover:bg-fuchsia-700 transition-colors"
              >
                Retry
              </button>
            </div>
          )}

          {filteredRooms.length === 0 && !error && (
            <div className="p-4 text-center">
              <MessageCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <h3 className="text-sm font-medium text-gray-900 mb-1">No conversations</h3>
              <p className="text-xs text-gray-500 mb-3">Start a new conversation</p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="px-3 py-1 bg-fuchsia-600 text-white text-sm rounded-lg hover:bg-fuchsia-700 transition-colors"
              >
                Create Room
              </button>
            </div>
          )}

          <div className="space-y-1 p-2">
            {filteredRooms.map((room, idx) => {
              const updated = room.updated_at || room.created_at;
              const dateText = updated ? (() => { const d = new Date(updated as any); return isNaN(d.getTime()) ? '' : d.toLocaleDateString(); })() : '';
              return (
              <button
                key={room.id ?? idx}
                onClick={() => handleRoomSelect(room.id)}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  selectedRoomId === room.id
                    ? 'bg-gradient-to-r from-fuchsia-50 to-pink-50 border border-fuchsia-200'
                    : 'hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-to-r from-fuchsia-600 to-pink-500 rounded-full flex items-center justify-center text-white text-lg">
                    {getRoomIcon(room.room_type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <h3 className="text-sm font-medium text-gray-900 truncate">
                        {room.name || 'Untitled room'}
                      </h3>
                      {room.room_type === 'direct' && (
                        <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                      )}
                    </div>
                    {room.description && (
                      <p className="text-xs text-gray-500 truncate">
                        {room.description}
                      </p>
                    )}
                    {dateText && (
                      <p className="text-xs text-gray-400">
                        {room.room_type} • {dateText}
                      </p>
                    )}
                  </div>
                </div>
              </button>
            )})}
          </div>
        </div>
      </div>

      {/* Chat Window */}
      <div className="flex-1 flex flex-col">
        <ChatWindow
          roomId={selectedRoomId}
          onRoomSelect={handleRoomSelect}
        />
      </div>

      {/* Create Room Modal */}
      {showCreateModal && (
        <CreateRoomModal
          onClose={() => setShowCreateModal(false)}
          onRoomCreated={handleRoomCreated}
        />
      )}
    </div>
  );
};

export default Chat;