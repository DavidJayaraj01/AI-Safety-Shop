import { useState, useEffect } from 'react';
import { settingsAPI, modeAPI } from '../services/api';
import type { SystemSettings, ModeConfig } from '../types';
import { Save, Bell, Camera, Thermometer, Wind } from 'lucide-react';
import toast from 'react-hot-toast';

export const Settings = () => {
  const [settings, setSettings] = useState<SystemSettings>({
    notifications: {
      email: true,
      sms: true,
      telegram: false,
      slack: false,
      inApp: true,
    },
    thresholds: {
      gas: {
        warning: 300,
        critical: 500,
      },
      temperature: {
        warning: 40,
        critical: 60,
      },
      vibration: {
        warning: 8,
        critical: 15,
      },
    },
    autoShutdown: false,
    alertCooldown: 5,
    ppeConfidenceThreshold: 0.6,
    cameraSettings: {
      enabled: true,
      fps: 30,
      resolution: '1920x1080',
    },
  });

  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const res = await settingsAPI.get();
      if (res.data.success && res.data.data) {
        setSettings(res.data.data);
      }
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  };

  const saveSettings = async () => {
    try {
      setSaving(true);
      await settingsAPI.update(settings);
      toast.success('Settings saved successfully');
    } catch (error) {
      console.error('Error saving settings:', error);
      toast.error('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          System Settings
        </h1>
        <button
          onClick={saveSettings}
          disabled={saving}
          className="btn-primary flex items-center"
        >
          <Save className="w-4 h-4 mr-2" />
          {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>

      {/* Notification Settings */}
      <div className="card">
        <div className="flex items-center mb-4">
          <Bell className="w-6 h-6 text-primary-600 mr-3" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Notification Channels
          </h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(settings.notifications).map(([key, value]) => (
            <label key={key} className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer">
              <input
                type="checkbox"
                checked={value}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    notifications: {
                      ...settings.notifications,
                      [key]: e.target.checked,
                    },
                  })
                }
                className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
              />
              <span className="text-gray-900 dark:text-white capitalize">
                {key.replace(/([A-Z])/g, ' $1').trim()}
              </span>
            </label>
          ))}
        </div>
      </div>

      {/* Sensor Thresholds */}
      <div className="card">
        <div className="flex items-center mb-4">
          <Thermometer className="w-6 h-6 text-primary-600 mr-3" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Sensor Thresholds
          </h2>
        </div>

        <div className="space-y-6">
          {/* Gas Sensor */}
          <div>
            <h3 className="font-medium mb-3 text-gray-900 dark:text-white flex items-center">
              <Wind className="w-4 h-4 mr-2" />
              Gas Sensor (PPM)
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                  Warning Level
                </label>
                <input
                  type="number"
                  value={settings.thresholds.gas.warning}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      thresholds: {
                        ...settings.thresholds,
                        gas: {
                          ...settings.thresholds.gas,
                          warning: Number(e.target.value),
                        },
                      },
                    })
                  }
                  className="input w-full"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                  Critical Level
                </label>
                <input
                  type="number"
                  value={settings.thresholds.gas.critical}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      thresholds: {
                        ...settings.thresholds,
                        gas: {
                          ...settings.thresholds.gas,
                          critical: Number(e.target.value),
                        },
                      },
                    })
                  }
                  className="input w-full"
                />
              </div>
            </div>
          </div>

          {/* Temperature Sensor */}
          <div>
            <h3 className="font-medium mb-3 text-gray-900 dark:text-white">
              Temperature Sensor (°C)
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                  Warning Level
                </label>
                <input
                  type="number"
                  value={settings.thresholds.temperature.warning}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      thresholds: {
                        ...settings.thresholds,
                        temperature: {
                          ...settings.thresholds.temperature,
                          warning: Number(e.target.value),
                        },
                      },
                    })
                  }
                  className="input w-full"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                  Critical Level
                </label>
                <input
                  type="number"
                  value={settings.thresholds.temperature.critical}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      thresholds: {
                        ...settings.thresholds,
                        temperature: {
                          ...settings.thresholds.temperature,
                          critical: Number(e.target.value),
                        },
                      },
                    })
                  }
                  className="input w-full"
                />
              </div>
            </div>
          </div>

          {/* Vibration Sensor */}
          <div>
            <h3 className="font-medium mb-3 text-gray-900 dark:text-white">
              Vibration Sensor (m/s²)
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                  Warning Level
                </label>
                <input
                  type="number"
                  value={settings.thresholds.vibration.warning}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      thresholds: {
                        ...settings.thresholds,
                        vibration: {
                          ...settings.thresholds.vibration,
                          warning: Number(e.target.value),
                        },
                      },
                    })
                  }
                  className="input w-full"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                  Critical Level
                </label>
                <input
                  type="number"
                  value={settings.thresholds.vibration.critical}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      thresholds: {
                        ...settings.thresholds,
                        vibration: {
                          ...settings.thresholds.vibration,
                          critical: Number(e.target.value),
                        },
                      },
                    })
                  }
                  className="input w-full"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Camera Settings */}
      <div className="card">
        <div className="flex items-center mb-4">
          <Camera className="w-6 h-6 text-primary-600 mr-3" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Camera & PPE Detection
          </h2>
        </div>

        <div className="space-y-4">
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={settings.cameraSettings.enabled}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  cameraSettings: {
                    ...settings.cameraSettings,
                    enabled: e.target.checked,
                  },
                })
              }
              className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
            />
            <span className="text-gray-900 dark:text-white">
              Enable Camera Detection
            </span>
          </label>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              PPE Detection Confidence Threshold
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={settings.ppeConfidenceThreshold}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  ppeConfidenceThreshold: Number(e.target.value),
                })
              }
              className="w-full"
            />
            <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
              <span>0%</span>
              <span className="font-medium text-primary-600">
                {(settings.ppeConfidenceThreshold * 100).toFixed(0)}%
              </span>
              <span>100%</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Frame Rate (FPS)
            </label>
            <select
              value={settings.cameraSettings.fps}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  cameraSettings: {
                    ...settings.cameraSettings,
                    fps: Number(e.target.value),
                  },
                })
              }
              className="input w-full"
            >
              <option value={15}>15 FPS</option>
              <option value={24}>24 FPS</option>
              <option value={30}>30 FPS</option>
              <option value={60}>60 FPS</option>
            </select>
          </div>
        </div>
      </div>

      {/* Safety Settings */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
          Safety Features
        </h2>
        <div className="space-y-4">
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={settings.autoShutdown}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  autoShutdown: e.target.checked,
                })
              }
              className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
            />
            <span className="text-gray-900 dark:text-white">
              Enable Auto-Shutdown on Critical Alerts
            </span>
          </label>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Alert Cooldown Period (minutes)
            </label>
            <input
              type="number"
              value={settings.alertCooldown}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  alertCooldown: Number(e.target.value),
                })
              }
              className="input w-full"
              min="1"
              max="60"
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Prevent duplicate alerts within this time period
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
