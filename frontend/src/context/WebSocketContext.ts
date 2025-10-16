import { useEffect, useRef, useCallback } from 'react';
import type { WebSocketMessage, Alert } from '../types';
import { useAlertStore } from './AlertContext';
import { useWebSocketStore } from './WebSocketStore';
import toast from 'react-hot-toast';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

export const useWebSocket = (onMessage?: (message: WebSocketMessage) => void) => {
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<number | undefined>(undefined);
  const { addAlert } = useAlertStore();
  const { setConnected } = useWebSocketStore();

  const connect = useCallback(() => {
    try {
      ws.current = new WebSocket(WS_URL);

      ws.current.onopen = () => {
        console.log('WebSocket connected');
        setConnected(true);
        // Removed toast notification - status shown in navbar instead
      };

      ws.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          
          // Handle alerts
          if (message.type === 'alert' && 'severity' in message.data && 'message' in message.data) {
            const alert = message.data as any;
            addAlert(alert);
            
            // Show toast notification based on severity
            if (alert.severity === 'critical') {
              toast.error(alert.message, { duration: 10000 });
            } else if (alert.severity === 'high') {
              toast.error(alert.message, { duration: 5000 });
            } else if (alert.severity === 'medium') {
              toast(alert.message, { icon: '⚠️' });
            }
          }

          // Call custom handler
          if (onMessage) {
            onMessage(message);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.current.onclose = () => {
        console.log('WebSocket disconnected');
        setConnected(false);
        // Removed toast notification - status shown in navbar instead
        
        // Attempt to reconnect after 5 seconds
        reconnectTimeout.current = setTimeout(() => {
          console.log('Attempting to reconnect...');
          connect();
        }, 5000);
      };
    } catch (error) {
      console.error('Error creating WebSocket:', error);
    }
  }, [addAlert, onMessage, setConnected]);

  const disconnect = useCallback(() => {
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
    }
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected');
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    sendMessage,
    disconnect,
    reconnect: connect,
    isConnected: ws.current?.readyState === WebSocket.OPEN,
  };
};
