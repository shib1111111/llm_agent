<template>
  <div class="login-container">
    <header class="header">
      <h1 class="app-title">SCM Chatbot</h1>
    </header>
    <main class="main-content">
      <div class="row g-0">
        <div class="col-md-6 left-section">
          <div class="intro-container">
            <h2 class="intro-title">Welcome Back</h2>
            <img
              src="/src/assets/scm_chatbot.jpg"
              alt="Login to SCM Chatbot"
              class="left-image"
            />
            <p class="intro-text">
              Log in to query databases, documents, and chat with our intelligent SCM agent!
            </p>
          </div>
        </div>
        <div class="col-md-6 right-section">
          <div class="login-form">
            <h2 class="form-title">Login Here</h2>
            <Alert
              v-if="alertMessage"
              :message="alertMessage"
              :type="alertType"
              @close="alertMessage = ''"
            />
            <form @submit.prevent="handleLogin">
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
              <button type="submit" class="btn login-btn w-100">
                <span>Login</span>
              </button>
            </form>
            <p class="mt-3 text-center login-link">
              New user?
              <router-link to="/signup" class="login-link-hover">Sign up here</router-link>
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
        username: '',
        password: '',
      },
      alertMessage: '',
      alertType: 'info',
    };
  },
  methods: {
    async handleLogin() {
      try {
        console.log('Attempting login with:', this.form);
        const response = await this.store.dispatch('login', this.form);
        console.log('Login successful:', response);
        this.alertMessage = 'Login successful!';
        this.alertType = 'success';
        setTimeout(() => {
          this.router.push('/home');
        }, 1000);
      } catch (error) {
        console.error('Login failed:', error);
        this.alertMessage = error;
        this.alertType = 'error';
      }
    },
  },
};
</script>

<style scoped>
.login-container {
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
.login-form {
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
.login-btn {
  background: #1976d2;
  color: #fff;
  font-weight: 600;
  padding: 0.75rem;
  border-radius: 6px;
  transition: background-color 0.3s ease;
}
.login-btn:hover {
  background: #1565c0;
}
.login-link {
  font-size: 0.9rem;
  color: #555;
}
.login-link-hover {
  color: #1976d2;
  text-decoration: none;
}
.login-link-hover:hover {
  text-decoration: underline;
}
</style>