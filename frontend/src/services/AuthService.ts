import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const AuthService = {
  // User signup
  signup: async (userData: {
    name: string;
    email: string;
    username: string;
    password: string;
    role: string;
  }) => {
    return api.post('/api/signup', userData)
      .then(response => response.data)
      .catch(error => {
        throw error.response?.data || error;
      });
  },
  
  // User login
  login: async (username: string, password: string) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    return api.post('/api/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
      .then(response => response.data)
      .catch(error => {
        throw error.response?.data || error;
      });
  },
  
  // User logout
  logout: async () => {
    const token = localStorage.getItem('token');
    if (!token) return Promise.resolve();
    
    return api.post('/api/logout', {}, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
      .then(response => response.data)
      .catch(error => {
        throw error.response?.data || error;
      });
  }
};