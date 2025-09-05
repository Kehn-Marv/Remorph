import React, { useState, useRef } from 'react';
import { Upload, Layers, AlertCircle, CheckCircle, Download } from 'lucide-react';
import { analyzeBatch } from '../services/api';
import LoadingSpinner from './LoadingSpinner';
import ResultCard from './ResultCard';

interface BatchResult {
  batch_id: string;
  total_images: number;
  results: Array<{
    id: string;
    success: boolean;
    face_found?: boolean;
    face_confidence?: number;
    heuristic_score?: number;
    features?: Record<string, number>;
    torch_available?: boolean;
    torch_probs?: number[];
    error?: string;
  }>;
}

const BatchAnalyzeSection: React.FC = () => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<BatchResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFilesSelect = (files: FileList) => {
    const imageFiles = Array.from(files).filter(file => file.type.startsWith('image/'));
    
    if (imageFiles.length === 0) {
      setError('Please select valid image files');
      return;
    }
    
    if (imageFiles.length > 5) {
      setError('Maximum 5 images allowed per batch');
      return;
    }

    setSelectedFiles(imageFiles);
    setResult(null);
    setError(null);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files.length > 0) {
      handleFilesSelect(e.dataTransfer.files);
    }
  };

  const handleAnalyze = async () => {
    if (selectedFiles.length === 0) return;

    setIsAnalyzing(true);
    setError(null);

    try {
      const batchResult = await analyzeBatch(selectedFiles);
      setResult(batchResult);
    } catch (err: any) {
      setError(err.message || 'Batch analysis failed. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles(files => files.filter((_, i) => i !== index));
  };

  const getScoreColor = (score: number) => {
    if (score < 0.3) return 'text-success-600';
    if (score < 0.7) return 'text-yellow-600';
    return 'text-danger-600';
  };

  const getScoreLabel = (score: number) => {
    if (score < 0.3) return 'Low Risk';
    if (score < 0.7) return 'Medium Risk';
    return 'High Risk';
  };

  const exportResults = () => {
    if (!result) return;
    
    const csvContent = [
      ['Image ID', 'Success', 'Face Found', 'Face Confidence', 'Heuristic Score', 'Risk Level', 'Error'].join(','),
      ...result.results.map(r => [
        r.id,
        r.success,
        r.face_found || false,
        r.face_confidence ? (r.face_confidence * 100).toFixed(1) + '%' : 'N/A',
        r.heuristic_score ? r.heuristic_score.toFixed(3) : 'N/A',
        r.heuristic_score ? getScoreLabel(r.heuristic_score) : 'N/A',
        r.error || ''
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `batch_analysis_${result.batch_id}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Batch Image Analysis</h2>
        <p className="text-gray-600">Upload multiple images for simultaneous deepfake detection (max 5 images)</p>
      </div>

      {/* File Upload */}
      <div className="card">
        <div
          className={`upload-zone ${dragOver ? 'dragover' : ''}`}
          onDrop={handleDrop}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            multiple
            onChange={(e) => e.target.files && handleFilesSelect(e.target.files)}
            className="hidden"
          />
          
          <div className="space-y-4">
            <Layers className="w-12 h-12 text-primary-500 mx-auto" />
            <div>
              <p className="text-lg font-medium text-gray-900">Drop your images here</p>
              <p className="text-gray-500">or click to browse files</p>
              <p className="text-sm text-gray-400 mt-2">
                Select up to 5 images (JPG, PNG, WebP, BMP, TIFF)
              </p>
            </div>
          </div>
        </div>

        {/* Selected Files */}
        {selectedFiles.length > 0 && (
          <div className="mt-6 space-y-4">
            <h3 className="font-medium text-gray-900">Selected Images ({selectedFiles.length}/5)</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {selectedFiles.map((file, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{file.name}</p>
                    <p className="text-xs text-gray-500">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                  <button
                    onClick={() => removeFile(index)}
                    className="ml-2 text-gray-400 hover:text-gray-600 text-sm"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
            
            <div className="flex justify-center">
              <button
                onClick={handleAnalyze}
                disabled={isAnalyzing}
                className="btn-primary flex items-center space-x-2"
              >
                {isAnalyzing ? (
                  <>
                    <LoadingSpinner size="sm" />
                    <span>Analyzing Batch...</span>
                  </>
                ) : (
                  <>
                    <Layers className="w-4 h-4" />
                    <span>Analyze Batch</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="card border-danger-200 bg-danger-50">
          <div className="flex items-center space-x-3">
            <AlertCircle className="w-5 h-5 text-danger-600" />
            <p className="text-danger-700">{error}</p>
          </div>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-6">
          {/* Summary */}
          <ResultCard title="Batch Analysis Summary" icon={Layers}>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-gray-900">{result.total_images}</p>
                <p className="text-sm text-gray-600">Total Images</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-success-600">
                  {result.results.filter(r => r.success).length}
                </p>
                <p className="text-sm text-gray-600">Successful</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-primary-600">
                  {result.results.filter(r => r.success && r.face_found).length}
                </p>
                <p className="text-sm text-gray-600">Faces Detected</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-danger-600">
                  {result.results.filter(r => r.success && r.heuristic_score && r.heuristic_score > 0.7).length}
                </p>
                <p className="text-sm text-gray-600">High Risk</p>
              </div>
            </div>
            
            <div className="mt-4 flex justify-center">
              <button
                onClick={exportResults}
                className="btn-secondary flex items-center space-x-2"
              >
                <Download className="w-4 h-4" />
                <span>Export Results (CSV)</span>
              </button>
            </div>
          </ResultCard>

          {/* Individual Results */}
          <ResultCard title="Individual Results" icon={CheckCircle}>
            <div className="space-y-4">
              {result.results.map((item, index) => (
                <div key={item.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-gray-900">Image {index + 1}</h4>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      item.success ? 'bg-success-100 text-success-700' : 'bg-danger-100 text-danger-700'
                    }`}>
                      {item.success ? 'Success' : 'Failed'}
                    </span>
                  </div>

                  {item.success ? (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">Face Found</span>
                        <p className="font-medium text-gray-900">
                          {item.face_found ? 'Yes' : 'No'}
                        </p>
                      </div>
                      {item.face_confidence && (
                        <div>
                          <span className="text-gray-600">Face Confidence</span>
                          <p className="font-medium text-gray-900">
                            {(item.face_confidence * 100).toFixed(1)}%
                          </p>
                        </div>
                      )}
                      {item.heuristic_score !== undefined && (
                        <div>
                          <span className="text-gray-600">Risk Level</span>
                          <p className={`font-medium ${getScoreColor(item.heuristic_score)}`}>
                            {getScoreLabel(item.heuristic_score)}
                          </p>
                        </div>
                      )}
                      {item.heuristic_score !== undefined && (
                        <div>
                          <span className="text-gray-600">Score</span>
                          <p className="font-medium text-gray-900">
                            {item.heuristic_score.toFixed(3)}
                          </p>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-sm">
                      <span className="text-gray-600">Error: </span>
                      <span className="text-danger-600">{item.error}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </ResultCard>
        </div>
      )}
    </div>
  );
};

export default BatchAnalyzeSection;