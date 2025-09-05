import axios from 'axios';

// Use a relative base so Vite dev server proxy (configured in vite.config.ts)
// forwards requests to the backend during development.
const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout for analysis
});

// Health endpoints
export const getHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const getDetailedHealth = async () => {
  const response = await api.get('/health/detailed');
  return response.data;
};

// Analysis endpoints
export const analyzeImage = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/analyze', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const analyzeBatch = async (files: File[]) => {
  const formData = new FormData();
  files.forEach(file => {
    formData.append('files', file);
  });
  
  const response = await api.post('/analyze/batch', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

// Stats endpoints
export const getStats = async () => {
  const response = await api.get('/stats');
  return response.data;
};

export const getFamilies = async () => {
  const response = await api.get('/families');
  return response.data;
};

// Error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.message || 'Server error';
      throw new Error(message);
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('Unable to connect to the server. Please check if the API is running.');
    } else {
      // Something else happened
      throw new Error('An unexpected error occurred');
    }
  }
);

export default api;