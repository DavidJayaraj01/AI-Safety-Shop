import { useEffect, useRef, useState } from 'react';
import { cameraAPI } from '../services/api';
import { Video, VideoOff, Play, Pause } from 'lucide-react';

export const CameraFeed = () => {
  const [isDetectionEnabled, setIsDetectionEnabled] = useState(true);
  const [isPlaying, setIsPlaying] = useState(true);
  const imgRef = useRef<HTMLImageElement>(null);

  const streamUrl = cameraAPI.getStreamUrl();

  const toggleDetection = async () => {
    try {
      await cameraAPI.toggleDetection(!isDetectionEnabled);
      setIsDetectionEnabled(!isDetectionEnabled);
    } catch (error) {
      console.error('Error toggling detection:', error);
    }
  };

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Live Camera Feed - PPE Detection
        </h3>
        <div className="flex gap-2">
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600"
          >
            {isPlaying ? (
              <Pause className="w-4 h-4" />
            ) : (
              <Play className="w-4 h-4" />
            )}
          </button>
          <button
            onClick={toggleDetection}
            className={`px-3 py-2 rounded-lg font-medium transition-colors ${
              isDetectionEnabled
                ? 'bg-success-600 text-white hover:bg-success-700'
                : 'bg-gray-300 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-400'
            }`}
          >
            {isDetectionEnabled ? (
              <Video className="w-4 h-4" />
            ) : (
              <VideoOff className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>

      <div className="relative bg-gray-900 rounded-lg overflow-hidden aspect-video">
        {isPlaying ? (
          <img
            ref={imgRef}
            src={streamUrl}
            alt="Camera Feed"
            className="w-full h-full object-contain"
          />
        ) : (
          <div className="flex items-center justify-center h-full text-white">
            <div className="text-center">
              <VideoOff className="w-16 h-16 mx-auto mb-2 opacity-50" />
              <p>Camera Feed Paused</p>
            </div>
          </div>
        )}
        
        <div className="absolute top-2 right-2 px-2 py-1 bg-black/70 text-white text-xs rounded">
          {isDetectionEnabled ? '🔴 Detection Active' : '⚪ Detection Off'}
        </div>
      </div>

      <div className="mt-4 grid grid-cols-5 gap-2 text-center">
        <div className="p-2 bg-gray-100 dark:bg-gray-700 rounded">
          <div className="text-2xl">🪖</div>
          <div className="text-xs font-medium mt-1">Helmet</div>
        </div>
        <div className="p-2 bg-gray-100 dark:bg-gray-700 rounded">
          <div className="text-2xl">🦺</div>
          <div className="text-xs font-medium mt-1">Vest</div>
        </div>
        <div className="p-2 bg-gray-100 dark:bg-gray-700 rounded">
          <div className="text-2xl">🧤</div>
          <div className="text-xs font-medium mt-1">Gloves</div>
        </div>
        <div className="p-2 bg-gray-100 dark:bg-gray-700 rounded">
          <div className="text-2xl">🥽</div>
          <div className="text-xs font-medium mt-1">Goggles</div>
        </div>
        <div className="p-2 bg-gray-100 dark:bg-gray-700 rounded">
          <div className="text-2xl">👢</div>
          <div className="text-xs font-medium mt-1">Shoes</div>
        </div>
      </div>
    </div>
  );
};
