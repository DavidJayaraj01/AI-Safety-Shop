import React, { useState, useEffect } from 'react';
import { cvApi } from '../services/api';
import type { Camera, CVDetection, CVStats } from '../types';
import CameraFeed from '../components/CameraFeed';
import ViolationCard from '../components/ViolationCard';
import { useModeContext } from '../context/ModeContext';
import {
  Camera as CameraIcon,
  AlertTriangle,
  Shield,
  Activity,
  TrendingUp,
  Eye,
  Zap,
  CheckCircle,
  Play,
  Pause,
  Monitor,
  Cpu,
} from 'lucide-react';
import toast from 'react-hot-toast';

const CVMonitoring: React.FC = () => {
  const { mode } = useModeContext();
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [detections, setDetections] = useState<CVDetection[]>([]);
  const [stats, setStats] = useState<CVStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedCamera, setSelectedCamera] = useState<number | null>(null);
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [filterAcknowledged, setFilterAcknowledged] = useState<boolean>(false);
  
  // YOLO Detection State
  const [detectorStatus, setDetectorStatus] = useState<any>(null);
  const [streamStatus, setStreamStatus] = useState<any>(null);
  
  // Live Camera State
  const [showLiveCamera, setShowLiveCamera] = useState(false);
  const [liveCameraId, setLiveCameraId] = useState(0);
  const liveStreamUrl = `http://localhost:8000/cv/stream/live?camera_id=${liveCameraId}`;

  useEffect(() => {
    loadData();
    loadDetectorStatus();
    const interval = setInterval(() => {
      loadData();
      if (showLiveCamera) {
        loadDetectorStatus(); // Update detector status when streaming
      }
    }, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, [selectedCamera, filterSeverity, filterAcknowledged, showLiveCamera]);

  const loadDetectorStatus = async () => {
    try {
      const streamRes = await fetch('http://localhost:8000/cv/stream/status');
      const streamData = await streamRes.json();
      setStreamStatus(streamData);
    } catch (error) {
      console.error('Failed to load detector status:', error);
    }
  };

  const loadData = async () => {
    try {
      const [camerasRes, detectionsRes, statsRes] = await Promise.all([
        cvApi.getAllCameras(),
        cvApi.getDetections({
          camera_id: selectedCamera || undefined,
          acknowledged: filterAcknowledged,
          hours: 24,
        }),
        cvApi.getCVStats(),
      ]);

      setCameras(camerasRes.data);
      let filteredDetections = detectionsRes.data;
      
      if (filterSeverity !== 'all') {
        filteredDetections = filteredDetections.filter(
          (d: CVDetection) => d.severity === filterSeverity
        );
      }
      
      setDetections(filteredDetections);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Error loading CV monitoring data:', error);
      toast.error('Failed to load CV monitoring data');
    } finally {
      setLoading(false);
    }
  };

  const handleAcknowledge = async (detectionId: number) => {
    try {
      await cvApi.acknowledgeDetection(detectionId);
      toast.success('Violation acknowledged');
      loadData();
    } catch (error) {
      console.error('Error acknowledging detection:', error);
      toast.error('Failed to acknowledge violation');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <Eye className="h-8 w-8 text-primary" />
            AI Computer Vision Monitoring
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Real-time safety violation detection using computer vision
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
            mode === 'heavy-industry' 
              ? 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400'
              : 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'
          }`}>
            {mode === 'heavy-industry' ? 'Heavy Industry Mode' : 'Shop Floor Mode'}
          </span>
        </div>
      </div>

      {/* YOLO Model Status Panel */}
      {streamStatus && (
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg shadow-lg p-6 text-white">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Cpu className="h-8 w-8" />
              <div>
                <h3 className="text-xl font-bold">YOLOv8 Detection System</h3>
                <p className="text-blue-100">Real-time AI safety monitoring</p>
              </div>
            </div>
            <div className={`px-3 py-1 rounded-full text-sm font-bold ${
              streamStatus.yolo_model?.loaded ? 'bg-green-500' : 'bg-red-500'
            }`}>
              {streamStatus.yolo_model?.loaded ? '🟢 READY' : '🔴 NOT LOADED'}
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white/10 rounded-lg p-4">
              <h4 className="font-semibold mb-2">Model Info</h4>
              <p className="text-sm">Model: {streamStatus.yolo_model?.model_name || 'Not loaded'}</p>
              <p className="text-sm">Classes: {streamStatus.yolo_model?.num_classes || 0}</p>
              <p className="text-sm">Confidence: {((streamStatus.yolo_model?.confidence_threshold || 0) * 100).toFixed(0)}%</p>
            </div>
            
            <div className="bg-white/10 rounded-lg p-4">
              <h4 className="font-semibold mb-2">Camera Status</h4>
              <p className="text-sm">Camera: {streamStatus.camera_available ? '🟢 Available' : '🔴 Not detected'}</p>
              <p className="text-sm">Stream: {showLiveCamera ? '🔴 Active' : '⚪ Inactive'}</p>
            </div>
            
            <div className="bg-white/10 rounded-lg p-4">
              <h4 className="font-semibold mb-2">Detection Types</h4>
              <div className="text-xs space-y-1">
                <div>• PPE Violations (Helmet, Vest, Gloves)</div>
                <div>• Fire & Smoke Detection</div>
                <div>• Vehicle & Equipment</div>
                <div>• Unsafe Behaviors</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Live Camera Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
        <div className="border-b border-gray-200 dark:border-gray-700 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Monitor className="h-6 w-6 text-blue-600" />
              <div>
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">Live YOLOv8 Detection</h2>
                <p className="text-gray-600 dark:text-gray-400">Real-time safety monitoring with AI detection</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <select
                value={liveCameraId}
                onChange={(e) => setLiveCameraId(Number(e.target.value))}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value={0}>Camera 0 (Default)</option>
                <option value={1}>Camera 1</option>
                <option value={2}>Camera 2</option>
              </select>
              
              <button
                onClick={() => setShowLiveCamera(!showLiveCamera)}
                disabled={!streamStatus?.camera_available && streamStatus !== null}
                className={`px-6 py-2 rounded-lg font-semibold transition-colors flex items-center gap-2 ${
                  showLiveCamera
                    ? 'bg-red-600 text-white hover:bg-red-700'
                    : 'bg-green-600 text-white hover:bg-green-700'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {showLiveCamera ? (
                  <>
                    <Pause className="h-4 w-4" />
                    Stop Stream
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4" />
                    Start Stream
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        <div className="p-6">
          {showLiveCamera && streamStatus?.camera_available ? (
            <div className="relative">
              <div className="rounded-lg overflow-hidden border-2 border-blue-500 bg-black">
                <img
                  src={liveStreamUrl}
                  alt="Live Camera Feed with YOLO Detection"
                  className="w-full h-auto"
                  style={{ maxHeight: '720px', objectFit: 'contain' }}
                  onError={(e) => {
                    console.error('Stream error:', e);
                    toast.error('Failed to load camera stream');
                  }}
                />
              </div>
              
              <div className="absolute top-4 left-4 flex flex-col gap-2">
                <div className="bg-red-600 text-white px-3 py-1 rounded-full text-sm font-bold flex items-center gap-2 shadow-lg">
                  <span className="w-2 h-2 bg-white rounded-full animate-pulse"></span>
                  🔴 LIVE YOLOv8
                </div>
                {streamStatus?.yolo_model?.loaded && (
                  <div className="bg-green-600 text-white px-3 py-1 rounded-full text-xs font-bold shadow-lg">
                    {streamStatus.yolo_model.model_name}
                  </div>
                )}
              </div>
              
              <div className="absolute bottom-4 left-4 bg-black/70 text-white px-3 py-2 rounded-lg text-sm">
                <div>Camera {liveCameraId} • Real-time Detection</div>
                <div className="text-xs text-gray-300">
                  Confidence: {((streamStatus?.yolo_model?.confidence_threshold || 0.75) * 100).toFixed(0)}%
                </div>
              </div>
            </div>
          ) : !showLiveCamera ? (
            <div className="text-center py-16 text-gray-500 dark:text-gray-400 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-900">
              <CameraIcon className="h-20 w-20 mx-auto mb-4 opacity-50" />
              <p className="text-xl font-semibold mb-2">Click "Start Stream" to begin live detection</p>
              <p className="text-sm mt-2">
                {streamStatus?.message || 'Real-time YOLO detection with bounding boxes will appear here'}
              </p>
              <div className="mt-6 flex items-center justify-center gap-6 text-sm">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span>PPE Detection</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-orange-500" />
                  <span>Fire/Smoke Detection</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-blue-500" />
                  <span>Vehicle Detection</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-purple-500" />
                  <span>Behavior Analysis</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-16 text-red-500">
              <AlertTriangle className="h-20 w-20 mx-auto mb-4" />
              <p className="text-xl font-semibold mb-2">Camera Not Available</p>
              <p className="text-sm">Please connect a camera and refresh the page</p>
            </div>
          )}
        </div>
      </div>

      {/* Statistics Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Cameras</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.total_cameras}</p>
              </div>
              <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                <CameraIcon className="h-6 w-6 text-blue-600" />
              </div>
            </div>
            <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              {stats.active_cameras} active
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Today's Detections</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.total_detections_today}</p>
              </div>
              <div className="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                <Activity className="h-6 w-6 text-purple-600" />
              </div>
            </div>
            <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              Last 24 hours
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Critical Violations</p>
                <p className="text-2xl font-bold text-red-600">{stats.critical_violations}</p>
              </div>
              <div className="p-3 bg-red-100 dark:bg-red-900/30 rounded-lg">
                <AlertTriangle className="h-6 w-6 text-red-600" />
              </div>
            </div>
            <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              Requires attention
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Detection Accuracy</p>
                <p className="text-2xl font-bold text-green-600">{Math.round(stats.average_confidence * 100)}%</p>
              </div>
              <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-lg">
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
            </div>
            <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              Average confidence
            </div>
          </div>
        </div>
      )}

      {/* PPE & Hazard Zone Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <div className="flex items-center gap-3">
              <Shield className="h-8 w-8 text-yellow-600" />
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">PPE Violations</p>
                <p className="text-xl font-bold text-gray-900 dark:text-white">{stats.ppe_violations}</p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <div className="flex items-center gap-3">
              <Zap className="h-8 w-8 text-red-600" />
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Hazard Zone Violations</p>
                <p className="text-xl font-bold text-gray-900 dark:text-white">{stats.hazard_zone_violations}</p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <div className="flex items-center gap-3">
              <CheckCircle className="h-8 w-8 text-green-600" />
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Compliance Rate</p>
                <p className="text-xl font-bold text-gray-900 dark:text-white">
                  {stats.total_detections_today > 0 
                    ? Math.round((1 - (stats.critical_violations / stats.total_detections_today)) * 100)
                    : 100}%
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Camera Grid */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Camera Feeds</h2>
          <button
            onClick={() => setSelectedCamera(null)}
            className={`px-3 py-1 rounded-lg text-sm transition-colors ${
              selectedCamera === null
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-500'
            }`}
          >
            All Cameras
          </button>
        </div>

        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-600 dark:text-gray-400 mt-2">Loading cameras...</p>
          </div>
        ) : cameras.length === 0 ? (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            <CameraIcon className="h-16 w-16 mx-auto mb-4 opacity-50" />
            <p>No cameras configured</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {cameras.map((camera) => (
              <CameraFeed
                key={camera.id}
                camera={camera}
                recentDetections={detections.filter(d => d.camera_id === camera.id)}
                onClick={() => setSelectedCamera(camera.id)}
                showLiveFeed={false} // Use simulation for camera grid
              />
            ))}
          </div>
        )}

        {cameras.length === 0 && (
          <div className="text-center py-12 text-gray-500 dark:text-gray-400">
            <CameraIcon className="h-12 w-12 mx-auto mb-2 opacity-50" />
            <p>No cameras configured</p>
          </div>
        )}
      </div>

      {/* Violations List */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            Recent Violations
            {detections.filter(d => d.severity === 'danger' && !d.acknowledged).length > 0 && (
              <span className="ml-2 px-2 py-1 bg-red-600 text-white text-sm rounded">
                {detections.filter(d => d.severity === 'danger' && !d.acknowledged).length} Critical
              </span>
            )}
          </h2>

          <div className="flex gap-2">
            <select
              value={filterSeverity}
              onChange={(e) => setFilterSeverity(e.target.value)}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="all">All Severities</option>
              <option value="danger">Danger</option>
              <option value="warning">Warning</option>
              <option value="info">Info</option>
            </select>

            <button
              onClick={() => setFilterAcknowledged(!filterAcknowledged)}
              className={`px-4 py-2 rounded ${
                filterAcknowledged
                  ? 'bg-primary text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              }`}
            >
              {filterAcknowledged ? 'Acknowledged Only' : 'Unacknowledged'}
            </button>
          </div>
        </div>

        <div className="space-y-3 max-h-[600px] overflow-y-auto">
          {detections.map((detection) => (
            <ViolationCard
              key={detection.id}
              detection={detection}
              onAcknowledge={handleAcknowledge}
            />
          ))}

          {detections.length === 0 && (
            <div className="text-center py-12 text-gray-500 dark:text-gray-400">
              <CheckCircle className="h-12 w-12 mx-auto mb-2 text-green-500" />
              <p>No violations detected</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CVMonitoring;
