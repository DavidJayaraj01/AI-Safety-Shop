import axios from 'axios';
import type { AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Arduino Sensors API (Real-time IoT data)
export const arduinoSensorsApi = {
  // Fetch live sensor data from Arduino via backend proxy (avoids CORS)
  getLiveSensorData: async () => {
    try {
      // Always use backend proxy to avoid CORS issues
      const proxyResponse = await api.get('/sensors/live/arduino');
      return { 
        data: proxyResponse.data.sensors, 
        status: proxyResponse.data.status,
        alerts: proxyResponse.data.alerts_triggered || []
      };
    } catch (error) {
      console.error('Arduino backend proxy error:', error);
      return { data: null, status: 'disconnected', error: error, alerts: [] };
    }
  },
  
  // Check Arduino status through backend
  getArduinoStatus: () => api.get('/api/arduino/status'),
  
  // Get parsed Arduino sensor data
  getArduinoSensors: () => api.get('/api/arduino/sensors'),
};

// Sensors API (Backend)
export const sensorsApi = {
  getAllSensors: () => api.get('/sensors'),
  getSensorData: (sensorType: string) => api.get(`/sensors/${sensorType}`),
  getSensorHistory: (sensorType?: string, hours: number = 24) => 
    sensorType 
      ? api.get(`/sensors/${sensorType}/history?hours=${hours}`)
      : api.get(`/sensors/history?hours=${hours}`),
  getRFIDLogs: (days: number = 7) => api.get(`/sensors/rfid/logs?days=${days}`),
  getStatistics: () => api.get('/sensors/statistics'),
  getLiveArduinoData: () => api.get('/sensors/live/arduino'),
};

// Alerts API
export const alertsApi = {
  getAllAlerts: () => api.get('/alerts'),
  getActiveAlerts: () => api.get('/alerts/active'),
  acknowledgeAlert: (alertId: string | number) => api.put(`/alerts/${alertId}/acknowledge`),
  getAlertHistory: (days: number = 7) => api.get(`/alerts/history?days=${days}`),
};

// Workers API
export const workersApi = {
  getAllWorkers: () => api.get('/workers'),
  getWorkerByRfid: (rfidTag: string) => api.get(`/workers/rfid/${rfidTag}`),
  getActiveWorkers: () => api.get('/workers/active'),
  getWorkerLogs: (days: number = 7) => api.get(`/workers/logs?days=${days}`),
};

// AI Detection API
export const aiApi = {
  getPredictions: () => api.get('/ai/predictions'),
  getAnomalies: () => api.get('/ai/anomalies'),
  getSafetyViolations: () => api.get('/ai/safety-violations'),
  detectPPE: (imageFile: File) => {
    const formData = new FormData();
    formData.append('image', imageFile);
    return api.post('/ai/detect-ppe', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

// Reports API
export const reportsApi = {
  getReport: (dateRange: string) => api.get(`/reports?range=${dateRange}`),
  getIncidentReport: () => api.get('/reports/incidents'),
};

// Settings API
export const settingsApi = {
  getSettings: () => api.get('/settings'),
  updateSettings: (settings: Record<string, any>) => api.put('/settings', settings),
  getThresholds: () => api.get('/settings/thresholds'),
  updateThresholds: (thresholds: Record<string, any>) => api.put('/settings/thresholds', thresholds),
};

// Dashboard API
export const dashboardApi = {
  getOverview: () => api.get('/dashboard/overview'),
  getSystemHealth: () => api.get('/dashboard/system-health'),
  getReports: (type: string = 'daily', period: number = 7) => 
    api.get(`/dashboard/reports?type=${type}&period=${period}`),
};

// CV Detection API
export const cvApi = {
  // Camera Management
  getAllCameras: () => api.get('/cv/cameras'),
  getCameraById: (cameraId: number) => api.get(`/cv/cameras/${cameraId}`),
  createCamera: (camera: Record<string, any>) => api.post('/cv/cameras', camera),
  updateCamera: (cameraId: number, updates: Record<string, any>) => 
    api.patch(`/cv/cameras/${cameraId}`, updates),
  deleteCamera: (cameraId: number) => api.delete(`/cv/cameras/${cameraId}`),
  
  // Detection Management
  getDetections: (params?: {
    camera_id?: number;
    detection_type?: string;
    violation_type?: string;
    acknowledged?: boolean;
    hours?: number;
  }) => api.get('/cv/detections', { params }),
  acknowledgeDetection: (detectionId: number) => 
    api.patch(`/cv/detections/${detectionId}/acknowledge`),
  simulateDetection: (cameraId: number) => 
    api.post(`/cv/detections/simulate/${cameraId}`),
  
  // Statistics & Analytics
  getCVStats: () => api.get('/cv/stats'),
  getDetectorStatus: () => api.get('/cv/detector/status'),
  analyzePPE: () => api.post('/cv/analyze/ppe'),
  analyzeHazardZones: () => api.post('/cv/analyze/hazard-zones'),
  analyzeUnsafeBehavior: () => api.post('/cv/analyze/unsafe-behavior'),
  
  // YOLO Image Detection
  uploadImageForDetection: (imageFile: File) => {
    const formData = new FormData();
    formData.append('file', imageFile);
    return api.post('/cv/detect/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  // Live Camera Streaming
  getLiveStreamUrl: (cameraId: number = 0) => 
    `${API_BASE_URL}/cv/stream/live?camera_id=${cameraId}`,
  getStreamStatus: () => api.get('/cv/stream/status'),
};

// WebSocket connection for real-time data
export const createWebSocketConnection = (
  onMessage: (data: any) => void, 
  onError?: (error: Event) => void
): WebSocket => {
  const wsUrl = API_BASE_URL.replace('http', 'ws');
  const ws = new WebSocket(`${wsUrl}/ws`);
  
  ws.onmessage = (event: MessageEvent) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  };
  
  ws.onerror = (error: Event) => {
    console.error('WebSocket error:', error);
    if (onError) onError(error);
  };
  
  ws.onclose = () => {
    console.log('WebSocket connection closed');
    setTimeout(() => {
      createWebSocketConnection(onMessage, onError);
    }, 5000);
  };
  
  return ws;
};

export default api;
