import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import toast from 'react-hot-toast';
import type { ToastPosition } from 'react-hot-toast';
import { alertsApi, createWebSocketConnection } from '../services/api';
import type { Alert } from '../types';

interface AlertContextType {
  alerts: Alert[];
  activeAlerts: Alert[];
  alertHistory: Alert[];
  isConnected: boolean;
  acknowledgeAlert: (alertId: string | number) => Promise<void>;
  dismissAlert: (alertId: string | number) => void;
  clearAllAlerts: () => void;
  loadAlerts: () => Promise<void>;
  loadAlertHistory: () => Promise<void>;
  getAlertCount: (severity: string) => number;
  getAlertsByType: (type: string) => Alert[];
  handleNewAlert: (alert: Alert) => void;
}

const AlertContext = createContext<AlertContextType | undefined>(undefined);

export const useAlertContext = (): AlertContextType => {
  const context = useContext(AlertContext);
  if (!context) {
    throw new Error('useAlertContext must be used within an AlertProvider');
  }
  return context;
};

interface AlertProviderProps {
  children: ReactNode;
}

export const AlertProvider: React.FC<AlertProviderProps> = ({ children }) => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [activeAlerts, setActiveAlerts] = useState<Alert[]>([]);
  const [alertHistory, setAlertHistory] = useState<Alert[]>([]);
  const [isConnected, setIsConnected] = useState<boolean>(false);

  // Initialize WebSocket connection
  useEffect(() => {
    const ws = createWebSocketConnection(
      handleWebSocketMessage,
      handleWebSocketError
    );

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  // Load initial alerts
  useEffect(() => {
    loadAlerts();
    loadAlertHistory();
  }, []);

  const handleWebSocketMessage = (data: any) => {
    setIsConnected(true);
    
    switch (data.type) {
      case 'sensor_data':
        // Handle real-time sensor data
        break;
      case 'alert':
        handleNewAlert(data.payload);
        break;
      case 'alert_resolved':
        handleAlertResolved(data.payload.alertId);
        break;
      default:
        console.log('Unknown WebSocket message type:', data.type);
    }
  };

  const handleWebSocketError = (_error: Event) => {
    setIsConnected(false);
    toast.error('Connection lost. Reconnecting...', {
      id: 'connection-error',
    });
  };

  const loadAlerts = async () => {
    try {
      const [allAlertsResponse, activeAlertsResponse] = await Promise.all([
        alertsApi.getAllAlerts(),
        alertsApi.getActiveAlerts()
      ]);
      
      setAlerts(allAlertsResponse.data);
      setActiveAlerts(activeAlertsResponse.data);
    } catch (error) {
      console.error('Error loading alerts:', error);
      toast.error('Failed to load alerts');
    }
  };

  const loadAlertHistory = async () => {
    try {
      const response = await alertsApi.getAlertHistory();
      setAlertHistory(response.data);
    } catch (error) {
      console.error('Error loading alert history:', error);
    }
  };

  const handleNewAlert = (alert: Alert) => {
    const newAlert: Alert = {
      ...alert,
      id: alert.id || Date.now(),
      timestamp: alert.timestamp || new Date().toISOString(),
    };

    setAlerts(prev => [newAlert, ...prev]);
    setActiveAlerts(prev => [newAlert, ...prev]);

    // Show toast notification based on severity
    const toastOptions: { duration: number; position: ToastPosition } = {
      duration: alert.severity === 'danger' ? 0 : 4000,
      position: 'top-right',
    };

    switch (alert.severity) {
      case 'danger':
        toast.error(`🚨 CRITICAL: ${alert.message}`, {
          ...toastOptions,
          id: `alert-${alert.id}`,
          style: {
            background: '#dc2626',
            color: 'white',
            fontWeight: 'bold',
          },
        });
        playAlertSound('danger');
        break;
      case 'warning':
        toast(() => (
          <div className="flex items-center">
            <span className="text-yellow-600 mr-2">⚠️</span>
            <span>{alert.message}</span>
          </div>
        ), {
          ...toastOptions,
          id: `alert-${alert.id}`,
          style: {
            background: '#f59e0b',
            color: 'white',
          },
        });
        playAlertSound('warning');
        break;
      case 'info':
        toast.success(`ℹ️ ${alert.message}`, {
          ...toastOptions,
          id: `alert-${alert.id}`,
        });
        break;
      default:
        toast(`📢 ${alert.message}`, toastOptions);
    }
  };

  const handleAlertResolved = (alertId: string | number) => {
    setActiveAlerts(prev => prev.filter(alert => alert.id !== alertId));
    setAlerts(prev => 
      prev.map(alert => 
        alert.id === alertId 
          ? { ...alert, status: 'resolved', resolvedAt: new Date().toISOString() }
          : alert
      )
    );
    toast.dismiss(`alert-${alertId}`);
  };

  const acknowledgeAlert = async (alertId: string | number) => {
    try {
      await alertsApi.acknowledgeAlert(alertId);
      setActiveAlerts(prev => 
        prev.map(alert => 
          alert.id === alertId 
            ? { ...alert, status: 'acknowledged', acknowledgedAt: new Date().toISOString() }
            : alert
        )
      );
      toast.dismiss(`alert-${alertId}`);
      toast.success('Alert acknowledged');
    } catch (error) {
      console.error('Error acknowledging alert:', error);
      toast.error('Failed to acknowledge alert');
    }
  };

  const dismissAlert = (alertId: string | number) => {
    toast.dismiss(`alert-${alertId}`);
  };

  const clearAllAlerts = () => {
    activeAlerts.forEach(alert => {
      toast.dismiss(`alert-${alert.id}`);
    });
    setActiveAlerts([]);
  };

  const playAlertSound = (severity: string) => {
    try {
      const audioContext = new AudioContext();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);

      const frequencies: Record<string, number[]> = {
        danger: [800, 1000, 800],
        warning: [600, 800],
        info: [400],
      };

      const freqs = frequencies[severity] || frequencies.info;
      let currentFreq = 0;

      const playFrequency = () => {
        if (currentFreq < freqs.length) {
          oscillator.frequency.setValueAtTime(freqs[currentFreq], audioContext.currentTime);
          gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
          gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
          
          currentFreq++;
          setTimeout(playFrequency, 300);
        } else {
          oscillator.stop();
        }
      };

      oscillator.start();
      playFrequency();
    } catch (error) {
      console.log('Audio not supported or blocked:', error);
    }
  };

  const getAlertCount = (severity: string): number => {
    return activeAlerts.filter(alert => alert.severity === severity).length;
  };

  const getAlertsByType = (type: string): Alert[] => {
    return alerts.filter(alert => alert.type === type);
  };

  const value: AlertContextType = {
    alerts,
    activeAlerts,
    alertHistory,
    isConnected,
    acknowledgeAlert,
    dismissAlert,
    clearAllAlerts,
    loadAlerts,
    loadAlertHistory,
    getAlertCount,
    getAlertsByType,
    handleNewAlert,
  };

  return (
    <AlertContext.Provider value={value}>
      {children}
    </AlertContext.Provider>
  );
};

export default AlertContext;
