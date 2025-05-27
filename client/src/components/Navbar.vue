<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary fixed-top shadow">
    <div class="container-fluid px-4">
      <router-link class="navbar-brand fw-bold" to="/home">
        SCM Chatbot
      </router-link>
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarContent"
        aria-controls="navbarContent"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarContent">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li class="nav-item">
            <router-link class="nav-link nav-btn" to="/home" active-class="active">Home</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link nav-btn" to="/db-query" active-class="active">Direct Query DB</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link nav-btn" to="/doc-query" active-class="active">Direct Query Doc</router-link>
          </li>
        </ul>
        <div class="d-flex align-items-center">
          <button v-if="isAuthenticated" class="btn btn-outline-light logout-btn" @click="handleLogout">
            Logout
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
import axios from 'axios';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

const BASE_URL = `${import.meta.env.VITE_BASE_URL}/api`;

export default {
  name: 'Navbar',
  setup() {
    const store = useStore();
    const router = useRouter();
    return { store, router };
  },
  computed: {
    isAuthenticated() {
      return !!this.store.state.access_token;
    },
  },
  methods: {
    async handleLogout() {
      try {
        console.log('Attempting logout');
        await this.store.dispatch('logout');
        console.log('Logout successful');
        this.router.push('/login');
      } catch (error) {
        console.error('Logout failed:', error);
        this.store.commit('clearAuth');
        this.router.push('/login');
      }
    },
  },
};
</script>

<style scoped>
.navbar {
  padding: 1rem;
}
.nav-btn {
  color: #ffffff;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}
.nav-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}
.active {
  background-color: #ffffff;
  color: #1976d2 !important;
}
.logout-btn {
  border-radius: 4px;
  padding: 0.5rem 1rem;
}
.logout-btn:hover {
  background-color: #ffffff;
  color: #dc3545;
}
@media (max-width: 991px) {
  .navbar-nav {
    margin-top: 1rem;
    text-align: center;
  }
  .nav-item {
    margin-bottom: 0.5rem;
  }
  .logout-btn {
    margin-top: 1rem;
    width: 100%;
  }
}
</style>