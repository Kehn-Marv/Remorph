import React, { useState, useEffect } from 'react';
import { BarChart3, RefreshCw, Database, TrendingUp } from 'lucide-react';
import { getStats } from '../services/api';
import LoadingSpinner from './LoadingSpinner';
import ResultCard from './ResultCard';

interface StatsData {
  attribution: {
    total_families: number;
    total_samples: number;
    families: Array<{
      name: string;
      sample_count: number;
      last_updated: string | null;
    }>;
  };
  system: {
    fingerprints_path: string;
    total_families: number;
  };
}

const StatsSection: React.FC = () => {
  const [statsData, setStatsData] = useState<StatsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchStats = async () => {
    setLoading(true);
    setError(null);

    try {
      const stats = await getStats();
      setStatsData(stats);
      setLastUpdated(new Date());
    } catch (err: any) {
      setError(err.message || 'Failed to fetch statistics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

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
          <h2 className="text-2xl font-bold text-gray-900 mb-2">System Statistics</h2>
          <p className="text-gray-600">View system performance and attribution database metrics</p>
        </div>
        <button
          onClick={fetchStats}
          className="btn-secondary flex items-center space-x-2"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Refresh</span>
        </button>
      </div>

      {error && (
        <div className="card border-danger-200 bg-danger-50">
          <div className="flex items-center space-x-3">
            <BarChart3 className="w-5 h-5 text-danger-600" />
            <p className="text-danger-700">{error}</p>
          </div>
        </div>
      )}

      {statsData && (
        <div className="space-y-6">
          {/* Overview Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="card text-center">
              <Database className="w-8 h-8 text-primary-600 mx-auto mb-3" />
              <p className="text-3xl font-bold text-gray-900 mb-1">
                {statsData.attribution.total_families}
              </p>
              <p className="text-sm text-gray-600">Attribution Families</p>
            </div>

            <div className="card text-center">
              <TrendingUp className="w-8 h-8 text-success-600 mx-auto mb-3" />
              <p className="text-3xl font-bold text-gray-900 mb-1">
                {statsData.attribution.total_samples}
              </p>
              <p className="text-sm text-gray-600">Total Samples</p>
            </div>

            <div className="card text-center">
              <BarChart3 className="w-8 h-8 text-yellow-600 mx-auto mb-3" />
              <p className="text-3xl font-bold text-gray-900 mb-1">
                {statsData.attribution.total_samples > 0 
                  ? (statsData.attribution.total_samples / statsData.attribution.total_families).toFixed(1)
                  : '0'
                }
              </p>
              <p className="text-sm text-gray-600">Avg Samples per Family</p>
            </div>
          </div>

          {/* Attribution Families */}
          <ResultCard title="Attribution Families" icon={Database}>
            {statsData.attribution.families.length > 0 ? (
              <div className="space-y-4">
                {statsData.attribution.families.map((family, index) => (
                  <div key={family.name} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900 capitalize">
                        {family.name.replace(/_/g, ' ')}
                      </h4>
                      {family.last_updated && (
                        <p className="text-sm text-gray-500">
                          Last updated: {new Date(family.last_updated).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                    
                    <div className="text-right">
                      <p className="text-lg font-semibold text-gray-900">
                        {family.sample_count}
                      </p>
                      <p className="text-sm text-gray-500">samples</p>
                    </div>
                    
                    {/* Visual representation */}
                    <div className="ml-4 w-20">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-primary-500 h-2 rounded-full"
                          style={{
                            width: `${Math.max(
                              (family.sample_count / Math.max(statsData.attribution.total_samples, 1)) * 100,
                              5
                            )}%`
                          }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Database className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-500">No attribution families found</p>
                <p className="text-sm text-gray-400 mt-1">
                  Families will appear here as the system learns from analyzed images
                </p>
              </div>
            )}
          </ResultCard>

          {/* System Information */}
          <ResultCard title="System Information" icon={BarChart3}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Database Status</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Fingerprints Path</span>
                    <code className="text-xs bg-gray-100 px-2 py-1 rounded font-mono">
                      {statsData.system.fingerprints_path}
                    </code>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Active Families</span>
                    <span className="font-medium text-gray-900">
                      {statsData.system.total_families}
                    </span>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-medium text-gray-900 mb-3">Learning Progress</h4>
                <div className="space-y-3">
                  {statsData.attribution.families.map((family) => (
                    <div key={family.name} className="flex items-center justify-between">
                      <span className="text-sm text-gray-600 capitalize">
                        {family.name.replace(/_/g, ' ')}
                      </span>
                      <div className="flex items-center space-x-2">
                        <div className="w-16 bg-gray-200 rounded-full h-1.5">
                          <div
                            className="bg-primary-500 h-1.5 rounded-full"
                            style={{
                              width: `${Math.min(
                                Math.max((family.sample_count / 100) * 100, 5),
                                100
                              )}%`
                            }}
                          />
                        </div>
                        <span className="text-xs text-gray-500 w-8 text-right">
                          {family.sample_count}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </ResultCard>

          {/* Last Updated */}
          {lastUpdated && (
            <div className="text-center text-sm text-gray-500">
              Statistics last updated: {lastUpdated.toLocaleString()}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default StatsSection;