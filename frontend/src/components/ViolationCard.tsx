import React from 'react';
import type { CVDetection } from '../types';
import { AlertTriangle, CheckCircle, Clock, Camera as CameraIcon } from 'lucide-react';

interface ViolationCardProps {
  detection: CVDetection;
  onAcknowledge?: (id: number) => void;
  showCamera?: boolean;
}

const formatTimeAgo = (dateString: string) => {
  const now = new Date();
  const past = new Date(dateString);
  const diffMs = now.getTime() - past.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
};

const ViolationCard: React.FC<ViolationCardProps> = ({ 
  detection, 
  onAcknowledge,
  showCamera = true 
}) => {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'danger': return 'border-red-500 bg-red-50 dark:bg-red-900/20';
      case 'warning': return 'border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20';
      case 'info': return 'border-blue-500 bg-blue-50 dark:bg-blue-900/20';
      default: return 'border-gray-500 bg-gray-50 dark:bg-gray-900/20';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'danger': return <AlertTriangle className="h-5 w-5 text-red-600" />;
      case 'warning': return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
      default: return <AlertTriangle className="h-5 w-5 text-blue-600" />;
    }
  };

  const getDetectionLabel = (type: string) => {
    return type.replace(/_/g, ' ').split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const getViolationLabel = (type?: string) => {
    if (!type) return null;
    return type.replace(/_/g, ' ').split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <div className={`border-l-4 rounded-lg p-4 ${getSeverityColor(detection.severity)}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3 flex-1">
          <div className="mt-0.5">
            {getSeverityIcon(detection.severity)}
          </div>
          
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <h4 className="font-semibold text-gray-900 dark:text-white">
                {getViolationLabel(detection.violation_type) || getDetectionLabel(detection.detection_type)}
              </h4>
              <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                detection.severity === 'danger' ? 'bg-red-600 text-white' :
                detection.severity === 'warning' ? 'bg-yellow-600 text-white' :
                'bg-blue-600 text-white'
              }`}>
                {detection.severity.toUpperCase()}
              </span>
            </div>

            {detection.description && (
              <p className="text-sm text-gray-700 dark:text-gray-300 mb-2">
                {detection.description}
              </p>
            )}

            <div className="flex flex-wrap items-center gap-3 text-xs text-gray-600 dark:text-gray-400">
              {showCamera && (
                <div className="flex items-center gap-1">
                  <CameraIcon className="h-3 w-3" />
                  <span>Camera {detection.camera_id}</span>
                </div>
              )}
              
              <div className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                <span>{formatTimeAgo(detection.timestamp)}</span>
              </div>

              <div className="flex items-center gap-1">
                <span className="font-semibold">Confidence:</span>
                <span>{Math.round(detection.confidence * 100)}%</span>
              </div>

              {detection.bbox && (
                <div className="flex items-center gap-1">
                  <span className="font-semibold">Location:</span>
                  <span>X:{detection.bbox.x} Y:{detection.bbox.y}</span>
                </div>
              )}
            </div>

            {detection.acknowledged && (
              <div className="mt-2 flex items-center gap-1 text-xs text-green-600 dark:text-green-400">
                <CheckCircle className="h-3 w-3" />
                <span>Acknowledged {detection.acknowledged_at && formatTimeAgo(detection.acknowledged_at)}</span>
              </div>
            )}
          </div>
        </div>

        {!detection.acknowledged && onAcknowledge && (
          <button
            onClick={() => onAcknowledge(detection.id)}
            className="ml-2 px-3 py-1 bg-primary text-white rounded hover:bg-primary/90 transition-colors text-sm whitespace-nowrap"
          >
            Acknowledge
          </button>
        )}
      </div>
    </div>
  );
};

export default ViolationCard;
