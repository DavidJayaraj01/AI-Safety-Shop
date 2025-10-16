import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';

type Mode = 'shop-floor' | 'heavy-industry';

interface AlertThresholds {
  warning: number;
  danger: number;
}

interface ModeConfig {
  name: string;
  description: string;
  primarySensors: string[];
  alertThresholds: Record<string, AlertThresholds>;
  features: Record<string, boolean>;
  colors: {
    primary: string;
    accent: string;
  };
}

interface ModeContextType {
  mode: Mode;
  setMode: (mode: Mode) => void;
  toggleMode: () => void;
  isDarkMode: boolean;
  setIsDarkMode: (isDark: boolean) => void;
  toggleDarkMode: () => void;
  modeConfig: ModeConfig;
}

const ModeContext = createContext<ModeContextType | undefined>(undefined);

export const useModeContext = (): ModeContextType => {
  const context = useContext(ModeContext);
  if (!context) {
    throw new Error('useModeContext must be used within a ModeProvider');
  }
  return context;
};

interface ModeProviderProps {
  children: ReactNode;
}

export const ModeProvider: React.FC<ModeProviderProps> = ({ children }) => {
  const [mode, setMode] = useState<Mode>('shop-floor');
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    const savedMode = localStorage.getItem('safety-mode') as Mode | null;
    const savedTheme = localStorage.getItem('theme-mode');
    
    if (savedMode && (savedMode === 'shop-floor' || savedMode === 'heavy-industry')) {
      setMode(savedMode);
    }
    
    if (savedTheme) {
      setIsDarkMode(savedTheme === 'dark');
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('safety-mode', mode);
    localStorage.setItem('theme-mode', isDarkMode ? 'dark' : 'light');
    
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [mode, isDarkMode]);

  const toggleMode = () => {
    setMode(prevMode => 
      prevMode === 'shop-floor' ? 'heavy-industry' : 'shop-floor'
    );
  };

  const toggleDarkMode = () => {
    setIsDarkMode(prev => !prev);
  };

  const getModeConfig = (): ModeConfig => {
    if (mode === 'heavy-industry') {
      return {
        name: 'Heavy Industry Mode',
        description: 'Gas leaks, vibration alerts, auto-shutdown',
        primarySensors: ['gas', 'temperature', 'vibration', 'ultrasonic'],
        alertThresholds: {
          gas: { warning: 50, danger: 100 },
          temperature: { warning: 60, danger: 80 },
          vibration: { warning: 5, danger: 10 },
          ultrasonic: { warning: 30, danger: 10 }
        },
        features: {
          autoShutdown: true,
          gasDetection: true,
          vibrationMonitoring: true,
          temperatureAlerts: true
        },
        colors: {
          primary: 'orange',
          accent: 'red'
        }
      };
    } else {
      return {
        name: 'Shop Floor Mode',
        description: 'PPE, proximity, posture/fall alerts',
        primarySensors: ['rfid', 'ultrasonic', 'environmental', 'temperature'],
        alertThresholds: {
          rfid: { warning: 1, danger: 0 },
          ultrasonic: { warning: 50, danger: 20 },
          environmental: { warning: 70, danger: 85 },
          temperature: { warning: 30, danger: 40 }
        },
        features: {
          ppeDetection: true,
          proximityAlerts: true,
          fallDetection: true,
          accessControl: true
        },
        colors: {
          primary: 'blue',
          accent: 'green'
        }
      };
    }
  };

  const value: ModeContextType = {
    mode,
    setMode,
    toggleMode,
    isDarkMode,
    setIsDarkMode,
    toggleDarkMode,
    modeConfig: getModeConfig(),
  };

  return (
    <ModeContext.Provider value={value}>
      {children}
    </ModeContext.Provider>
  );
};

export default ModeContext;
