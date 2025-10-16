// Sensor Types
export interface Sensor {
  id: string;
  name: string;
  type: 'gas' | 'temperature' | 'vibration' | 'ultrasonic' | 'rfid' | 'environmental';
  value: number | string;
  unit: string;
  status: 'normal' | 'warning' | 'danger';
  lastUpdate: string;
  threshold?: {
    warning: number;
    danger: number;
  };
  icon?: any;
  trend?: 'up' | 'down' | 'stable';
}

// Alert Types
export interface Alert {
  id: string | number;
  title?: string;
  message: string;
  severity: 'info' | 'warning' | 'danger';
  timestamp: string;
  sensor?: string;
  type?: string;
  status?: 'active' | 'acknowledged' | 'resolved';
  acknowledgedAt?: string;
  resolvedAt?: string;
}

// Mode Configuration Types
export interface ModeConfig {
  name: string;
  description: string;
  primarySensors: string[];
  alertThresholds: Record<string, { warning: number; danger: number } | undefined>;
  features: Record<string, boolean>;
  colors: {
    primary: string;
    accent: string;
  };
}

// RFID Log Types
export interface RFIDLog {
  id: number;
  workerId: string;
  workerName: string;
  action: 'entry' | 'exit';
  timestamp: string;
  location: string;
}

// Statistics Types
export interface Statistics {
  totalWorkers: number;
  activeAlerts: number;
  systemUptime: number;
  dataPoints: number;
}

// Chart Data Types
export interface ChartData {
  timestamp: string;
  value: number;
  [key: string]: any;
}

// Report Types
export interface ReportData {
  summary: {
    totalIncidents: number;
    totalWarnings: number;
    resolvedAlerts: number;
    averageResponseTime: number;
    uptime: number;
    totalDataPoints: number;
  };
  timeline: Array<{
    timestamp: string;
    incidents: number;
    warnings: number;
    normal: number;
  }>;
  sensorBreakdown: Array<{
    sensor: string;
    incidents: number;
    warnings: number;
    normal: number;
  }>;
  incidentTypes: Array<{
    type: string;
    count: number;
    severity: 'high' | 'medium' | 'low';
  }>;
  predictions: {
    nextWeekRisk: 'high' | 'medium' | 'low';
    likelyIncidents: string[];
    confidence: number;
  };
}

// Settings Types
export interface Settings {
  enableSoundAlerts: boolean;
  enableEmailAlerts: boolean;
  enableSMSAlerts: boolean;
  alertEmailAddress: string;
  alertPhoneNumber: string;
  gasWarningThreshold: number;
  gasDangerThreshold: number;
  tempWarningThreshold: number;
  tempDangerThreshold: number;
  vibrationWarningThreshold: number;
  vibrationDangerThreshold: number;
  proximityWarningThreshold: number;
  proximityDangerThreshold: number;
  dataRefreshInterval: number;
  autoShutdownEnabled: boolean;
  maintenanceMode: boolean;
  apiEndpoint: string;
  mqttBroker: string;
  databaseUrl: string;
  aiPredictionEnabled: boolean;
  aiConfidenceThreshold: number;
  anomalyDetectionSensitivity: 'low' | 'medium' | 'high';
}

// Computer Vision Detection Types
export type DetectionType = 
  | 'ppe_violation' 
  | 'unsafe_behavior' 
  | 'hazard_zone' 
  | 'fire_smoke' 
  | 'slip_trip_fall' 
  | 'vehicle_collision' 
  | 'crowd_density' 
  | 'equipment_misuse';

export type ViolationType = 
  | 'no_helmet' 
  | 'no_vest' 
  | 'no_gloves' 
  | 'no_goggles' 
  | 'no_mask' 
  | 'restricted_area' 
  | 'unsafe_posture' 
  | 'running' 
  | 'smoking' 
  | 'phone_use';

export type CameraStatus = 'online' | 'offline' | 'error' | 'maintenance';

export interface BoundingBox {
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface Camera {
  id: number;
  camera_id: string;
  name: string;
  location: string;
  rtsp_url?: string;
  status: CameraStatus;
  resolution?: string;
  fps?: number;
  detection_enabled: boolean;
  detection_types?: DetectionType[];
  operating_mode: 'heavy-industry' | 'shop-floor';
  created_at: string;
  last_seen: string;
  extra_data?: Record<string, any>;
}

export interface CVDetection {
  id: number;
  camera_id: number;
  detection_type: DetectionType;
  violation_type?: ViolationType;
  confidence: number;
  bbox?: BoundingBox;
  snapshot_path?: string;
  worker_id?: number;
  severity: 'info' | 'warning' | 'danger';
  description?: string;
  timestamp: string;
  acknowledged: boolean;
  acknowledged_at?: string;
  extra_data?: Record<string, any>;
}

export interface CVStats {
  total_cameras: number;
  active_cameras: number;
  total_detections_today: number;
  critical_violations: number;
  ppe_violations: number;
  hazard_zone_violations: number;
  average_confidence: number;
}

export interface CameraWithDetections extends Camera {
  recent_detections: CVDetection[];
}

