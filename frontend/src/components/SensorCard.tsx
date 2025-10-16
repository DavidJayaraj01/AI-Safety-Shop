import React from 'react';
import { 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  TrendingUp,
  TrendingDown,
  Minus
} from 'lucide-react';

const SensorCard = ({ sensor }) => {
  const {
    id,
    name,
    type,
    value,
    unit,
    status, // 'normal', 'warning', 'danger'
    lastUpdate,
    threshold,
    icon: IconComponent,
    trend // 'up', 'down', 'stable'
  } = sensor;

  const getStatusColor = () => {
    switch (status) {
      case 'danger':
        return 'border-danger-500 bg-danger-50 dark:bg-danger-900/20';
      case 'warning':
        return 'border-warning-500 bg-warning-50 dark:bg-warning-900/20';
      case 'normal':
      default:
        return 'border-success-500 bg-success-50 dark:bg-success-900/20';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'danger':
        return <XCircle className="h-6 w-6 text-danger-600 dark:text-danger-400" />;
      case 'warning':
        return <AlertTriangle className="h-6 w-6 text-warning-600 dark:text-warning-400" />;
      case 'normal':
      default:
        return <CheckCircle className="h-6 w-6 text-success-600 dark:text-success-400" />;
    }
  };

  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-4 w-4 text-danger-500" />;
      case 'down':
        return <TrendingDown className="h-4 w-4 text-success-500" />;
      case 'stable':
      default:
        return <Minus className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusLabel = () => {
    switch (status) {
      case 'danger':
        return 'CRITICAL';
      case 'warning':
        return 'WARNING';
      case 'normal':
      default:
        return 'NORMAL';
    }
  };

  const formatLastUpdate = () => {
    if (!lastUpdate) return 'Never';
    const now = new Date();
    const updateTime = new Date(lastUpdate);
    const diffSeconds = Math.floor((now - updateTime) / 1000);
    
    if (diffSeconds < 60) return `${diffSeconds}s ago`;
    if (diffSeconds < 3600) return `${Math.floor(diffSeconds / 60)}m ago`;
    return `${Math.floor(diffSeconds / 3600)}h ago`;
  };

  return (
    <div className={`card card-hover border-l-4 ${getStatusColor()} ${
      status === 'danger' ? 'animate-pulse-slow' : ''
    }`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`p-3 rounded-lg ${
            status === 'danger' 
              ? 'bg-danger-100 dark:bg-danger-900/40' 
              : status === 'warning'
              ? 'bg-warning-100 dark:bg-warning-900/40'
              : 'bg-success-100 dark:bg-success-900/40'
          }`}>
            {IconComponent && <IconComponent className={`h-6 w-6 ${
              status === 'danger'
                ? 'text-danger-600 dark:text-danger-400'
                : status === 'warning'
                ? 'text-warning-600 dark:text-warning-400'
                : 'text-success-600 dark:text-success-400'
            }`} />}
          </div>
          <div>
            <h3 className="font-semibold text-lg text-gray-900 dark:text-white">
              {name}
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 capitalize">
              {type}
            </p>
          </div>
        </div>
        {getStatusIcon()}
      </div>

      {/* Value Display */}
      <div className="mb-4">
        <div className="flex items-baseline space-x-2">
          <span className={`text-4xl font-bold ${
            status === 'danger'
              ? 'text-danger-600 dark:text-danger-400'
              : status === 'warning'
              ? 'text-warning-600 dark:text-warning-400'
              : 'text-success-600 dark:text-success-400'
          }`}>
            {typeof value === 'number' ? value.toFixed(1) : value}
          </span>
          <span className="text-xl text-gray-500 dark:text-gray-400">
            {unit}
          </span>
          {trend && (
            <div className="ml-2">
              {getTrendIcon()}
            </div>
          )}
        </div>
      </div>

      {/* Threshold and Status */}
      {threshold && (
        <div className="mb-3 p-2 bg-gray-100 dark:bg-slate-700 rounded">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600 dark:text-gray-400">Threshold:</span>
            <span className="font-medium text-gray-900 dark:text-white">
              {threshold.warning} / {threshold.danger} {unit}
            </span>
          </div>
          <div className="mt-1 w-full bg-gray-200 dark:bg-slate-600 rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all duration-300 ${
                status === 'danger'
                  ? 'bg-danger-500'
                  : status === 'warning'
                  ? 'bg-warning-500'
                  : 'bg-success-500'
              }`}
              style={{ 
                width: `${Math.min(
                  100, 
                  (value / threshold.danger) * 100
                )}%` 
              }}
            />
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between pt-3 border-t border-gray-200 dark:border-slate-700">
        <div className="flex items-center space-x-2">
          <div className={`h-2 w-2 rounded-full ${
            status === 'danger'
              ? 'bg-danger-500 animate-pulse'
              : status === 'warning'
              ? 'bg-warning-500 animate-pulse'
              : 'bg-success-500'
          }`} />
          <span className={`text-sm font-semibold ${
            status === 'danger'
              ? 'text-danger-600 dark:text-danger-400'
              : status === 'warning'
              ? 'text-warning-600 dark:text-warning-400'
              : 'text-success-600 dark:text-success-400'
          }`}>
            {getStatusLabel()}
          </span>
        </div>
        <span className="text-xs text-gray-500 dark:text-gray-400">
          Updated {formatLastUpdate()}
        </span>
      </div>
    </div>
  );
};

export default SensorCard;
