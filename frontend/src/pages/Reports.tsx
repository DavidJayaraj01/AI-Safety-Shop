import { useState, useEffect } from 'react';
import {
  FileText,
  Download,
  Calendar,
  Filter,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  BarChart3
} from 'lucide-react';
import Chart from '../components/Chart';
import toast from 'react-hot-toast';

interface Report {
  id: number;
  type: string;
  title: string;
  date: string;
  status: 'completed' | 'pending' | 'failed';
  incidents: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

const Reports = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [selectedPeriod, setSelectedPeriod] = useState('week');
  const [selectedType, setSelectedType] = useState('all');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchReports();
  }, [selectedPeriod, selectedType]);

  const fetchReports = async () => {
    try {
      // Simulate API call
      setTimeout(() => {
        const mockReports: Report[] = [
          {
            id: 1,
            type: 'safety',
            title: 'Weekly Safety Report',
            date: '2024-10-15',
            status: 'completed',
            incidents: 3,
            severity: 'medium'
          },
          {
            id: 2,
            type: 'sensor',
            title: 'Sensor Performance Analysis',
            date: '2024-10-14',
            status: 'completed',
            incidents: 0,
            severity: 'low'
          },
          {
            id: 3,
            type: 'alert',
            title: 'Alert Summary Report',
            date: '2024-10-13',
            status: 'completed',
            incidents: 7,
            severity: 'high'
          },
          {
            id: 4,
            type: 'compliance',
            title: 'Compliance Report',
            date: '2024-10-12',
            status: 'pending',
            incidents: 2,
            severity: 'medium'
          },
          {
            id: 5,
            type: 'maintenance',
            title: 'Maintenance Log',
            date: '2024-10-11',
            status: 'completed',
            incidents: 1,
            severity: 'low'
          }
        ];
        setReports(mockReports);
        setIsLoading(false);
      }, 500);
    } catch (error) {
      console.error('Error fetching reports:', error);
      toast.error('Failed to load reports');
      setIsLoading(false);
    }
  };

  const handleDownloadReport = (report: Report) => {
    toast.success(`Downloading ${report.title}...`);
    // Implement actual download logic here
  };

  const handleGenerateReport = () => {
    toast.success('Generating new report...');
    // Implement report generation logic here
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-success-600" />;
      case 'pending':
        return <Clock className="h-5 w-5 text-warning-600" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-danger-600" />;
      default:
        return null;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'low':
        return 'bg-success-100 text-success-700 dark:bg-success-900/30 dark:text-success-300';
      case 'medium':
        return 'bg-warning-100 text-warning-700 dark:bg-warning-900/30 dark:text-warning-300';
      case 'high':
        return 'bg-danger-100 text-danger-700 dark:bg-danger-900/30 dark:text-danger-300';
      case 'critical':
        return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300';
      default:
        return 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-300';
    }
  };

  const filteredReports = reports.filter(report => 
    selectedType === 'all' || report.type === selectedType
  );

  // Mock data for charts
  const incidentTrendData = [
    { timestamp: 'Mon', value: 3 },
    { timestamp: 'Tue', value: 5 },
    { timestamp: 'Wed', value: 2 },
    { timestamp: 'Thu', value: 7 },
    { timestamp: 'Fri', value: 4 },
    { timestamp: 'Sat', value: 1 },
    { timestamp: 'Sun', value: 3 }
  ];

  const severityDistribution = [
    { timestamp: 'Low', value: 45 },
    { timestamp: 'Medium', value: 30 },
    { timestamp: 'High', value: 20 },
    { timestamp: 'Critical', value: 5 }
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Reports & Analytics
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            View and download system reports
          </p>
        </div>
        <button
          onClick={handleGenerateReport}
          className="btn-primary flex items-center space-x-2"
        >
          <FileText size={18} />
          <span>Generate New Report</span>
        </button>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              <Calendar className="inline h-4 w-4 mr-1" />
              Time Period
            </label>
            <select
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="today">Today</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="quarter">This Quarter</option>
              <option value="year">This Year</option>
            </select>
          </div>

          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              <Filter className="inline h-4 w-4 mr-1" />
              Report Type
            </label>
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="all">All Reports</option>
              <option value="safety">Safety Reports</option>
              <option value="sensor">Sensor Reports</option>
              <option value="alert">Alert Reports</option>
              <option value="compliance">Compliance Reports</option>
              <option value="maintenance">Maintenance Reports</option>
            </select>
          </div>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card gradient-primary text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm opacity-90">Total Reports</p>
              <p className="text-3xl font-bold">{reports.length}</p>
            </div>
            <FileText className="h-10 w-10 opacity-80" />
          </div>
        </div>

        <div className="card gradient-success text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm opacity-90">Completed</p>
              <p className="text-3xl font-bold">
                {reports.filter(r => r.status === 'completed').length}
              </p>
            </div>
            <CheckCircle className="h-10 w-10 opacity-80" />
          </div>
        </div>

        <div className="card gradient-warning text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm opacity-90">Total Incidents</p>
              <p className="text-3xl font-bold">
                {reports.reduce((sum, r) => sum + r.incidents, 0)}
              </p>
            </div>
            <AlertTriangle className="h-10 w-10 opacity-80" />
          </div>
        </div>

        <div className="card bg-gradient-to-br from-purple-500 to-purple-700 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm opacity-90">Avg Severity</p>
              <p className="text-3xl font-bold">Medium</p>
            </div>
            <TrendingUp className="h-10 w-10 opacity-80" />
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Chart
          title="Incident Trend"
          data={incidentTrendData}
          dataKey="value"
          type="line"
          color="#3b82f6"
        />
        <Chart
          title="Severity Distribution"
          data={severityDistribution}
          dataKey="value"
          type="bar"
          color="#8b5cf6"
        />
      </div>

      {/* Reports List */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Recent Reports
          </h2>
          <BarChart3 className="h-5 w-5 text-gray-400" />
        </div>

        {filteredReports.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-500 dark:text-gray-400">No reports found</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-slate-700">
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">
                    Report
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">
                    Type
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">
                    Date
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">
                    Status
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">
                    Incidents
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">
                    Severity
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredReports.map((report, index) => (
                  <tr
                    key={report.id}
                    className={`border-b border-gray-100 dark:border-slate-700 ${
                      index % 2 === 0 ? 'bg-gray-50 dark:bg-slate-800/50' : ''
                    }`}
                  >
                    <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white">
                      {report.title}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400 capitalize">
                      {report.type}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                      {new Date(report.date).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(report.status)}
                        <span className="text-sm capitalize text-gray-600 dark:text-gray-400">
                          {report.status}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900 dark:text-white">
                      {report.incidents}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium capitalize ${getSeverityColor(
                          report.severity
                        )}`}
                      >
                        {report.severity}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => handleDownloadReport(report)}
                        className="text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
                        title="Download Report"
                      >
                        <Download size={18} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Reports;