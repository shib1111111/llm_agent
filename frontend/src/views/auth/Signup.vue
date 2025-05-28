<script setup lang="ts">
import { ref, computed } from 'vue';
import { useStore } from 'vuex';
import AlertMessage from '../../components/common/AlertMessage.vue';
import LoadingSpinner from '../../components/common/LoadingSpinner.vue';

const store = useStore();

const name = ref('');
const email = ref('');
const username = ref('');
const password = ref('');
const confirmPassword = ref('');
const role = ref('admin'); // Default role
const roles = ["admin", "planning", "finance", "operations"]; // Example roles

const loading = computed(() => store.getters['auth/isLoading']);
const error = computed(() => store.getters['auth/authError']);

const validationError = ref('');

const validateForm = () => {
  if (!name.value || !email.value || !username.value || !password.value || !confirmPassword.value) {
    validationError.value = 'All fields are required';
    return false;
  }
  
  if (password.value !== confirmPassword.value) {
    validationError.value = 'Passwords do not match';
    return false;
  }
  
  if (password.value.length < 6) {
    validationError.value = 'Password must be at least 6 characters long';
    return false;
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email.value)) {
    validationError.value = 'Please enter a valid email address';
    return false;
  }
  
  validationError.value = '';
  return true;
};

const handleSignup = async () => {
  if (!validateForm()) return;
  
  await store.dispatch('auth/signup', {
    name: name.value,
    email: email.value,
    username: username.value,
    password: password.value,
    role: role.value
  });
};
</script>

<template>
  <div class="signup-page">
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-content">
          <div class="text-center mb-4">
            <i class="bi bi-person-plus-fill display-4 text-primary"></i>
            <h2 class="mt-3">Create Account</h2>
            <p class="text-muted">Sign up to get started</p>
          </div>
          
          <AlertMessage 
            v-if="error || validationError" 
            type="danger" 
            :message="validationError || error" 
          />
          
          <form @submit.prevent="handleSignup">
            <div class="row">
              <div class="col-md-6 mb-3">
                <label for="name" class="form-label">Full Name</label>
                <div class="input-group">
                  <span class="input-group-text">
                    <i class="bi bi-person"></i>
                  </span>
                  <input 
                    id="name"
                    v-model="name"
                    type="text" 
                    class="form-control" 
                    placeholder="Enter your name"
                    required
                    :disabled="loading"
                  />
                </div>
              </div>
              
              <div class="col-md-6 mb-3">
                <label for="email" class="form-label">Email</label>
                <div class="input-group">
                  <span class="input-group-text">
                    <i class="bi bi-envelope"></i>
                  </span>
                  <input 
                    id="email"
                    v-model="email"
                    type="email" 
                    class="form-control" 
                    placeholder="Enter your email"
                    required
                    :disabled="loading"
                  />
                </div>
              </div>
            </div>
            
            <div class="mb-3">
              <label for="username" class="form-label">Username</label>
              <div class="input-group">
                <span class="input-group-text">
                  <i class="bi bi-at"></i>
                </span>
                <input 
                  id="username"
                  v-model="username"
                  type="text" 
                  class="form-control" 
                  placeholder="Choose a username"
                  required
                  :disabled="loading"
                />
              </div>
            </div>
            
            <div class="row">
              <div class="col-md-6 mb-3">
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
                    placeholder="Choose a password"
                    required
                    :disabled="loading"
                  />
                </div>
              </div>
              
              <div class="col-md-6 mb-3">
                <label for="confirmPassword" class="form-label">Confirm Password</label>
                <div class="input-group">
                  <span class="input-group-text">
                    <i class="bi bi-lock-fill"></i>
                  </span>
                  <input 
                    id="confirmPassword"
                    v-model="confirmPassword"
                    type="password" 
                    class="form-control" 
                    placeholder="Confirm your password"
                    required
                    :disabled="loading"
                  />
                </div>
              </div>
            </div>
            
            <div class="mb-4">
              <label for="role" class="form-label">Role</label>
              <div class="input-group">
                <span class="input-group-text">
                  <i class="bi bi-person-badge"></i>
                </span>
                <select 
                  id="role"
                  v-model="role"
                  class="form-select" 
                  required
                  :disabled="loading"
                >
                  <option v-for="r in roles" :key="r" :value="r">
                    {{ r.charAt(0).toUpperCase() + r.slice(1) }}
                  </option>
                </select>
              </div>
            </div>
            
            <button 
              type="submit" 
              class="btn btn-primary w-100 py-2"
              :disabled="loading"
            >
              <LoadingSpinner v-if="loading" size="sm" text="Creating account..." />
              <span v-else>
                <i class="bi bi-person-plus me-1"></i> Create Account
              </span>
            </button>
            
            <div class="text-center mt-4">
              <p>
                Already have an account? 
                <router-link to="/login" class="text-primary fw-bold">
                  Sign in
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
.signup-page {
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
  max-width: 800px;
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

.form-control, .form-select {
  border-left: none;
  padding: 0.75rem 1rem;
}

.form-control:focus, .form-select:focus {
  box-shadow: none;
  border-color: var(--neutral-300);
}

.input-group:focus-within {
  box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.25);
}

.input-group:focus-within .input-group-text,
.input-group:focus-within .form-control,
.input-group:focus-within .form-select {
  border-color: var(--primary);
}

.btn-primary {
  padding: 0.75rem;
  font-weight: 600;
  font-size: 1.1rem;
}
</style>