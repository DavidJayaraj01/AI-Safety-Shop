import type { Worker } from '../types';
import { User, MapPin, Clock, Shield, ShieldAlert } from 'lucide-react';
import { format } from 'date-fns';

interface WorkerCardProps {
  worker: Worker;
}

export const WorkerCard = ({ worker }: WorkerCardProps) => {
  const getStatusColor = (status: Worker['status']) => {
    switch (status) {
      case 'active':
        return 'bg-success-100 dark:bg-success-900 text-success-700 dark:text-success-300';
      case 'on_break':
        return 'bg-warning-100 dark:bg-warning-900 text-warning-700 dark:text-warning-300';
      default:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300';
    }
  };

  return (
    <div className="card hover:shadow-md transition-shadow">
      <div className="flex items-start space-x-4">
        <div className="relative">
          {worker.photoUrl ? (
            <img
              src={worker.photoUrl}
              alt={worker.name}
              className="w-16 h-16 rounded-full object-cover"
            />
          ) : (
            <div className="w-16 h-16 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
              <User className="w-8 h-8 text-primary-600" />
            </div>
          )}
          <div
            className={`absolute -bottom-1 -right-1 w-5 h-5 rounded-full border-2 border-white dark:border-gray-800 ${
              worker.status === 'active'
                ? 'bg-success-500'
                : worker.status === 'on_break'
                ? 'bg-warning-500'
                : 'bg-gray-400'
            }`}
          />
        </div>

        <div className="flex-1">
          <h4 className="font-semibold text-gray-900 dark:text-white">
            {worker.name}
          </h4>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {worker.role} • {worker.department}
          </p>

          <div className="mt-2 space-y-1">
            <div className="flex items-center text-xs text-gray-600 dark:text-gray-400">
              <MapPin className="w-3 h-3 mr-1" />
              {worker.location.zone}
            </div>
            <div className="flex items-center text-xs text-gray-600 dark:text-gray-400">
              <Clock className="w-3 h-3 mr-1" />
              {format(new Date(worker.lastSeen), 'HH:mm:ss')}
            </div>
          </div>

          <div className="mt-3 flex items-center justify-between">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(worker.status)}`}>
              {worker.status.replace('_', ' ')}
            </span>
            <div className="flex items-center">
              {worker.ppeCompliance ? (
                <div className="flex items-center text-success-600 text-xs">
                  <Shield className="w-4 h-4 mr-1" />
                  PPE OK
                </div>
              ) : (
                <div className="flex items-center text-danger-600 text-xs animate-pulse">
                  <ShieldAlert className="w-4 h-4 mr-1" />
                  PPE Missing
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
