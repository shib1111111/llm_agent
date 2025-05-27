import { createStore } from 'vuex';
import axios from 'axios';
import { jwtDecode } from 'jwt-decode'; // Import jwt-decode to extract role from token

const BASE_URL = `${import.meta.env.VITE_BASE_URL}/api`;

export default createStore({
  state: {
    access_token: localStorage.getItem('access_token') || null,
    role: localStorage.getItem('role') || null,
    chatMessages: [],
  },
  mutations: {
    setAuth(state, { access_token, role }) {
      state.access_token = access_token;
      state.role = role;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('role', role);
      console.log('Auth set:', { access_token, role });
    },
    addMessage(state, message) {
      state.chatMessages.push(message);
      console.log('Message added:', message);
    },
    clearMessages(state) {
      state.chatMessages = [];
      console.log('Messages cleared');
    },
    clearAuth(state) {
      state.access_token = null;
      state.role = null;
      localStorage.removeItem('access_token');
      localStorage.removeItem('role');
      console.log('Auth cleared');
    },
  },
  actions: {
    initializeAuth({ commit }) {
      const access_token = localStorage.getItem('access_token');
      const role = localStorage.getItem('role');
      if (access_token && role) {
        commit('setAuth', { access_token, role });
        console.log('Auth initialized from localStorage');
      }
    },
    async login({ commit }, { username, password }) {
      try {
        console.log('Login request:', { username });
        const response = await axios.post(`${BASE_URL}/login`, new URLSearchParams({
          username,
          password,
        }));
        const { access_token } = response.data.data;
        // Decode the JWT to extract the role
        const decoded = jwtDecode(access_token);
        const role = decoded.role;
        commit('setAuth', { access_token, role });
        console.log('Login successful, role extracted:', role);
        return response.data;
      } catch (error) {
        console.error('Login error:', error);
        throw error.response?.data?.detail || 'Login failed.';
      }
    },
    async signup({ commit }, userData) {
      try {
        console.log('Signup request:', userData);
        const response = await axios.post(`${BASE_URL}/signup`, userData);
        return response.data;
      } catch (error) {
        console.error('Signup error:', error);
        throw error.response?.data?.detail || 'Signup failed.';
      }
    },
    async logout({ commit, state }) {
      try {
        console.log('Logout request');
        await axios.post(`${BASE_URL}/logout`, {}, {
          headers: { Authorization: `Bearer ${state.access_token}` },
        });
        commit('clearAuth');
      } catch (error) {
        console.error('Logout error:', error);
        commit('clearAuth');
        throw error.response?.data?.detail || 'Logout failed.';
      }
    },
    async connectDB({ state }) {
      try {
        console.log('Connecting to database');
        const response = await axios.get(`${BASE_URL}/connect`, {
          headers: { Authorization: `Bearer ${state.access_token}` },
        });
        return response.data;
      } catch (error) {
        console.error('Database connection error:', error);
        throw error.response?.data?.detail || 'Failed to connect to database.';
      }
    },
    async queryAgent({ commit, state }, query) {
      try {
        console.log('Agent query:', query);
        const response = await axios.post(`${BASE_URL}/query`, { query }, {
          headers: { Authorization: `Bearer ${state.access_token}` },
        });
        const message = {
          id: Date.now(),
          query,
          response: response.data.data.response,
          type: 'agent',
          timestamp: new Date().toLocaleTimeString(),
        };
        commit('addMessage', message);
        return response.data;
      } catch (error) {
        console.error('Agent query error:', error);
        throw error.response?.data?.detail || 'Agent query failed.';
      }
    },
    async queryDB({ commit, state }, query) {
      try {
        console.log('DB query:', query);
        const response = await axios.post(`${BASE_URL}/db/query`, { query }, {
          headers: { Authorization: `Bearer ${state.access_token}` },
        });
        const message = {
          id: Date.now(),
          query,
          response: response.data.data.natural_language_response,
          type: 'db',
          timestamp: new Date().toLocaleTimeString(),
        };
        commit('addMessage', message);
        return response.data;
      } catch (error) {
        console.error('DB query error:', error);
        throw error.response?.data?.detail || 'Database query failed.';
      }
    },
    async queryDoc({ commit, state }, query) {
      try {
        console.log('Document query:', query);
        const response = await axios.post(`${BASE_URL}/documents/query`, { query }, {
          headers: { Authorization: `Bearer ${state.access_token}` },
        });
        const message = {
          id: Date.now(),
          query,
          response: response.data.data.response,
          type: 'doc',
          timestamp: new Date().toLocaleTimeString(),
        };
        commit('addMessage', message);
        return response.data;
      } catch (error) {
        console.error('Document query error:', error);
        throw error.response?.data?.detail || 'Document query failed.';
      }
    },
  },
});