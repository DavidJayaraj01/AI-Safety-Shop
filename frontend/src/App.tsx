import { useState } from 'react';
import { Toaster } from 'react-hot-toast';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import CVMonitoring from './pages/CVMonitoring';
import Reports from './pages/Reports';
import Settings from './pages/Settings';
import { ModeProvider } from './context/ModeContext';
import { AlertProvider } from './context/AlertContext';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState<string>('dashboard');
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(false);

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />;
      case 'cv-monitoring':
        return <CVMonitoring />;
      case 'reports':
        return <Reports />;
      case 'settings':
        return <Settings />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <ModeProvider>
      <AlertProvider>
        <div className="min-h-screen bg-gray-50 dark:bg-slate-900 transition-colors duration-200">
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
              success: {
                duration: 3000,
                iconTheme: {
                  primary: '#22c55e',
                  secondary: '#fff',
                },
              },
              error: {
                duration: 5000,
                iconTheme: {
                  primary: '#ef4444',
                  secondary: '#fff',
                },
              },
            }}
          />
          
          <Navbar 
            currentPage={currentPage} 
            setCurrentPage={setCurrentPage}
            isSidebarOpen={isSidebarOpen}
            setIsSidebarOpen={setIsSidebarOpen}
          />
          
          <div className="flex min-h-screen pt-16">
            <Sidebar 
              currentPage={currentPage} 
              setCurrentPage={setCurrentPage}
              isOpen={isSidebarOpen}
              setIsOpen={setIsSidebarOpen}
            />
            
            <main className="flex-1 w-full lg:ml-64 transition-all duration-300">
              <div className="w-full h-full p-4 sm:p-6 lg:p-8">
                <div className="w-full max-w-full">
                  {renderPage()}
                </div>
              </div>
            </main>
          </div>

          {/* Footer */}
          <footer className="bg-white dark:bg-slate-800 border-t border-gray-200 dark:border-slate-700 mt-8 sm:mt-12">
            <div className="w-full px-4 sm:px-6 lg:px-8 py-4">
              <div className="text-center text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                <p>© 2024 AI-Powered Safety Monitoring System. All rights reserved.</p>
                <p className="mt-1">Smart Shop Floors - Ensuring Workplace Safety with AI</p>
              </div>
            </div>
          </footer>
        </div>
      </AlertProvider>
    </ModeProvider>
  );
}

export default App;
