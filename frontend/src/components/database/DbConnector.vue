<script setup lang="ts">
import { ref, computed } from 'vue';
import { useStore } from 'vuex';
import AlertMessage from '../common/AlertMessage.vue';

const store = useStore();
const connecting = ref(false);
const errorMessage = ref('');
const showSchema = ref(false);

const isConnected = computed(() => store.getters['queries/isDatabaseConnected']);
const dbSchema = computed(() => store.getters['queries/databaseSchema']);

const connectToDatabase = async () => {
  connecting.value = true;
  errorMessage.value = '';
  
  try {
    const result = await store.dispatch('queries/connectToDatabase');
    
    if (result) {
      showSchema.value = true;
    } else {
      errorMessage.value = 'Failed to connect to database. Please try again.';
    }
  } catch (error: any) {
    errorMessage.value = error.message || 'Database connection failed. Please try again.';
  } finally {
    connecting.value = false;
  }
};

const toggleSchema = () => {
  showSchema.value = !showSchema.value;
};
</script>

<template>
  <div class="db-connector card">
    <div class="card-header bg-secondary">
      <div class="d-flex justify-content-between align-items-center">
        <div class="d-flex align-items-center">
          <i class="bi bi-database me-2"></i>
          <span class="fw-bold">Database Connection</span>
        </div>
        <div v-if="isConnected" class="badge bg-success">
          <i class="bi bi-check-circle-fill me-1"></i> Connected
        </div>
      </div>
    </div>
    <div class="card-body">
      <AlertMessage 
        v-if="errorMessage" 
        type="danger" 
        :message="errorMessage" 
        :auto-close="true" 
      />
      
      <div v-if="!isConnected">
        <p>Connect to the database to view schema and run queries.</p>
        <button 
          class="btn btn-secondary" 
          @click="connectToDatabase" 
          :disabled="connecting"
        >
          <span v-if="connecting">
            <span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
            Connecting...
          </span>
          <span v-else>
            <i class="bi bi-plug me-1"></i> Connect to Database
          </span>
        </button>
      </div>
      
      <div v-else>
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h5 class="mb-0">Database Connected</h5>
          <button class="btn btn-sm btn-outline-secondary" @click="toggleSchema">
            <i :class="['bi', showSchema ? 'bi-eye-slash' : 'bi-eye']"></i>
            {{ showSchema ? 'Hide Schema' : 'Show Schema' }}
          </button>
        </div>
        
        <div v-if="showSchema" class="schema-container">
          <h6>Database Schema:</h6>
          <pre class="code-block">{{ JSON.stringify(dbSchema, null, 2) }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.db-connector {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card-header.bg-secondary {
  background-color: var(--secondary) !important;
  color: white;
}

.schema-container {
  margin-top: 1rem;
}

.code-block {
  background-color: var(--neutral-900);
  color: var(--neutral-100);
  padding: 12px;
  border-radius: 8px;
  font-size: 0.9rem;
  max-height: 300px;
  overflow-y: auto;
}

.btn-secondary {
  background-color: var(--secondary);
  border-color: var(--secondary);
}

.btn-secondary:hover, .btn-secondary:focus {
  background-color: var(--secondary-dark);
  border-color: var(--secondary-dark);
}

.btn-outline-secondary {
  color: var(--secondary);
  border-color: var(--secondary);
}

.btn-outline-secondary:hover, .btn-outline-secondary:focus {
  background-color: var(--secondary);
  color: white;
}
</style>