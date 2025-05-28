<script setup lang="ts">
import { ref, computed } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import AlertMessage from '../../components/common/AlertMessage.vue';
import LoadingSpinner from '../../components/common/LoadingSpinner.vue';

const store = useStore();
const router = useRouter();

const username = ref('');
const password = ref('');
const rememberMe = ref(false);

const loading = computed(() => store.getters['auth/isLoading']);
const error = computed(() => store.getters['auth/authError']);

const handleLogin = async () => {
  if (!username.value || !password.value) return;
  
  const success = await store.dispatch('auth/login', {
    username: username.value,
    password: password.value
  });
  
  if (success) {
    router.push({ name: 'Home' });
  }
};
</script>

<template>
  <div class="login-page">
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-content">
          <div class="text-center mb-4">
            <i class="bi bi-database-fill display-4 text-primary"></i>
            <h2 class="mt-3">Welcome Back</h2>
            <p class="text-muted">Sign in to access your account</p>
          </div>
          
          <AlertMessage 
            v-if="error" 
            type="danger" 
            :message="error" 
          />
          
          <form @submit.prevent="handleLogin">
            <div class="mb-3">
              <label for="username" class="form-label">Username</label>
              <div class="input-group">
                <span class="input-group-text">
                  <i class="bi bi-person"></i>
                </span>
                <input 
                  id="username"
                  v-model="username"
                  type="text" 
                  class="form-control" 
                  placeholder="Enter your username"
                  required
                  :disabled="loading"
                />
              </div>
            </div>
            
            <div class="mb-4">
              <label for="password" class="form-label">Password</label>
              <div class="input-group">
                <span class="input-group-text">
                  <i class="bi bi-lock"></i>
                </span>
                <input 
                  id="password"
                  v-model="password"
                  type="password" 
                  class="form-control" 
                  placeholder="Enter your password"
                  required
                  :disabled="loading"
                />
              </div>
            </div>
            
            <div class="mb-4">
              <div class="form-check">
                <input 
                  id="rememberMe"
                  v-model="rememberMe"
                  type="checkbox" 
                  class="form-check-input" 
                  :disabled="loading"
                />
                <label class="form-check-label" for="rememberMe">
                  Remember me
                </label>
              </div>
            </div>
            
            <button 
              type="submit" 
              class="btn btn-primary w-100 py-2"
              :disabled="loading || !username || !password"
            >
              <LoadingSpinner v-if="loading" size="sm" text="Signing in..." />
              <span v-else>
                <i class="bi bi-box-arrow-in-right me-1"></i> Sign In
              </span>
            </button>
            
            <div class="text-center mt-4">
              <p>
                Don't have an account? 
                <router-link to="/signup" class="text-primary fw-bold">
                  Sign up
                </router-link>
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
  
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.auth-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: center;
}

.auth-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 24px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 500px;
  overflow: hidden;
}

.auth-content {
  padding: 3rem;
}

.input-group-text {
  background-color: var(--neutral-100);
  border-right: none;
  padding: 0.75rem 1rem;
}

.form-control {
  border-left: none;
  padding: 0.75rem 1rem;
}

.form-control:focus {
  box-shadow: none;
  border-color: var(--neutral-300);
}

.input-group:focus-within {
  box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.25);
}

.input-group:focus-within .input-group-text,
.input-group:focus-within .form-control {
  border-color: var(--primary);
}

.form-check-input:checked {
  background-color: var(--primary);
  border-color: var(--primary);
}

.btn-primary {
  padding: 0.75rem;
  font-weight: 600;
  font-size: 1.1rem;
}
</style>