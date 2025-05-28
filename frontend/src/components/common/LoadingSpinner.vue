<script setup lang="ts">
defineProps({
  size: {
    type: String,
    default: 'md'
  },
  color: {
    type: String,
    default: 'primary'
  },
  text: {
    type: String,
    default: 'Loading...'
  },
  showText: {
    type: Boolean,
    default: true
  }
});
</script>

<template>
  <div class="d-flex align-items-center justify-content-center">
    <div 
      class="spinner-border me-2" 
      :class="[
        `text-${color}`, 
        {
          'spinner-border-sm': size === 'sm',
          '': size === 'md',
          'spinner-border-lg': size === 'lg'
        }
      ]" 
      role="status"
    >
      <span class="visually-hidden">Loading...</span>
    </div>
    <span v-if="showText" class="loading-text">{{ text }}</span>
  </div>
</template>

<style scoped>
.spinner-border-lg {
  width: 2.5rem;
  height: 2.5rem;
}

.loading-text {
  font-size: 0.9rem;
  color: var(--neutral-600);
}
</style>