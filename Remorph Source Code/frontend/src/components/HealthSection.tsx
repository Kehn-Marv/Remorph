import React, { useState, useEffect } from 'react';
import { Activity, CheckCircle, AlertCircle, XCircle, RefreshCw } from 'lucide-react';
import { getHealth, getDetailedHealth } from '../services/api';
import LoadingSpinner from './LoadingSpinner';
import ResultCard from './ResultCard';

interface HealthData {
  status: string;
  timestamp: string;
  system?: {
    memory_usage_percent: number;
    disk_usage_percent: number;
    available_memory_gb: number;
  };
  components?: {
    output_directory: boolean;
    fingerprints_db: boolean;
    torch_weights: boolean;
    face_detector: boolean;
  };
  paths?: {
    output_dir: string;
    fingerprints: string;
    weights: string;
  };
}

interface DetailedHealthData {
  timestamp: string;
  components: Record<string, string>;
}

const HealthSection: React.FC = () => {
  const [healthData, setHealthData] = useState<HealthData | null>(null);
  const [detailedHealth, setDetailedHealth] = useState<DetailedHealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchHealthData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [health, detailed] = await Promise.all([
        getHealth(),
        getDetailedHealth()
      ]);
      
      setHealthData(health);
      setDetailedHealth(detailed);
      setLastUpdated(new Date());
    } catch (err: any) {
      setError(err.message || 'Failed to fetch health data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealthData();
  }, []);

  const getStatusIcon = (status: boolean | string) => {
    if (typeof status === 'boolean') {
      return status ? (
        <CheckCircle className="w-5 h-5 text-success-600" />
      ) : (
        <XCircle className="w-5 h-5 text-danger-600" />
      );
    }
    
    if (status.includes('available')) {
      return <CheckCircle className="w-5 h-5 text-success-600" />;
    } else if (status.includes('error')) {
      return <XCircle className="w-5 h-5 text-danger-600" />;
    } else {
      return <AlertCircle className="w-5 h-5 text-yellow-600" />;
    }
  };

  const getStatusColor = (status: boolean | string) => {
    if (typeof status === 'boolean') {
      return status ? 'text-success-600' : 'text-danger-600';
    }
    
    if (status.includes('available')) {
      return 'text-success-600';
    } else if (status.includes('error')) {
      return 'text-danger-600';
    } else {
      return 'text-yellow-600';
    }
  };

  const getUsageColor = (percentage: number) => {
    if (percentage < 50) return 'bg-success-500';
    if (percentage < 80) return 'bg-yellow-500';
    return 'bg-danger-500';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">System Health</h2>
          <p className="text-gray-600">Monitor system status and component health</p>
        </div>
        <button
          onClick={fetchHealthData}
          className="btn-secondary flex items-center space-x-2"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Refresh</span>
        </button>
      </div>

      {error && (
        <div className="card border-danger-200 bg-danger-50">
          <div className="flex items-center space-x-3">
            <AlertCircle className="w-5 h-5 text-danger-600" />
            <p className="text-danger-700">{error}</p>
          </div>
        </div>
      )}

      {healthData && (
        <div className="space-y-6">
          {/* Overall Status */}
          <ResultCard title="Overall Status" icon={Activity}>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                {healthData.status === 'healthy' ? (
                  <CheckCircle className="w-8 h-8 text-success-600" />
                ) : (
                  <XCircle className="w-8 h-8 text-danger-600" />
                )}
                <div>
                  <p className={`text-lg font-semibold ${
                    healthData.status === 'healthy' ? 'text-success-600' : 'text-danger-600'
                  }`}>
                    {healthData.status === 'healthy' ? 'System Healthy' : 'System Issues Detected'}
                  </p>
                  {lastUpdated && (
                    <p className="text-sm text-gray-500">
                      Last updated: {lastUpdated.toLocaleTimeString()}
                    </p>
                  )}
                </div>
              </div>
            </div>
          </ResultCard>

          {/* System Resources */}
          {healthData.system && (
            <ResultCard title="System Resources" icon={Activity}>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-gray-700">Memory Usage</span>
                    <span className="text-sm text-gray-600">
                      {healthData.system.memory_usage_percent.toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${getUsageColor(healthData.system.memory_usage_percent)}`}
                      style={{ width: `${healthData.system.memory_usage_percent}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {healthData.system.available_memory_gb.toFixed(1)} GB available
                  </p>
                </div>

                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-gray-700">Disk Usage</span>
                    <span className="text-sm text-gray-600">
                      {healthData.system.disk_usage_percent.toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${getUsageColor(healthData.system.disk_usage_percent)}`}
                      style={{ width: `${healthData.system.disk_usage_percent}%` }}
                    />
                  </div>
                </div>
              </div>
            </ResultCard>
          )}

          {/* Component Status */}
          {healthData.components && (
            <ResultCard title="Component Status" icon={CheckCircle}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(healthData.components).map(([component, status]) => (
                  <div key={component} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span className="text-sm font-medium text-gray-700 capitalize">
                      {component.replace(/_/g, ' ')}
                    </span>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(status)}
                      <span className={`text-sm font-medium ${getStatusColor(status)}`}>
                        {typeof status === 'boolean' ? (status ? 'Available' : 'Unavailable') : status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </ResultCard>
          )}

          {/* Detailed Component Health */}
          {detailedHealth && (
            <ResultCard title="Detailed Component Health" icon={Activity}>
              <div className="space-y-3">
                {Object.entries(detailedHealth.components).map(([component, status]) => (
                  <div key={component} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span className="text-sm font-medium text-gray-700 capitalize">
                      {component.replace(/_/g, ' ')}
                    </span>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(status)}
                      <span className={`text-sm ${getStatusColor(status)}`}>
                        {status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </ResultCard>
          )}

          {/* System Paths */}
          {healthData.paths && (
            <details className="card">
              <summary className="cursor-pointer font-medium text-gray-900 mb-4">
                System Paths
              </summary>
              <div className="space-y-3 text-sm">
                {Object.entries(healthData.paths).map(([key, path]) => (
                  <div key={key} className="flex items-center justify-between">
                    <span className="text-gray-600 capitalize">
                      {key.replace(/_/g, ' ')}
                    </span>
                    <code className="text-xs bg-gray-100 px-2 py-1 rounded font-mono">
                      {path}
                    </code>
                  </div>
                ))}
              </div>
            </details>
          )}
        </div>
      )}
    </div>
  );
};

export default HealthSection;