import { useState, useEffect } from 'react';
import {
  Flame,
  Thermometer,
  Activity,
  Ruler,
  CreditCard,
  Droplets,
  AlertTriangle
} from 'lucide-react';
import SensorCard from '../components/SensorCard';
import Chart from '../components/Chart';
import AlertPanel from '../components/AlertPanel';
import ModeSwitch from '../components/ModeSwitch';
import { useModeContext } from '../context/ModeContext';
import { arduinoSensorsApi } from '../services/api';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const { } = useModeContext();
  const [sensors, setSensors] = useState<any[]>([]);
  const [sensorHistory, setSensorHistory] = useState<any>({});
  const [rfidTag, setRfidTag] = useState('None');
  const [isConnected, setIsConnected] = useState(false);
  const [statistics, setStatistics] = useState({
    totalWorkers: 0,
    activeAlerts: 0,
    systemUptime: 0,
    dataPoints: 0
  });
  const [isLoading, setIsLoading] = useState(true);

  // Sensor configurations matching Arduino output
  const sensorConfig = {
    temperature: {
      name: 'Temperature',
      type: 'temperature',
      unit: '°C',
      icon: Thermometer,
      threshold: { warning: 35, danger: 45 }
    },
    humidity: {
      name: 'Humidity',
      type: 'humidity',
      unit: '%',
      icon: Droplets,
      threshold: { warning: 70, danger: 85 }
    },
    smoke: {
      name: 'Smoke Level',
      type: 'smoke',
      unit: 'ppm',
      icon: Flame,
      threshold: { warning: 300, danger: 500 }
    },
    distance: {
      name: 'Distance',
      type: 'distance',
      unit: 'cm',
      icon: Ruler,
      threshold: { warning: 50, danger: 20 }
    },
    rfid: {
      name: 'RFID Tag',
      type: 'rfid',
      unit: '',
      icon: CreditCard,
      threshold: null
    }
  };

  useEffect(() => {
    fetchArduinoData();
    const interval = setInterval(fetchArduinoData, 2000); // Update every 2 seconds for real-time data
    return () => clearInterval(interval);
  }, []);

  const fetchArduinoData = async () => {
    try {
      const response = await arduinoSensorsApi.getLiveSensorData();
      
      if (response.status === 'connected' && response.data) {
        setIsConnected(true);
        
        // Parse Arduino sensor data
        // Expected format from Arduino: { temperature: 25.5, humidity: 60, smoke: 150, distance: 30, rfid: "ABC123" }
        const arduinoData = response.data;
        
        // Transform Arduino data to match our sensor format
        const transformedSensors = Object.entries(sensorConfig).map(([key, config]) => {
          let value;
          
          if (key === 'temperature') {
            value = parseFloat(arduinoData.temperature || 0);
          } else if (key === 'humidity') {
            value = parseFloat(arduinoData.humidity || 0);
          } else if (key === 'smoke') {
            value = parseInt(arduinoData.smoke || 0);
          } else if (key === 'distance') {
            value = parseFloat(arduinoData.distance || 0);
          } else if (key === 'rfid') {
            value = arduinoData.rfid || 'None';
            setRfidTag(value);
          }
          
          const status = determineStatus(value, config.threshold);
          
          return {
            id: key,
            ...config,
            value,
            status,
            lastUpdate: new Date().toISOString(),
            trend: 'stable' // Can be enhanced later with trend analysis
          };
        });
        
        setSensors(transformedSensors);
        
        // Update sensor history for charts
        updateSensorHistory(arduinoData);
        
        // Update statistics
        const alertCount = transformedSensors.filter(s => s.status === 'danger' || s.status === 'warning').length;
        setStatistics(prev => ({
          ...prev,
          activeAlerts: alertCount,
          dataPoints: prev.dataPoints + 1
        }));
        
        // Show toast notification for critical alerts
        const dangerSensors = transformedSensors.filter(s => s.status === 'danger');
        if (dangerSensors.length > 0) {
          toast.error(`Critical Alert: ${dangerSensors.map(s => s.name).join(', ')} exceeded danger threshold!`);
        }
        
        setIsLoading(false);
      } else {
        // Arduino disconnected
        setIsConnected(false);
        if (!isLoading) {
          toast.error('Arduino connection lost! Using mock data...');
        }
        generateMockData();
      }
    } catch (error) {
      console.error('Error fetching Arduino data:', error);
      setIsConnected(false);
      if (!isLoading) {
        toast.error('Failed to connect to Arduino sensors');
      }
      generateMockData();
    }
  };

  const updateSensorHistory = (data: any) => {
    const timestamp = new Date().toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
    
    setSensorHistory((prev: any) => {
      const newHistory = { ...prev };
      const maxDataPoints = 20;
      
      // Update history for each sensor
      ['temperature', 'humidity', 'smoke', 'distance'].forEach(key => {
        if (!newHistory[key]) {
          newHistory[key] = [];
        }
        
        newHistory[key] = [
          ...newHistory[key].slice(-maxDataPoints + 1),
          {
            timestamp,
            value: parseFloat(data[key] || 0)
          }
        ];
      });
      
      return newHistory;
    });
  };

  const determineStatus = (value: any, threshold: any) => {
    if (!threshold || value === 'None' || value === null) return 'normal';
    const numValue = parseFloat(value);
    if (isNaN(numValue)) return 'normal';
    if (numValue >= threshold.danger) return 'danger';
    if (numValue >= threshold.warning) return 'warning';
    return 'normal';
  };

  const generateMockData = () => {
    const mockSensors = Object.entries(sensorConfig).map(([key, config]) => {
      let value;
      if (key === 'smoke') value = Math.random() * 600;
      else if (key === 'temperature') value = 20 + Math.random() * 30;
      else if (key === 'humidity') value = 30 + Math.random() * 60;
      else if (key === 'distance') value = Math.random() * 100;
      else if (key === 'rfid') value = 'None';

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
    const mockHistory: any = {};
    Object.keys(sensorConfig).forEach(key => {
      if (key !== 'rfid') {
        mockHistory[key] = Array.from({ length: 20 }, (_, i) => ({
          timestamp: new Date(Date.now() - (19 - i) * 60000).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
          }),
          value: Math.random() * 100
        }));
      }
    });
    setSensorHistory(mockHistory);

    setStatistics({
      totalWorkers: 0,
      activeAlerts: mockSensors.filter(s => s.status !== 'normal').length,
      systemUptime: 99.8,
      dataPoints: 0
    });
    setIsLoading(false);
  };

  // Filter sensors based on mode
  const getActiveSensors = () => {
    return sensors;
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
      {/* Connection Status Banner */}
      <div className={`card ${isConnected ? 'bg-success-50 dark:bg-success-900/20 border-2 border-success-300 dark:border-success-700' : 'bg-danger-50 dark:bg-danger-900/20 border-2 border-danger-300 dark:border-danger-700'}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`h-3 w-3 rounded-full ${isConnected ? 'bg-success-500' : 'bg-danger-500'} animate-pulse`} />
            <div>
              <p className="font-semibold text-gray-900 dark:text-white">
                Arduino {isConnected ? 'Connected' : 'Disconnected'}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {isConnected ? 'Receiving live sensor data from http://10.115.11.112/' : 'Showing mock data - Check Arduino connection'}
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-xs text-gray-500 dark:text-gray-400">Current RFID Tag</p>
            <p className="text-lg font-bold text-gray-900 dark:text-white">{rfidTag}</p>
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card gradient-primary text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm opacity-90">Temperature</p>
              <p className="text-3xl font-bold">
                {sensors.find(s => s.type === 'temperature')?.value?.toFixed(1) || '--'}°C
              </p>
            </div>
            <Thermometer className="h-10 w-10 opacity-80" />
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
              <p className="text-sm opacity-90">Humidity</p>
              <p className="text-3xl font-bold">
                {sensors.find(s => s.type === 'humidity')?.value?.toFixed(1) || '--'}%
              </p>
            </div>
            <Droplets className="h-10 w-10 opacity-80" />
          </div>
        </div>

        <div className="card bg-gradient-to-br from-purple-500 to-purple-700 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm opacity-90">Data Points</p>
              <p className="text-3xl font-bold">{statistics.dataPoints}</p>
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
          Live Sensor Monitoring
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
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
          {['temperature', 'humidity', 'smoke', 'distance'].map(sensorType => {
            const sensor = sensors.find(s => s.type === sensorType);
            return sensorHistory[sensorType] && sensor && (
              <Chart
                key={sensorType}
                title={`${sensor.name} Trend`}
                data={sensorHistory[sensorType]}
                dataKey="value"
                type="line"
                color={
                  sensor.status === 'danger' ? '#ef4444' :
                  sensor.status === 'warning' ? '#f59e0b' :
                  '#22c55e'
                }
              />
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
