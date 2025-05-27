<template>
  <div class="signup-container">
    <header class="header">
      <h1 class="app-title">SCM Chatbot</h1>
    </header>
    <main class="main-content">
      <div class="row g-0">
        <div class="col-md-6 left-section">
          <div class="intro-container">
            <h2 class="intro-title">Join SCM Chatbot</h2>
            <img
              src="/src/assets/scm_chatbot.jpg"
              alt="Sign up for SCM Chatbot"
              class="left-image"
            />
            <p class="intro-text">
              Sign up to explore and query with our intelligent chatbot!
            </p>
          </div>
        </div>
        <div class="col-md-6 right-section">
          <div class="signup-form">
            <h2 class="form-title">Register Here</h2>
            <Alert
              v-if="alertMessage"
              :message="alertMessage"
              :type="alertType"
              @close="alertMessage = ''"
            />
            <form @submit.prevent="handleSignup">
              <div class="mb-3">
                <input
                  v-model.trim="form.email"
                  type="email"
                  class="form-control custom-input"
                  placeholder="Email"
                  required
                />
              </div>
              <div class="mb-3">
                <input
                  v-model.trim="form.username"
                  type="text"
                  class="form-control custom-input"
                  placeholder="Username"
                  required
                />
              </div>
              <div class="mb-3">
                <input
                  v-model="form.password"
                  type="password"
                  class="form-control custom-input"
                  placeholder="Password"
                  required
                />
              </div>
              <div class="mb-3">
                <input
                  v-model="form.confirmPassword"
                  type="password"
                  class="form-control custom-input"
                  placeholder="Confirm Password"
                  required
                />
              </div>
              <div class="mb-3">
                <select v-model="form.role" class="form-select custom-input" required>
                  <option value="" disabled>Select Role</option>
                  <option value="user">User</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
              <button type="submit" class="btn signup-btn w-100">
                <span>Sign Up</span>
              </button>
            </form>
            <p class="mt-3 text-center signup-link">
              Already a user?
              <router-link to="/login" class="signup-link-hover">Login here</router-link>
            </p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import Alert from '@/components/Alert.vue';

export default {
  components: { Alert },
  setup() {
    const store = useStore();
    const router = useRouter();
    return { store, router };
  },
  data() {
    return {
      form: {
        email: '',
        username: '',
        password: '',
        confirmPassword: '',
        role: '',
      },
      alertMessage: '',
      alertType: 'info',
    };
  },
  methods: {
    async handleSignup() {
      if (this.form.password !== this.form.confirmPassword) {
        this.alertMessage = 'Passwords do not match.';
        this.alertType = 'error';
        console.error('Signup failed: Passwords do not match');
        return;
      }
      try {
        console.log('Attempting signup with:', this.form);
        const response = await this.store.dispatch('signup', {
          email: this.form.email,
          username: this.form.username,
          password: this.form.password,
          role: this.form.role,
        });
        console.log('Signup successful:', response);
        this.alertMessage = 'Signup successful! Please login.';
        this.alertType = 'success';
        setTimeout(() => {
          this.router.push('/login');
        }, 1000);
      } catch (error) {
        console.error('Signup failed:', error);
        this.alertMessage = error;
        this.alertType = 'error';
      }
    },
  },
};
</script>

<style scoped>
.signup-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  display: flex;
  flex-direction: column;
}
.header {
  padding: 1.5rem;
  text-align: center;
  background: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.app-title {
  font-size: 2rem;
  font-weight: bold;
  color: #1976d2;
}
.main-content {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 2rem;
}
.left-section {
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}
.intro-container {
  text-align: center;
}
.intro-title {
  font-size: 2rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 1rem;
}
.left-image {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin-bottom: 1rem;
}
.intro-text {
  font-size: 1.1rem;
  color: #555;
}
.right-section {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
}
.signup-form {
  background: #ffffff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}
.form-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 1.5rem;
  text-align: center;
}
.custom-input {
  border-radius: 6px;
  border: 1px solid #ced4da;
  padding: 0.75rem;
}
.signup-btn {
  background: #1976d2;
  color: #fff;
  font-weight: 600;
  padding: 0.75rem;
  border-radius: 6px;
  transition: background-color 0.3s ease;
}
.signup-btn:hover {
  background: #1565c0;
}
.signup-link {
  font-size: 0.9rem;
  color: #555;
}
.signup-link-hover {
  color: #1976d2;
  text-decoration: none;
}
.signup-link-hover:hover {
  text-decoration: underline;
}
</style>