import React, { useState, useRef } from 'react';
import type { Camera, CVDetection } from '../types';
import { Video, VideoOff, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

interface CameraFeedProps {
  camera: Camera;
  recentDetections?: CVDetection[];
  onClick?: () => void;
}

const CameraFeed: React.FC<CameraFeedProps> = ({ camera, recentDetections = [], onClick }) => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamError, setStreamError] = useState<string | null>(null);
  const [cameraSource, setCameraSource] = useState('0'); // Default to webcam
  const imgRef = useRef<HTMLImageElement>(null);

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

  const startStream = () => {
    if (imgRef.current) {
      const streamUrl = `http://localhost:8000/cv/cameras/${camera.id}/stream?source=${encodeURIComponent(cameraSource)}`;
      imgRef.current.src = streamUrl;
      setIsStreaming(true);
      setStreamError(null);
    }
  };

  const stopStream = () => {
    if (imgRef.current) {
      imgRef.current.src = '';
      setIsStreaming(false);
    }
  };

  const handleImageError = () => {
    setStreamError('Failed to load camera stream');
    setIsStreaming(false);
  };

  const handleImageLoad = () => {
    setStreamError(null);
  };

  const criticalDetections = recentDetections.filter(d => d.severity === 'danger' && !d.acknowledged);
  const warningDetections = recentDetections.filter(d => d.severity === 'warning' && !d.acknowledged);

  return (
    <div 
      className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
    >
      {/* Camera Feed */}
      <div className="relative bg-gray-900 aspect-video flex items-center justify-center">
        {camera.status === 'online' ? (
          <>
            {/* Live Video Stream */}
            <div className="absolute inset-0">
              {isStreaming ? (
                <img
                  ref={imgRef}
                  className="w-full h-full object-cover"
                  alt={`Camera ${camera.id} live feed`}
                  onError={handleImageError}
                  onLoad={handleImageLoad}
                />
              ) : (
                <div className="absolute inset-0 bg-gradient-to-br from-gray-800 to-gray-900 flex items-center justify-center">
                  <div className="text-center">
                    <Video className="h-20 w-20 text-gray-600 mx-auto mb-4" />
                    <p className="text-gray-400 text-sm mb-4">Click to start live feed with YOLO detection</p>
                    <button
                      onClick={startStream}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded flex items-center gap-2 mx-auto"
                    >
                      <Video className="h-4 w-4" />
                      Start Live Feed
                    </button>
                  </div>
                </div>
              )}
              
              {/* Stream error message */}
              {streamError && (
                <div className="absolute inset-0 bg-red-900/80 flex items-center justify-center">
                  <div className="text-center text-white">
                    <AlertTriangle className="h-12 w-12 mx-auto mb-2" />
                    <p>{streamError}</p>
                    <button
                      onClick={startStream}
                      className="mt-2 bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm"
                    >
                      Retry
                    </button>
                  </div>
                </div>
              )}
              
              {/* Live Indicator */}
              {isStreaming && (
                <div className="absolute top-2 left-2 flex items-center gap-1 bg-red-600 text-white px-2 py-1 rounded text-xs font-bold">
                  <span className="h-2 w-2 bg-white rounded-full animate-pulse"></span>
                  LIVE - YOLO DETECTION
                </div>
              )}
              
              {/* Stream Controls */}
              {isStreaming && (
                <div className="absolute top-2 right-2 flex gap-1">
                  <button
                    onClick={stopStream}
                    className="bg-red-600 hover:bg-red-700 text-white px-2 py-1 rounded text-xs"
                  >
                    Stop
                  </button>
                </div>
              )}
              
              {/* Camera Source Input */}
              {!isStreaming && (
                <div className="absolute bottom-2 left-2 right-2">
                  <input
                    type="text"
                    value={cameraSource}
                    onChange={(e) => setCameraSource(e.target.value)}
                    placeholder="Camera source (0 for webcam, URL for IP camera)"
                    className="w-full bg-black/50 text-white px-2 py-1 rounded text-xs"
                  />
                  <p className="text-gray-400 text-xs mt-1">
                    Examples: 0 (webcam), rtsp://camera_ip/stream, http://ip/video
                  </p>
                </div>
              )}
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
      <div className="p-4" onClick={onClick}>
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

        {/* YOLO Detection Status */}
        <div className="mb-2 p-2 bg-blue-50 dark:bg-blue-900/20 rounded text-sm">
          <div className="flex items-center gap-2 text-blue-700 dark:text-blue-300">
            <AlertTriangle className="h-4 w-4" />
            <span className="font-semibold">YOLO AI Detection: {isStreaming ? 'Active' : 'Inactive'}</span>
          </div>
          <p className="text-blue-600 dark:text-blue-400 text-xs mt-1">
            Real-time PPE and safety violation detection using YOLOv8 models
          </p>
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
                <span>No violations detected</span>
              </div>
            )}
          </div>
        )}

        {/* Camera Details */}
        <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
          ID: {camera.camera_id} | {camera.resolution || '640x480'} | Source: {cameraSource}
        </div>
      </div>
    </div>
  );
};

export default CameraFeed;
