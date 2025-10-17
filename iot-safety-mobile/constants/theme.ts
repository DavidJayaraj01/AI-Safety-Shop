// Theme colors
export const Colors = {
  light: {
    primary: '#3b82f6',
    background: '#f8fafc',
    card: '#ffffff',
    text: '#1e293b',
    textSecondary: '#64748b',
    border: '#e2e8f0',
    success: '#22c55e',
    warning: '#f59e0b',
    danger: '#ef4444',
    info: '#3b82f6',
  },
  dark: {
    primary: '#3b82f6',
    background: '#0f172a',
    card: '#1e293b',
    text: '#f1f5f9',
    textSecondary: '#94a3b8',
    border: '#334155',
    success: '#22c55e',
    warning: '#f59e0b',
    danger: '#ef4444',
    info: '#3b82f6',
  },
};

// Status colors
export const StatusColors = {
  normal: '#22c55e',
  warning: '#f59e0b',
  danger: '#ef4444',
  active: '#22c55e',
  inactive: '#94a3b8',
  error: '#ef4444',
};

// Severity colors
export const SeverityColors = {
  low: '#22c55e',
  medium: '#f59e0b',
  high: '#ef4444',
  critical: '#dc2626',
};

// Spacing
export const Spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
};

// Border radius
export const BorderRadius = {
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
};

// Font sizes
export const FontSizes = {
  xs: 12,
  sm: 14,
  md: 16,
  lg: 18,
  xl: 20,
  xxl: 24,
};

// API Configuration
// Backend server running on your computer
export const API_BASE_URL = 'http://10.54.156.140:8000';
export const REFRESH_INTERVAL = 15000; // 15 seconds
export const MAX_CHART_POINTS = 20;
export const USE_MOCK_DATA = false; // Using real ESP8266 data via backend

// Notification types
export const NotificationTypes = {
  SENSOR_ALERT: 'sensor_alert',
  CV_VIOLATION: 'cv_violation',
  SYSTEM_ERROR: 'system_error',
};
