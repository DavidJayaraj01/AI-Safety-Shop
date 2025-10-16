import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  FileText, 
  Settings, 
  Bell, 
  Moon, 
  Sun,
  Activity
} from 'lucide-react';
import { useState, useEffect } from 'react';
import { useAlertStore } from '../context/AlertContext';
import { useModeStore } from '../context/ModeContext';
import { useWebSocketStore } from '../context/WebSocketStore';

export const Navbar = () => {
  const location = useLocation();
  const [darkMode, setDarkMode] = useState(false);
  const { unreadCount } = useAlertStore();
  const { mode } = useModeStore();
  const { isConnected } = useWebSocketStore();

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Reports', path: '/reports', icon: FileText },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <nav className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Activity className="w-8 h-8 text-primary-600 mr-3" />
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">
              AI Safety IoT Dashboard
            </h1>
            <div className="ml-4 px-3 py-1 rounded-full text-xs font-medium bg-primary-100 dark:bg-primary-900 text-primary-800 dark:text-primary-200">
              {mode === 'heavy_industry' ? 'Heavy Industry' : 'Shop Floor'} Mode
            </div>
            
            {/* Connection Status Indicator */}
            <div 
              className="ml-3 flex items-center cursor-default"
              title={isConnected ? 'Connected to real-time updates' : 'Disconnected - Attempting to reconnect...'}
            >
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-success-500' : 'bg-danger-500'} ${isConnected ? 'animate-pulse' : ''}`} />
              <span className="ml-2 text-xs text-gray-600 dark:text-gray-400">
                {isConnected ? 'Live' : 'Offline'}
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {item.name}
                </Link>
              );
            })}

            <button className="relative p-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md">
              <Bell className="w-5 h-5" />
              {unreadCount > 0 && (
                <span className="absolute top-1 right-1 w-4 h-4 bg-danger-600 text-white text-xs rounded-full flex items-center justify-center">
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </button>

            <button
              onClick={() => setDarkMode(!darkMode)}
              className="p-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md"
            >
              {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};
