import React from 'react';
import { format } from 'date-fns';
import { Reply, MoreVertical } from 'lucide-react';
import type { ChatMessage } from '../services/chat';

interface MessageListProps {
  messages: ChatMessage[];
  currentUserId?: number;
  onReply?: (messageId: number) => void;
}

const MessageList: React.FC<MessageListProps> = ({ 
  messages, 
  currentUserId, 
  onReply 
}) => {
  const formatMessageTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
    
    if (diffInHours < 24) {
      return format(date, 'HH:mm');
    } else if (diffInHours < 24 * 7) {
      return format(date, 'EEE HH:mm');
    } else {
      return format(date, 'MMM dd, HH:mm');
    }
  };

  const formatMessageDate = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
    
    if (diffInDays === 0) {
      return 'Today';
    } else if (diffInDays === 1) {
      return 'Yesterday';
    } else if (diffInDays < 7) {
      return format(date, 'EEEE');
    } else {
      return format(date, 'MMMM dd, yyyy');
    }
  };

  const shouldShowDate = (currentMessage: ChatMessage, previousMessage?: ChatMessage) => {
    if (!previousMessage) return true;
    
    const currentDate = new Date(currentMessage.created_at).toDateString();
    const previousDate = new Date(previousMessage.created_at).toDateString();
    
    return currentDate !== previousDate;
  };

  const shouldShowAvatar = (currentMessage: ChatMessage, nextMessage?: ChatMessage) => {
    if (!nextMessage) return true;
    
    return (
      currentMessage.sender_id !== nextMessage.sender_id ||
      new Date(nextMessage.created_at).getTime() - new Date(currentMessage.created_at).getTime() > 5 * 60 * 1000 // 5 minutes
    );
  };

  const getMessageBubbleClass = (message: ChatMessage) => {
    const isOwn = message.sender_id === currentUserId;
    const baseClass = "max-w-xs lg:max-w-md px-4 py-2 rounded-2xl";
    
    if (isOwn) {
      return `${baseClass} bg-gradient-to-r from-fuchsia-600 to-pink-500 text-white ml-auto`;
    } else {
      return `${baseClass} bg-gray-100 text-gray-900`;
    }
  };

  const getAvatarClass = (message: ChatMessage) => {
    const isOwn = message.sender_id === currentUserId;
    return `w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium ${
      isOwn 
        ? 'bg-gradient-to-r from-fuchsia-600 to-pink-500' 
        : 'bg-gradient-to-r from-blue-500 to-purple-500'
    }`;
  };

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">💬</span>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No messages yet</h3>
          <p className="text-gray-500">Start the conversation by sending a message!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
      {messages.map((message, index) => {
        const previousMessage = index > 0 ? messages[index - 1] : undefined;
        const nextMessage = index < messages.length - 1 ? messages[index + 1] : undefined;
        const showDate = shouldShowDate(message, previousMessage);
        const showAvatar = shouldShowAvatar(message, nextMessage);
        const isOwn = message.sender_id === currentUserId;

        return (
          <div key={message.id}>
            {/* Date Separator */}
            {showDate && (
              <div className="flex items-center justify-center my-6">
                <div className="bg-gray-100 text-gray-600 text-sm px-3 py-1 rounded-full">
                  {formatMessageDate(message.created_at)}
                </div>
              </div>
            )}

            {/* Message */}
            <div className={`flex items-end space-x-2 ${isOwn ? 'flex-row-reverse space-x-reverse' : ''}`}>
              {/* Avatar */}
              {showAvatar ? (
                <div className={getAvatarClass(message)}>
                  {message.sender_name?.charAt(0).toUpperCase() || '?'}
                </div>
              ) : (
                <div className="w-8 h-8" /> // Spacer
              )}

              {/* Message Content */}
              <div className={`flex flex-col ${isOwn ? 'items-end' : 'items-start'}`}>
                {/* Sender Name (only for other users and when showing avatar) */}
                {!isOwn && showAvatar && (
                  <span className="text-sm font-medium text-gray-700 mb-1">
                    {message.sender_name}
                  </span>
                )}

                {/* Message Bubble */}
                <div className="group relative">
                  <div className={getMessageBubbleClass(message)}>
                    {message.reply_to_id && (
                      <div className="text-xs opacity-75 mb-1 border-l-2 border-current pl-2">
                        Replying to message
                      </div>
                    )}
                    <p className="text-sm whitespace-pre-wrap break-words">
                      {message.content}
                    </p>
                  </div>

                  {/* Message Actions */}
                  <div className={`absolute top-0 ${isOwn ? 'left-0 -translate-x-12' : 'right-0 translate-x-12'} opacity-0 group-hover:opacity-100 transition-opacity flex items-center space-x-1`}>
                    <button
                      onClick={() => onReply?.(message.id)}
                      className="p-1 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100 transition-colors"
                      title="Reply"
                    >
                      <Reply className="w-4 h-4" />
                    </button>
                    <button className="p-1 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100 transition-colors">
                      <MoreVertical className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Timestamp */}
                <span className="text-xs text-gray-500 mt-1">
                  {formatMessageTime(message.created_at)}
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default MessageList;