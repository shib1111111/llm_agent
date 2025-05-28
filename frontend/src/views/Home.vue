<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import QueryBox from '../components/query/QueryBox.vue';
import ResponseCard from '../components/query/ResponseCard.vue';
import AlertMessage from '../components/common/AlertMessage.vue';

const store = useStore();
const responses = computed(() => store.getters['queries/getAgentResponses']);
const loading = computed(() => store.getters['queries/isLoading']);
const error = computed(() => store.getters['queries/getError']);

const welcomeMessage = ref('');
const showWelcome = ref(false);

onMounted(() => {
  const currentUser = store.getters['auth/currentUser'];
  if (currentUser) {
    welcomeMessage.value = `Welcome ! I'm your AI assistant. How can I help you today?`;
    showWelcome.value = true;
  }
});

const handleSubmit = async (query: string) => {
  await store.dispatch('queries/sendAgentQuery', query);
};
</script>

<template>
  <div class="home-container container py-5">
    <div class="row">
      <div class="col-lg-10 mx-auto">
        <div class="card mb-4">
          <div class="card-header bg-primary">
            <div class="d-flex justify-content-between align-items-center">
              <div class="d-flex align-items-center">
                <i class="bi bi-robot me-2"></i>
                <span class="fw-bold">AI Assistant</span>
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
              <div v-if="showWelcome && responses.length === 0" class="system-message p-3 mb-4">
                <p class="mb-0">{{ welcomeMessage }}</p>
              </div>
              
              <div v-if="responses.length === 0 && !showWelcome" class="text-center my-5">
                <i class="bi bi-chat-dots display-1 text-muted"></i>
                <p class="mt-3 text-muted">Ask me anything about your data or documents.</p>
              </div>
              
              <div v-else>
                <ResponseCard 
                  v-for="(response, index) in responses" 
                  :key="index"
                  :query="response.query"
                  :response="response.response"
                  :timestamp="new Date()"
                  type="agent"
                />
              </div>
            </div>
            
            <QueryBox 
              placeholder="Ask me anything about your data or documents..."
              :loading="loading"
              button-text="Ask Question"
              @submit="handleSubmit"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-container {
  min-height: calc(100vh - 56px);
}

.system-message {
  background-color: var(--neutral-200);
  border-radius: 16px 16px 16px 4px;
  max-width: 80%;
}
</style>