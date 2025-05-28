<script setup lang="ts">
import { onMounted } from 'vue';
import { useStore } from 'vuex';
import Navbar from './components/layout/Navbar.vue';

const store = useStore();

onMounted(() => {
  // Check if there's a token in local storage and initialize auth state
  const token = localStorage.getItem('token');
  if (token) {
    store.dispatch('auth/initializeAuth', token);
  }
});
</script>

<template>
  <Navbar />
  <main>
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </main>
    <footer class="footer">
    <div class="footer-content">
      &copy; 2025 Chatbot. All rights reserved.
    </div>
  </footer>
</template>

<style scoped>
main {
  min-height: calc(100vh - 56px);
  padding-top: 56px;
}
.footer {
  background-color: #f8f8f8;
  padding: 1rem;
  text-align: center;
  border-top: 1px solid #e7e7e7;
  height: 60px;
  width: 100%;
  bottom: 0;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  font-size: 0.9rem;
  color: #666;
}
</style>