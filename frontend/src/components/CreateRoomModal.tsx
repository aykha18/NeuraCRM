import React, { useState, useEffect } from 'react';
import { X, Users, Hash, User } from 'lucide-react';
import { chatService, type ChatRoom, type OrganizationUser } from '../services/chat';
import { useAuth } from '../contexts/AuthContext';

interface CreateRoomModalProps {
  onClose: () => void;
  onRoomCreated: (room: ChatRoom) => void;
}

const CreateRoomModal: React.FC<CreateRoomModalProps> = ({ onClose, onRoomCreated }) => {
  const { user } = useAuth();
  const [roomName, setRoomName] = useState('');
  const [roomDescription, setRoomDescription] = useState('');
  const [roomType, setRoomType] = useState<'direct' | 'group' | 'channel'>('group');
  const [selectedUsers, setSelectedUsers] = useState<number[]>([]);
  const [organizationUsers, setOrganizationUsers] = useState<OrganizationUser[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load organization users
  useEffect(() => {
    if (user?.organization_id) {
      loadOrganizationUsers();
    }
  }, [user]);

  const loadOrganizationUsers = async () => {
    try {
      const users = await chatService.getOrganizationUsers(user!.organization_id);
      setOrganizationUsers(users.filter(u => u.id !== user!.id)); // Exclude current user
    } catch (err) {
      console.error('Error loading organization users:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!roomName.trim() || !user?.organization_id) return;

    setLoading(true);
    setError(null);

    try {
      const newRoom = await chatService.createRoom({
        name: roomName.trim(),
        description: roomDescription.trim() || undefined,
        room_type: roomType,
        organization_id: user.organization_id,
        participant_ids: selectedUsers
      });

      onRoomCreated(newRoom);
    } catch (err) {
      setError('Failed to create room');
      console.error('Error creating room:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUserToggle = (userId: number) => {
    setSelectedUsers(prev => 
      prev.includes(userId) 
        ? prev.filter(id => id !== userId)
        : [...prev, userId]
    );
  };

  const getRoomTypeIcon = (type: string) => {
    switch (type) {
      case 'direct':
        return <User className="w-5 h-5" />;
      case 'group':
        return <Users className="w-5 h-5" />;
      case 'channel':
        return <Hash className="w-5 h-5" />;
      default:
        return <Users className="w-5 h-5" />;
    }
  };

  const getRoomTypeDescription = (type: string) => {
    switch (type) {
      case 'direct':
        return 'Private conversation between two people';
      case 'group':
        return 'Private group conversation';
      case 'channel':
        return 'Public channel for team discussions';
      default:
        return '';
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Create New Room</h2>
          <button
            onClick={onClose}
            className="p-1 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Room Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Room Name *
            </label>
            <input
              type="text"
              value={roomName}
              onChange={(e) => setRoomName(e.target.value)}
              placeholder="Enter room name..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-fuchsia-500 focus:border-transparent"
              required
            />
          </div>

          {/* Room Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              value={roomDescription}
              onChange={(e) => setRoomDescription(e.target.value)}
              placeholder="Enter room description (optional)..."
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-fuchsia-500 focus:border-transparent resize-none"
            />
          </div>

          {/* Room Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Room Type
            </label>
            <div className="space-y-2">
              {(['group', 'channel', 'direct'] as const).map((type) => (
                <label
                  key={type}
                  className={`flex items-center p-3 border rounded-lg cursor-pointer transition-colors ${
                    roomType === type
                      ? 'border-fuchsia-500 bg-fuchsia-50'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                >
                  <input
                    type="radio"
                    name="roomType"
                    value={type}
                    checked={roomType === type}
                    onChange={(e) => setRoomType(e.target.value as any)}
                    className="sr-only"
                  />
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-lg ${
                      roomType === type
                        ? 'bg-fuchsia-100 text-fuchsia-600'
                        : 'bg-gray-100 text-gray-500'
                    }`}>
                      {getRoomTypeIcon(type)}
                    </div>
                    <div>
                      <div className="font-medium text-gray-900 capitalize">{type}</div>
                      <div className="text-sm text-gray-500">
                        {getRoomTypeDescription(type)}
                      </div>
                    </div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Add Members (for group and channel) */}
          {roomType !== 'direct' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Add Members
              </label>
              <div className="max-h-40 overflow-y-auto space-y-2">
                {organizationUsers.map((orgUser) => (
                  <label
                    key={orgUser.id}
                    className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-50 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={selectedUsers.includes(orgUser.id)}
                      onChange={() => handleUserToggle(orgUser.id)}
                      className="w-4 h-4 text-fuchsia-600 border-gray-300 rounded focus:ring-fuchsia-500"
                    />
                    <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white text-sm font-medium">
                      {orgUser.name.charAt(0).toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-gray-900 truncate">
                        {orgUser.name}
                      </div>
                      <div className="text-xs text-gray-500 truncate">
                        {orgUser.email}
                      </div>
                    </div>
                  </label>
                ))}
              </div>
              {selectedUsers.length > 0 && (
                <div className="mt-2 text-sm text-gray-600">
                  {selectedUsers.length} member{selectedUsers.length !== 1 ? 's' : ''} selected
                </div>
              )}
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center justify-end space-x-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!roomName.trim() || loading}
              className="px-4 py-2 bg-gradient-to-r from-fuchsia-600 to-pink-500 text-white rounded-lg hover:from-fuchsia-700 hover:to-pink-600 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transition-all duration-200"
            >
              {loading ? 'Creating...' : 'Create Room'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateRoomModal;
