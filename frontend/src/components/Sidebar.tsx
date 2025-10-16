import { 
  LayoutDashboard, 
  FileText, 
  Settings, 
  X,
  ToggleLeft,
  ToggleRight,
  Factory,
  HardHat,
  Eye
} from 'lucide-react';
import { useModeContext } from '../context/ModeContext';

interface SidebarProps {
  currentPage: string;
  setCurrentPage: (page: string) => void;
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ currentPage, setCurrentPage, isOpen, setIsOpen }) => {
  const { mode, toggleMode, modeConfig } = useModeContext();

  const navigationItems = [
    {
      id: 'dashboard',
      name: 'Dashboard',
      icon: LayoutDashboard,
      description: 'Overview and monitoring'
    },
    {
      id: 'cv-monitoring',
      name: 'CV Monitoring',
      icon: Eye,
      description: 'Computer vision detection'
    },
    {
      id: 'reports',
      name: 'Reports',
      icon: FileText,
      description: 'Analytics and history'
    },
    {
      id: 'settings',
      name: 'Settings',
      icon: Settings,
      description: 'System configuration'
    }
  ];

  const handleNavigation = (pageId: string) => {
    setCurrentPage(pageId);
    if (window.innerWidth < 1024) {
      setIsOpen(false);
    }
  };

  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-20 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed left-0 top-16 h-[calc(100vh-4rem)] w-64 bg-white dark:bg-slate-800 shadow-xl border-r border-gray-200 dark:border-slate-700 z-30 transform transition-transform duration-300 ease-in-out overflow-y-auto
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0
      `}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-slate-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Navigation
          </h2>
          <button
            onClick={() => setIsOpen(false)}
            className="lg:hidden p-1 rounded-md text-gray-500 hover:bg-gray-100 dark:hover:bg-slate-700"
          >
            <X size={20} />
          </button>
        </div>

        {/* Mode Toggle */}
        <div className="p-4 border-b border-gray-200 dark:border-slate-700">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Operating Mode
            </span>
            <button
              onClick={toggleMode}
              className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-700 transition-colors"
            >
              {mode === 'heavy-industry' ? (
                <Factory className="h-5 w-5 text-orange-600 dark:text-orange-400" />
              ) : (
                <HardHat className="h-5 w-5 text-blue-600 dark:text-blue-400" />
              )}
              {mode === 'heavy-industry' ? (
                <ToggleRight className="h-6 w-6 text-orange-600" />
              ) : (
                <ToggleLeft className="h-6 w-6 text-blue-600" />
              )}
            </button>
          </div>
          
          <div className={`p-3 rounded-lg ${
            mode === 'heavy-industry' 
              ? 'bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800' 
              : 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800'
          }`}>
            <h3 className={`font-medium text-sm ${
              mode === 'heavy-industry' 
                ? 'text-orange-800 dark:text-orange-300' 
                : 'text-blue-800 dark:text-blue-300'
            }`}>
              {modeConfig.name}
            </h3>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
              {modeConfig.description}
            </p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 p-4 space-y-2">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPage === item.id;
            
            return (
              <button
                key={item.id}
                onClick={() => handleNavigation(item.id)}
                className={`
                  w-full flex items-center space-x-3 px-3 py-3 rounded-lg text-left transition-all duration-200
                  ${isActive
                    ? `${mode === 'heavy-industry' 
                        ? 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 border-l-4 border-orange-500' 
                        : 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border-l-4 border-blue-500'
                      }`
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700 hover:text-gray-900 dark:hover:text-white'
                  }
                `}
              >
                <Icon size={20} />
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">
                    {item.name}
                  </p>
                  <p className="text-xs opacity-75 truncate">
                    {item.description}
                  </p>
                </div>
              </button>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 dark:border-slate-700">
          <div className="text-center">
            <p className="text-xs text-gray-500 dark:text-gray-400">
              AI Safety Monitoring System
            </p>
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
              © 2024 Smart Shop Floors
            </p>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
