import { create } from 'zustand';
import type { OperatingMode, ModeConfig } from '../types';

interface ModeStore {
  mode: OperatingMode;
  config: ModeConfig;
  setMode: (mode: OperatingMode) => void;
  updateConfig: (config: Partial<ModeConfig>) => void;
}

export const useModeStore = create<ModeStore>((set) => ({
  mode: 'shop_floor',
  config: {
    mode: 'shop_floor',
    features: {
      gasDetection: true,
      vibrationMonitoring: true,
      ppeDetection: true,
      proximityAlerts: true,
      fallDetection: true,
      autoShutdown: false,
    },
    thresholds: {
      gas: 400,
      temperature: 50,
      vibration: 10,
      proximity: 100,
    },
  },
  setMode: (mode) =>
    set((state) => {
      const features =
        mode === 'heavy_industry'
          ? {
              gasDetection: true,
              vibrationMonitoring: true,
              ppeDetection: false,
              proximityAlerts: true,
              fallDetection: false,
              autoShutdown: true,
            }
          : {
              gasDetection: true,
              vibrationMonitoring: true,
              ppeDetection: true,
              proximityAlerts: true,
              fallDetection: true,
              autoShutdown: false,
            };

      return {
        mode,
        config: { ...state.config, mode, features },
      };
    }),
  updateConfig: (config) =>
    set((state) => ({
      config: { ...state.config, ...config },
    })),
}));
