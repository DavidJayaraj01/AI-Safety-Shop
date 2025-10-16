import React, { useState } from 'react';
import {
  Settings as SettingsIcon,
  Bell,
  Zap,
  Database,
  Wifi,
  Save,
  RotateCcw,
  Shield,
  Mail,
  Phone
} from 'lucide-react';
import { useModeContext } from '../context/ModeContext';
import toast from 'react-hot-toast';

const Settings = () => {
  const { mode, modeConfig, toggleMode, isDarkMode, toggleDarkMode } = useModeContext();

  const [settings, setSettings] = useState({
    // Alert Settings
    enableSoundAlerts: true,
    enableEmailAlerts: true,
    enableSMSAlerts: false,
    alertEmailAddress: 'admin@safetysystem.com',
    alertPhoneNumber: '+1234567890',
    
    // Threshold Settings
    gasWarningThreshold: 50,
    gasDangerThreshold: 100,
    tempWarningThreshold: 35,
    tempDangerThreshold: 45,
    vibrationWarningThreshold: 5,
    vibrationDangerThreshold: 10,
    proximityWarningThreshold: 50,
    proximityDangerThreshold: 20,

    // System Settings
    dataRefreshInterval: 5,
    autoShutdownEnabled: true,
    maintenanceMode: false,
    
    // Connection Settings
    apiEndpoint: 'http://localhost:8000',
    mqttBroker: 'mqtt://localhost:1883',
    databaseUrl: 'mongodb://localhost:27017',
    
    // AI Settings
    aiPredictionEnabled: true,
    aiConfidenceThreshold: 75,
    anomalyDetectionSensitivity: 'medium'
  });

  const [hasChanges, setHasChanges] = useState(false);

  const handleInputChange = (field, value) => {
    setSettings(prev => ({ ...prev, [field]: value }));
    setHasChanges(true);
  };

  const handleSaveSettings = () => {
    // In a real app, this would save to the backend
    localStorage.setItem('safetySystemSettings', JSON.stringify(settings));
    toast.success('Settings saved successfully!');
    setHasChanges(false);
  };

  const handleResetSettings = () => {
    // Reset to defaults
    toast((t) => (
      <div>
        <p className="font-semibold mb-2">Reset all settings to default?</p>
        <div className="flex space-x-2">
          <button
            onClick={() => {
              setSettings({
                ...settings,
                gasWarningThreshold: 50,
                gasDangerThreshold: 100,
                tempWarningThreshold: 35,
                tempDangerThreshold: 45,
                vibrationWarningThreshold: 5,
                vibrationDangerThreshold: 10,
                proximityWarningThreshold: 50,
                proximityDangerThreshold: 20,
                dataRefreshInterval: 5,
              });
              toast.success('Settings reset to default');
              toast.dismiss(t.id);
              setHasChanges(true);
            }}
            className="btn-danger text-sm"
          >
            Reset
          </button>
          <button
            onClick={() => toast.dismiss(t.id)}
            className="px-3 py-1 text-sm bg-gray-300 dark:bg-slate-600 rounded-lg"
          >
            Cancel
          </button>
        </div>
      </div>
    ), { duration: 5000 });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            System Settings
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Configure system preferences and thresholds
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={handleResetSettings}
            className="flex items-center space-x-2 px-4 py-2 rounded-lg border border-gray-300 dark:border-slate-600 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700 transition-colors"
          >
            <RotateCcw size={18} />
            <span>Reset</span>
          </button>
          <button
            onClick={handleSaveSettings}
            disabled={!hasChanges}
            className={`btn-primary flex items-center space-x-2 ${
              !hasChanges ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            <Save size={18} />
            <span>Save Changes</span>
          </button>
        </div>
      </div>

      {/* Operating Mode */}
      <div className="card">
        <div className="flex items-center space-x-3 mb-4">
          <Shield className="h-6 w-6 text-primary-600 dark:text-primary-400" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Operating Mode
          </h2>
        </div>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 rounded-lg bg-gray-50 dark:bg-slate-800/50">
            <div>
              <p className="font-medium text-gray-900 dark:text-white">
                Current Mode: {modeConfig.name}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                {modeConfig.description}
              </p>
            </div>
            <button
              onClick={toggleMode}
              className="btn-primary"
            >
              Switch Mode
            </button>
          </div>

          <div className="flex items-center justify-between p-4 rounded-lg bg-gray-50 dark:bg-slate-800/50">
            <div>
              <p className="font-medium text-gray-900 dark:text-white">
                Theme: {isDarkMode ? 'Dark' : 'Light'} Mode
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Toggle between light and dark appearance
              </p>
            </div>
            <button
              onClick={toggleDarkMode}
              className="btn-primary"
            >
              Toggle Theme
            </button>
          </div>
        </div>
      </div>

      {/* Alert Configuration */}
      <div className="card">
        <div className="flex items-center space-x-3 mb-4">
          <Bell className="h-6 w-6 text-primary-600 dark:text-primary-400" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Alert Configuration
          </h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Sound Alerts
              </label>
              <input
                type="checkbox"
                checked={settings.enableSoundAlerts}
                onChange={(e) => handleInputChange('enableSoundAlerts', e.target.checked)}
                className="h-5 w-5 rounded text-primary-600 focus:ring-primary-500"
              />
            </div>
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Email Alerts
              </label>
              <input
                type="checkbox"
                checked={settings.enableEmailAlerts}
                onChange={(e) => handleInputChange('enableEmailAlerts', e.target.checked)}
                className="h-5 w-5 rounded text-primary-600 focus:ring-primary-500"
              />
            </div>
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                SMS Alerts
              </label>
              <input
                type="checkbox"
                checked={settings.enableSMSAlerts}
                onChange={(e) => handleInputChange('enableSMSAlerts', e.target.checked)}
                className="h-5 w-5 rounded text-primary-600 focus:ring-primary-500"
              />
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <Mail className="inline h-4 w-4 mr-1" />
                Alert Email Address
              </label>
              <input
                type="email"
                value={settings.alertEmailAddress}
                onChange={(e) => handleInputChange('alertEmailAddress', e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <Phone className="inline h-4 w-4 mr-1" />
                Alert Phone Number
              </label>
              <input
                type="tel"
                value={settings.alertPhoneNumber}
                onChange={(e) => handleInputChange('alertPhoneNumber', e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Sensor Thresholds */}
      <div className="card">
        <div className="flex items-center space-x-3 mb-4">
          <Zap className="h-6 w-6 text-primary-600 dark:text-primary-400" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Sensor Thresholds
          </h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Gas Sensor */}
          <div className="space-y-3">
            <h3 className="font-medium text-gray-900 dark:text-white">Gas Sensor (ppm)</h3>
            <div>
              <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">
                Warning Threshold
              </label>
              <input
                type="number"
                value={settings.gasWarningThreshold}
                onChange={(e) => handleInputChange('gasWarningThreshold', Number(e.target.value))}
                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">
                Danger Threshold
              </label>
              <input
                type="number"
                value={settings.gasDangerThreshold}
                onChange={(e) => handleInputChange('gasDangerThreshold', Number(e.target.value))}
                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          {/* Temperature Sensor */}
          <div className="space-y-3">
            <h3 className="font-medium text-gray-900 dark:text-white">Temperature (°C)</h3>
            <div>
              <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">
                Warning Threshold
              </label>
              <input
                type="number"
                value={settings.tempWarningThreshold}
                onChange={(e) => handleInputChange('tempWarningThreshold', Number(e.target.value))}
                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">
                Danger Threshold
              </label>
              <input
                type="number"
                value={settings.tempDangerThreshold}
                onChange={(e) => handleInputChange('tempDangerThreshold', Number(e.target.value))}
                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          {/* Vibration Sensor */}
          <div className="space-y-3">
            <h3 className="font-medium text-gray-900 dark:text-white">Vibration (g)</h3>
            <div>
              <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">
                Warning Threshold
              </label>
              <input
                type="number"
                value={settings.vibrationWarningThreshold}
                onChange={(e) => handleInputChange('vibrationWarningThreshold', Number(e.target.value))}
                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">
                Danger Threshold
              </label>
              <input
                type="number"
                value={settings.vibrationDangerThreshold}
                onChange={(e) => handleInputChange('vibrationDangerThreshold', Number(e.target.value))}
                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          {/* Proximity Sensor */}
          <div className="space-y-3">
            <h3 className="font-medium text-gray-900 dark:text-white">Proximity (cm)</h3>
            <div>
              <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">
                Warning Threshold
              </label>
              <input
                type="number"
                value={settings.proximityWarningThreshold}
                onChange={(e) => handleInputChange('proximityWarningThreshold', Number(e.target.value))}
                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">
                Danger Threshold
              </label>
              <input
                type="number"
                value={settings.proximityDangerThreshold}
                onChange={(e) => handleInputChange('proximityDangerThreshold', Number(e.target.value))}
                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>
        </div>
      </div>

      {/* System Configuration */}
      <div className="card">
        <div className="flex items-center space-x-3 mb-4">
          <Database className="h-6 w-6 text-primary-600 dark:text-primary-400" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            System Configuration
          </h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Data Refresh Interval (seconds)
            </label>
            <input
              type="number"
              value={settings.dataRefreshInterval}
              onChange={(e) => handleInputChange('dataRefreshInterval', Number(e.target.value))}
              min="1"
              max="60"
              className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Auto-Shutdown System
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Automatically shutdown on critical alerts
              </p>
            </div>
            <input
              type="checkbox"
              checked={settings.autoShutdownEnabled}
              onChange={(e) => handleInputChange('autoShutdownEnabled', e.target.checked)}
              className="h-5 w-5 rounded text-primary-600 focus:ring-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              <Wifi className="inline h-4 w-4 mr-1" />
              API Endpoint
            </label>
            <input
              type="url"
              value={settings.apiEndpoint}
              onChange={(e) => handleInputChange('apiEndpoint', e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              MQTT Broker
            </label>
            <input
              type="text"
              value={settings.mqttBroker}
              onChange={(e) => handleInputChange('mqttBroker', e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>
      </div>

      {/* AI Configuration */}
      <div className="card bg-gradient-to-br from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20 border-2 border-purple-200 dark:border-purple-800">
        <div className="flex items-center space-x-3 mb-4">
          <Zap className="h-6 w-6 text-purple-600 dark:text-purple-400" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            AI Configuration
          </h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                AI Prediction
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Enable predictive analysis
              </p>
            </div>
            <input
              type="checkbox"
              checked={settings.aiPredictionEnabled}
              onChange={(e) => handleInputChange('aiPredictionEnabled', e.target.checked)}
              className="h-5 w-5 rounded text-purple-600 focus:ring-purple-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Confidence Threshold (%)
            </label>
            <input
              type="number"
              value={settings.aiConfidenceThreshold}
              onChange={(e) => handleInputChange('aiConfidenceThreshold', Number(e.target.value))}
              min="0"
              max="100"
              className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Anomaly Detection Sensitivity
            </label>
            <select
              value={settings.anomalyDetectionSensitivity}
              onChange={(e) => handleInputChange('anomalyDetectionSensitivity', e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="low">Low - Fewer false positives</option>
              <option value="medium">Medium - Balanced</option>
              <option value="high">High - More sensitive</option>
            </select>
          </div>
        </div>
      </div>

      {/* Save/Reset Actions */}
      {hasChanges && (
        <div className="card bg-warning-50 dark:bg-warning-900/20 border-2 border-warning-300 dark:border-warning-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Bell className="h-6 w-6 text-warning-600 dark:text-warning-400" />
              <div>
                <p className="font-semibold text-gray-900 dark:text-white">
                  You have unsaved changes
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Don't forget to save your settings before leaving this page
                </p>
              </div>
            </div>
            <button
              onClick={handleSaveSettings}
              className="btn-primary"
            >
              Save Now
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Settings;
