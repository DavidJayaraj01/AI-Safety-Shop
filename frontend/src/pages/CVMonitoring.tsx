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

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, [selectedCamera, filterSeverity, filterAcknowledged]);

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

  const handleSimulateDetection = async (cameraId: number) => {
    try {
      const res = await cvApi.simulateDetection(cameraId);
      if (res.data.detections && res.data.detections.length > 0) {
        toast.success(`Detected ${res.data.detections.length} violation(s)`);
      } else {
        toast('No violations detected', { icon: '✅' });
      }
      loadData();
    } catch (error) {
      console.error('Error simulating detection:', error);
      toast.error('Failed to simulate detection');
    }
  };

  const unacknowledgedDetections = detections.filter(d => !d.acknowledged);
  const criticalDetections = unacknowledgedDetections.filter(d => d.severity === 'danger');

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
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Live Camera Feeds</h2>
          <button
            onClick={() => setSelectedCamera(null)}
            className={`px-4 py-2 rounded ${
              selectedCamera === null 
                ? 'bg-primary text-white' 
                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}
          >
            All Cameras
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {cameras
            .filter(cam => selectedCamera === null || cam.id === selectedCamera)
            .map((camera) => (
              <div key={camera.id} className="relative">
                <CameraFeed
                  camera={camera}
                  onClick={() => setSelectedCamera(camera.id)}
                />
                <button
                  onClick={() => handleSimulateDetection(camera.id)}
                  className="absolute bottom-2 right-2 px-2 py-1 bg-purple-600 text-white text-xs rounded hover:bg-purple-700 transition-colors"
                >
                  Test Detection
                </button>
              </div>
            ))}
        </div>

        {cameras.length === 0 && (
          <div className="text-center py-12 text-gray-500 dark:text-gray-400">
            <CameraIcon className="h-12 w-12 mx-auto mb-2 opacity-50" />
            <p>No cameras configured yet</p>
          </div>
        )}
      </div>

      {/* Violations List */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            Recent Violations
            {criticalDetections.length > 0 && (
              <span className="ml-2 px-2 py-1 bg-red-600 text-white text-sm rounded">
                {criticalDetections.length} Critical
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
