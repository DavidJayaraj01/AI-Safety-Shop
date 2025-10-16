import { useEffect, useState } from 'react';
import { SensorCard } from '../components/SensorCard';
import { AlertPanel } from '../components/AlertPanel';
import { ModeSwitch } from '../components/ModeSwitch';
import { CameraFeed } from '../components/CameraFeed';
import { WorkerCard } from '../components/WorkerCard';
import { Chart } from '../components/Chart';
import { useWebSocket } from '../context/WebSocketContext';
import { sensorAPI, workerAPI, analyticsAPI } from '../services/api';
import type { Sensor, SensorReading, Worker, AnalyticsData, ChartDataPoint, WebSocketMessage } from '../types';
import { Activity, Users, AlertTriangle, CheckCircle2 } from 'lucide-react';

export const Dashboard = () => {
  const [sensors, setSensors] = useState<Sensor[]>([]);
  const [latestReadings, setLatestReadings] = useState<Record<string, SensorReading>>({});
  const [workers, setWorkers] = useState<Worker[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);
  const [loading, setLoading] = useState(true);

  // WebSocket handler for real-time updates
  useWebSocket((message: WebSocketMessage) => {
    if (message.type === 'sensor_update' && 'sensorId' in message.data) {
      const reading = message.data as SensorReading;
      setLatestReadings((prev) => ({
        ...prev,
        [reading.sensorId]: reading,
      }));

      // Update chart data
      setChartData((prev) => [
        ...prev.slice(-20),
        {
          timestamp: new Date(reading.timestamp).toLocaleTimeString(),
          value: reading.value,
        },
      ]);
    }
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [sensorsRes, workersRes, analyticsRes, readingsRes] = await Promise.all([
        sensorAPI.getAll(),
        workerAPI.getActive(),
        analyticsAPI.getDashboard('today'),
        sensorAPI.getLatestReadings(),
      ]);

      if (sensorsRes.data.success && sensorsRes.data.data) {
        setSensors(sensorsRes.data.data);
      }

      if (workersRes.data.success && workersRes.data.data) {
        setWorkers(workersRes.data.data);
      }

      if (analyticsRes.data.success && analyticsRes.data.data) {
        setAnalytics(analyticsRes.data.data);
      }

      if (readingsRes.data.success && readingsRes.data.data) {
        const readingsMap: Record<string, SensorReading> = {};
        readingsRes.data.data.forEach((reading) => {
          readingsMap[reading.sensorId] = reading;
        });
        setLatestReadings(readingsMap);
      }
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Activity className="w-16 h-16 animate-spin text-primary-600 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Analytics Cards */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="card bg-gradient-to-br from-primary-500 to-primary-600 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm opacity-90">Active Sensors</p>
                <p className="text-3xl font-bold mt-1">{analytics.activeSensors}</p>
              </div>
              <Activity className="w-12 h-12 opacity-80" />
            </div>
          </div>

          <div className="card bg-gradient-to-br from-success-500 to-success-600 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm opacity-90">Active Workers</p>
                <p className="text-3xl font-bold mt-1">{analytics.activeWorkers}</p>
              </div>
              <Users className="w-12 h-12 opacity-80" />
            </div>
          </div>

          <div className="card bg-gradient-to-br from-warning-500 to-warning-600 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm opacity-90">Total Alerts</p>
                <p className="text-3xl font-bold mt-1">{analytics.totalAlerts}</p>
              </div>
              <AlertTriangle className="w-12 h-12 opacity-80" />
            </div>
          </div>

          <div className="card bg-gradient-to-br from-emerald-500 to-emerald-600 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm opacity-90">PPE Compliance</p>
                <p className="text-3xl font-bold mt-1">{analytics.ppeComplianceRate}%</p>
              </div>
              <CheckCircle2 className="w-12 h-12 opacity-80" />
            </div>
          </div>
        </div>
      )}

      {/* Mode Switch and Camera Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <ModeSwitch />
        </div>
        <div className="lg:col-span-2">
          <CameraFeed />
        </div>
      </div>

      {/* Sensor Cards */}
      <div>
        <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
          Sensor Monitoring
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sensors.map((sensor) => (
            <SensorCard
              key={sensor.id}
              sensor={sensor}
              latestReading={latestReadings[sensor.id]}
            />
          ))}
        </div>
      </div>

      {/* Charts */}
      {chartData.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Chart
            data={chartData}
            title="Real-Time Sensor Data"
            type="line"
            color="#0ea5e9"
            yAxisLabel="Value"
          />
          <Chart
            data={chartData}
            title="Trend Analysis"
            type="area"
            color="#10b981"
            yAxisLabel="Value"
          />
        </div>
      )}

      {/* Workers and Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
            Active Workers
          </h2>
          <div className="space-y-4">
            {workers.slice(0, 5).map((worker) => (
              <WorkerCard key={worker.id} worker={worker} />
            ))}
            {workers.length === 0 && (
              <div className="card text-center py-8 text-gray-500 dark:text-gray-400">
                No active workers
              </div>
            )}
          </div>
        </div>

        <div>
          <AlertPanel />
        </div>
      </div>
    </div>
  );
};
