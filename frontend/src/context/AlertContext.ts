import { create } from 'zustand';
import type { Alert } from '../types';

interface AlertStore {
  alerts: Alert[];
  unreadCount: number;
  addAlert: (alert: Alert) => void;
  removeAlert: (id: string) => void;
  markAsRead: (id: string) => void;
  clearAll: () => void;
  setAlerts: (alerts: Alert[]) => void;
}

export const useAlertStore = create<AlertStore>((set) => ({
  alerts: [],
  unreadCount: 0,
  addAlert: (alert) =>
    set((state) => ({
      alerts: [alert, ...state.alerts],
      unreadCount: state.unreadCount + 1,
    })),
  removeAlert: (id) =>
    set((state) => ({
      alerts: state.alerts.filter((a) => a.id !== id),
    })),
  markAsRead: (id) =>
    set((state) => {
      const alert = state.alerts.find((a) => a.id === id);
      if (alert && alert.resolved === false) {
        return {
          alerts: state.alerts.map((a) =>
            a.id === id ? { ...a, resolved: true } : a
          ),
          unreadCount: Math.max(0, state.unreadCount - 1),
        };
      }
      return state;
    }),
  clearAll: () => set({ alerts: [], unreadCount: 0 }),
  setAlerts: (alerts) =>
    set({
      alerts,
      unreadCount: alerts.filter((a) => !a.resolved).length,
    }),
}));
