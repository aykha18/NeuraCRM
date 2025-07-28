import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, X, Sparkles } from 'lucide-react';
import { sendAIMessage, type ChatMessage } from '../services/ai';

interface AISidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const AISidebar: React.FC<AISidebarProps> = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      message: '',
      response: "Hello! I'm your AI Sales Assistant. I can help you with:\n\n• Analyzing your deals and pipeline\n• Finding your hottest leads\n• Suggesting follow-up actions\n• Answering questions about your CRM data\n\nWhat would you like to know?",
      timestamp: new Date(),
      isUser: false
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setIsLoading(true);

    // Add user message
    const newUserMessage: ChatMessage = {
      id: Date.now().toString(),
      message: userMessage,
      response: '',
      timestamp: new Date(),
      isUser: true
    };

    setMessages(prev => [...prev, newUserMessage]);

    try {
      // Send to AI
      const response = await sendAIMessage({
        message: userMessage,
        user_id: 1 // TODO: Get from auth context
      });

      // Add AI response
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        message: '',
        response: response.response,
        timestamp: new Date(),
        isUser: false
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      // Add error message
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        message: '',
        response: "Sorry, I'm having trouble connecting right now. Please try again in a moment.",
        timestamp: new Date(),
        isUser: false
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-white shadow-2xl border-l border-gray-200 flex flex-col z-50">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-white/20 rounded-lg">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-semibold">AI Sales Assistant</h3>
            <p className="text-sm text-blue-100">Powered by AI</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-2 hover:bg-white/20 rounded-lg transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div key={message.id} className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-xs lg:max-w-md ${message.isUser ? 'order-2' : 'order-1'}`}>
              <div className={`flex items-start space-x-2 ${message.isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  message.isUser 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-gradient-to-r from-blue-500 to-purple-500 text-white'
                }`}>
                  {message.isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                </div>
                <div className={`flex-1 ${message.isUser ? 'text-right' : ''}`}>
                  <div className={`inline-block px-4 py-2 rounded-lg ${
                    message.isUser
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    <div className="whitespace-pre-wrap text-sm">
                      {message.isUser ? message.message : message.response}
                    </div>
                  </div>
                  <div className={`text-xs text-gray-500 mt-1 ${message.isUser ? 'text-right' : ''}`}>
                    {formatTime(message.timestamp)}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {/* Loading indicator */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="max-w-xs lg:max-w-md">
              <div className="flex items-start space-x-2">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-white" />
                </div>
                <div className="flex-1">
                  <div className="inline-block px-4 py-2 rounded-lg bg-gray-100">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <div className="flex space-x-2">
          <div className="flex-1 relative">
            <input
              ref={inputRef}
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about your sales data..."
              className="w-full px-4 py-2 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              disabled={isLoading}
            />
            <div className="absolute right-3 top-2.5">
              <Sparkles className="w-4 h-4 text-gray-400" />
            </div>
          </div>
          <button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center space-x-2"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2 text-center">
          Press Enter to send • Shift+Enter for new line
        </p>
      </div>
    </div>
  );
};

export default AISidebar; 