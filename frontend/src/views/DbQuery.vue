<script setup lang="ts">
import { computed } from 'vue';
import { useStore } from 'vuex';
import QueryBox from '../components/query/QueryBox.vue';
import ResponseCard from '../components/query/ResponseCard.vue';
import DbConnector from '../components/database/DbConnector.vue';
import AlertMessage from '../components/common/AlertMessage.vue';

const store = useStore();
const responses = computed(() => store.getters['queries/getDbResponses']);
const loading = computed(() => store.getters['queries/isLoading']);
const error = computed(() => store.getters['queries/getError']);
const isConnected = computed(() => store.getters['queries/isDatabaseConnected']);

const handleSubmit = async (query: string) => {
  await store.dispatch('queries/sendDbQuery', query);
};
</script>

<template>
  <div class="db-query-container container py-5">
    <div class="row">
      <div class="col-lg-4 mb-4">
        <DbConnector />
      </div>
      
      <div class="col-lg-8">
        <div class="card mb-4">
          <div class="card-header bg-secondary">
            <div class="d-flex justify-content-between align-items-center">
              <div class="d-flex align-items-center">
                <i class="bi bi-database me-2"></i>
                <span class="fw-bold">Database Query</span>
              </div>
            </div>
          </div>
          <div class="card-body">
            <AlertMessage 
              v-if="error" 
              type="danger" 
              :message="error" 
            />
            
            <div v-if="!isConnected" class="text-center my-5">
              <i class="bi bi-plug display-1 text-muted"></i>
              <p class="mt-3 text-muted">Please connect to the database first.</p>
            </div>
            
            <div v-else>
              <div class="chat-container">
                <div v-if="responses.length === 0" class="text-center my-5">
                  <i class="bi bi-database-fill display-1 text-muted"></i>
                  <p class="mt-3 text-muted">Ask a question about your database.</p>
                </div>
                
                <div v-else>
                  <ResponseCard 
                    v-for="(response, index) in responses" 
                    :key="index"
                    :query="response.query"
                    :response="response.naturalLanguageResponse"
                    :sql-query="response.sqlQuery"
                    :raw-response="response.rawResponse"
                    :timestamp="new Date()"
                    type="db"
                  />
                </div>
              </div>
              
              <QueryBox 
                placeholder="Ask a question about your database data..."
                :loading="loading"
                button-text="Query Database"
                @submit="handleSubmit"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.db-query-container {
  min-height: calc(100vh - 56px);
}
</style>