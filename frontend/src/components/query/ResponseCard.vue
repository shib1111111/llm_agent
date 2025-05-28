<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps({
  query: {
    type: String,
    required: true
  },
  response: {
    type: String,
    required: true
  },
  timestamp: {
    type: Date,
    default: () => new Date()
  },
  type: {
    type: String,
    default: 'agent',
    validator: (value: string) => ['agent', 'db', 'doc'].includes(value)
  },
  sqlQuery: {
    type: String,
    default: ''
  },
  rawResponse: {
    type: Object,
    default: null
  }
});

const formattedTime = computed(() => {
  return new Intl.DateTimeFormat('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).format(props.timestamp);
});

const typeIcon = computed(() => {
  switch (props.type) {
    case 'agent': return 'bi-robot';
    case 'db': return 'bi-database';
    case 'doc': return 'bi-file-text';
    default: return 'bi-chat-dots';
  }
});

const typeTitle = computed(() => {
  switch (props.type) {
    case 'agent': return 'Agent Query';
    case 'db': return 'Database Query';
    case 'doc': return 'Document Query';
    default: return 'Query';
  }
});

const typeClass = computed(() => {
  switch (props.type) {
    case 'agent': return 'primary';
    case 'db': return 'secondary';
    case 'doc': return 'accent';
    default: return 'primary';
  }
});
</script>

<template>
  <div class="response-card card mb-4">
    <div class="card-header" :class="`bg-${typeClass}`">
      <div class="d-flex justify-content-between align-items-center">
        <div class="d-flex align-items-center">
          <i :class="`bi ${typeIcon} me-2`"></i>
          <span class="fw-bold">{{ typeTitle }}</span>
        </div>
        <small class="text-opacity-75">{{ formattedTime }}</small>
      </div>
    </div>
    <div class="card-body">
      <div class="query mb-3">
        <strong>Your query:</strong>
        <p class="mb-1 user-query">{{ query }}</p>
      </div>
      
      <div class="response">
        <strong>Response:</strong>
        <p class="mb-0 system-response">{{ response }}</p>
      </div>
      
      <div v-if="sqlQuery" class="sql-query mt-3">
        <strong>Generated SQL:</strong>
        <pre class="code-block">{{ sqlQuery }}</pre>
      </div>
      
      <div v-if="rawResponse && type === 'db'" class="raw-results mt-3">
        <strong>Raw Results:</strong>
        <pre class="code-block">{{ JSON.stringify(rawResponse, null, 2) }}</pre>
      </div>
    </div>
  </div>
</template>

<style scoped>
.response-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card-header {
  padding: 12px 16px;
  color: white;
}

.card-header.bg-primary {
  background-color: var(--primary) !important;
}

.card-header.bg-secondary {
  background-color: var(--secondary) !important;
}

.card-header.bg-accent {
  background-color: var(--accent) !important;
}

.user-query {
  background-color: var(--neutral-100);
  padding: 12px;
  border-radius: 8px;
  font-style: italic;
}

.system-response {
  padding: 12px;
  border-radius: 8px;
  background-color: rgba(0, 113, 227, 0.05);
  white-space: pre-line;
}

.code-block {
  background-color: var(--neutral-900);
  color: var(--neutral-100);
  padding: 12px;
  border-radius: 8px;
  font-size: 0.9rem;
  overflow-x: auto;
}
</style>