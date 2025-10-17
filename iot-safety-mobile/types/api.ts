// API Response Types
export interface SensorData {
  value: number;
  unit: string;
  status: 'normal' | 'warning' | 'danger';
}

export interface RFIDData {
  value: string;
  status: 'scanned' | 'idle';
}

export interface SensorResponse {
  sensors: {
    temperature: SensorData;
    humidity: SensorData;
    gas: SensorData;
    ultrasonic: SensorData;
    rfid: RFIDData;
  };
  timestamp: string;
}

export interface Camera {
  id: number;
  name: string;
  location: string;
  status: 'active' | 'inactive' | 'error';
  violation_count: number;
}

export interface Detection {
  id: number;
  camera_id: number;
  detection_type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  confidence: number;
  timestamp: string;
  acknowledged: boolean;
}

export interface ReportStats {
  total_violations: number;
  critical_alerts: number;
  active_cameras: number;
  average_response_time: number;
}

export interface SeverityDistribution {
  low: number;
  medium: number;
  high: number;
  critical: number;
}

export interface ReportResponse {
  period: string;
  stats: ReportStats;
  severity_distribution: SeverityDistribution;
  incidents_by_day: Array<{
    date: string;
    count: number;
  }>;
}

export interface Settings {
  theme: 'light' | 'dark' | 'auto';
  notifications_enabled: boolean;
  refresh_interval: number;
  thresholds: {
    temperature: { min: number; max: number };
    humidity: { min: number; max: number };
    gas: { max: number };
    ultrasonic: { min: number };
  };
}

export type SensorType = 'temperature' | 'humidity' | 'gas' | 'ultrasonic' | 'rfid';
