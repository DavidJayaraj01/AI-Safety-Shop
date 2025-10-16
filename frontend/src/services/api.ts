import axios from 'axios';
import type {
  Sensor,
  SensorReading,
  Alert,
  Worker,
  PPEDetection,
  RFIDEvent,
  Incident,
  AnomalyPrediction,
  AnalyticsData,
  SystemSettings,
  ModeConfig,
  ApiResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptors for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Sensor APIs
export const sensorAPI = {
  getAll: () => api.get<ApiResponse<Sensor[]>>('/sensors'),
  getById: (id: string) => api.get<ApiResponse<Sensor>>(`/sensors/${id}`),
  getReadings: (sensorId: string, limit = 100) =>
    api.get<ApiResponse<SensorReading[]>>(`/sensors/${sensorId}/readings`, {
      params: { limit },
    }),
  getLatestReadings: () => api.get<ApiResponse<SensorReading[]>>('/sensors/readings/latest'),
};

// Alert APIs
export const alertAPI = {
  getAll: (params?: { severity?: string; resolved?: boolean; limit?: number }) =>
    api.get<ApiResponse<Alert[]>>('/alerts', { params }),
  getById: (id: string) => api.get<ApiResponse<Alert>>(`/alerts/${id}`),
  resolve: (id: string, data: { resolvedBy: string; actions: string[] }) =>
    api.put<ApiResponse<Alert>>(`/alerts/${id}/resolve`, data),
  create: (alert: Omit<Alert, 'id' | 'timestamp' | 'resolved'>) =>
    api.post<ApiResponse<Alert>>('/alerts', alert),
};

// Worker APIs
export const workerAPI = {
  getAll: () => api.get<ApiResponse<Worker[]>>('/workers'),
  getById: (id: string) => api.get<ApiResponse<Worker>>(`/workers/${id}`),
  getActive: () => api.get<ApiResponse<Worker[]>>('/workers/active'),
  updateLocation: (id: string, location: { x: number; y: number; zone: string }) =>
    api.put<ApiResponse<Worker>>(`/workers/${id}/location`, location),
};

// PPE Detection APIs
export const ppeAPI = {
  getLatest: () => api.get<ApiResponse<PPEDetection[]>>('/ppe/detections/latest'),
  getByWorker: (workerId: string, limit = 50) =>
    api.get<ApiResponse<PPEDetection[]>>(`/ppe/detections/worker/${workerId}`, {
      params: { limit },
    }),
  getComplianceRate: (timeRange: string) =>
    api.get<ApiResponse<{ rate: number }>>('/ppe/compliance', {
      params: { timeRange },
    }),
};

// RFID APIs
export const rfidAPI = {
  getEvents: (limit = 100) =>
    api.get<ApiResponse<RFIDEvent[]>>('/rfid/events', { params: { limit } }),
  getByWorker: (workerId: string, limit = 50) =>
    api.get<ApiResponse<RFIDEvent[]>>(`/rfid/events/worker/${workerId}`, {
      params: { limit },
    }),
};

// Incident APIs
export const incidentAPI = {
  getAll: (params?: { status?: string; severity?: string; limit?: number }) =>
    api.get<ApiResponse<Incident[]>>('/incidents', { params }),
  getById: (id: string) => api.get<ApiResponse<Incident>>(`/incidents/${id}`),
  create: (incident: Omit<Incident, 'id' | 'timestamp'>) =>
    api.post<ApiResponse<Incident>>('/incidents', incident),
  update: (id: string, data: Partial<Incident>) =>
    api.put<ApiResponse<Incident>>(`/incidents/${id}`, data),
  exportPDF: (id: string) =>
    api.get(`/incidents/${id}/export`, { responseType: 'blob' }),
};

// Anomaly Detection APIs
export const anomalyAPI = {
  getPredictions: () => api.get<ApiResponse<AnomalyPrediction[]>>('/anomalies/predictions'),
  getBySensor: (sensorId: string) =>
    api.get<ApiResponse<AnomalyPrediction[]>>(`/anomalies/sensor/${sensorId}`),
  getForecasts: (sensorId: string, minutes: number) =>
    api.get<ApiResponse<AnomalyPrediction[]>>(`/anomalies/forecast/${sensorId}`, {
      params: { minutes },
    }),
};

// Analytics APIs
export const analyticsAPI = {
  getDashboard: (timeRange: string) =>
    api.get<ApiResponse<AnalyticsData>>('/analytics/dashboard', {
      params: { timeRange },
    }),
  getReport: (startDate: string, endDate: string) =>
    api.get<ApiResponse<any>>('/analytics/report', {
      params: { startDate, endDate },
    }),
  exportReport: (startDate: string, endDate: string) =>
    api.get('/analytics/export', {
      params: { startDate, endDate },
      responseType: 'blob',
    }),
};

// Settings APIs
export const settingsAPI = {
  get: () => api.get<ApiResponse<SystemSettings>>('/settings'),
  update: (settings: Partial<SystemSettings>) =>
    api.put<ApiResponse<SystemSettings>>('/settings', settings),
};

// Mode APIs
export const modeAPI = {
  getCurrent: () => api.get<ApiResponse<ModeConfig>>('/mode'),
  switch: (mode: 'heavy_industry' | 'shop_floor') =>
    api.post<ApiResponse<ModeConfig>>('/mode/switch', { mode }),
};

// Camera Feed APIs
export const cameraAPI = {
  getStreamUrl: () => `${API_BASE_URL}/camera/stream`,
  getSnapshot: () => api.get('/camera/snapshot', { responseType: 'blob' }),
  toggleDetection: (enabled: boolean) =>
    api.post<ApiResponse<{ enabled: boolean }>>('/camera/detection', { enabled }),
};

export default api;
