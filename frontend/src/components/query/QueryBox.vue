<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps({
  placeholder: {
    type: String,
    default: 'Type your query here...'
  },
  loading: {
    type: Boolean,
    default: false
  },
  buttonText: {
    type: String,
    default: 'Submit'
  }
});

const emit = defineEmits(['submit']);
const query = ref('');

const submitQuery = () => {
  if (!query.value.trim() || props.loading) return;
  
  emit('submit', query.value);
  query.value = '';
};

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    submitQuery();
  }
};
</script>

<template>
  <div class="query-box">
    <textarea
      v-model="query"
      :placeholder="placeholder"
      @keydown="handleKeydown"
      class="form-control"
      rows="3"
      :disabled="loading"
    ></textarea>
    <button
      class="btn btn-primary mt-2"
      :disabled="loading || !query.trim()"
      @click="submitQuery"
    >
      <span v-if="loading">
        <span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
        Processing...
      </span>
      <span v-else>
        <i class="bi bi-send me-1"></i> {{ buttonText }}
      </span>
    </button>
  </div>
</template>

<style scoped>
.query-box {
  margin-top: 1rem;
  border-radius: 12px;
}

.form-control {
  resize: none;
  border-radius: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.form-control:focus {
  box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.25);
  border-color: var(--primary);
}

.btn {
  border-radius: 8px;
  min-width: 120px;
  font-weight: 500;
  transition: all 0.2s ease;
}
</style>