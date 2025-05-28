<script setup lang="ts">
import { ref, watch } from 'vue';

const props = defineProps({
  type: {
    type: String,
    default: 'info',
    validator: (value: string) => ['info', 'success', 'warning', 'danger'].includes(value)
  },
  message: {
    type: String,
    required: true
  },
  dismissible: {
    type: Boolean,
    default: true
  },
  autoClose: {
    type: Boolean,
    default: false
  },
  duration: {
    type: Number,
    default: 5000
  }
});

const visible = ref(true);
let timer: number | null = null;

const dismiss = () => {
  visible.value = false;
  if (timer) {
    clearTimeout(timer);
    timer = null;
  }
};

watch(() => props.message, () => {
  visible.value = true;
  if (props.autoClose) {
    if (timer) clearTimeout(timer);
    timer = window.setTimeout(dismiss, props.duration);
  }
}, { immediate: true });
</script>

<template>
  <transition name="fade">
    <div 
      v-if="visible" 
      class="alert mb-4" 
      :class="`alert-${type}`" 
      role="alert"
    >
      <div class="d-flex align-items-center">
        <i 
          class="bi me-2" 
          :class="{
            'bi-info-circle-fill': type === 'info',
            'bi-check-circle-fill': type === 'success',
            'bi-exclamation-triangle-fill': type === 'warning',
            'bi-x-circle-fill': type === 'danger'
          }"
        ></i>
        <div>{{ message }}</div>
      </div>
      <button 
        v-if="dismissible" 
        type="button" 
        class="btn-close" 
        @click="dismiss" 
        aria-label="Close"
      ></button>
    </div>
  </transition>
</template>

<style scoped>
.alert {
  position: relative;
  border: none;
  border-radius: 8px;
  padding: 12px 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.alert-info {
  background-color: rgba(13, 110, 253, 0.1);
  color: #0d6efd;
}

.alert-success {
  background-color: rgba(25, 135, 84, 0.1);
  color: #198754;
}

.alert-warning {
  background-color: rgba(255, 193, 7, 0.1);
  color: #ffc107;
}

.alert-danger {
  background-color: rgba(220, 53, 69, 0.1);
  color: #dc3545;
}

.btn-close {
  position: absolute;
  top: 12px;
  right: 12px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>