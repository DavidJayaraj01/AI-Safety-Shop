import { create } from 'zustand';

interface WebSocketStore {
  isConnected: boolean;
  setConnected: (connected: boolean) => void;
}

export const useWebSocketStore = create<WebSocketStore>((set) => ({
  isConnected: false,
  setConnected: (connected) => set({ isConnected: connected }),
}));
