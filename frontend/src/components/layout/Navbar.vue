<script setup lang="ts">
import { computed, ref, watchEffect } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

const store = useStore();
const router = useRouter();
const isAuthenticated = computed(() => store.getters['auth/isAuthenticated']);
const currentUser = computed(() => store.getters['auth/currentUser']);

const isCollapsed = ref(true);
const toggleNavbar = () => {
  isCollapsed.value = !isCollapsed.value;
};

const closeNavbar = () => {
  isCollapsed.value = true;
};

const logout = async () => {
  await store.dispatch('auth/logout');
  closeNavbar();
};

// Close navbar on route change
watchEffect(() => {
  router.currentRoute.value.path; // Track route changes
  closeNavbar();
});
</script>

<template>
  <nav class="navbar navbar-expand-lg fixed-top navbar-light bg-white">
    <div class="container">
      <router-link class="navbar-brand d-flex align-items-center" to="/">
        <i class="bi bi-database-fill me-2 text-primary"></i>
        <span class="fw-bold">Chatbot</span>
      </router-link>
      
      <button 
        class="navbar-toggler" 
        type="button" 
        @click="toggleNavbar"
        aria-controls="navbarNav" 
        aria-expanded="false" 
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      
      <div 
        class="collapse navbar-collapse" 
        :class="{ 'show': !isCollapsed }" 
        id="navbarNav"
      >
        <ul class="navbar-nav ms-auto">
          <template v-if="isAuthenticated">
            <li class="nav-item">
              <router-link class="nav-link" to="/">
                <i class="bi bi-robot me-1"></i> Agent
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/db-query">
                <i class="bi bi-database me-1"></i> DB Query
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/doc-query">
                <i class="bi bi-file-text me-1"></i> Doc Query
              </router-link>
            </li>
            <li class="nav-item dropdown">
              <a 
                class="nav-link dropdown-toggle" 
                href="#" 
                id="navbarDropdown" 
                role="button" 
                data-bs-toggle="dropdown" 
                aria-expanded="false"
              >
                <i class="bi bi-person-circle me-1"></i>
                {{ currentUser?.username || 'Account' }}
              </a>
              <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="navbarDropdown">
                <li>
                  <div class="dropdown-item-text">
                    <small class="text-muted">Role: {{ currentUser?.role || 'User' }}</small>
                  </div>
                </li>
                <li><hr class="dropdown-divider"></li>
                <li>
                  <a class="dropdown-item" href="#" @click.prevent="logout">
                    <i class="bi bi-box-arrow-right me-1"></i> Logout
                  </a>
                </li>
              </ul>
            </li>
          </template>
          <template v-else>
            <li class="nav-item">
              <router-link class="nav-link" to="/login">
                <i class="bi bi-box-arrow-in-right me-1"></i> Login
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/signup">
                <i class="bi bi-person-plus me-1"></i> Sign Up
              </router-link>
            </li>
          </template>
        </ul>
      </div>
    </div>
  </nav>

</template>

<style scoped>
.navbar {
  transition: all 0.3s ease;
}

.navbar-brand {
  font-size: 1.4rem;
}

.dropdown-menu {
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

.dropdown-item {
  padding: 8px 16px;
  transition: background-color 0.2s ease;
}

.dropdown-item:hover {
  background-color: var(--neutral-100);
}

.nav-link {
  position: relative;
}

.nav-link::after {
  content: '';
  position: absolute;
  width: 0;
  height: 2px;
  bottom: 0;
  left: 50%;
  background-color: var(--primary);
  transition: width 0.3s ease, left 0.3s ease;
}

.nav-link:hover::after,
.nav-link.router-link-active::after {
  width: 80%;
  left: 10%;
}
</style>