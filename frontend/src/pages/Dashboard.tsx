import React, { useState, useEffect } from 'react';
import {
  Flame,
  Thermometer,
  Activity,
  Ruler,
  CreditCard,
  Wind,
  TrendingUp,
  Users,
  AlertTriangle
} from 'lucide-react';
import SensorCard from '../components/SensorCard';
import Chart from '../components/Chart';
import AlertPanel from '../components/AlertPanel';
import ModeSwitch from '../components/ModeSwitch';
import { useModeContext } from '../context/ModeContext';
import { sensorsApi } from '../services/api';

const Dashboard = () => {
  const { mode, modeConfig } = useModeContext();
  const [sensors, setSensors] = useState([]);
  const [sensorHistory, setSensorHistory] = useState({});
  const [rfidLogs, setRfidLogs] = useState([]);
  const [statistics, setStatistics] = useState({
    totalWorkers: 0,
    activeAlerts: 0,
    systemUptime: 0,
    dataPoints: 0
  });
  const [isLoading, setIsLoading] = useState(true);

  // Sensor configurations
  const sensorConfig = {
    gas: {
      name: 'Gas Sensor',
      type: 'gas',
      unit: 'ppm',
      icon: Flame,
      threshold: { warning: 50, danger: 100 }
    },
    temperature: {
      name: 'Temperature',
      type: 'temperature',
      unit: '°C',
      icon: Thermometer,
      threshold: { warning: 35, danger: 45 }
    },
    vibration: {
      name: 'Vibration',
      type: 'vibration',
      unit: 'g',
      icon: Activity,
      threshold: { warning: 5, danger: 10 }
    },
    ultrasonic: {
      name: 'Proximity',
      type: 'ultrasonic',
      unit: 'cm',
      icon: Ruler,
      threshold: { warning: 50, danger: 20 }
    },
    rfid: {
      name: 'RFID Access',
      type: 'rfid',
      unit: 'workers',
      icon: CreditCard,
      threshold: null
    },
    environmental: {
      name: 'Air Quality',
      type: 'environmental',
      unit: 'AQI',
      icon: Wind,
      threshold: { warning: 100, danger: 150 }
    }
  };

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [sensorsResponse, historyResponse, rfidResponse, statsResponse] = await Promise.all([
        sensorsApi.getAllSensors(),
        sensorsApi.getSensorHistory(),
        sensorsApi.getRFIDLogs(),
        sensorsApi.getStatistics()
      ]);

      // Transform sensor data
      const transformedSensors = Object.entries(sensorsResponse.data || {}).map(([key, data]) => {
        const config = sensorConfig[key] || {};
        const status = determineStatus(data.value, config.threshold);
        
        return {
          id: key,
          ...config,
          value: data.value,
          status,
          lastUpdate: data.timestamp,
          trend: data.trend || 'stable'
        };
      });

      setSensors(transformedSensors);
      setSensorHistory(historyResponse.data || {});
      setRfidLogs(rfidResponse.data || []);
      setStatistics(statsResponse.data || statistics);
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      // Use mock data on error
      generateMockData();
      setIsLoading(false);
    }
  };

  const determineStatus = (value, threshold) => {
    if (!threshold) return 'normal';
    if (value >= threshold.danger) return 'danger';
    if (value >= threshold.warning) return 'warning';
    return 'normal';
  };

  const generateMockData = () => {
    const mockSensors = Object.entries(sensorConfig).map(([key, config]) => {
      let value;
      if (key === 'gas') value = Math.random() * 120;
      else if (key === 'temperature') value = 20 + Math.random() * 30;
      else if (key === 'vibration') value = Math.random() * 12;
      else if (key === 'ultrasonic') value = Math.random() * 100;
      else if (key === 'environmental') value = Math.random() * 200;
      else value = Math.floor(Math.random() * 10);

      const status = determineStatus(value, config.threshold);

      return {
        id: key,
        ...config,
        value,
        status,
        lastUpdate: new Date().toISOString(),
        trend: ['up', 'down', 'stable'][Math.floor(Math.random() * 3)]
      };
    });

    setSensors(mockSensors);

    // Generate mock history
    const mockHistory = {};
    Object.keys(sensorConfig).forEach(key => {
      mockHistory[key] = Array.from({ length: 20 }, (_, i) => ({
        timestamp: new Date(Date.now() - (19 - i) * 60000).toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit'
        }),
        value: Math.random() * 100
      }));
    });
    setSensorHistory(mockHistory);

    // Generate mock RFID logs
    const mockRfidLogs = Array.from({ length: 5 }, (_, i) => ({
      id: i + 1,
      workerId: `W${1000 + i}`,
      workerName: `Worker ${i + 1}`,
      action: i % 2 === 0 ? 'entry' : 'exit',
      timestamp: new Date(Date.now() - i * 300000).toISOString(),
      location: ['Gate A', 'Gate B', 'Workshop', 'Storage'][Math.floor(Math.random() * 4)]
    }));
    setRfidLogs(mockRfidLogs);

    setStatistics({
      totalWorkers: 12,
      activeAlerts: mockSensors.filter(s => s.status !== 'normal').length,
      systemUptime: 99.8,
      dataPoints: 15420
    });
  };

  // Filter sensors based on mode
  const getActiveSensors = () => {
    return sensors.filter(sensor => 
      modeConfig.primarySensors.includes(sensor.type)
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const activeSensors = getActiveSensors();

  return (
    <div className="space-y-6">
      {/* Statistics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card gradient-primary text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm opacity-90">Total Workers</p>
              <p className="text-3xl font-bold">{statistics.totalWorkers}</p>
            </div>
            <Users className="h-10 w-10 opacity-80" />
          </div>
        </div>

        <div className="card gradient-warning text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm opacity-90">Active Alerts</p>
              <p className="text-3xl font-bold">{statistics.activeAlerts}</p>
            </div>
            <AlertTriangle className="h-10 w-10 opacity-80" />
          </div>
        </div>

        <div className="card gradient-success text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm opacity-90">System Uptime</p>
              <p className="text-3xl font-bold">{statistics.systemUptime}%</p>
            </div>
            <TrendingUp className="h-10 w-10 opacity-80" />
          </div>
        </div>

        <div className="card bg-gradient-to-br from-purple-500 to-purple-700 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm opacity-90">Data Points</p>
              <p className="text-3xl font-bold">{statistics.dataPoints.toLocaleString()}</p>
            </div>
            <Activity className="h-10 w-10 opacity-80" />
          </div>
        </div>
      </div>

      {/* Mode Switch and Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <ModeSwitch />
        </div>
        <div className="lg:col-span-2">
          <AlertPanel />
        </div>
      </div>

      {/* Sensor Cards */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          Sensor Monitoring
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {activeSensors.map(sensor => (
            <SensorCard key={sensor.id} sensor={sensor} />
          ))}
        </div>
      </div>

      {/* Charts */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          Real-Time Analytics
        </h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {activeSensors.slice(0, 4).map(sensor => (
            sensorHistory[sensor.id] && (
              <Chart
                key={sensor.id}
                title={`${sensor.name} Trend`}
                data={sensorHistory[sensor.id]}
                dataKey="value"
                type="line"
                color={
                  sensor.status === 'danger' ? '#ef4444' :
                  sensor.status === 'warning' ? '#f59e0b' :
                  '#22c55e'
                }
              />
            )
          ))}
        </div>
      </div>

      {/* RFID Logs */}
      {modeConfig.features.accessControl && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Recent RFID Activity
          </h3>
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-slate-700">
                  <th className="px-4 py-2 text-left text-sm font-semibold text-gray-900 dark:text-white">
                    Worker
                  </th>
                  <th className="px-4 py-2 text-left text-sm font-semibold text-gray-900 dark:text-white">
                    Action
                  </th>
                  <th className="px-4 py-2 text-left text-sm font-semibold text-gray-900 dark:text-white">
                    Location
                  </th>
                  <th className="px-4 py-2 text-left text-sm font-semibold text-gray-900 dark:text-white">
                    Time
                  </th>
                </tr>
              </thead>
              <tbody>
                {rfidLogs.map((log, index) => (
                  <tr
                    key={log.id}
                    className={`border-b border-gray-100 dark:border-slate-700 ${
                      index % 2 === 0 ? 'bg-gray-50 dark:bg-slate-800/50' : ''
                    }`}
                  >
                    <td className="px-4 py-3 text-sm text-gray-900 dark:text-white">
                      {log.workerName} ({log.workerId})
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          log.action === 'entry'
                            ? 'bg-success-100 dark:bg-success-900/30 text-success-700 dark:text-success-300'
                            : 'bg-danger-100 dark:bg-danger-900/30 text-danger-700 dark:text-danger-300'
                        }`}
                      >
                        {log.action.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                      {log.location}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
