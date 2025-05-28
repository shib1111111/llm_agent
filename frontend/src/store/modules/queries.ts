import { Module } from 'vuex';
import { ApiService } from '../../services/ApiService';

interface QueryState {
  dbSchema: any | null;
  dbConnected: boolean;
  agentResponses: Array<{query: string; response: string}>;
  dbResponses: Array<{
    query: string;
    sqlQuery: string;
    rawResponse: any;
    naturalLanguageResponse: string;
  }>;
  docResponses: Array<{query: string; response: string}>;
  uploadedDocs: string[];
  loading: boolean;
  error: string | null;
}

const queriesModule: Module<QueryState, any> = {
  namespaced: true,
  
  state: () => ({
    dbSchema: null,
    dbConnected: false,
    agentResponses: [],
    dbResponses: [],
    docResponses: [],
    uploadedDocs: [],
    loading: false,
    error: null
  }),
  
  getters: {
    isDatabaseConnected(state): boolean {
      return state.dbConnected;
    },
    databaseSchema(state): any | null {
      return state.dbSchema;
    },
    getAgentResponses(state): Array<{query: string; response: string}> {
      return state.agentResponses;
    },
    getDbResponses(state): Array<{
      query: string;
      sqlQuery: string;
      rawResponse: any;
      naturalLanguageResponse: string;
    }> {
      return state.dbResponses;
    },
    getDocResponses(state): Array<{query: string; response: string}> {
      return state.docResponses;
    },
    getUploadedDocs(state): string[] {
      return state.uploadedDocs;
    },
    isLoading(state): boolean {
      return state.loading;
    },
    getError(state): string | null {
      return state.error;
    }
  },
  
  mutations: {
    setDbSchema(state, schema) {
      state.dbSchema = schema;
      state.dbConnected = true;
    },
    setDbConnection(state, status) {
      state.dbConnected = status;
    },
    addAgentResponse(state, { query, response }) {
      state.agentResponses.push({ query, response });
    },
    addDbResponse(state, { query, sqlQuery, rawResponse, naturalLanguageResponse }) {
      state.dbResponses.push({
        query,
        sqlQuery,
        rawResponse,
        naturalLanguageResponse
      });
    },
    addDocResponse(state, { query, response }) {
      state.docResponses.push({ query, response });
    },
    addUploadedDoc(state, filename) {
      if (!state.uploadedDocs.includes(filename)) {
        state.uploadedDocs.push(filename);
      }
    },
    setLoading(state, loading) {
      state.loading = loading;
    },
    setError(state, error) {
      state.error = error;
    },
    clearError(state) {
      state.error = null;
    }
  },
  
  actions: {
    async connectToDatabase({ commit }) {
      try {
        commit('setLoading', true);
        commit('clearError');
        
        const response = await ApiService.connectToDb();
        
        if (response.status === 'success' && response.data?.schema) {
          commit('setDbSchema', response.data.schema);
          return true;
        } else {
          throw new Error(response.message || 'Failed to connect to database');
        }
      } catch (error: any) {
        commit('setError', error.message || 'Database connection failed');
        commit('setDbConnection', false);
        return false;
      } finally {
        commit('setLoading', false);
      }
    },
    
    async sendAgentQuery({ commit }, query) {
      try {
        commit('setLoading', true);
        commit('clearError');
        
        const response = await ApiService.agentQuery(query);
        
        if (response.status === 'success' && response.data) {
          commit('addAgentResponse', {
            query: response.data.query,
            response: response.data.response
          });
          return response.data;
        } else {
          throw new Error(response.message || 'Query failed');
        }
      } catch (error: any) {
        commit('setError', error.message || 'Agent query failed');
        return null;
      } finally {
        commit('setLoading', false);
      }
    },
    
    async sendDbQuery({ commit }, query) {
      try {
        commit('setLoading', true);
        commit('clearError');
        
        const response = await ApiService.dbQuery(query);
        
        if (response.status === 'success' && response.data) {
          commit('addDbResponse', {
            query: response.data.query,
            sqlQuery: response.data.sql_query,
            rawResponse: response.data.raw_response,
            naturalLanguageResponse: response.data.natural_language_response
          });
          return response.data;
        } else {
          throw new Error(response.message || 'Database query failed');
        }
      } catch (error: any) {
        commit('setError', error.message || 'Database query failed');
        return null;
      } finally {
        commit('setLoading', false);
      }
    },
    
    async sendDocQuery({ commit }, query) {
      try {
        commit('setLoading', true);
        commit('clearError');
        
        const response = await ApiService.docQuery(query);
        
        if (response.status === 'success' && response.data) {
          commit('addDocResponse', {
            query: response.data.query,
            response: response.data.response
          });
          return response.data;
        } else {
          throw new Error(response.message || 'Document query failed');
        }
      } catch (error: any) {
        commit('setError', error.message || 'Document query failed');
        return null;
      } finally {
        commit('setLoading', false);
      }
    },
    
    async uploadDocument({ commit }, file) {
      try {
        commit('setLoading', true);
        commit('clearError');
        
        const response = await ApiService.uploadDocument(file);
        
        if (response.status === 'success' && response.data) {
          commit('addUploadedDoc', response.data.filename);
          return true;
        } else {
          throw new Error(response.message || 'Upload failed');
        }
      } catch (error: any) {
        commit('setError', error.message || 'Document upload failed');
        return false;
      } finally {
        commit('setLoading', false);
      }
    }
  }
};

export default queriesModule;