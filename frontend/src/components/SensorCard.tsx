import type { Sensor, SensorReading } from '../types';
import { TrendingUp, TrendingDown, Minus, AlertTriangle } from 'lucide-react';

interface SensorCardProps {
  sensor: Sensor;
  latestReading?: SensorReading;
}

export const SensorCard = ({ sensor, latestReading }: SensorCardProps) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'normal':
        return 'bg-success-100 dark:bg-success-900 text-success-700 dark:text-success-300 border-success-300';
      case 'warning':
        return 'bg-warning-100 dark:bg-warning-900 text-warning-700 dark:text-warning-300 border-warning-300';
      case 'critical':
        return 'bg-danger-100 dark:bg-danger-900 text-danger-700 dark:text-danger-300 border-danger-300';
      default:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-gray-300';
    }
  };

  const getIcon = () => {
    switch (sensor.type) {
      case 'gas':
        return '🌫️';
      case 'temperature':
        return '🌡️';
      case 'vibration':
        return '📳';
      case 'ultrasonic':
        return '📡';
      case 'environmental':
        return '🌍';
      default:
        return '📊';
    }
  };

  const getTrendIcon = () => {
    if (!latestReading) return <Minus className="w-4 h-4" />;
    if (latestReading.value > sensor.thresholds.warning) {
      return <TrendingUp className="w-4 h-4 text-danger-600" />;
    } else if (latestReading.value < sensor.thresholds.warning * 0.8) {
      return <TrendingDown className="w-4 h-4 text-success-600" />;
    }
    return <Minus className="w-4 h-4 text-gray-400" />;
  };

  return (
    <div
      className={`card border-l-4 ${
        latestReading ? getStatusColor(latestReading.status) : 'border-gray-300'
      }`}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center">
          <span className="text-3xl mr-3">{getIcon()}</span>
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white">
              {sensor.name}
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {sensor.location}
            </p>
          </div>
        </div>
        {latestReading?.status === 'critical' && (
          <AlertTriangle className="w-5 h-5 text-danger-600 animate-pulse" />
        )}
      </div>

      {latestReading ? (
        <div className="space-y-2">
          <div className="flex items-end justify-between">
            <div>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {latestReading.value.toFixed(2)}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {latestReading.unit}
              </p>
            </div>
            {getTrendIcon()}
          </div>

          <div className="flex justify-between text-xs text-gray-600 dark:text-gray-400">
            <span>Warning: {sensor.thresholds.warning}</span>
            <span>Critical: {sensor.thresholds.critical}</span>
          </div>

          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all ${
                latestReading.status === 'critical'
                  ? 'bg-danger-600'
                  : latestReading.status === 'warning'
                  ? 'bg-warning-500'
                  : 'bg-success-500'
              }`}
              style={{
                width: `${Math.min(
                  (latestReading.value / sensor.thresholds.critical) * 100,
                  100
                )}%`,
              }}
            />
          </div>

          <p className="text-xs text-gray-500 dark:text-gray-400">
            Last updated:{' '}
            {new Date(latestReading.timestamp).toLocaleTimeString()}
          </p>
        </div>
      ) : (
        <div className="text-center py-4 text-gray-500 dark:text-gray-400">
          No data available
        </div>
      )}
    </div>
  );
};
