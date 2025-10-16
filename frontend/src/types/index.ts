// Sensor Types
export type SensorType = 'gas' | 'temperature' | 'vibration' | 'ultrasonic' | 'rfid' | 'environmental';

export interface SensorReading {
  id: string;
  sensorId: string;
  type: SensorType;
  value: number;
  unit: string;
  timestamp: string;
  location: string;
  status: 'normal' | 'warning' | 'critical';
}

export interface Sensor {
  id: string;
  name: string;
  type: SensorType;
  location: string;
  status: 'active' | 'inactive' | 'maintenance';
  lastReading: SensorReading | null;
  thresholds: {
    warning: number;
    critical: number;
  };
}

// Alert Types
export type AlertSeverity = 'low' | 'medium' | 'high' | 'critical';
export type AlertType = 'ppe_violation' | 'gas_leak' | 'high_temperature' | 'vibration_anomaly' | 'proximity_warning' | 'fall_detected' | 'equipment_fault' | 'unauthorized_access';

export interface Alert {
  id: string;
  type: AlertType;
  severity: AlertSeverity;
  message: string;
  timestamp: string;
  workerId?: string;
  sensorId?: string;
  location: string;
  resolved: boolean;
  resolvedAt?: string;
  resolvedBy?: string;
  actions: string[];
}

// PPE Detection Types
export interface PPEItem {
  type: 'helmet' | 'vest' | 'gloves' | 'goggles' | 'safety_shoes';
  detected: boolean;
  confidence: number;
  boundingBox?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

export interface PPEDetection {
  id: string;
  workerId: string;
  timestamp: string;
  items: PPEItem[];
  overallCompliance: boolean;
  confidence: number;
  imageUrl?: string;
}

// Worker Types
export interface Worker {
  id: string;
  name: string;
  role: string;
  department: string;
  assignedArea: string;
  photoUrl?: string;
  status: 'active' | 'on_break' | 'offline';
  lastSeen: string;
  ppeCompliance: boolean;
  location: {
    x: number;
    y: number;
    zone: string;
  };
}

// RFID Types
export interface RFIDEvent {
  id: string;
  workerId: string;
  workerName: string;
  eventType: 'entry' | 'exit';
  location: string;
  timestamp: string;
  accessGranted: boolean;
}

// Incident Types
export interface Incident {
  id: string;
  type: AlertType;
  severity: AlertSeverity;
  description: string;
  timestamp: string;
  location: string;
  workersInvolved: string[];
  sensorsInvolved: string[];
  actionsTaken: string[];
  status: 'open' | 'investigating' | 'resolved' | 'false_alarm';
  reportedBy: string;
  resolvedBy?: string;
  resolvedAt?: string;
  images?: string[];
  videoUrl?: string;
}

// Anomaly Detection Types
export interface AnomalyPrediction {
  id: string;
  sensorId: string;
  type: SensorType;
  predictedValue: number;
  currentValue: number;
  confidence: number;
  timestamp: string;
  forecastMinutes: number;
  anomalyType: 'spike' | 'drop' | 'trend_change' | 'pattern_break';
  severity: AlertSeverity;
  recommendation: string;
}

// Operating Mode Types
export type OperatingMode = 'heavy_industry' | 'shop_floor';

export interface ModeConfig {
  mode: OperatingMode;
  features: {
    gasDetection: boolean;
    vibrationMonitoring: boolean;
    ppeDetection: boolean;
    proximityAlerts: boolean;
    fallDetection: boolean;
    autoShutdown: boolean;
  };
  thresholds: {
    gas: number;
    temperature: number;
    vibration: number;
    proximity: number;
  };
}

// Analytics Types
export interface AnalyticsData {
  totalAlerts: number;
  criticalAlerts: number;
  resolvedAlerts: number;
  averageResponseTime: number;
  ppeComplianceRate: number;
  activeWorkers: number;
  activeSensors: number;
  incidentsToday: number;
  timeRange: 'today' | 'week' | 'month' | 'year';
}

// Chart Data Types
export interface ChartDataPoint {
  timestamp: string;
  value: number;
  label?: string;
}

// WebSocket Message Types
export interface WebSocketMessage {
  type: 'sensor_update' | 'alert' | 'ppe_detection' | 'rfid_event' | 'anomaly_prediction';
  data: SensorReading | Alert | PPEDetection | RFIDEvent | AnomalyPrediction;
  timestamp: string;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// Settings Types
export interface SystemSettings {
  notifications: {
    email: boolean;
    sms: boolean;
    telegram: boolean;
    slack: boolean;
    inApp: boolean;
  };
  thresholds: {
    gas: {
      warning: number;
      critical: number;
    };
    temperature: {
      warning: number;
      critical: number;
    };
    vibration: {
      warning: number;
      critical: number;
    };
  };
  autoShutdown: boolean;
  alertCooldown: number; // minutes
  ppeConfidenceThreshold: number;
  cameraSettings: {
    enabled: boolean;
    fps: number;
    resolution: string;
  };
}
