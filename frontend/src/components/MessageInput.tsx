import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, Smile, X } from 'lucide-react';

interface MessageInputProps {
  onSendMessage: (content: string, messageType?: string, replyToId?: number) => void;
  onTyping?: (isTyping: boolean) => void;
  disabled?: boolean;
  placeholder?: string;
  replyTo?: {
    id: number;
    content: string;
    senderName: string;
  };
  onCancelReply?: () => void;
}

const MessageInput: React.FC<MessageInputProps> = ({
  onSendMessage,
  onTyping,
  disabled = false,
  placeholder = "Type a message...",
  replyTo,
  onCancelReply
}) => {
  const [message, setMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  // Handle typing indicators
  useEffect(() => {
    if (message.trim() && !isTyping) {
      setIsTyping(true);
      onTyping?.(true);
    } else if (!message.trim() && isTyping) {
      setIsTyping(false);
      onTyping?.(false);
    }

    // Clear existing timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    // Set new timeout to stop typing indicator
    if (message.trim()) {
      typingTimeoutRef.current = setTimeout(() => {
        setIsTyping(false);
        onTyping?.(false);
      }, 1000);
    }

    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    };
  }, [message, isTyping, onTyping]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!message.trim() || disabled) return;

    onSendMessage(message.trim(), 'text', replyTo?.id);
    setMessage('');
    
    // Stop typing indicator
    if (isTyping) {
      setIsTyping(false);
      onTyping?.(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleFileUpload = () => {
    // TODO: Implement file upload
    // file upload clicked
  };

  const handleEmojiClick = () => {
    // TODO: Implement emoji picker
    // emoji picker clicked
  };

  return (
    <div className="border-t border-gray-200 bg-white p-4">
      {/* Reply Preview */}
      {replyTo && (
        <div className="mb-3 p-3 bg-gray-50 rounded-lg border-l-4 border-fuchsia-500">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="text-sm font-medium text-gray-700 mb-1">
                Replying to {replyTo.senderName}
              </div>
              <div className="text-sm text-gray-600 truncate">
                {replyTo.content}
              </div>
            </div>
            <button
              onClick={onCancelReply}
              className="p-1 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-200 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Message Input */}
      <form onSubmit={handleSubmit} className="flex items-end space-x-3">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-2xl resize-none focus:outline-none focus:ring-2 focus:ring-fuchsia-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            rows={1}
            style={{ minHeight: '48px', maxHeight: '120px' }}
          />
          
          {/* Input Actions */}
          <div className="absolute right-3 bottom-3 flex items-center space-x-1">
            <button
              type="button"
              onClick={handleEmojiClick}
              className="p-1 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100 transition-colors"
              disabled={disabled}
            >
              <Smile className="w-5 h-5" />
            </button>
            <button
              type="button"
              onClick={handleFileUpload}
              className="p-1 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100 transition-colors"
              disabled={disabled}
            >
              <Paperclip className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Send Button */}
        <button
          type="submit"
          disabled={!message.trim() || disabled}
          className="p-3 bg-gradient-to-r from-fuchsia-600 to-pink-500 text-white rounded-full hover:from-fuchsia-700 hover:to-pink-600 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105 disabled:hover:scale-100"
        >
          <Send className="w-5 h-5" />
        </button>
      </form>

      {/* Typing Indicator */}
      {isTyping && (
        <div className="mt-2 text-sm text-gray-500">
          Typing...
        </div>
      )}

      {/* Connection Status */}
      {disabled && (
        <div className="mt-2 text-sm text-red-500">
          Disconnected - messages will be sent when connection is restored
        </div>
      )}
    </div>
  );
};

export default MessageInput;
