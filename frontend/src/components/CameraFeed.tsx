import React from 'react';
import type { Camera, CVDetection } from '../types';
import { Video, VideoOff, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

interface CameraFeedProps {
  camera: Camera;
  recentDetections?: CVDetection[];
  onClick?: () => void;
}

const CameraFeed: React.FC<CameraFeedProps> = ({ camera, recentDetections = [], onClick }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'bg-green-500';
      case 'offline': return 'bg-gray-500';
      case 'error': return 'bg-red-500';
      case 'maintenance': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online': return <CheckCircle className="h-4 w-4" />;
      case 'offline': return <XCircle className="h-4 w-4" />;
      case 'error': return <AlertTriangle className="h-4 w-4" />;
      default: return <Video className="h-4 w-4" />;
    }
  };

  const criticalDetections = recentDetections.filter(d => d.severity === 'danger' && !d.acknowledged);
  const warningDetections = recentDetections.filter(d => d.severity === 'warning' && !d.acknowledged);

  return (
    <div 
      className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden cursor-pointer hover:shadow-xl transition-shadow"
      onClick={onClick}
    >
      {/* Camera Feed Placeholder */}
      <div className="relative bg-gray-900 aspect-video flex items-center justify-center">
        {camera.status === 'online' ? (
          <>
            {/* Simulated Video Feed */}
            <div className="absolute inset-0 bg-gradient-to-br from-gray-800 to-gray-900">
              <div className="absolute inset-0 flex items-center justify-center">
                <Video className="h-20 w-20 text-gray-600 animate-pulse" />
              </div>
              
              {/* Detection Bounding Boxes Overlay */}
              {recentDetections.slice(0, 3).map((detection) => (
                detection.bbox && (
                  <div
                    key={detection.id}
                    className={`absolute border-2 ${
                      detection.severity === 'danger' ? 'border-red-500' : 'border-yellow-500'
                    }`}
                    style={{
                      left: `${(detection.bbox.x / 1920) * 100}%`,
                      top: `${(detection.bbox.y / 1080) * 100}%`,
                      width: `${(detection.bbox.w / 1920) * 100}%`,
                      height: `${(detection.bbox.h / 1080) * 100}%`,
                    }}
                  >
                    <div className={`absolute -top-6 left-0 px-2 py-1 text-xs rounded ${
                      detection.severity === 'danger' ? 'bg-red-500' : 'bg-yellow-500'
                    } text-white`}>
                      {detection.violation_type?.replace('_', ' ').toUpperCase()} - {Math.round(detection.confidence * 100)}%
                    </div>
                  </div>
                )
              ))}
              
              {/* Live Indicator */}
              <div className="absolute top-2 left-2 flex items-center gap-1 bg-red-600 text-white px-2 py-1 rounded text-xs font-bold">
                <span className="h-2 w-2 bg-white rounded-full animate-pulse"></span>
                LIVE
              </div>
              
              {/* FPS Counter */}
              <div className="absolute top-2 right-2 bg-black/50 text-white px-2 py-1 rounded text-xs">
                {camera.fps || 30} FPS
              </div>
            </div>
          </>
        ) : (
          <div className="flex flex-col items-center gap-2 text-gray-500">
            <VideoOff className="h-16 w-16" />
            <span className="text-sm">Camera {camera.status}</span>
          </div>
        )}
      </div>

      {/* Camera Info */}
      <div className="p-4">
        <div className="flex items-start justify-between mb-2">
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white">{camera.name}</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">{camera.location}</p>
          </div>
          <div className={`flex items-center gap-1 ${getStatusColor(camera.status)} text-white px-2 py-1 rounded text-xs`}>
            {getStatusIcon(camera.status)}
            <span className="capitalize">{camera.status}</span>
          </div>
        </div>

        {/* Detection Summary */}
        {camera.detection_enabled && (
          <div className="flex gap-2 text-sm">
            {criticalDetections.length > 0 && (
              <div className="flex items-center gap-1 text-red-600 dark:text-red-400">
                <AlertTriangle className="h-4 w-4" />
                <span className="font-semibold">{criticalDetections.length} Critical</span>
              </div>
            )}
            {warningDetections.length > 0 && (
              <div className="flex items-center gap-1 text-yellow-600 dark:text-yellow-400">
                <AlertTriangle className="h-4 w-4" />
                <span className="font-semibold">{warningDetections.length} Warnings</span>
              </div>
            )}
            {criticalDetections.length === 0 && warningDetections.length === 0 && (
              <div className="flex items-center gap-1 text-green-600 dark:text-green-400">
                <CheckCircle className="h-4 w-4" />
                <span>No violations</span>
              </div>
            )}
          </div>
        )}

        {/* Camera Details */}
        <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
          ID: {camera.camera_id} | {camera.resolution || '1920x1080'}
        </div>
      </div>
    </div>
  );
};

export default CameraFeed;
