import { 
  ShieldCheck, 
  Settings, 
  Moon, 
  Sun, 
  Bell, 
  Wifi, 
  WifiOff,
  Menu,
  X
} from 'lucide-react';
import { useModeContext } from '../context/ModeContext';
import { useAlertContext } from '../context/AlertContext';

interface NavbarProps {
  currentPage: string;
  setCurrentPage: (page: string) => void;
  isSidebarOpen: boolean;
  setIsSidebarOpen: (isOpen: boolean) => void;
}

const Navbar: React.FC<NavbarProps> = ({ currentPage, setCurrentPage, isSidebarOpen, setIsSidebarOpen }) => {
  const { isDarkMode, toggleDarkMode, modeConfig } = useModeContext();
  const { activeAlerts, isConnected } = useAlertContext();

  const dangerCount = activeAlerts.filter(alert => alert.severity === 'danger').length;
  const warningCount = activeAlerts.filter(alert => alert.severity === 'warning').length;

  const getStatusColor = () => {
    if (dangerCount > 0) return 'text-red-500';
    if (warningCount > 0) return 'text-yellow-500';
    return 'text-green-500';
  };

  return (
    <nav className="bg-white dark:bg-slate-800 shadow-lg border-b border-gray-200 dark:border-slate-700">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Left section */}
          <div className="flex items-center">
            {/* Mobile menu button */}
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="lg:hidden p-2 rounded-md text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              {isSidebarOpen ? <X size={24} /> : <Menu size={24} />}
            </button>

            {/* Logo and title */}
            <div className="flex items-center ml-2 lg:ml-0">
              <div className={`p-2 rounded-lg ${
                modeConfig.colors.primary === 'orange' 
                  ? 'bg-orange-100 dark:bg-orange-900' 
                  : 'bg-blue-100 dark:bg-blue-900'
              }`}>
                <ShieldCheck className={`h-8 w-8 ${
                  modeConfig.colors.primary === 'orange'
                    ? 'text-orange-600 dark:text-orange-400'
                    : 'text-blue-600 dark:text-blue-400'
                }`} />
              </div>
              <div className="ml-3">
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                  AI Safety IoT Dashboard
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {modeConfig.name}
                </p>
              </div>
            </div>
          </div>

          {/* Center section - Page title (hidden on mobile) */}
          <div className="hidden md:flex items-center">
            <h2 className="text-lg font-semibold text-gray-700 dark:text-gray-300 capitalize">
              {currentPage.replace('-', ' ')}
            </h2>
          </div>

          {/* Right section */}
          <div className="flex items-center space-x-4">
            {/* Connection status */}
            <div className="flex items-center space-x-2">
              {isConnected ? (
                <Wifi className="h-5 w-5 text-green-500" />
              ) : (
                <WifiOff className="h-5 w-5 text-red-500" />
              )}
              <span className="hidden sm:inline text-sm text-gray-600 dark:text-gray-400">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>

            {/* Alert indicator */}
            <div className="relative">
              <Bell className={`h-6 w-6 ${getStatusColor()}`} />
              {(dangerCount > 0 || warningCount > 0) && (
                <div className="absolute -top-2 -right-2 h-5 w-5 bg-red-500 rounded-full flex items-center justify-center">
                  <span className="text-xs text-white font-bold">
                    {dangerCount + warningCount > 9 ? '9+' : dangerCount + warningCount}
                  </span>
                </div>
              )}
            </div>

            {/* System status indicator */}
            <div className="hidden sm:flex items-center space-x-2">
              <div className={`h-3 w-3 rounded-full ${getStatusColor().replace('text-', 'bg-')} animate-pulse`} />
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {dangerCount > 0 ? 'DANGER' : warningCount > 0 ? 'WARNING' : 'NORMAL'}
              </span>
            </div>

            {/* Dark mode toggle */}
            <button
              onClick={toggleDarkMode}
              className="p-2 rounded-lg bg-gray-100 dark:bg-slate-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-slate-600 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-colors"
            >
              {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
            </button>

            {/* Settings button */}
            <button
              onClick={() => setCurrentPage('settings')}
              className={`p-2 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 ${
                currentPage === 'settings'
                  ? 'bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-400'
                  : 'bg-gray-100 dark:bg-slate-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-slate-600'
              }`}
            >
              <Settings size={20} />
            </button>
          </div>
        </div>
      </div>

      {/* Mobile page title */}
      <div className="md:hidden px-4 pb-2">
        <h2 className="text-lg font-semibold text-gray-700 dark:text-gray-300 capitalize">
          {currentPage.replace('-', ' ')}
        </h2>
      </div>
    </nav>
  );
};

export default Navbar;
