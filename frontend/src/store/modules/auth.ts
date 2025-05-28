import { Module } from 'vuex';
import router from '../../router';
import { AuthService } from '../../services/AuthService';

interface AuthState {
  token: string | null;
  user: any | null;
  loading: boolean;
  error: string | null;
}

const authModule: Module<AuthState, any> = {
  namespaced: true,
  
  state: () => ({
    token: null,
    user: null,
    loading: false,
    error: null
  }),
  
  getters: {
    isAuthenticated(state): boolean {
      return !!state.token;
    },
    currentUser(state): any {
      return state.user;
    },
    authError(state): string | null {
      return state.error;
    },
    isLoading(state): boolean {
      return state.loading;
    }
  },
  
  mutations: {
    setToken(state, token: string) {
      state.token = token;
      localStorage.setItem('token', token);
    },
    setUser(state, user: any) {
      state.user = user;
    },
    setLoading(state, loading: boolean) {
      state.loading = loading;
    },
    setError(state, error: string | null) {
      state.error = error;
    },
    clearAuth(state) {
      state.token = null;
      state.user = null;
      localStorage.removeItem('token');
    }
  },
  
  actions: {
    async login({ commit }, credentials) {
      try {
        commit('setLoading', true);
        commit('setError', null);
        
        const response = await AuthService.login(credentials.username, credentials.password);
        
        if (response.status === 'success' && response.data?.access_token) {
          commit('setToken', response.data.access_token);
          
          // Get user data from token (basic implementation)
          // In a real app, you might want to fetch user profile separately
          const userParts = atob(response.data.access_token.split('.')[1]);
          const userData = JSON.parse(userParts);
          commit('setUser', userData);
          
          router.push({ name: 'Home' });
          return true;
        } else {
          throw new Error(response.message || 'Login failed');
        }
      } catch (error: any) {
        commit('setError', error.message || 'Login failed');
        return false;
      } finally {
        commit('setLoading', false);
      }
    },
    
    async signup({ commit }, userData) {
      try {
        commit('setLoading', true);
        commit('setError', null);
        
        const response = await AuthService.signup(userData);
        
        if (response.status === 'success') {
          router.push({ name: 'Login' });
          return true;
        } else {
          throw new Error(response.message || 'Signup failed');
        }
      } catch (error: any) {
        commit('setError', error.message || 'Signup failed');
        return false;
      } finally {
        commit('setLoading', false);
      }
    },
    
    async logout({ commit }) {
      try {
        commit('setLoading', true);
        await AuthService.logout();
        // Even if the server-side logout fails, we'll clear local auth
        commit('clearAuth');
        router.push({ name: 'Login' });
      } catch (error) {
        console.error('Logout error:', error);
      } finally {
        commit('setLoading', false);
      }
    },
    
    initializeAuth({ commit }, token: string) {
      if (token) {
        try {
          // Parse the JWT token to get user data
          const userParts = atob(token.split('.')[1]);
          const userData = JSON.parse(userParts);
          
          // Check if token is expired
          const expirationTime = userData.exp * 1000; // Convert to milliseconds
          if (Date.now() >= expirationTime) {
            commit('clearAuth');
            return;
          }
          
          commit('setToken', token);
          commit('setUser', userData);
        } catch (e) {
          // If token parsing fails, clear auth
          commit('clearAuth');
        }
      }
    }
  }
};

export default authModule;