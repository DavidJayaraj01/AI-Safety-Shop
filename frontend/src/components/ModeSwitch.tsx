import React from 'react';
import { Factory, HardHat, ToggleLeft, ToggleRight } from 'lucide-react';
import { useModeContext } from '../context/ModeContext';

const ModeSwitch = () => {
  const { mode, toggleMode, modeConfig } = useModeContext();

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Operating Mode
        </h3>
        <button
          onClick={toggleMode}
          className={`p-2 rounded-lg transition-all transform hover:scale-105 ${
            mode === 'heavy-industry'
              ? 'bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400'
              : 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
          }`}
        >
          {mode === 'heavy-industry' ? (
            <ToggleRight className="h-8 w-8" />
          ) : (
            <ToggleLeft className="h-8 w-8" />
          )}
        </button>
      </div>

      {/* Current Mode Display */}
      <div className={`p-6 rounded-lg border-2 transition-all ${
        mode === 'heavy-industry'
          ? 'border-orange-300 dark:border-orange-700 bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20'
          : 'border-blue-300 dark:border-blue-700 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20'
      }`}>
        <div className="flex items-center space-x-4 mb-4">
          <div className={`p-4 rounded-full ${
            mode === 'heavy-industry'
              ? 'bg-orange-200 dark:bg-orange-800/50'
              : 'bg-blue-200 dark:bg-blue-800/50'
          }`}>
            {mode === 'heavy-industry' ? (
              <Factory className={`h-8 w-8 ${
                mode === 'heavy-industry'
                  ? 'text-orange-700 dark:text-orange-300'
                  : 'text-blue-700 dark:text-blue-300'
              }`} />
            ) : (
              <HardHat className={`h-8 w-8 ${
                mode === 'heavy-industry'
                  ? 'text-orange-700 dark:text-orange-300'
                  : 'text-blue-700 dark:text-blue-300'
              }`} />
            )}
          </div>
          <div>
            <h4 className={`text-xl font-bold ${
              mode === 'heavy-industry'
                ? 'text-orange-800 dark:text-orange-200'
                : 'text-blue-800 dark:text-blue-200'
            }`}>
              {modeConfig.name}
            </h4>
            <p className={`text-sm ${
              mode === 'heavy-industry'
                ? 'text-orange-700 dark:text-orange-300'
                : 'text-blue-700 dark:text-blue-300'
            }`}>
              {modeConfig.description}
            </p>
          </div>
        </div>

        {/* Features List */}
        <div className="space-y-2">
          <p className={`text-sm font-semibold ${
            mode === 'heavy-industry'
              ? 'text-orange-800 dark:text-orange-200'
              : 'text-blue-800 dark:text-blue-200'
          }`}>
            Active Features:
          </p>
          <ul className="space-y-1">
            {Object.entries(modeConfig.features).map(([feature, enabled]) => (
              enabled && (
                <li
                  key={feature}
                  className={`flex items-center space-x-2 text-sm ${
                    mode === 'heavy-industry'
                      ? 'text-orange-700 dark:text-orange-300'
                      : 'text-blue-700 dark:text-blue-300'
                  }`}
                >
                  <div className={`h-2 w-2 rounded-full ${
                    mode === 'heavy-industry'
                      ? 'bg-orange-500'
                      : 'bg-blue-500'
                  }`} />
                  <span className="capitalize">
                    {feature.replace(/([A-Z])/g, ' $1').trim()}
                  </span>
                </li>
              )
            ))}
          </ul>
        </div>

        {/* Monitored Sensors */}
        <div className="mt-4 pt-4 border-t border-current/20">
          <p className={`text-sm font-semibold mb-2 ${
            mode === 'heavy-industry'
              ? 'text-orange-800 dark:text-orange-200'
              : 'text-blue-800 dark:text-blue-200'
          }`}>
            Primary Sensors:
          </p>
          <div className="flex flex-wrap gap-2">
            {modeConfig.primarySensors.map((sensor) => (
              <span
                key={sensor}
                className={`px-3 py-1 rounded-full text-xs font-medium ${
                  mode === 'heavy-industry'
                    ? 'bg-orange-200 dark:bg-orange-800/50 text-orange-800 dark:text-orange-200'
                    : 'bg-blue-200 dark:bg-blue-800/50 text-blue-800 dark:text-blue-200'
                }`}
              >
                {sensor.toUpperCase()}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Switch Button */}
      <button
        onClick={toggleMode}
        className={`w-full mt-4 py-3 rounded-lg font-semibold transition-all transform hover:scale-105 ${
          mode === 'heavy-industry'
            ? 'bg-blue-600 hover:bg-blue-700 text-white'
            : 'bg-orange-600 hover:bg-orange-700 text-white'
        }`}
      >
        Switch to {mode === 'heavy-industry' ? 'Shop Floor' : 'Heavy Industry'} Mode
      </button>
    </div>
  );
};

export default ModeSwitch;
