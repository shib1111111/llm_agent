<template>
  <div class="home-container">
    <Navbar />
    <div class="chat-container">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="chat-title">Chat with SCM Agent</h2>
        <button class="btn btn-outline-primary connect-btn" @click="connectDB">
          Connect to DB
        </button>
      </div>
      <Alert
        v-if="alertMessage"
        :message="alertMessage"
        :type="alertType"
        @close="alertMessage = ''"
      />
      <div class="chat-box">
        <div v-for="message in messages" :key="message.id" class="message" :class="{ 'user-message': message.query }">
          <div v-if="message.query" class="user-query">
            <strong>You:</strong> {{ message.query }}
            <small class="text-muted">{{ message.timestamp }}</small>
          </div>
          <div v-if="message.response" class="bot-response">
            <strong>Agent:</strong> {{ message.response }}
            <small class="text-muted">{{ message.timestamp }}</small>
          </div>
        </div>
      </div>
      <form @submit.prevent="sendQuery" class="input-group mt-4">
        <input
          v-model="query"
          type="text"
          class="form-control custom-input"
          placeholder="Type your query..."
          required
        />
        <button type="submit" class="btn btn-primary">Send</button>
      </form>
    </div>
  </div>
</template>

<script>
import { useStore } from 'vuex';
import Navbar from '@/components/Navbar.vue';
import Alert from '@/components/Alert.vue';

export default {
  components: { Navbar, Alert },
  setup() {
    const store = useStore();
    return { store };
  },
  data() {
    return {
      query: '',
      alertMessage: '',
      alertType: 'info',
    };
  },
  computed: {
    messages() {
      return this.store.state.chatMessages.filter(m => m.type === 'agent');
    },
  },
  methods: {
    async connectDB() {
      try {
        console.log('Attempting to connect to database');
        const response = await this.store.dispatch('connectDB');
        console.log('Database connection successful:', response);
        this.alertMessage = response.message;
        this.alertType = 'success';
      } catch (error) {
        console.error('Database connection failed:', error);
        this.alertMessage = error;
        this.alertType = 'error';
      }
    },
    async sendQuery() {
      try {
        console.log('Sending agent query:', this.query);
        await this.store.dispatch('queryAgent', this.query);
        console.log('Agent query successful');
        this.query = '';
      } catch (error) {
        console.error('Agent query failed:', error);
        this.alertMessage = error;
        this.alertType = 'error';
      }
    },
  },
};
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding-top: 80px;
}
.chat-container {
  max-width: 900px;
  margin: 2rem auto;
  padding: 2rem;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.chat-title {
  font-size: 1.8rem;
  font-weight: 600;
  color: #333;
}
.connect-btn {
  border-radius: 6px;
}
.chat-box {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1.5rem;
  max-height: 600px;
  overflow-y: auto;
  background: #f8f9fa;
}
.message {
  margin-bottom: 1.5rem;
}
.user-query {
  background: #e3f2fd;
  padding: 1rem;
  border-radius: 8px;
  margin-left: 2rem;
}
.bot-response {
  background: #e8f5e9;
  padding: 1rem;
  border-radius: 8px;
  margin-right: 2rem;
}
.user-query, .bot-response {
  position: relative;
}
.text-muted {
  display: block;
  font-size: 0.85rem;
  color: #6c757d;
}
.custom-input {
  border-radius: 6px 0 0 6px;
}
.btn-primary {
  border-radius: 0 6px 6px 0;
}
</style>