import React, { useState } from 'react';
import { X, Users, Settings, UserPlus, Crown, Shield, User } from 'lucide-react';
import type { ChatRoom, ChatParticipant } from '../services/chat';

interface ChatSidebarProps {
  room: ChatRoom | null;
  participants: ChatParticipant[];
  onClose: () => void;
}

const ChatSidebar: React.FC<ChatSidebarProps> = ({ room, participants, onClose }) => {
  const [activeTab, setActiveTab] = useState<'members' | 'settings'>('members');

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'admin':
        return <Crown className="w-4 h-4 text-yellow-500" />;
      case 'moderator':
        return <Shield className="w-4 h-4 text-blue-500" />;
      default:
        return <User className="w-4 h-4 text-gray-500" />;
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'admin':
        return 'text-yellow-600 bg-yellow-50';
      case 'moderator':
        return 'text-blue-600 bg-blue-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  if (!room) {
    return null;
  }

  return (
    <div className="w-80 bg-white border-l border-gray-200 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Room Info</h3>
          <button
            onClick={onClose}
            className="p-1 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Room Info */}
      <div className="p-4 border-b border-gray-200">
        <div className="space-y-3">
          <div>
            <h4 className="font-medium text-gray-900">{room.name}</h4>
            {room.description && (
              <p className="text-sm text-gray-500 mt-1">{room.description}</p>
            )}
          </div>
          
          <div className="flex items-center space-x-4 text-sm text-gray-500">
            <div className="flex items-center space-x-1">
              <Users className="w-4 h-4" />
              <span>{participants.length} members</span>
            </div>
            <div className="flex items-center space-x-1">
              <span className="capitalize">{room.room_type}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200">
        <button
          onClick={() => setActiveTab('members')}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === 'members'
              ? 'text-fuchsia-600 border-b-2 border-fuchsia-600 bg-fuchsia-50'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          <div className="flex items-center justify-center space-x-2">
            <Users className="w-4 h-4" />
            <span>Members</span>
          </div>
        </button>
        <button
          onClick={() => setActiveTab('settings')}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === 'settings'
              ? 'text-fuchsia-600 border-b-2 border-fuchsia-600 bg-fuchsia-50'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          <div className="flex items-center justify-center space-x-2">
            <Settings className="w-4 h-4" />
            <span>Settings</span>
          </div>
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'members' && (
          <div className="p-4">
            <div className="flex items-center justify-between mb-4">
              <h4 className="font-medium text-gray-900">Members ({participants.length})</h4>
              <button className="p-1 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100 transition-colors">
                <UserPlus className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3">
              {participants.map((participant) => (
                <div
                  key={participant.id}
                  className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  {/* Avatar */}
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-medium">
                    {participant.user_name?.charAt(0).toUpperCase() || '?'}
                  </div>

                  {/* User Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {participant.user_name}
                      </p>
                      {getRoleIcon(participant.role)}
                    </div>
                    <p className="text-xs text-gray-500 truncate">
                      {participant.user_email}
                    </p>
                  </div>

                  {/* Role Badge */}
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getRoleColor(participant.role)}`}>
                    {participant.role}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="p-4 space-y-4">
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Room Settings</h4>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900">Notifications</p>
                    <p className="text-xs text-gray-500">Get notified about new messages</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" className="sr-only peer" defaultChecked />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-fuchsia-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-fuchsia-600"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900">Mute Room</p>
                    <p className="text-xs text-gray-500">Hide notifications from this room</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" className="sr-only peer" />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-fuchsia-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-fuchsia-600"></div>
                  </label>
                </div>
              </div>
            </div>

            <div className="border-t border-gray-200 pt-4">
              <h4 className="font-medium text-gray-900 mb-3">Danger Zone</h4>
              
              <div className="space-y-2">
                <button className="w-full text-left px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                  Leave Room
                </button>
                {room.room_type === 'group' && (
                  <button className="w-full text-left px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                    Delete Room
                  </button>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatSidebar;
