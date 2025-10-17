import { create } from 'zustand';
import { SensorResponse } from '../types/api';
import { apiService } from '../services/api';
import { USE_MOCK_DATA } from '../constants/theme';

interface ChartDataPoint {
  timestamp: string;
  temperature: number;
  humidity: number;
  gas: number;
  ultrasonic: number;
}

interface SensorStore {
  sensorData: SensorResponse | null;
  chartData: ChartDataPoint[];
  loading: boolean;
  error: string | null;
  lastUpdated: Date | null;
  isOffline: boolean;
  fetchSensorData: () => Promise<void>;
  addChartDataPoint: (data: SensorResponse) => void;
  setOffline: (offline: boolean) => void;
  clearError: () => void;
}

export const useSensorStore = create<SensorStore>((set, get) => ({
  sensorData: null,
  chartData: [],
  loading: false,
  error: null,
  lastUpdated: null,
  isOffline: false,

  fetchSensorData: async () => {
    set({ loading: true, error: null });
    try {
      const data = await apiService.getSensorData();
      const state = get();
      
      set({
        sensorData: data,
        loading: false,
        lastUpdated: new Date(),
        isOffline: false,
      });

      // Add to chart data
      state.addChartDataPoint(data);
    } catch (error) {
      // Don't show offline error if using mock data
      if (!USE_MOCK_DATA) {
        set({
          loading: false,
          error: error instanceof Error ? error.message : 'Failed to fetch sensor data',
          isOffline: true,
        });
      } else {
        set({ loading: false });
      }
    }
  },

  addChartDataPoint: (data: SensorResponse) => {
    const state = get();
    const newPoint: ChartDataPoint = {
      timestamp: data.timestamp,
      temperature: data.sensors.temperature.value,
      humidity: data.sensors.humidity.value,
      gas: data.sensors.gas.value,
      ultrasonic: data.sensors.ultrasonic.value,
    };

    const updatedChartData = [...state.chartData, newPoint];
    // Keep only last 20 points
    if (updatedChartData.length > 20) {
      updatedChartData.shift();
    }

    set({ chartData: updatedChartData });
  },

  setOffline: (offline: boolean) => set({ isOffline: offline }),
  
  clearError: () => set({ error: null }),
}));
