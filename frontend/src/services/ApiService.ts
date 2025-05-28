import axios from 'axios';
import store from '../store';

const api = axios.create({
  baseURL: import.meta.env.VITE_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor to add authorization header
api.interceptors.request.use(
  (config) => {
    const token = store.state.auth?.token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Unauthorized - clear auth and redirect to login
      store.commit('auth/clearAuth');
      window.location.href = '/login';
    }
    return Promise.reject(error.response?.data || error);
  }
);

export const ApiService = {
  // Database Connection
  connectToDb: async () => {
    return api.get('/api/connect');
  },
  
  // Agent Query
  agentQuery: async (query: string) => {
    return api.post('/api/query', { query });
  },
  
  // DB Query
  dbQuery: async (query: string) => {
    return api.post('/api/db/query', { query });
  },
  
  // Document Query
  docQuery: async (query: string) => {
    return api.post('/api/documents/query', { query });
  },
  
  // Document Upload
  uploadDocument: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    return api.post('/api/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  }
};