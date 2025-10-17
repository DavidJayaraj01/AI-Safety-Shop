import { create } from 'zustand';
import { Settings } from '../types/api';
import { apiService } from '../services/api';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface SettingsStore {
  settings: Settings;
  loading: boolean;
  error: string | null;
  fetchSettings: () => Promise<void>;
  updateSettings: (settings: Partial<Settings>) => Promise<void>;
  toggleTheme: () => void;
  saveSettingsLocally: () => Promise<void>;
  loadSettingsLocally: () => Promise<void>;
  resetSettings: () => Promise<void>;
  clearError: () => void;
}

const defaultSettings: Settings = {
  theme: 'auto',
  notifications_enabled: true,
  refresh_interval: 15000,
  thresholds: {
    temperature: { min: 15, max: 35 },
    humidity: { min: 30, max: 80 },
    gas: { max: 300 },
    ultrasonic: { min: 50 },
  },
};

export const useSettingsStore = create<SettingsStore>((set, get) => ({
  settings: defaultSettings,
  loading: false,
  error: null,

  fetchSettings: async () => {
    set({ loading: true, error: null });
    try {
      const settings = await apiService.getSettings();
      set({ settings, loading: false });
      await get().saveSettingsLocally();
    } catch (error) {
      set({
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to fetch settings',
      });
      // Load from local storage if API fails
      await get().loadSettingsLocally();
    }
  },

  updateSettings: async (newSettings: Partial<Settings>) => {
    set({ loading: true, error: null });
    try {
      const state = get();
      const updatedSettings = { 
        ...state.settings, 
        ...newSettings,
        // Ensure boolean values are properly cast
        notifications_enabled: newSettings.notifications_enabled !== undefined 
          ? Boolean(newSettings.notifications_enabled) 
          : state.settings.notifications_enabled,
      };
      
      try {
        const savedSettings = await apiService.updateSettings(newSettings);
        set({ settings: savedSettings, loading: false });
      } catch (apiError) {
        // If API call fails, update locally
        set({ settings: updatedSettings, loading: false });
      }
      
      await get().saveSettingsLocally();
    } catch (error) {
      set({
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to update settings',
      });
    }
  },

  toggleTheme: () => {
    const state = get();
    const themes: Array<'light' | 'dark' | 'auto'> = ['light', 'dark', 'auto'];
    const currentIndex = themes.indexOf(state.settings.theme);
    const nextIndex = (currentIndex + 1) % themes.length;
    const newTheme = themes[nextIndex];
    
    set({
      settings: { ...state.settings, theme: newTheme },
    });
    
    get().saveSettingsLocally();
  },

  saveSettingsLocally: async () => {
    try {
      const state = get();
      await AsyncStorage.setItem('settings', JSON.stringify(state.settings));
    } catch (error) {
      console.error('Failed to save settings locally:', error);
    }
  },

  loadSettingsLocally: async () => {
    try {
      const settingsJson = await AsyncStorage.getItem('settings');
      if (settingsJson) {
        const parsedSettings = JSON.parse(settingsJson);
        // Ensure proper type casting for boolean values
        const settings: Settings = {
          ...parsedSettings,
          notifications_enabled: Boolean(parsedSettings.notifications_enabled),
          refresh_interval: Number(parsedSettings.refresh_interval) || 15000,
        };
        set({ settings });
      }
    } catch (error) {
      console.error('Failed to load settings locally:', error);
      // Reset to default settings on error
      set({ settings: defaultSettings });
    }
  },

  resetSettings: async () => {
    try {
      await AsyncStorage.removeItem('settings');
      set({ settings: defaultSettings });
    } catch (error) {
      console.error('Failed to reset settings:', error);
    }
  },

  clearError: () => set({ error: null }),
}));
