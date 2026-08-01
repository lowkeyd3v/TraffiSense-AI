import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export const authService = {
  login: async (credentials) => {
    // Matches FastAPI OAuth2PasswordRequestForm or Custom JSON Auth
    const response = await api.post('/auth/login', credentials);
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
    }
    return response.data;
  },
  logout: () => {
    localStorage.removeItem('token');
  },
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

export const trafficService = {
  getRealtimeMetrics: async () => {
    try {
      const response = await api.get('/traffic/realtime');
      return response.data;
    } catch {
      // Fallback mock data matching UI design
      return {
        activeSignals: 142,
        congestionIndex: '64%',
        activeIncidents: 18,
        aiOptimizationScore: '92%',
      };
    }
  },
  getIncidents: async () => {
    try {
      const response = await api.get('/traffic/incidents');
      return response.data;
    } catch {
      return [
        { id: 'INC-8921', location: '7th Ave & 42nd St', type: 'Collision', severity: 'High', status: 'In Progress', timestamp: '10 mins ago' },
        { id: 'INC-8922', location: 'Broadway & 14th St', type: 'Signal Malfunction', severity: 'Medium', status: 'Dispatched', timestamp: '25 mins ago' },
        { id: 'INC-8923', location: 'FDR Drive North Exit 9', type: 'Debris on Road', severity: 'Low', status: 'Resolved', timestamp: '1 hour ago' },
      ];
    }
  },
  reportIncident: async (incidentData) => {
    const response = await api.post('/traffic/incidents', incidentData);
    return response.data;
  },
};

export const predictionService = {
  getTrafficPrediction: async (params) => {
    try {
      const response = await api.post('/predictions/forecast', params);
      return response.data;
    } catch {
      return {
        predictedCongestion: '78%',
        recommendedSignalTiming: '+15s Green Phase on Main Corridor',
        confidenceScore: '89.4%',
      };
    }
  },
};

export default api;