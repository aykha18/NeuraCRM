import { useEffect, useRef, useState, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';

export interface WebSocketMessage {
  type: string;
  content?: string;
  room_id?: number;
  is_typing?: boolean;
  message_type?: string;
  reply_to_id?: number;
  [key: string]: any;
}

export interface UseWebSocketOptions {
  roomId?: number;
  onMessage?: (message: WebSocketMessage) => void;
  onError?: (error: Event) => void;
  onOpen?: () => void;
  onClose?: () => void;
}

export const useWebSocket = (options: UseWebSocketOptions = {}) => {
  const { roomId, onMessage, onError, onOpen, onClose } = options;
  const { getAuthToken } = useAuth();
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      const token = getAuthToken();
      if (!token) {
        setConnectionError('No authentication token available');
        return;
      }

      const wsUrl = `ws://localhost:8000/ws/chat/${roomId || 0}?token=${encodeURIComponent(token)}`;
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        setIsConnected(true);
        setConnectionError(null);
        reconnectAttempts.current = 0;
        onOpen?.();
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          onMessage?.(message);
        } catch (error) {
          // failed to parse WebSocket message
        }
      };

      ws.onerror = (error) => {
        setConnectionError('WebSocket connection error');
        onError?.(error);
      };

      ws.onclose = (event) => {
        setIsConnected(false);
        onClose?.();

        // Attempt to reconnect if not a normal closure
        if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttempts.current++;
            connect();
          }, delay);
        }
      };

      wsRef.current = ws;
    } catch (error) {
      setConnectionError('Failed to create WebSocket connection');
    }
  }, [roomId, getAuthToken, onMessage, onError, onOpen, onClose]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.close(1000, 'User disconnected');
      wsRef.current = null;
    }
    
    setIsConnected(false);
  }, []);

  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      // websocket not connected
    }
  }, []);

  const sendChatMessage = useCallback((content: string, messageType: string = 'text', replyToId?: number) => {
    sendMessage({
      type: 'message',
      content,
      message_type: messageType,
      reply_to_id: replyToId
    });
  }, [sendMessage]);

  const sendTypingIndicator = useCallback((isTyping: boolean) => {
    sendMessage({
      type: 'typing',
      is_typing: isTyping
    });
  }, [sendMessage]);

  const joinRoom = useCallback((newRoomId: number) => {
    sendMessage({
      type: 'join_room',
      room_id: newRoomId
    });
  }, [sendMessage]);

  const leaveRoom = useCallback((roomIdToLeave: number) => {
    sendMessage({
      type: 'leave_room',
      room_id: roomIdToLeave
    });
  }, [sendMessage]);

  // Connect when roomId changes or component mounts
  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    isConnected,
    connectionError,
    sendMessage,
    sendChatMessage,
    sendTypingIndicator,
    joinRoom,
    leaveRoom,
    connect,
    disconnect
  };
};