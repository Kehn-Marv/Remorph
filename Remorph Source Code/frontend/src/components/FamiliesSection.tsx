import React, { useState, useEffect } from 'react';
import { Database, RefreshCw, Info } from 'lucide-react';
import { getFamilies } from '../services/api';
import LoadingSpinner from './LoadingSpinner';
import ResultCard from './ResultCard';

interface FamilyData {
  families: string[];
  count: number;
}

const FamiliesSection: React.FC = () => {
  const [familiesData, setFamiliesData] = useState<FamilyData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchFamilies = async () => {
    setLoading(true);
    setError(null);

    try {
      const families = await getFamilies();
      setFamiliesData(families);
      setLastUpdated(new Date());
    } catch (err: any) {
      setError(err.message || 'Failed to fetch attribution families');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFamilies();
  }, []);

  const getFamilyDescription = (familyName: string) => {
    const descriptions: Record<string, string> = {
      'faceswap_blend': 'Traditional face swapping techniques using blending algorithms',
      'diffusion_inpaint': 'AI-generated content using diffusion models for face inpainting',
      'stylegan_family': 'StyleGAN-based synthetic face generation methods',
      'deepfakes_classic': 'Classic deepfake generation using autoencoder architectures',
      'face2face_realtime': 'Real-time facial reenactment and expression transfer',
      'first_order_motion': 'First-order motion model for face animation',
      'wav2lip_sync': 'Audio-driven lip synchronization techniques',
      'neural_head_avatars': 'Neural rendering for photorealistic head avatars'
    };

    return descriptions[familyName] || 'Advanced deepfake generation technique';
  };

  const getFamilyColor = (index: number) => {
    const colors = [
      'bg-blue-100 text-blue-800',
      'bg-green-100 text-green-800',
      'bg-purple-100 text-purple-800',
      'bg-yellow-100 text-yellow-800',
      'bg-pink-100 text-pink-800',
      'bg-indigo-100 text-indigo-800',
      'bg-red-100 text-red-800',
      'bg-gray-100 text-gray-800'
    ];
    return colors[index % colors.length];
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
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Attribution Families</h2>
          <p className="text-gray-600">Explore known deepfake generation techniques and their characteristics</p>
        </div>
        <button
          onClick={fetchFamilies}
          className="btn-secondary flex items-center space-x-2"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Refresh</span>
        </button>
      </div>

      {error && (
        <div className="card border-danger-200 bg-danger-50">
          <div className="flex items-center space-x-3">
            <Database className="w-5 h-5 text-danger-600" />
            <p className="text-danger-700">{error}</p>
          </div>
        </div>
      )}

      {familiesData && (
        <div className="space-y-6">
          {/* Overview */}
          <ResultCard title="Overview" icon={Database}>
            <div className="text-center">
              <p className="text-3xl font-bold text-gray-900 mb-2">
                {familiesData.count}
              </p>
              <p className="text-gray-600">
                Attribution families available for deepfake detection and classification
              </p>
            </div>
          </ResultCard>

          {/* Families List */}
          <ResultCard title="Known Attribution Families" icon={Info}>
            {familiesData.families.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {familiesData.families.map((family, index) => (
                  <div key={family} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-3">
                      <h3 className="font-semibold text-gray-900 capitalize">
                        {family.replace(/_/g, ' ')}
                      </h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getFamilyColor(index)}`}>
                        Family {index + 1}
                      </span>
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-3">
                      {getFamilyDescription(family)}
                    </p>
                    
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>Detection Method</span>
                      <span className="font-medium">Forensic Analysis</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Database className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-500">No attribution families found</p>
                <p className="text-sm text-gray-400 mt-1">
                  The system will learn and identify new families as it processes more images
                </p>
              </div>
            )}
          </ResultCard>

          {/* Information */}
          <div className="card bg-blue-50 border-blue-200">
            <div className="flex items-start space-x-3">
              <Info className="w-5 h-5 text-blue-600 mt-0.5" />
              <div>
                <h3 className="font-medium text-blue-900 mb-2">About Attribution Families</h3>
                <div className="text-sm text-blue-800 space-y-2">
                  <p>
                    Attribution families represent different deepfake generation techniques and their unique forensic signatures.
                    The system uses these patterns to not only detect deepfakes but also identify the likely method used to create them.
                  </p>
                  <p>
                    Each family is characterized by specific forensic features such as frequency domain artifacts, 
                    compression patterns, and statistical anomalies that are typical of particular generation methods.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Last Updated */}
          {lastUpdated && (
            <div className="text-center text-sm text-gray-500">
              Families data last updated: {lastUpdated.toLocaleString()}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FamiliesSection;