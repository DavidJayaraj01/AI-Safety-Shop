import { useState } from 'react';
import {
  AlertTriangle,
  X,
  CheckCircle,
  Info,
  XCircle,
  Clock,
} from 'lucide-react';
import { useAlertContext } from '../context/AlertContext';
import type { Alert } from '../types';

const AlertPanel = () => {
  const { activeAlerts, acknowledgeAlert, dismissAlert, clearAllAlerts } = useAlertContext();
  const [filterSeverity, setFilterSeverity] = useState<string>('all');

  const filteredAlerts = filterSeverity === 'all'
    ? activeAlerts
    : activeAlerts.filter(alert => alert.severity === filterSeverity);

  const getAlertIcon = (severity) => {
    switch (severity) {
      case 'danger':
        return <XCircle className="h-5 w-5" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5" />;
      case 'info':
        return <Info className="h-5 w-5" />;
      default:
        return <CheckCircle className="h-5 w-5" />;
    }
  };

  const getAlertColor = (severity) => {
    switch (severity) {
      case 'danger':
        return 'bg-danger-50 dark:bg-danger-900/20 border-danger-200 dark:border-danger-800 text-danger-800 dark:text-danger-200';
      case 'warning':
        return 'bg-warning-50 dark:bg-warning-900/20 border-warning-200 dark:border-warning-800 text-warning-800 dark:text-warning-200';
      case 'info':
        return 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 text-blue-800 dark:text-blue-200';
      default:
        return 'bg-gray-50 dark:bg-slate-700 border-gray-200 dark:border-slate-600 text-gray-800 dark:text-gray-200';
    }
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const getTimeAgo = (timestamp) => {
    if (!timestamp) return '';
    const now = new Date();
    const time = new Date(timestamp);
    const diffSeconds = Math.floor((now - time) / 1000);
    
    if (diffSeconds < 60) return `${diffSeconds}s ago`;
    if (diffSeconds < 3600) return `${Math.floor(diffSeconds / 60)}m ago`;
    return `${Math.floor(diffSeconds / 3600)}h ago`;
  };

  return (
    <div className="card">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Active Alerts
          </h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {filteredAlerts.length} active alert{filteredAlerts.length !== 1 ? 's' : ''}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          {/* Filter */}
          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="px-3 py-1 text-sm rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All</option>
            <option value="danger">Critical</option>
            <option value="warning">Warning</option>
            <option value="info">Info</option>
          </select>

          {/* Clear All Button */}
          {activeAlerts.length > 0 && (
            <button
              onClick={clearAllAlerts}
              className="px-3 py-1 text-sm bg-gray-200 dark:bg-slate-700 hover:bg-gray-300 dark:hover:bg-slate-600 text-gray-700 dark:text-gray-300 rounded-lg transition-colors"
            >
              Clear All
            </button>
          )}
        </div>
      </div>

      {/* Alerts List */}
      <div className="space-y-3 max-h-[500px] overflow-y-auto">
        {filteredAlerts.length === 0 ? (
          <div className="text-center py-8">
            <CheckCircle className="h-12 w-12 text-success-500 mx-auto mb-3" />
            <p className="text-gray-500 dark:text-gray-400">
              No active alerts
            </p>
            <p className="text-sm text-gray-400 dark:text-gray-500">
              All systems operational
            </p>
          </div>
        ) : (
          filteredAlerts.map((alert) => (
            <div
              key={alert.id}
              className={`p-4 border-l-4 rounded-lg ${getAlertColor(alert.severity)} ${
                alert.severity === 'danger' ? 'animate-pulse-slow' : ''
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  <div className="mt-0.5">
                    {getAlertIcon(alert.severity)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-1">
                      <h4 className="font-semibold text-sm">
                        {alert.title || 'Alert'}
                      </h4>
                      <span className="text-xs uppercase font-bold px-2 py-0.5 rounded">
                        {alert.severity}
                      </span>
                    </div>
                    <p className="text-sm mb-2">
                      {alert.message}
                    </p>
                    {alert.sensor && (
                      <p className="text-xs opacity-75">
                        Sensor: {alert.sensor}
                      </p>
                    )}
                    <div className="flex items-center space-x-3 mt-2 text-xs opacity-75">
                      <div className="flex items-center space-x-1">
                        <Clock className="h-3 w-3" />
                        <span>{formatTime(alert.timestamp)}</span>
                      </div>
                      <span>•</span>
                      <span>{getTimeAgo(alert.timestamp)}</span>
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex items-center space-x-1 ml-2">
                  <button
                    onClick={() => acknowledgeAlert(alert.id)}
                    className="p-1 rounded hover:bg-white/50 dark:hover:bg-black/20 transition-colors"
                    title="Acknowledge"
                  >
                    <CheckCircle className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => dismissAlert(alert.id)}
                    className="p-1 rounded hover:bg-white/50 dark:hover:bg-black/20 transition-colors"
                    title="Dismiss"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Summary Footer */}
      {activeAlerts.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-slate-700">
          <div className="flex justify-around text-center">
            <div>
              <div className="text-2xl font-bold text-danger-600 dark:text-danger-400">
                {activeAlerts.filter(a => a.severity === 'danger').length}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">Critical</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-warning-600 dark:text-warning-400">
                {activeAlerts.filter(a => a.severity === 'warning').length}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">Warning</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {activeAlerts.filter(a => a.severity === 'info').length}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">Info</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AlertPanel;
