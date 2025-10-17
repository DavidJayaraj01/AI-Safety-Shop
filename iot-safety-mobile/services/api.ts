import axios, { AxiosError } from 'axios';
import { API_BASE_URL, USE_MOCK_DATA } from '../constants/theme';
import { SensorResponse, Camera, Detection, ReportResponse, Settings } from '../types/api';
import { 
  getMockSensorData, 
  getMockCameras, 
  getMockDetections, 
  getMockReports, 
  getMockSettings 
} from './mockData';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Error handler
export const handleApiError = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError;
    if (axiosError.response) {
      return `Server error: ${axiosError.response.status}`;
    } else if (axiosError.request) {
      return 'Network error: Unable to reach server';
    }
  }
  return 'An unexpected error occurred';
};

// API Methods
export const apiService = {
  // Sensor endpoints
  getSensorData: async (): Promise<SensorResponse> => {
    if (USE_MOCK_DATA) {
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 500));
      return getMockSensorData();
    }
    
    try {
      const response = await api.get<SensorResponse>('/sensors/live/arduino');
      return response.data;
    } catch (error) {
      console.log('API failed, using mock data');
      return getMockSensorData();
    }
  },

  // Camera endpoints
  getCameras: async (): Promise<Camera[]> => {
    if (USE_MOCK_DATA) {
      await new Promise(resolve => setTimeout(resolve, 500));
      return getMockCameras();
    }
    
    try {
      const response = await api.get<Camera[]>('/cv/cameras');
      return response.data;
    } catch (error) {
      console.log('API failed, using mock data');
      return getMockCameras();
    }
  },

  getDetections: async (limit?: number): Promise<Detection[]> => {
    if (USE_MOCK_DATA) {
      await new Promise(resolve => setTimeout(resolve, 500));
      return getMockDetections();
    }
    
    try {
      const response = await api.get<Detection[]>('/cv/detections', {
        params: { limit: limit || 50 },
      });
      return response.data;
    } catch (error) {
      console.log('API failed, using mock data');
      return getMockDetections();
    }
  },

  acknowledgeDetection: async (detectionId: number): Promise<void> => {
    if (USE_MOCK_DATA) {
      await new Promise(resolve => setTimeout(resolve, 300));
      console.log(`Mock: Acknowledged detection ${detectionId}`);
      return;
    }
    
    try {
      await api.post(`/cv/detections/${detectionId}/acknowledge`);
    } catch (error) {
      console.log('API failed, using mock acknowledgment');
    }
  },

  // Reports endpoints
  getReports: async (period: 'day' | 'week' | 'month' = 'week'): Promise<ReportResponse> => {
    if (USE_MOCK_DATA) {
      await new Promise(resolve => setTimeout(resolve, 500));
      return getMockReports(period);
    }
    
    try {
      const response = await api.get<ReportResponse>('/reports', {
        params: { period },
      });
      return response.data;
    } catch (error) {
      console.log('API failed, using mock data');
      return getMockReports(period);
    }
  },

  // Settings endpoints
  getSettings: async (): Promise<Settings> => {
    if (USE_MOCK_DATA) {
      await new Promise(resolve => setTimeout(resolve, 500));
      return getMockSettings();
    }
    
    try {
      const response = await api.get<Settings>('/settings');
      // Ensure proper type casting for boolean values from API
      const data = response.data;
      return {
        ...data,
        notifications_enabled: Boolean(data.notifications_enabled),
        refresh_interval: Number(data.refresh_interval) || 15000,
      };
    } catch (error) {
      console.log('API failed, using mock data');
      return getMockSettings();
    }
  },

  updateSettings: async (settings: Partial<Settings>): Promise<Settings> => {
    if (USE_MOCK_DATA) {
      await new Promise(resolve => setTimeout(resolve, 500));
      return { ...getMockSettings(), ...settings };
    }
    
    try {
      const response = await api.put<Settings>('/settings', settings);
      // Ensure proper type casting for boolean values from API
      const data = response.data;
      return {
        ...data,
        notifications_enabled: Boolean(data.notifications_enabled),
        refresh_interval: Number(data.refresh_interval) || 15000,
      };
    } catch (error) {
      console.log('API failed, using mock data');
      return { ...getMockSettings(), ...settings };
    }
  },

  // Push notification endpoint
  registerDeviceToken: async (token: string): Promise<void> => {
    if (USE_MOCK_DATA) {
      console.log(`Mock: Registered device token ${token}`);
      return;
    }
    
    try {
      await api.post('/notifications/register', { token });
    } catch (error) {
      console.log('Failed to register device token');
    }
  },
};

export default api;
