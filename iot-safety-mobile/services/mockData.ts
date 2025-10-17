import { SensorResponse, Camera, Detection, ReportResponse, Settings } from '../types/api';

// Mock sensor data generator
export const getMockSensorData = (): SensorResponse => {
  const getRandomValue = (min: number, max: number) => 
    Math.floor(Math.random() * (max - min + 1)) + min;

  const temperature = getRandomValue(20, 30);
  const humidity = getRandomValue(40, 70);
  const gas = getRandomValue(100, 250);
  const distance = getRandomValue(60, 200);

  return {
    sensors: {
      temperature: {
        value: temperature,
        unit: '°C',
        status: temperature > 28 ? 'warning' : temperature > 32 ? 'danger' : 'normal',
      },
      humidity: {
        value: humidity,
        unit: '%',
        status: humidity > 75 ? 'warning' : humidity > 85 ? 'danger' : 'normal',
      },
      gas: {
        value: gas,
        unit: 'ppm',
        status: gas > 200 ? 'warning' : gas > 300 ? 'danger' : 'normal',
      },
      ultrasonic: {
        value: distance,
        unit: 'cm',
        status: distance < 50 ? 'danger' : distance < 100 ? 'warning' : 'normal',
      },
      rfid: {
        value: Math.random() > 0.7 ? 'ABC123DEF456' : 'No card detected',
        status: Math.random() > 0.7 ? 'scanned' : 'idle',
      },
    },
    timestamp: new Date().toISOString(),
  };
};

// Mock cameras
export const getMockCameras = (): Camera[] => {
  return [
    {
      id: 1,
      name: 'Main Entrance',
      location: 'Building A - Floor 1',
      status: 'active',
      violation_count: 12,
    },
    {
      id: 2,
      name: 'Production Floor',
      location: 'Building B - Floor 2',
      status: 'active',
      violation_count: 8,
    },
    {
      id: 3,
      name: 'Storage Area',
      location: 'Building C - Floor 1',
      status: 'inactive',
      violation_count: 3,
    },
    {
      id: 4,
      name: 'Loading Dock',
      location: 'Building A - Ground',
      status: 'active',
      violation_count: 15,
    },
  ];
};

// Mock detections
const detectionTypes = [
  'No Safety Helmet',
  'No Safety Vest',
  'Restricted Area Access',
  'Unsafe Behavior',
  'Equipment Misuse',
  'Fire Hazard',
];

const severities: Array<'low' | 'medium' | 'high' | 'critical'> = ['low', 'medium', 'high', 'critical'];

export const getMockDetections = (): Detection[] => {
  const detections: Detection[] = [];
  const now = Date.now();

  for (let i = 0; i < 20; i++) {
    const timeOffset = i * 1000 * 60 * 5; // 5 minutes apart
    detections.push({
      id: i + 1,
      camera_id: Math.floor(Math.random() * 4) + 1,
      detection_type: detectionTypes[Math.floor(Math.random() * detectionTypes.length)],
      severity: severities[Math.floor(Math.random() * severities.length)],
      confidence: Math.floor(Math.random() * 20) + 80, // 80-100%
      timestamp: new Date(now - timeOffset).toISOString(),
      acknowledged: Math.random() > 0.6,
    });
  }

  return detections.sort((a, b) => 
    new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );
};

// Mock reports
export const getMockReports = (period: 'day' | 'week' | 'month' = 'week'): ReportResponse => {
  const getDaysInPeriod = () => {
    switch (period) {
      case 'day': return 1;
      case 'week': return 7;
      case 'month': return 30;
    }
  };

  const days = getDaysInPeriod();
  const incidents_by_day = [];
  const now = new Date();

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    incidents_by_day.push({
      date: date.toISOString().split('T')[0],
      count: Math.floor(Math.random() * 15) + 5,
    });
  }

  return {
    period,
    stats: {
      total_violations: Math.floor(Math.random() * 100) + 50,
      critical_alerts: Math.floor(Math.random() * 20) + 5,
      active_cameras: 4,
      average_response_time: Math.floor(Math.random() * 300) + 120, // seconds
    },
    severity_distribution: {
      low: Math.floor(Math.random() * 30) + 20,
      medium: Math.floor(Math.random() * 25) + 15,
      high: Math.floor(Math.random() * 20) + 10,
      critical: Math.floor(Math.random() * 10) + 5,
    },
    incidents_by_day,
  };
};

// Mock settings
export const getMockSettings = (): Settings => {
  return {
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
};
