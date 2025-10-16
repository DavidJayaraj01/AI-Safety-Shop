import { useAlertStore } from '../context/AlertContext';
import { AlertTriangle, CheckCircle, X, Clock } from 'lucide-react';
import { format } from 'date-fns';
import type { Alert } from '../types';

export const AlertPanel = () => {
  const { alerts, markAsRead, removeAlert } = useAlertStore();

  const getSeverityColor = (severity: Alert['severity']) => {
    switch (severity) {
      case 'critical':
        return 'bg-danger-50 dark:bg-danger-900/20 border-danger-300';
      case 'high':
        return 'bg-warning-50 dark:bg-warning-900/20 border-warning-300';
      case 'medium':
        return 'bg-primary-50 dark:bg-primary-900/20 border-primary-300';
      default:
        return 'bg-gray-50 dark:bg-gray-800 border-gray-300';
    }
  };

  const getSeverityIcon = (severity: Alert['severity']) => {
    switch (severity) {
      case 'critical':
      case 'high':
        return <AlertTriangle className="w-5 h-5 text-danger-600" />;
      case 'medium':
        return <AlertTriangle className="w-5 h-5 text-warning-600" />;
      default:
        return <Clock className="w-5 h-5 text-gray-600" />;
    }
  };

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Recent Alerts
        </h3>
        <span className="px-2 py-1 bg-danger-100 dark:bg-danger-900 text-danger-700 dark:text-danger-300 rounded-full text-xs font-medium">
          {alerts.filter((a) => !a.resolved).length} Active
        </span>
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {alerts.length === 0 ? (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            <CheckCircle className="w-12 h-12 mx-auto mb-2 text-success-500" />
            <p>No alerts - All systems normal</p>
          </div>
        ) : (
          alerts.map((alert) => (
            <div
              key={alert.id}
              className={`p-3 rounded-lg border-l-4 ${getSeverityColor(
                alert.severity
              )}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  {getSeverityIcon(alert.severity)}
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="font-semibold text-gray-900 dark:text-white text-sm">
                        {alert.type.replace(/_/g, ' ').toUpperCase()}
                      </h4>
                      <span className="text-xs text-gray-500">
                        {format(new Date(alert.timestamp), 'HH:mm:ss')}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 dark:text-gray-300">
                      {alert.message}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      📍 {alert.location}
                    </p>
                    {!alert.resolved && (
                      <button
                        onClick={() => markAsRead(alert.id)}
                        className="text-xs text-primary-600 hover:text-primary-700 mt-2"
                      >
                        Mark as resolved
                      </button>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => removeAlert(alert.id)}
                  className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded"
                >
                  <X className="w-4 h-4 text-gray-500" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
