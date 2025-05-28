<script setup lang="ts">
import { computed } from 'vue';
import { useStore } from 'vuex';
import QueryBox from '../components/query/QueryBox.vue';
import ResponseCard from '../components/query/ResponseCard.vue';
import DocumentUploader from '../components/document/DocumentUploader.vue';
import AlertMessage from '../components/common/AlertMessage.vue';

const store = useStore();
const responses = computed(() => store.getters['queries/getDocResponses']);
const uploadedDocs = computed(() => store.getters['queries/getUploadedDocs']);
const loading = computed(() => store.getters['queries/isLoading']);
const error = computed(() => store.getters['queries/getError']);

const handleSubmit = async (query: string) => {
  await store.dispatch('queries/sendDocQuery', query);
};
</script>

<template>
  <div class="doc-query-container container py-5">
    <div class="row">
      <div class="col-lg-4 mb-4">
        <DocumentUploader />
        
        <div v-if="uploadedDocs.length > 0" class="card mt-4">
          <div class="card-header bg-accent">
            <div class="d-flex align-items-center">
              <i class="bi bi-files me-2"></i>
              <span class="fw-bold">Uploaded Documents</span>
            </div>
          </div>
          <div class="card-body">
            <ul class="list-group list-group-flush">
              <li v-for="(doc, index) in uploadedDocs" :key="index" class="list-group-item d-flex align-items-center">
                <i class="bi bi-file-pdf me-2 text-danger"></i>
                <span>{{ doc }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
      
      <div class="col-lg-8">
        <div class="card mb-4">
          <div class="card-header bg-accent">
            <div class="d-flex justify-content-between align-items-center">
              <div class="d-flex align-items-center">
                <i class="bi bi-file-text me-2"></i>
                <span class="fw-bold">Document Query</span>
              </div>
            </div>
          </div>
          <div class="card-body">
            <AlertMessage 
              v-if="error" 
              type="danger" 
              :message="error" 
            />
            
            <div class="chat-container">
              <div v-if="responses.length === 0" class="text-center my-5">
                <i class="bi bi-file-earmark-text display-1 text-muted"></i>
                <p class="mt-3 text-muted">Ask a question about your documents.</p>
              </div>
              
              <div v-else>
                <ResponseCard 
                  v-for="(response, index) in responses" 
                  :key="index"
                  :query="response.query"
                  :response="response.response"
                  :timestamp="new Date()"
                  type="doc"
                />
              </div>
            </div>
            
            <QueryBox 
              placeholder="Ask a question about your documents..."
              :loading="loading"
              button-text="Query Documents"
              @submit="handleSubmit"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.doc-query-container {
  min-height: calc(100vh - 56px);
}

.list-group-item {
  border-left: none;
  border-right: none;
  padding: 12px 0;
}
</style>