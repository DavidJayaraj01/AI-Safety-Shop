import React, { useState, useRef, useEffect } from 'react';
import type { Camera, CVDetection } from '../types';
import { Video, VideoOff, AlertTriangle, CheckCircle, XCircle, Play, Pause, Maximize } from 'lucide-react';

interface CameraFeedProps {
  camera: Camera;
  recentDetections?: CVDetection[];
  onClick?: () => void;
  showLiveFeed?: boolean;
}

const CameraFeed: React.FC<CameraFeedProps> = ({ 
  camera, 
  recentDetections = [], 
  onClick,
  showLiveFeed = false 
}) => {
  const [isStreamActive, setIsStreamActive] = useState(false);
  const [streamError, setStreamError] = useState<string | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

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

  const startStream = () => {
    if (imgRef.current && camera.status === 'online') {
      setStreamError(null);
      setIsStreamActive(true);
      
      // Use the backend streaming endpoint
      const streamUrl = `http://localhost:8000/cv/stream/live?camera_id=${camera.camera_id || 0}`;
      imgRef.current.src = streamUrl;
      
      imgRef.current.onload = () => {
        setStreamError(null);
      };
      
      imgRef.current.onerror = () => {
        setStreamError('Failed to load camera stream');
        setIsStreamActive(false);
      };
    }
  };

  const stopStream = () => {
    if (imgRef.current) {
      imgRef.current.src = '';
      setIsStreamActive(false);
      setStreamError(null);
    }
  };

  const toggleFullscreen = () => {
    if (!isFullscreen && containerRef.current) {
      if (containerRef.current.requestFullscreen) {
        containerRef.current.requestFullscreen();
        setIsFullscreen(true);
      }
    } else if (isFullscreen) {
      if (document.exitFullscreen) {
        document.exitFullscreen();
        setIsFullscreen(false);
      }
    }
  };

  // Auto-start stream if showLiveFeed is true and camera is online
  useEffect(() => {
    if (showLiveFeed && camera.status === 'online') {
      startStream();
    } else {
      stopStream();
    }
    
    return () => {
      stopStream();
    };
  }, [showLiveFeed, camera.status]);

  // Handle fullscreen changes
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
    };
  }, []);

  return (
    <div 
      ref={containerRef}
      className={`bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden cursor-pointer hover:shadow-xl transition-shadow ${
        isFullscreen ? 'fixed inset-0 z-50 rounded-none' : ''
      }`}
      onClick={onClick}
    >
      {/* Camera Feed */}
      <div className={`relative bg-gray-900 flex items-center justify-center ${
        isFullscreen ? 'h-full' : 'aspect-video'
      }`}>
        {camera.status === 'online' ? (
          <>
            {/* Live Camera Stream or Simulated Feed */}
            {showLiveFeed && isStreamActive ? (
              <img
                ref={imgRef}
                className="w-full h-full object-cover"
                alt={`Live feed from ${camera.name}`}
                style={{ imageRendering: 'auto' }}
              />
            ) : (
              /* Simulated Video Feed */
              <div className="absolute inset-0 bg-gradient-to-br from-gray-800 to-gray-900">
                <div className="absolute inset-0 flex items-center justify-center">
                  <Video className="h-20 w-20 text-gray-600 animate-pulse" />
                </div>
                
                {/* Detection Bounding Boxes Overlay (for simulated view) */}
                {!showLiveFeed && recentDetections.slice(0, 3).map((detection) => (
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
              </div>
            )}
            
            {/* Stream Error Overlay */}
            {streamError && (
              <div className="absolute inset-0 bg-black/70 flex items-center justify-center">
                <div className="text-center text-white">
                  <VideoOff className="h-16 w-16 mx-auto mb-2" />
                  <p className="text-sm">{streamError}</p>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      startStream();
                    }}
                    className="mt-2 px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm"
                  >
                    Retry
                  </button>
                </div>
              </div>
            )}
            
            {/* Stream Controls */}
            <div className="absolute top-2 left-2 flex items-center gap-2">
              {/* Live Indicator */}
              <div className={`flex items-center gap-1 px-2 py-1 rounded text-xs font-bold ${
                isStreamActive ? 'bg-red-600 text-white' : 'bg-gray-600 text-white'
              }`}>
                <span className={`h-2 w-2 rounded-full ${
                  isStreamActive ? 'bg-white animate-pulse' : 'bg-gray-400'
                }`}></span>
                {isStreamActive ? 'LIVE YOLOv8' : 'SIMULATED'}
              </div>
            </div>
            
            {/* Stream Control Buttons */}
            <div className="absolute top-2 right-2 flex items-center gap-1">
              {/* Play/Pause Button */}
              {showLiveFeed && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    isStreamActive ? stopStream() : startStream();
                  }}
                  className="bg-black/50 hover:bg-black/70 text-white p-1 rounded"
                  title={isStreamActive ? 'Stop Stream' : 'Start Stream'}
                >
                  {isStreamActive ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                </button>
              )}
              
              {/* Fullscreen Button */}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  toggleFullscreen();
                }}
                className="bg-black/50 hover:bg-black/70 text-white p-1 rounded"
                title="Toggle Fullscreen"
              >
                <Maximize className="h-4 w-4" />
              </button>
            </div>
            
            {/* FPS Counter */}
            <div className="absolute bottom-2 right-2 bg-black/50 text-white px-2 py-1 rounded text-xs">
              {camera.fps || 30} FPS
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
