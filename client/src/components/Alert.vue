<template>
  <transition name="slide">
    <div v-if="visible" :class="['alert', alertTypeClass]" role="alert">
      <slot>{{ message }}</slot>
      <button v-if="dismissible" type="button" class="btn-close" @click="closeAlert"></button>
    </div>
  </transition>
</template>

<script>
import { ref, computed, onMounted } from 'vue';

export default {
  props: {
    message: { type: String, default: '' },
    type: { type: String, default: 'info' },
    duration: { type: Number, default: 3000 },
    dismissible: { type: Boolean, default: true },
  },
  emits: ['close'],
  setup(props, { emit }) {
    const visible = ref(true);

    const alertTypeClass = computed(() => ({
      'alert-danger': props.type === 'error',
      'alert-success': props.type === 'success',
      'alert-warning': props.type === 'warning',
      'alert-info': props.type === 'info',
    }));

    function closeAlert() {
      visible.value = false;
      emit('close');
    }

    onMounted(() => {
      if (props.duration > 0) {
        setTimeout(closeAlert, props.duration);
      }
    });

    return { visible, alertTypeClass, closeAlert };
  },
};
</script>

<style scoped>
.alert {
  position: relative;
  padding-right: 3rem;
}
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.5s ease, opacity 0.5s ease;
}
.slide-enter-from,
.slide-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}
.btn-close {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
}
</style>