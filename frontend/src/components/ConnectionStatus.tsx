import { Activity } from 'lucide-react';

interface ConnectionStatusProps {
  isConnected: boolean;
}

export const ConnectionStatus = ({ isConnected }: ConnectionStatusProps) => {
  return (
    <div 
      className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-100 dark:bg-gray-700 transition-all"
      title={isConnected ? 'Connected to real-time updates' : 'Disconnected - Attempting to reconnect...'}
    >
      {/* Status Dot */}
      <div className="relative flex items-center justify-center">
        <div 
          className={`
            w-2 h-2 rounded-full
            ${isConnected ? 'bg-success-500' : 'bg-danger-500'}
            ${isConnected ? 'animate-pulse' : ''}
          `}
        />
        {isConnected && (
          <div className="absolute w-2 h-2 rounded-full bg-success-500 opacity-20 animate-ping" />
        )}
      </div>

      {/* Status Text */}
      <span className={`text-xs font-medium ${
        isConnected 
          ? 'text-success-700 dark:text-success-400' 
          : 'text-danger-700 dark:text-danger-400'
      }`}>
        {isConnected ? 'Live' : 'Offline'}
      </span>

      {/* Activity Icon (optional) */}
      {isConnected && (
        <Activity className="w-3 h-3 text-success-600 dark:text-success-400" />
      )}
    </div>
  );
};
